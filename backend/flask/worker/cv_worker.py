import json
import sys
import time
import signal
import uuid
from pathlib import Path
from datetime import datetime, timezone

current_dir = Path(__file__).resolve().parent
flask_dir = current_dir.parent
backend_dir = flask_dir.parent

for p in [flask_dir, backend_dir]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

llm_service_dir = backend_dir / "service" / "llm_service"
if str(llm_service_dir) not in sys.path:
    sys.path.insert(0, str(llm_service_dir))

from src.core.agent_engine.manager import CareerAgentManager

from core.redis_client import (
    redis_client,
    STREAM_NAME,
    DLQ_STREAM_NAME,
    GROUP_NAME,
    MAX_RETRY,
)

# ---------- Config ----------
CONSUMER_NAME = f"worker-{uuid.uuid4().hex[:6]}"
BLOCK_MS = 5000  # XREADGROUP block 5 秒
BATCH_SIZE = 1   # 一次拉1筆

_running = True


def _run_analysis(survey_data: dict) -> dict:
    """
    Stub wrapper — 測試時會被 monkeypatch 覆蓋，不會真正呼叫 LLM。
    正式環境才會執行 API_test_main.run_analysis。
    """
    # from API_test_main import run_analysis
    # return run_analysis(survey_data)
    raise NotImplementedError(
        "_run_analysis 尚未注入實作，請確認 API_test_main 是否可匯入"
    )


def _signal_handler(sig, frame):
    global _running
    print(f"[Worker {CONSUMER_NAME}] 收到終止信號，準備關閉...")
    _running = False


signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


def ensure_group():
    try:
        redis_client.xgroup_create(STREAM_NAME, GROUP_NAME, id="0", mkstream=True)
        print(f"[Worker] 建立 consumer group '{GROUP_NAME}' on '{STREAM_NAME}'")
    except Exception as e:
        if "BUSYGROUP" in str(e):
            print(f"[Worker] Consumer group '{GROUP_NAME}' 已存在，繼續...")
        else:
            raise

def process_job(job_id: str, task_type: str) -> dict:

    hash_key = f"job:{job_id}"
    job_data = redis_client.hgetall(hash_key)

    if not job_data:
        raise ValueError(f"Job {job_id} not found in Redis")

    print(f"[Worker {CONSUMER_NAME}] 開始處理 job={job_id} task_type={task_type} ...")

    # ===== survey_analysis: 呼叫 CareerAgentManager =====
    if task_type == "survey_analysis":
        user_id = job_data.get("user_id", "")

        # 從 career_survey 表取最新的 questionnaire_response 和 personality
        from core.supabase_client import supabase

        survey_row = (
            supabase.table("career_survey")
            .select("questionnaire_response, personality")
            .eq("user_id", user_id)
            .order("survey_id", desc=True)
            .limit(2)
            .execute()
        )

        if not survey_row.data:
            raise ValueError(f"career_survey 中找不到 user_id={user_id} 的問卷資料")

        # questionnaire_response 和 personality 分別存在不同的 row，合併取值
        survey_dict = {}
        trait_dict = {}
        for row in survey_row.data:
            if not survey_dict and row.get("questionnaire_response"):
                survey_dict = row["questionnaire_response"]
            if not trait_dict and row.get("personality"):
                trait_dict = row["personality"]

        # 移除 trait_raw_responses（不送給 model）
        trait_dict.pop("trait_raw_responses", None)

        print(f"[Worker {CONSUMER_NAME}] survey_dict={survey_dict}")
        print(f"[Worker {CONSUMER_NAME}] trait_dict={trait_dict}")
        survey_json_str = json.dumps(survey_dict, ensure_ascii=False)
        trait_json_str = json.dumps(trait_dict, ensure_ascii=False)

        user_input = {
            "user_id": user_id,
            "survey_json": survey_json_str,
            "trait_json": trait_json_str,
        }

        manager = CareerAgentManager()
        report = manager.run_task(task_type_str="career_analysis", user_input=user_input)

        if report.get("status") == "error":
            raise RuntimeError(report.get("message", "Unknown error in LLM"))

        return {"result": report, "suggestions": {}}


    elif task_type == "resume_analysis":
        user_id = job_data.get("user_id", "")
        user_input = {"user_id": user_id}
        manager = CareerAgentManager()

        # 1. 取得履歷分析 (D-03 Suggestions)
        report_analysis = manager.run_task(task_type_str="resume_analysis", user_input=user_input)
        if isinstance(report_analysis, dict) and report_analysis.get("status") == "error":
            raise RuntimeError(report_analysis.get("message", "Unknown error in LLM (resume_analysis)"))

        return {"result": {}, "suggestions": report_analysis}

    elif task_type == "resume_opt":
        user_id = job_data.get("user_id", "")
        user_input = {"user_id": user_id}
        manager = CareerAgentManager()

        # 2. 取得履歷優化 (D-04 Results)
        report_opt = manager.run_task(task_type_str="resume_opt", user_input=user_input)
        if isinstance(report_opt, dict) and report_opt.get("status") == "error":
            raise RuntimeError(report_opt.get("message", "Unknown error in LLM (resume_opt)"))

        return {"result": report_opt, "suggestions": {}}


class NonRecoverableError(Exception):
    """自訂不可恢復之錯誤 Exception (如: Parser Error, 400 Bad Request 等)"""
    pass


def handle_message(msg_id: str, fields: dict):
    """處理一筆 stream message。"""
    job_id = fields.get("job_id", "")
    task_type = fields.get("task_type", "resume_analysis")
    retry_count = int(fields.get("retry_count", "0"))
    hash_key = f"job:{job_id}"
    now = datetime.now(timezone.utc).isoformat()

    try:
        redis_client.hset(hash_key, mapping={
            "status": "processing",
            "updated_at": now,
        })

        output = process_job(job_id, task_type)

        redis_client.hset(hash_key, mapping={
            "status": "done",
            "result": json.dumps(output["result"], ensure_ascii=False),
            "suggestions": json.dumps(output["suggestions"], ensure_ascii=False),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })

        # ACK
        redis_client.xack(STREAM_NAME, GROUP_NAME, msg_id)
        print(f"[Worker {CONSUMER_NAME}] job={job_id} 完成")

    except Exception as e:
        error_msg = str(e)
        
        # 判斷是否為不可恢復錯誤
        is_non_recoverable = False
        if isinstance(e, NonRecoverableError):
            is_non_recoverable = True
        elif "JSON" in error_msg.upper() or "400" in error_msg:
            is_non_recoverable = True

        if is_non_recoverable:
             print(f"[Worker {CONSUMER_NAME}] job={job_id} 發生不可恢復錯誤: {e}")
             redis_client.xadd(DLQ_STREAM_NAME, {
                 "job_id": job_id,
                 "task_type": fields.get("task_type", ""),
                 "retry_count": str(retry_count),
                 "error": str(e),
                 "failed_at": datetime.now(timezone.utc).isoformat(),
             })
             redis_client.hset(hash_key, mapping={
                 "status": "dlq",
                 "error": f"不可恢復的錯誤: {e}",
                 "updated_at": datetime.now(timezone.utc).isoformat(),
             })
             redis_client.xack(STREAM_NAME, GROUP_NAME, msg_id)
             return

        retry_count += 1
        print(f"[Worker {CONSUMER_NAME}] job={job_id} 失敗 (retry={retry_count}/{MAX_RETRY}): {e}")

        if retry_count >= MAX_RETRY:
            # 超過重試上限 → DLQ
            redis_client.xadd(DLQ_STREAM_NAME, {
                "job_id": job_id,
                "task_type": fields.get("task_type", ""),
                "retry_count": str(retry_count),
                "error": str(e),
                "failed_at": datetime.now(timezone.utc).isoformat(),
            })
            redis_client.hset(hash_key, mapping={
                "status": "dlq",
                "error": f"超過重試上限 ({MAX_RETRY} 次): {e}",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })
            # ACK 掉原訊息（已轉到 DLQ）
            redis_client.xack(STREAM_NAME, GROUP_NAME, msg_id)
            print(f"[Worker {CONSUMER_NAME}] 🪦 job={job_id} 已移至 DLQ")
        else:
            # Exponential Backoff 機制
            backoff_seconds = (2 ** retry_count) # 2, 4, 8 秒延遲
            print(f"[Worker {CONSUMER_NAME}] 等待 {backoff_seconds} 秒後重新排隊...")
            time.sleep(backoff_seconds)
            
            # 重新排隊（新 message）
            redis_client.xadd(STREAM_NAME, {
                "job_id": job_id,
                "task_type": fields.get("task_type", ""),
                "retry_count": str(retry_count),
            })
            redis_client.hset(hash_key, mapping={
                "status": "retrying",
                "retry_count": str(retry_count),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })
            # ACK 掉舊訊息
            redis_client.xack(STREAM_NAME, GROUP_NAME, msg_id)
            print(f"[Worker {CONSUMER_NAME}] job={job_id} 重新排隊 (retry={retry_count})")



def main():
    ensure_group()
    print(f"[Worker {CONSUMER_NAME}] 啟動，等待任務... (stream={STREAM_NAME}, group={GROUP_NAME})")

    while _running:
        try:
            # XREADGROUP：讀新訊息（">" = 尚未投遞給任何 consumer 的）
            messages = redis_client.xreadgroup(
                GROUP_NAME,
                CONSUMER_NAME,
                {STREAM_NAME: ">"},
                count=BATCH_SIZE,
                block=BLOCK_MS,
            )

            if not messages:
                continue  # timeout，繼續等

            for stream_name, msg_list in messages:
                for msg_id, fields in msg_list:
                    handle_message(msg_id, fields)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[Worker {CONSUMER_NAME}] Loop 錯誤: {e}")
            time.sleep(2)  # backoff

    print(f"[Worker {CONSUMER_NAME}] 已關閉。")


if __name__ == "__main__":
    main()

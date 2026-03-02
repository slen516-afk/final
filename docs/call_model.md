# 模型接收的前端參數

### 💡 履歷分析

參數1 - task_type_str = **resume_analysis**

參數2 - 將下表資料包成字典型態

| key     | value      | 型別 |
| ------- | ---------- | ---- |
| user_id | <使用者ID> | str  |

### 💡 履歷優化

參數1 - task_type_str = **resume_opt**

參數2 - 將下表資料包成字典型態

| key     | value      | 型別 |
| ------- | ---------- | ---- |
| user_id | <使用者ID> | str  |

### 💡 缺口分析

參數 1 - task_type_str：**career_analysis**

參數 2 - 下方參數，以字典結構打包

| key         | value                  | 型別 |
| ----------- | ---------------------- | ---- |
| user_id     | <使用者ID>             | str  |
| survey_json | <職能問卷填寫結果>     | str  |
| trait_json  | <人格特質問卷填寫結果> | str  |

# 📝 直串 `manager.py` 測試步驟 (以職能缺口分析為例)

目前 `cv_worker.py` 已改為直接導入 `src.core.agent_engine.manager.CareerAgentManager` 呼叫模型（路徑解析皆使用 `pathlib.Path` 而非 `os`），你可以透過以下兩種方式進行測試：

### 方式一：透過 API 與 Worker 進行完整流程測試

1. **啟動 Redis 伺服器** (確保 Docker 或本機 Redis 已執行)
2. **啟動 Worker** (會監聽 Redis Queue)

   ```shell
   cd backend/flask
   python -m worker.cv_worker
   ```
3. **啟動 Flask API 伺服器**

   ```shell
   cd backend/flask
   python app.py
   ```
4. **送出 API 請求**

   - **POST** `/api/analysis/tasks` 帶入 `resume_id`, `survey_id` 以及 `task_type: "resume_analysis"` 或 `"resume_opt"`
   - 取得 `job_id`
   - **GET** `/api/analysis/jobs/<job_id>` 輪詢結果，Worker 會在背後直接調用 `manager.run_task()` 跑 CrewAI 任務並回傳結構化 JSON。

### 方式二：本機直接寫 Script 呼叫 (不透過 API 與 Queue)

如果想單獨測試 `CareerAgentManager` 模型產出是否符合預期，可建立一個簡單 Python 腳本（例如 `test_manager.py`）：

```python
import json
import sys
from pathlib import Path

# 使用 pathlib 載入 llm_service 模組
root_dir = Path(__file__).resolve().parent
llm_service_dir = root_dir / "llm_service"
sys.path.insert(0, str(llm_service_dir))

from src.core.agent_engine.manager import CareerAgentManager

def test_career_analysis():
    # 準備假資料
    user_id = "test_user_001"
    survey_data = {
        "module_a": {"q1_languages": ["Python", "JavaScript"]},
        "module_b": {},
        "module_c": {},
        "module_d": {}
    }
  
    # 依照 💡 缺口分析 定義的輸入參數
    user_input = {
        "user_id": user_id,
        "survey_json": json.dumps(survey_data, ensure_ascii=False),
        "trait_json": "{}"
    }

    # 初始化管理器並執行
    manager = CareerAgentManager(model_name="o3-mini")
    print("啟動 CrewAI...")
  
    # 測試職能缺口分析
    report = manager.run_task(
        task_type_str="career_analysis",
        user_input=user_input
    )
  
    print("\n--- 產出結果 (career_analysis) ---")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    # 測試履歷優化建議 (D-03)
    report_resume_analysis = manager.run_task(
        task_type_str="resume_analysis",
        user_input={"user_id": user_id}
    )
    print("\n--- 產出結果 (resume_analysis) ---")
    print(json.dumps(report_resume_analysis, indent=2, ensure_ascii=False))

    # 測試履歷優化生成 (D-04)
    report_resume_opt = manager.run_task(
        task_type_str="resume_opt",
        user_input={"user_id": user_id}
    )
    print("\n--- 產出結果 (resume_opt) ---")
    print(json.dumps(report_resume_opt, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_career_analysis()
```

執行該檔案將可驗證模型輸出的結構是否與預期相符。

---

## 🧪 Mock 模式（不呼叫 LLM）

`CareerAgentManager` 支援 **Mock 模式**，啟用後不會初始化 LLM / Supabase，也不會執行 CrewAI pipeline，直接回傳符合 Pydantic schema 的假資料。適用於前後端串接測試、CI 環境。

### 啟用方式

**方式 A：環境變數**

```shell
# Windows
set MOCK_MODE=true

# Linux / macOS
export MOCK_MODE=true
```

設定後啟動 Worker 或直呼 `CareerAgentManager()` 即自動進入 Mock 模式。

**方式 B：建構子參數**

```python
manager = CareerAgentManager(mock_mode=True)
```

### Mock 回傳結構

| task_type_str                                                                           | 對應 Pydantic Model    | Mock 資料辨識               |
| --------------------------------------------------------------------------------------- | ---------------------- | --------------------------- |
| `career_analysis` / `career_analysis_experienced` / `career_analysis_entry_level` | `CareerReport`       | 文字均以 `【Mock】` 開頭  |
| `resume_analysis`                                                                     | `ResumeAnalysis`     | 同上                        |
| `resume_opt`                                                                          | `ResumeOptimization` | 同上                        |
| 其他                                                                                    | 通用 stub              | `{"status": "mock", ...}` |

### 搭配 Worker 完整測試

```shell
# 1. 啟動 Redis
docker compose up redis -d

# 2. 以 Mock 模式啟動 Worker
set MOCK_MODE=true
cd backend/flask
python -m worker.cv_worker

# 3. 另一個終端啟動 Flask API
cd backend/flask
python app.py

# 4. 用 curl / Postman 打 API，Worker 會回傳假資料
```

### 直接呼叫測試

```python
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "llm_service"))
from src.core.agent_engine.manager import CareerAgentManager

manager = CareerAgentManager(mock_mode=True)

# 缺口分析
result = manager.run_task("career_analysis", {"user_id": "test_001", "survey_json": "{}", "trait_json": "{}"})
print(json.dumps(result, indent=2, ensure_ascii=False))

# 履歷分析
result = manager.run_task("resume_analysis", {"user_id": "test_001"})
print(json.dumps(result, indent=2, ensure_ascii=False))

# 履歷優化
result = manager.run_task("resume_opt", {"user_id": "test_001"})
print(json.dumps(result, indent=2, ensure_ascii=False))
```

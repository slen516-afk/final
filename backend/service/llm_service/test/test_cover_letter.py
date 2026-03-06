import os
import json
# import pytest
from src.core.agent_engine.manager import CareerAgentManager

def test_cover_letter_flow_with_optimization_id():
    """
    測試求職推薦信模組 (使用 optimization_id)。
    """
    manager = CareerAgentManager()
    
    # 模擬前端傳入的參數
    user_id = "2"
    task_type_str = "cover_letter"
    
    # 使用指定的 optimization_id 與 job_id
    user_input = {
        "user_id": user_id,
        "optimization_id": "7", 
        "resume_id":"",
        "job_id": 60 # 假設 job_id 為 60
    }
    
    print(f">>> 啟動 Cover Letter 推薦測試 (使用 optimization_id)...")
    print(f">>> 模擬前端傳入 - User ID: {user_id}, Optimization ID: {user_input['optimization_id']}")
    print(f">>> 職缺 ID: {user_input['job_id']}")
    
    try:
        final_result = manager.run_task(
            task_type_str=task_type_str,
            user_input=user_input,
        )
        
        # 驗證生成結果結構
        assert "subject" in final_result, "回傳結果應包含主旨 (subject)"
        assert "content" in final_result, "回傳結果應包含正文 (content)"
        
        print("\n" + "="*50)
        print("[測試成功] 求職信生成成功！(optimization_id)")
        print(f"[主旨]: {final_result['subject']}")
        print("-" * 30)
        print("[正文內容]:")
        print(final_result["content"])
        print("="*50 + "\n")
        print("完整輸出結構")
        print(final_result)
        
    except Exception as e:
        print(f"\n❌ [測試失敗] 流程執行出現錯誤: {e}")
        pytest.fail(f"Cover Letter 流程執行失敗 (optimization_id): {e}")

def test_cover_letter_flow_with_resume_id():
    """
    測試求職推薦信模組 (使用 resume_id)。
    """
    manager = CareerAgentManager()
    
    # 模擬前端傳入的參數
    user_id = "4"
    task_type_str = "cover_letter"
    
    # 使用指定的 resume_id 與 job_id
    user_input = {
        "user_id": user_id,
        "resume_id": "4", 
        "optimization_id": "",
        "job_id": 61 # 假設 job_id 為 61
    }
    
    print(f">>> 啟動 Cover Letter 推薦測試 (使用 resume_id)...")
    print(f">>> 模擬前端傳入 - User ID: {user_id}, Resume ID: {user_input['resume_id']}")
    print(f">>> 職缺 ID: {user_input['job_id']}")
    
    try:
        final_result = manager.run_task(
            task_type_str=task_type_str,
            user_input=user_input,
        )
        
        # 驗證生成結果結構
        assert "subject" in final_result, "回傳結果應包含主旨 (subject)"
        assert "content" in final_result, "回傳結果應包含正文 (content)"
        
        print("\n" + "="*50)
        print("[測試成功] 求職信生成成功！(resume_id)")
        print(f"[主旨]: {final_result['subject']}")
        print("-" * 30)
        print("[正文內容]:")
        print(final_result["content"])
        print("="*50 + "\n")
        print("完整輸出結構")
        print(final_result)
        
    except Exception as e:
        print(f"\n❌ [測試失敗] 流程執行出現錯誤: {e}")
        pytest.fail(f"Cover Letter 流程執行失敗 (resume_id): {e}")

if __name__ == "__main__":
    # print("=== 執行 Cover Letter 測試 ===")
    # print("1. 測試 optimization_id")
    # test_cover_letter_flow_with_optimization_id()
    
    print("\n2. 測試 resume_id")
    test_cover_letter_flow_with_resume_id()

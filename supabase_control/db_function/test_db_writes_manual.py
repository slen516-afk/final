"""
最小可跑測試：直接呼叫一個 db_writes 函數，確認連線與寫入正常。

邏輯與其他 db_writes 函數相同，測通此處即可類推到問卷、個人檔案、履歷等。

執行方式（擇一）：
  cd supabase_control
  python db_function/test_db_writes_manual.py

  # 或從專案根目錄
  set PYTHONPATH=supabase_control
  python supabase_control/db_function/test_db_writes_manual.py
"""

import os
import sys

# 讓 import db_function 可找到（supabase_control 要在 path 裡）
_this_dir = os.path.dirname(os.path.abspath(__file__))
_supabase_control = os.path.dirname(_this_dir)
if _supabase_control not in sys.path:
    sys.path.insert(0, _supabase_control)

def main():
    from db_function.db_writes import create_upload_event

    print("=" * 50)
    print("測試 db_writes：create_upload_event")
    print("=" * 50)

    # 使用測試用參數（請依你的 DB 調整 user_id，或先用 1）
    user_id = 1
    file_name = "test_resume.pdf"
    file_path = "uploads/user_1/test_resume.pdf"

    try:
        result = create_upload_event(
            user_id=user_id,
            file_name=file_name,
            file_path=file_path,
            upload_type="resume",
        )
        print("OK 寫入成功")
        print("回傳資料:", result)
        return 0
    except FileNotFoundError as e:
        print("請在 supabase_control/ 或 supabase_control/Erd/ 放置 .env")
        print("內容需有: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY")
        print("錯誤:", e)
        return 1
    except ValueError as e:
        print("參數錯誤:", e)
        return 1
    except RuntimeError as e:
        print("寫入失敗:", e)
        return 1
    except Exception as e:
        print("未預期錯誤:", e)
        return 1

if __name__ == "__main__":
    sys.exit(main())

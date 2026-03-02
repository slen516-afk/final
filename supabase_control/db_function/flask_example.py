"""
最小 Flask 範例：一個 route 呼叫 db_writes，示範後端怎麼接、怎麼呼叫、怎麼回傳。

邏輯與其他 db_writes 函數相同，接到後端併進專案時可照同樣方式接問卷、個人檔案、履歷等。

執行方式（擇一）：
  cd supabase_control
  python db_function/flask_example.py

  # 或從專案根目錄
  set PYTHONPATH=supabase_control
  python supabase_control/db_function/flask_example.py

啟動後用 Postman 或 curl 測試：
  POST http://127.0.0.1:5000/api/upload-event
  Content-Type: application/json
  Body: {"user_id": 1, "file_name": "my_resume.pdf", "file_path": "uploads/1/my_resume.pdf"}
"""

import os
import sys

# 讓 import db_function 可找到
_this_dir = os.path.dirname(os.path.abspath(__file__))
_supabase_control = os.path.dirname(_this_dir)
if _supabase_control not in sys.path:
    sys.path.insert(0, _supabase_control)

from flask import Flask, request, jsonify
from db_function.db_writes import create_upload_event

app = Flask(__name__)


@app.route("/api/upload-event", methods=["POST"])
def api_upload_event():
    """
    接收前端 JSON，呼叫 create_upload_event 寫入 DB，回傳寫入結果。
    實際專案中 user_id 應從 session 或 JWT 取得，這裡為示範從 body 讀。
    """
    body = request.get_json()
    if not body:
        return jsonify({"ok": False, "error": "需要 JSON body"}), 400

    user_id = body.get("user_id")
    file_name = body.get("file_name")
    file_path = body.get("file_path")
    if user_id is None or not file_name or not file_path:
        return jsonify({
            "ok": False,
            "error": "必填: user_id, file_name, file_path"
        }), 400

    try:
        result = create_upload_event(
            user_id=int(user_id),
            file_name=str(file_name),
            file_path=str(file_path),
            upload_type=body.get("upload_type", "resume"),
        )
        return jsonify({"ok": True, "data": result}), 201
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    return (
        "Flask 範例已啟動。請用 POST /api/upload-event 測試，"
        "body: {\"user_id\": 1, \"file_name\": \"x.pdf\", \"file_path\": \"uploads/1/x.pdf\"}"
    )


if __name__ == "__main__":
    print("Flask 範例：POST http://127.0.0.1:5000/api/upload-event")
    app.run(host="127.0.0.1", port=5000, debug=True)

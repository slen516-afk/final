import sys
import os
backend_dir = r"d:\AIPE\FP\Code\final\backend"
flask_dir = r"d:\AIPE\FP\Code\final\backend\flask"
sys.path.insert(0, backend_dir)
sys.path.insert(0, flask_dir)

try:
    from core.supabase_client import supabase
    print("Core import success")
    from api.auth import login_required
    print("API import success")
    from main import create_app
    print("Main import success")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()

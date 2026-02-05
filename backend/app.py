from flask import Flask, request, jsonify
from flask_cors import CORS
from core.supabase_client import supabase
from datetime import datetime
from api.auth import auth_bp
from api.user_preference import user_preference_bp
from api.resume import resume_bp
from api.analysis import analysis_bp
from api.resume_processing import resume_proc_bp 
from api.recommendation import rec_bp           



app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp, url_prefix='/api/auth')

# 履歷分析
app.register_blueprint(user_preference_bp, url_prefix='/api')
app.register_blueprint(resume_bp, url_prefix='/api/resumes')
app.register_blueprint(analysis_bp, url_prefix='/api/analysis')







app.register_blueprint(resume_proc_bp, url_prefix='/api/resumes')
app.register_blueprint(rec_bp, url_prefix='/api')



if __name__ == "__main__":
    print("\n====== 目前註冊的所有 API 路徑 ======")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule}")
    print("======================================\n")

    app.run(debug=True)
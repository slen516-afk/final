from flask import Flask, request, jsonify
from flask_cors import CORS
from core.supabase_client import supabase
from datetime import datetime
from api.auth import auth_bp
from api.user_preference import user_preference_bp
from api.resume import resume_bp
from api.analysis import analysis_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp, url_prefix='/api/auth')

# 履歷分析
app.register_blueprint(user_preference_bp, url_prefix='/api')
app.register_blueprint(resume_bp, url_prefix='/api/resumes')
app.register_blueprint(analysis_bp, url_prefix='/api/analysis')

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, request, jsonify
from flask_cors import CORS
from core.supabase_client import supabase
from datetime import datetime
from api.auth import auth_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp, url_prefix='/api/auth')

if __name__ == "__main__":
    app.run(debug=True)
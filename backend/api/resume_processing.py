# api/resume_processing.py
from flask import Blueprint

# 取個簡短的 blueprint 名稱
resume_proc_bp = Blueprint('resume_proc', __name__) 

@resume_proc_bp.route('/upload', methods=['POST'])
def upload_resume():
    pass

@resume_proc_bp.route('/<id>/status', methods=['GET'])
def check_ocr_status(id):
    pass
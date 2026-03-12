from flask import Flask
import sys
import os

# Add paths
backend_dir = r"d:\AIPE\FP\Code\final\backend"
sys.path.insert(0, backend_dir)
sys.path.insert(0, os.path.join(backend_dir, "flask"))

from app import create_app

app = create_app()
with app.app_context():
    print(f"{'Endpoint':<40} | {'URL Rule'}")
    print("-" * 80)
    for rule in app.url_map.iter_rules():
        if 'resume_process' in str(rule):
            print(f"{rule.endpoint:<40} | {rule}")

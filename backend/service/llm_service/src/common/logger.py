import logging
import os
import sys

def setup_logger(log_folder="logs"):
    """
    職星領航員專案專用 Logger：
    1. 自動建立資料夾
    2. 控制台即時輸出 (INFO) 方便 Docker 監控
    3. 單一檔案記錄 (ERROR) 方便災難追蹤
    """
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    logger = logging.getLogger("CareerPilot")
    
    if not logger.handlers:
        logger.setLevel(logging.INFO) 
        log_format = logging.Formatter('%(asctime)s | [%(levelname)s] | %(name)s | %(message)s')

        # 開啟控制台輸出 (INFO)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(log_format)

        # 靜態單一檔名記錄 (ERROR)
        log_filename = os.path.join(log_folder, "career_system_error.log")
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(log_format)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger

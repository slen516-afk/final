import time

def extract_text_from_image(image_path):
    """
    這個函式負責接收圖片路徑，執行 OCR，並回傳文字字串。
    """
    print(f"[OCR Service] 正在處理圖片：{image_path}")
    
    # -----------------------------------------------------
    # TODO (未來): 在這裡貼上你原本的 olmOCR 程式碼
    # 你的程式碼應該要讀取 image_path，然後把結果存到 result_text
    # -----------------------------------------------------

    # --- 模擬運算過程 (假裝在跑 OCR) ---
    time.sleep(2) 
    
    # --- 暫時回傳的假資料 (讓你測試前端用) ---
    result_text = """
    蘇宏恩的履歷 (測試版)
    技能: Python, Flask, React
    經驗: 正在開發一個超酷的全端履歷分析專案
    """
    
    print("[OCR Service] 辨識完成！")
    return result_text
import torch
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from PIL import Image
import os
import fitz  # PyMuPDF: 用來處理 PDF

# ================= 設定區 =================
MODEL_ID = "Qwen/Qwen2-VL-2B-Instruct" 

_global_model = None
_global_processor = None

def load_model():
    global _global_model, _global_processor
    if _global_model is not None:
        return

    print(f"🚀 [OCR Service] 正在啟動輕量級模型 ({MODEL_ID})...")
    
    try:
        # 加入顯存優化設定
        model = Qwen2VLForConditionalGeneration.from_pretrained(
            MODEL_ID,
            torch_dtype="auto",
            device_map="auto", 
            trust_remote_code=True,
        )
        processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
        
        _global_model = model
        _global_processor = processor
        print("✅ [OCR Service] 模型載入完成！")
        
    except Exception as e:
        print(f"❌ [OCR Service] 模型載入失敗: {e}")
        raise e

# === 新增功能: PDF 轉圖片 ===
def _convert_pdf_to_image(pdf_path):
    # ... (前面的 code 不變) ...
    
    doc = fitz.open(pdf_path)
    images = []

    # 【修改這裡】設定最大頁數限制，例如只讀前 3 頁
    max_pages = 3 
    total_pages = len(doc)
    pages_to_process = min(total_pages, max_pages)

    if total_pages > max_pages:
        print(f"⚠️ [OCR Service] PDF 頁數過多 ({total_pages} 頁)，僅讀取前 {max_pages} 頁以避免顯存爆炸。")

    for page_num in range(pages_to_process): # 改用 pages_to_process
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) 
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    
    doc.close()

    # ... (後面的拼接 code 不變) ...

    if not images:
        raise ValueError("PDF 檔案是空的或無法讀取")

    # 如果只有一頁，直接回傳
    if len(images) == 1:
        return images[0]

    # 如果有多頁，將它們垂直拼接
    total_width = max(img.width for img in images)
    total_height = sum(img.height for img in images)
    
    # 建立一張新的長畫布
    combined_image = Image.new('RGB', (total_width, total_height), (255, 255, 255))
    
    y_offset = 0
    for img in images:
        # 為了美觀，將圖片置中貼上 (雖然通常寬度都一樣)
        x_offset = (total_width - img.width) // 2
        combined_image.paste(img, (x_offset, y_offset))
        y_offset += img.height
    
    print(f"[OCR Service] PDF 轉換完成，拼接了 {len(images)} 頁")
    return combined_image

def extract_text_from_image(file_path):
    global _global_model, _global_processor

    print(f"[OCR Service] 收到請求，處理檔案：{file_path}")

    if _global_model is None:
        try:
            load_model()
        except:
            return "錯誤：模型載入失敗，請檢查後端 logs。"

    if not os.path.exists(file_path):
        return "錯誤：找不到檔案"

    image = None
    try:
        # === 修改核心：判斷副檔名 ===
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            image = _convert_pdf_to_image(file_path)
        else:
            # 原本的圖片處理邏輯
            image = Image.open(file_path).convert("RGB") 
        
        # ===========================
        
        messages = [{
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": "Identify and transcribe the text in this resume into structured Markdown format. Keep the original language (Traditional Chinese). DO NOT TRANSLATE."}
            ]
        }]
        
        # 1. 準備輸入
        text_input = _global_processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = _global_processor(text=[text_input], images=[image], return_tensors="pt")
        inputs = {k: v.to(_global_model.device) for k, v in inputs.items()}
        
        # 2. 推論
        generated_ids = _global_model.generate(**inputs, max_new_tokens=1500)
        
        # 剪掉 Prompt
        input_token_len = inputs['input_ids'].shape[1]
        generated_ids_trimmed = generated_ids[:, input_token_len:]
        
        # 3. 解碼
        generated_text = _global_processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True)[0]
        
        # 顯式關閉圖片釋放資源 (雖然 Python 會自動回收，但好習慣)
        if hasattr(image, 'close'):
            image.close()

        print("[OCR Service] 辨識完成！")
        return generated_text

    except Exception as e:
        print(f"[OCR Service] 發生錯誤: {e}")
        # 發生錯誤時嘗試清理顯存
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return f"OCR 辨識失敗: {str(e)}"
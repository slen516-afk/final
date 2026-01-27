import torch
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from PIL import Image
import os

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

def extract_text_from_image(image_path):
    global _global_model, _global_processor

    print(f"[OCR Service] 收到請求，處理圖片：{image_path}")

    if _global_model is None:
        try:
            load_model()
        except:
            return "錯誤：模型載入失敗，請檢查後端 logs。"

    if not os.path.exists(image_path):
        return "錯誤：找不到圖片檔案"

    try:
        image = Image.open(image_path).convert("RGB") 
        
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
        
        # --- 【關鍵修正】 剪掉前面的 Prompt ---
        # 計算輸入 tokens 的長度
        input_token_len = inputs['input_ids'].shape[1]
        
        # 只保留輸入長度之後的 tokens (也就是 AI 新寫的部分)
        generated_ids_trimmed = generated_ids[:, input_token_len:]
        
        # 3. 解碼 (現在只會解出純淨的履歷內容)
        generated_text = _global_processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True)[0]
        # ------------------------------------
        
        image.close()
        print("[OCR Service] 辨識完成！")
        return generated_text

    except Exception as e:
        print(f"[OCR Service] 發生錯誤: {e}")
        return f"OCR 辨識失敗: {str(e)}"
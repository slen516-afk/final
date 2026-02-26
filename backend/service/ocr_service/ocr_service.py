import os
import torch
import uuid
import json
import time  # 引入時間模組
import re
from PIL import Image
import fitz
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor, TextStreamer
from qwen_vl_utils import process_vision_info
from dotenv import load_dotenv


# 嘗試引入 Supabase
try:
    from supabase import create_client, Client
except ImportError:
    create_client = None

load_dotenv()

# ================= 全域變數 =================
model = None
processor = None
MODEL_ID = "Qwen/Qwen2-VL-2B-Instruct"

# Supabase 設定
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
sb = None
if SUPABASE_URL and SUPABASE_KEY and create_client:
    try:
        sb = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[OCR Service] Supabase 連線成功")
    except Exception as e:
        print(f"[OCR Service] Supabase 連線失敗: {e}")

#輔助函數
def clean_json_output(raw_text):
    """
    清理 LLM 輸出的文字，確保它是一個乾淨的 JSON 格式
    (LLM 經常會自作聰明加上 ```json ... ```)
    """
    cleaned = re.sub(r'^```json\s*', '', raw_text, flags=re.MULTILINE)
    cleaned = re.sub(r'^```\s*$', '', cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()
    return cleaned

# ================= 核心功能 =================

def load_model():
    """
    載入模型 (使用 bfloat16 以節省記憶體並加速)
    """
    global model, processor
    if model is not None:
        return

    print(f"[OCR Service] 正在載入模型: {MODEL_ID} ...")
    try:
        # 1. 直接載入 bfloat16 (記憶體只需約 4GB，不會 Killed)
        model = Qwen2VLForConditionalGeneration.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.bfloat16,  # 使用 bfloat16 以節省記憶體
            device_map="cpu",
            trust_remote_code=True,
        )

        # 2. 載入處理器
        processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
        
        print("[OCR Service] 模型載入完成 (bfloat16)！")
    except Exception as e:
        print(f"[OCR Service] 模型載入失敗: {e}")
        raise e

def _convert_pdf_to_image(file_path):
    print(f"[OCR Service] 正在將 PDF 轉換為圖片: {file_path}")
    try:
        # 1. 打開 PDF 檔案
        doc = fitz.open(file_path)
        if len(doc) == 0:
            print("[OCR Service] ⚠️ 這是一個空白的 PDF")
            return None
        
        # 2. 讀取第一頁 (履歷通常最重要的是第一頁，為了節省記憶體先取第一頁)
        page = doc.load_page(0)
        
        # 3. 將 PDF 頁面渲染成圖片 (設定 dpi=200 保證清晰度，又不會讓檔案太大)
        pix = page.get_pixmap(dpi=200)
        
        # 4. 轉換為 PIL Image 格式，這是 Qwen2-VL 認得的格式
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        print("[OCR Service] ✅ PDF 成功轉換為圖片！")
        return image

    except Exception as e:
        print(f"[OCR Service] ❌ PDF 轉換失敗: {e}")
        return None

def extract_text_from_image(file_path):
    global model, processor
    print(f"[OCR Service] >>> 正在處理：{file_path}")
    
    if model is None:
        load_model()

    file_ext = os.path.splitext(file_path)[1].lower()
    image = None
    
    try:
        if file_ext == '.pdf':
            image = _convert_pdf_to_image(file_path)
            if image is None: return {"error": "PDF not supported"}
        else:
            image = Image.open(file_path).convert("RGB")
        
        # 縮圖至 768px 
        # 1024 對 CPU 還是太累，768 通常夠用
        max_dimension = 768
        if max(image.size) > max_dimension:
            print(f"[OCR Service] 圖片過大 {image.size}，強力縮小至 {max_dimension}px...")
            image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            print(f"[OCR Service] 縮圖完成：{image.size}")
        
        json_prompt = """
        You are an expert ATS (Applicant Tracking System) resume parser. 
        Extract information from this resume image and output ONLY a valid JSON object. 
        Do NOT output any markdown tags like ```json or any conversational text.
        
        CRITICAL INSTRUCTION: 
        The JSON structure below is a TEMPLATE. DO NOT copy the placeholders. 
        You MUST read the ACTUAL image and extract the REAL information from the candidate's resume.
        If a field is not found in the resume, leave it as an empty string "", an empty array [], or null.

        The output MUST strictly follow this exact JSON structure:
        {
            "structured_data": {
                "skills": [
                    {"name": "Skill_Name", "level": 8}
                ],
                "privacy": "public",
                "summary": "A brief professional summary",
                "projects": [
                    "Project name and brief description 1"
                ],
                "education": [
                    {"details": ""} 
                ],
                "experience": [
                    {
                        "title": "Job Title",
                        "years": "Number of years (e.g., '2' or '0.5')",
                        "company": "Company Name",
                        "achievements": "Key achievements or impact",
                        "responsibilities": "Brief summary of responsibilities"
                    }
                ]
            },
            "normalized_data": {
                "skills": ["Skill_Name1", "Skill_Name2"],
                "contact": {
                    "name": "Candidate Full Name",
                    "email": "email@example.com",
                    "github": "GitHub URL if available",
                    "location": "City or Region"
                },
                "work_history": [
                    {
                        "role": "Job Title",
                        "company": "Company Name",
                        "duration_years": 2.5
                    }
                ]
            }
        }
        
        CRITICAL EXTRACTION RULES (YOU MUST FOLLOW THESE):
        1. **Name Formatting**: You MUST format the candidate's name as `Chinese Name (English Name)`, for example `王俊傑 (Jason Wang)` or `蔡志強 (Alex Tsai)`. If the resume contains both, combine them. If the resume ONLY has a Chinese name, you MUST generate its Romanization/Pinyin and put it in parentheses.
        2. **Contact Info**: Search thoroughly for `github` and `location`. For `location`, extract ONLY the city or county name (e.g., "Taipei", "Hsinchu", "New Taipei"). DO NOT include "Taiwan", ", Taiwan", or any country names. If not found, output "".
        3. **Work Experience Completeness**: Extract EVERY SINGLE job experience into BOTH `structured_data.experience` and `normalized_data.work_history`. Do not skip any roles.
        4. **Education**: Extract the ACTUAL education details (School, Major, Degree, Year) from the resume into `education[0].details`. DO NOT copy placeholder text.
        5. **Skills**: Extract all technical/soft skills. Estimate level (1-10).
        6. **Duration**: Calculate `years` (string) and `duration_years` (number) based on start/end dates. 6 months = 0.5.
        7. **Language**: Keep the extracted text in its original language.
        """
        
        # 準備 Prompt
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": json_prompt} # <--- 這裡改用 json_prompt！
                ],
            }
        ]

        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to("cpu")

        streamer = TextStreamer(processor, skip_prompt=True, skip_special_tokens=True)

        print("[OCR Service] 開始推論 (請看下方文字輸出)...")
        start_time = time.time()
        
        generated_ids = model.generate(
            **inputs, 
            max_new_tokens=1500,  
            do_sample=False,      
            streamer=streamer     
        )
        
        end_time = time.time()
        print(f"\n[OCR Service] ✅ 辨識完成！耗時: {end_time - start_time:.2f} 秒")

        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        
        # ==========================================
        # 🔥 修正 3：統一變數名稱為 raw_output
        # ==========================================
        raw_output = processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]

        try:
            # 清理文字並轉為 Dict (現在 raw_output 已經有東西了！)
            clean_json_str = clean_json_output(raw_output)
            parsed_data = json.loads(clean_json_str)
            
            return parsed_data

        except json.JSONDecodeError:
            print("[OCR Service] ❌ 解析 JSON 失敗，模型可能沒有照格式輸出")
            print("原始輸出:", raw_output)
            return {"error": "Failed to parse JSON from model output", "raw_output": raw_output}
            
    except Exception as e:
        print(f"[OCR Service] ❌ 致命錯誤: {e}")
        return {"error": str(e)}
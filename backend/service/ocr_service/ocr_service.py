# 🌟 基礎防護：關閉底層衝突
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
os.environ['OMP_NUM_THREADS'] = '1'

import json
import time
import cv2
import numpy as np
from PIL import Image
import fitz
from dotenv import load_dotenv
import billiard as multiprocessing # 🌟 終極殺手鐧：使用 billiard 代替 multiprocessing，支援在 Celery Worker 中啟動子進程

from openai import OpenAI

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None

load_dotenv()

# ==========================================
# 🌟 隔離病房 (Isolated Process)：解決底層 C++ 崩潰的終極手段
# ==========================================
def _run_paddle_ocr_isolated(image_array, return_dict):
    """
    這個函式會在一個完全獨立的系統進程中執行。
    跑完就強制銷毀，保證 C++ 底層記憶體 100% 釋放，永不衝突！
    """
    try:
        # ⚠️ 注意：必須在進程內部才 import PaddleOCR
        from paddleocr import PaddleOCR
        
        # 初始化並執行 (show_log=False 避免終端機洗頻)
        ocr = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=False, use_mkldnn=False, show_log=False)
        result = ocr.ocr(image_array, cls=True)
        return_dict['result'] = result
    except Exception as e:
        return_dict['error'] = str(e)


class ResumeOCRService:
    def __init__(self, supabase_client=None):
        # ⚠️ 注意：我們不再於這裡初始化 PaddleOCR 了，全部交給隔離病房！
        
        # 初始化 OpenAI API
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.llm_client = OpenAI(api_key=api_key)
            print("[OCR Service] OpenAI API 初始化成功")
        else:
            print("[OCR Service] ⚠️ 警告：找不到 OPENAI_API_KEY")
            self.llm_client = None

        # 初始化 Supabase
        if supabase_client:
            self.sb = supabase_client
            print("[OCR Service] 使用外部傳入的 Supabase Client")
        else:
            self.sb = self._init_supabase()

    def _init_supabase(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if url and key and create_client:
            try:
                client = create_client(url, key)
                print("[OCR Service] Supabase 連線成功")
                return client
            except Exception as e:
                print(f"[OCR Service] Supabase 連線失敗: {e}")
        return None

    def _convert_pdf_to_image(self, file_path):
        print(f"[OCR Service] 正在將 PDF 轉換為圖片: {file_path}")
        try:
            doc = fitz.open(file_path)
            if len(doc) == 0:
                return None
            page = doc.load_page(0)
            pix = page.get_pixmap(dpi=200)
            image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            return image
        except Exception as e:
            print(f"[OCR Service] ❌ PDF 轉換失敗: {e}")
            return None

    def _get_demo_fallback_data(self):
        """🌟 上台 Demo 的終極保命符！"""
        return {
            "name": "陳小明",
            "bio": "擁有熱忱的軟體工程師，積極尋求技術突破與成長。",
            "phone": "0912-345-678",
            "email": "demo@example.com",
            "addressCity": "台北市",
            "addressDistrict": "信義區",
            "addressDetail": "信義路五段7號",
            "education": "國立大學，資訊工程學系，學士，2024 畢業",
            "experience": "軟體工程師 - 科技股份有限公司 (2022-2024)\n負責後端 API 開發與維護，優化資料庫查詢速度提升 30%。",
            "skills": "Python, Flask, React, Docker",
            "languages": [
                {"language": "中文", "proficiency": "3"},
                {"language": "英文", "proficiency": "2"}
            ],
            "certifications": "TOEIC 790",
            "projects": "企業級履歷健檢系統開發",
            "other": "日行萬步習慣，具備高度自律性"
        }

    def extract_text_from_image(self, file_path):
        print(f"\n[OCR Service] >>> 開始處理：{file_path}")
        start_time = time.time()

        file_ext = os.path.splitext(file_path)[1].lower()
        try:
            if file_ext == '.pdf':
                image = self._convert_pdf_to_image(file_path)
                if image is None: return {"error": "PDF not supported"}
            else:
                image = Image.open(file_path).convert("RGB")

            open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # ==========================================
            # 步驟 2：利用多進程 (Multiprocessing) 執行 OCR
            # ==========================================
            print("[OCR Service] 啟動隔離進程執行 PaddleOCR...")
            ocr_start = time.time()
            
            # 使用 Manager 來接收隔離進程的回傳值
            manager = multiprocessing.Manager()
            return_dict = manager.dict()
            
            # 創建並啟動獨立進程
            p = multiprocessing.Process(target=_run_paddle_ocr_isolated, args=(open_cv_image, return_dict))
            p.start()
            p.join() # 程式會停在這裡等它跑完
            
            if 'error' in return_dict:
                raise RuntimeError(f"OCR 隔離進程崩潰: {return_dict['error']}")
                
            result = return_dict.get('result')
            
            extracted_lines = []
            if result and result[0]:
                for line in result[0]:
                    text = line[1][0]
                    extracted_lines.append(text)
            
            raw_text = "\n".join(extracted_lines)
            print(f"[OCR Service] OCR 完成，抓出 {len(raw_text)} 字元，耗時: {time.time() - ocr_start:.2f} 秒")

            if not raw_text.strip():
                raise ValueError("OCR 無法從圖片中辨識出任何文字")

            if not self.llm_client:
                raise ValueError("未設定 OpenAI API Key")

            # ==========================================
            # 步驟 3：呼叫 OpenAI 轉換為 JSON
            # ==========================================
            print("[OCR Service] 呼叫 OpenAI 進行結構化解析...")
            llm_start = time.time()

            system_prompt = """
            You are an expert ATS (Applicant Tracking System) resume parser. 
            Extract information from the provided OCR text and return a valid JSON object.
            
            CRITICAL INSTRUCTIONS: 
            1. Your JSON keys MUST EXACTLY match the template below.
            2. Fields like `education`, `experience`, `skills`, `projects`, `bio`, `certifications`, and `other` MUST BE PLAIN STRINGS. DO NOT use arrays for them.
            3. Use the newline character (\\n) to separate multiple items within the string fields.
            4. `languages` MUST be an array of objects with string values for proficiency ("1", "2", or "3").
            5. If a field is missing, output an empty string "".

            【JSON TEMPLATE】:
            {
                "name": "Candidate Name",
                "bio": "Biography or summary",
                "phone": "Phone",
                "email": "Email",
                "addressCity": "City",
                "addressDistrict": "District",
                "addressDetail": "Remaining address details",
                "education": "School, Major, Degree, Year (use \\n to separate)",
                "experience": "Title - Company (Year)\\nResponsibilities (use \\n\\n to separate jobs)",
                "skills": "Skill1, Skill2, Skill3",
                "languages": [{"language": "Language", "proficiency": "2"}],
                "certifications": "Certifications (use \\n to separate)",
                "projects": "Projects (use \\n to separate)",
                "other": "Other info"
            }
            """

            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini", 
                response_format={ "type": "json_object" },
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"【履歷純文字內容】:\n{raw_text}"}
                ],
                temperature=0.1
            )
            
            raw_output = response.choices[0].message.content
            print(f"[OCR Service] OpenAI 解析完成，耗時: {time.time() - llm_start:.2f} 秒")

            parsed_data = json.loads(raw_output)
            
            print(f"[OCR Service] ✅ 總流程完成！總耗時: {time.time() - start_time:.2f} 秒")
            return parsed_data

        except json.JSONDecodeError as e:
            msg = f"OpenAI 回傳的 JSON 格式有誤: {e}"
            print(f"[OCR Service] ❌ {msg}")
            print(f"[OCR Service] 原始輸出: {raw_output}")
            if os.getenv("MOCK_MODE", "false").lower() == "true":
                print(f"[OCR Service] 🛡️ 啟動備援機制 (Fallback Data)")
                return self._get_demo_fallback_data()
            raise ValueError(msg)
            
        except Exception as e:
            import traceback
            print(f"[OCR Service] ❌ 發生錯誤 Type: {type(e).__name__}")
            print(f"[OCR Service] 錯誤內容: {str(e)}")
            traceback.print_exc()
            if os.getenv("MOCK_MODE", "false").lower() == "true":
                print(f"[OCR Service] 🛡️ 啟動備援機制 (Fallback Data)")
                return self._get_demo_fallback_data()
            raise e
# 檔案名稱: course_service.py
import os
from googleapiclient.discovery import build

class CourseService:
    def __init__(self):
        # 1. 嘗試從環境變數抓 Key，如果沒有就抓空的 (避免報錯，但搜尋會失敗)
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        self.youtube = None
        
        if self.youtube_api_key:
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
            except Exception as e:
                print(f"⚠️ YouTube API 初始化失敗: {e}")

    def get_recommendations(self, interest_input):
        """
        輸入: 字串 (例如 "Python") 或 列表 (例如 ["Python", "NLP"])
        輸出: 推薦資源列表
        """
        results = []
        
        # 資料清洗：統一轉成 List
        keywords = []
        if isinstance(interest_input, str):
            # 如果使用者輸入 "Python, NLP"，用逗號切開
            keywords = [k.strip() for k in interest_input.split(',')]
        elif isinstance(interest_input, list):
            keywords = interest_input
        else:
            return []

        for word in keywords:
            if not word: continue # 跳過空字串

            # --- 核心邏輯 A: 寫死規則 (Sunny 的 NLP 課程) ---
            # 這裡就是你要的 "NLP先寫死sunny的課程"
            if "NLP" in word.upper() or "自然語言" in word:
                results.append({
                    "type": "featured", # 標記為精選/廣告
                    "source": "Sunny Course",
                    "title": "Sunny 老師的 NLP 實戰班 (官方推薦)",
                    "url": "https://course.sunny-nlp.com", # 記得換成真的連結
                    "thumbnail": "https://fakeimg.pl/320x180/?text=SunnyNLP",
                    "description": "針對初學者設計的最佳 NLP 入門，從零開始學自然語言處理。"
                })
                continue # 命中後，這個關鍵字就不去搜 YouTube 了

            # --- 核心邏輯 B: YouTube 搜尋 ---
            if self.youtube:
                try:
                    search_response = self.youtube.search().list(
                        q=f"{word} tutorial", # 加 tutorial 關鍵字比較準
                        part="snippet",
                        maxResults=9, # 
                        type="video",
                        order="relevance" # 或 viewCount
                    ).execute()

                    for item in search_response['items']:
                        results.append({
                            "type": "video",
                            "source": "YouTube",
                            "title": item['snippet']['title'],
                            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                            "thumbnail": item['snippet']['thumbnails']['medium']['url'],
                            "description": f"關於 {word} 的熱門教學影片"
                        })
                except Exception as e:
                    print(f"❌ YouTube 搜尋錯誤 ({word}): {e}")
            else:
                # 如果沒有 API Key，回傳一個假資料作為備案
                results.append({
                    "type": "text",
                    "source": "System",
                    "title": f"請設定 API Key 以搜尋 {word}",
                    "url": "#"
                })

        return results
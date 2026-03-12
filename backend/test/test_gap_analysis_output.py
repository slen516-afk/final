import re
import json

def transform_result(result):
    if not isinstance(result, dict):
        return result
    
    # 1. 處理核心洞察與個人總結的拆分
    pre_summary = result.get("preliminary_summary", {})
    core_insight = pre_summary.get("core_insight", "")
    
    # 匹配 【產業洞察】 與 【個人總結】
    industry_match = re.search(r'【產業洞察】[：:]?\s*(.*?)(?=【|$)', core_insight, re.S)
    personal_match = re.search(r'【個人總結】[：:]?\s*(.*)', core_insight, re.S)
    
    if industry_match:
        pre_summary["industry_insight"] = industry_match.group(1).strip()
    else:
        # 如果沒找到標籤，嘗試以常見的句式拆分，或者直接當成產業洞察
        pre_summary["industry_insight"] = core_insight
        
    if personal_match:
        pre_summary["personal_summary"] = personal_match.group(1).strip()
    else:
        # 如果沒找到個人總結標籤，設為空
        pre_summary["personal_summary"] = ""
    
    result["preliminary_summary"] = pre_summary

    # 2. 處理匹配度百分比符號移除
    gap_analysis = result.get("gap_analysis", {})
    target_pos = gap_analysis.get("target_position", {})
    match_score = target_pos.get("match_score", "0")
    
    if isinstance(match_score, str):
        # 移除所有非數字內容
        clean_score = re.sub(r'[^\d]', '', match_score)
        try:
            target_pos["match_score"] = int(clean_score)
        except ValueError:
            target_pos["match_score"] = 0
    
    gap_analysis["target_position"] = target_pos
    result["gap_analysis"] = gap_analysis
    
    return result

# 模擬從 20260311_user49.md 提取並適配 Pydantic Schema 的資料
mock_pydantic_result = {
    "preliminary_summary": {
        "core_insight": "【產業洞察】：數據顯示，未來五年內，後端開發工程師的需求將持續增長，尤其是在擁有全端能力的團隊中。【個人總結】：Chloe Lin 在前端開發上展現的元件化思維與狀態管理技巧，為她轉型至後端開發奠定了堅實基礎。"
    },
    "radar_chart": {
        "dimensions": [
            {"axis": "前端開發", "score": 0.5},
            {"axis": "後端開發", "score": 0.5},
            {"axis": "運維部署", "score": 0.5},
            {"axis": "AI與數據", "score": 0.5},
            {"axis": "工程品質", "score": 3.0},
            {"axis": "軟實力", "score": 3.5}
        ]
    },
    "gap_analysis": {
        "target_position": {
            "role": "後端工程師",
            "match_score": "82%",
            "gap_description": "【優勢 (Strengths)】：Chloe 的UI/UX合作經驗...【劣勢 (Weaknesses)】：目前的技能偏向前端開發..."
        }
    },
    "action_plan": {
        "short_term": "學習並精通SQL與NoSQL資料庫...",
        "mid_term": "取得相關認證...",
        "long_term": "承擔更多技術領導角色..."
    }
}

if __name__ == "__main__":
    print("=== 原始模擬資料 ===")
    print(json.dumps(mock_pydantic_result, indent=2, ensure_ascii=False))
    
    transformed = transform_result(mock_pydantic_result)
    
    print("\n=== 轉換後資料 (應符合 Skills.tsx 格式) ===")
    print(json.dumps(transformed, indent=2, ensure_ascii=False))
    
    # 驗證
    assert "industry_insight" in transformed["preliminary_summary"]
    assert "personal_summary" in transformed["preliminary_summary"]
    assert isinstance(transformed["gap_analysis"]["target_position"]["match_score"], int)
    
    print("\n✅ 測試成功：格式已正確對齊並移除了百分比符號。")

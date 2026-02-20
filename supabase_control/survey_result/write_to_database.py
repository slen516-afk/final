"""
將 converted_input.json 的問卷資料寫入 Supabase CAREER_SURVEY 表

使用方式:
    python write_to_database.py
    
    或指定輸入檔案:
    python write_to_database.py --input converted_input.json
    
    或指定是否為測試模式（不會實際寫入）:
    python write_to_database.py --dry-run
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# 添加父目錄到路徑，以便導入 supabase_connection
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from supabase_connection import connect_to_supabase


def extract_user_id(user_id_str):
    """
    從 "user_1" 格式提取數字 ID
    
    Args:
        user_id_str: 字串格式的 user_id，如 "user_1"
    
    Returns:
        int: 數字 ID，如 1
    """
    if isinstance(user_id_str, int):
        return user_id_str
    
    if isinstance(user_id_str, str):
        # 移除 "user_" 前綴
        if user_id_str.startswith("user_"):
            try:
                return int(user_id_str.replace("user_", ""))
            except ValueError:
                raise ValueError(f"無法從 '{user_id_str}' 提取 user_id")
        else:
            try:
                return int(user_id_str)
            except ValueError:
                raise ValueError(f"無法將 '{user_id_str}' 轉換為整數")
    
    raise ValueError(f"不支援的 user_id 格式: {user_id_str}")


def parse_timestamp(timestamp_str):
    """
    將 ISO 格式的時間字串轉換為 DATETIME 格式
    
    Args:
        timestamp_str: ISO 格式時間字串，如 "2026-02-19T23:12:51.367412Z"
    
    Returns:
        str: DATETIME 格式字串，如 "2026-02-19 23:12:51"
    """
    try:
        # 解析 ISO 格式
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        # 轉換為本地時間（移除時區資訊）
        dt_local = dt.replace(tzinfo=None)
        # 格式化為 DATETIME 字串
        return dt_local.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        raise ValueError(f"無法解析時間戳記 '{timestamp_str}': {e}")


def build_questionnaire_response(data):
    """
    構建 questionnaire_response JSONB 結構
    
    Args:
        data: converted_input.json 中的單筆資料
    
    Returns:
        dict: 包含 module_a/b/c/d 的完整結構
    """
    return {
        "module_a": data.get("module_a", {}),
        "module_b": data.get("module_b", {}),
        "module_c": data.get("module_c", {}),
        "module_d": data.get("module_d", {})
    }


def extract_career_preference(data):
    """
    從 module_c 提取職涯偏好
    
    Args:
        data: converted_input.json 中的單筆資料
    
    Returns:
        dict: 職涯偏好 JSONB 結構，包含目標職位和產業
    """
    module_c = data.get("module_c", {})
    if not module_c:
        return None
    
    career_pref = {
        "target_role": module_c.get("q17_target_role"),
        "industry": module_c.get("q18_industry"),
        "current_level": module_c.get("q16_current_level"),
        "search_status": module_c.get("q19_search_status")
    }
    
    # 如果所有值都是 None，返回 None
    if all(v is None for v in career_pref.values()):
        return None
    
    return career_pref


def extract_skill_self_assessment(data):
    """
    從 module_a.q1_languages 提取技能自評
    
    Args:
        data: converted_input.json 中的單筆資料
    
    Returns:
        dict: 技能自評 JSONB 結構，格式為 {"技能名稱": 分數}
    """
    module_a = data.get("module_a", {})
    languages = module_a.get("q1_languages", [])
    
    if not languages:
        return None
    
    skill_assessment = {}
    for lang in languages:
        if isinstance(lang, dict) and "name" in lang and "score" in lang:
            skill_name = lang["name"]
            score = lang["score"]
            # 轉換為整數（1-10分）
            try:
                skill_assessment[skill_name] = int(score)
            except (ValueError, TypeError):
                skill_assessment[skill_name] = score
    
    return skill_assessment if skill_assessment else None


def extract_career_motivation(data):
    """
    從 module_d 提取職涯轉換動機
    
    Args:
        data: converted_input.json 中的單筆資料
    
    Returns:
        dict: 職涯轉換動機 JSONB 結構
    """
    module_d = data.get("module_d", {})
    if not module_d:
        return None
    
    motivation = {
        "values_top3": module_d.get("q20_values_top3"),
        "pressure": module_d.get("q21_pressure"),
        "career_type": module_d.get("q22_career_type"),
        "learning_style": module_d.get("q23_learning_style")
    }
    
    # 如果所有值都是 None，返回 None
    if all(v is None for v in motivation.values()):
        return None
    
    return motivation


def prepare_survey_data(data):
    """
    準備寫入 CAREER_SURVEY 表的資料（嚴格遵循 ERD 設計）
    
    Args:
        data: converted_input.json 中的單筆資料
    
    Returns:
        dict: 準備好的資料庫記錄，包含所有可提取的欄位
    """
    user_id = extract_user_id(data.get("user_id", ""))
    timestamp = data.get("timestamp", datetime.now().isoformat())
    completed_at = parse_timestamp(timestamp)
    questionnaire_response = build_questionnaire_response(data)
    
    # 提取各欄位資料
    career_preference = extract_career_preference(data)
    skill_self_assessment = extract_skill_self_assessment(data)
    career_motivation = extract_career_motivation(data)
    
    # 構建資料庫記錄（嚴格遵循 ERD 欄位定義）
    record = {
        "user_id": user_id,
        "questionnaire_response": questionnaire_response,
        "completed_at": completed_at,
        "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    # 只有當欄位有值時才加入（避免寫入 None）
    if career_preference is not None:
        record["career_preference"] = career_preference
    
    if skill_self_assessment is not None:
        record["skill_self_assessment"] = skill_self_assessment
    
    if career_motivation is not None:
        record["career_motivation"] = career_motivation
    
    # 以下欄位在問卷中沒有對應資料，保持為 None（資料庫允許 NULL）
    # salary_min, salary_max, location_preference, remote_preference
    # 這些欄位可能需要從其他來源補充，或由使用者後續填寫
    
    return record


def load_survey_data(input_file):
    """
    載入問卷資料（使用相對於腳本目錄的路徑）
    
    Args:
        input_file: 輸入 JSON 檔案路徑（相對或絕對路徑）
    
    Returns:
        list: 問卷資料列表
    """
    # 如果輸入是相對路徑，相對於腳本目錄
    if not Path(input_file).is_absolute():
        input_path = current_dir / input_file
    else:
        input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"找不到檔案: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        raise ValueError("輸入檔案必須是 JSON 陣列格式")
    
    return data


def write_surveys_to_database(survey_data_list, supabase, dry_run=False):
    """
    將問卷資料寫入資料庫
    
    Args:
        survey_data_list: 準備好的問卷資料列表
        supabase: Supabase 客戶端
        dry_run: 是否為測試模式（不實際寫入）
    
    Returns:
        tuple: (成功數量, 失敗數量, 錯誤列表)
    """
    success_count = 0
    fail_count = 0
    errors = []
    
    print(f"\n{'='*60}")
    print(f"準備寫入 {len(survey_data_list)} 筆問卷資料")
    if dry_run:
        print("⚠️  測試模式：不會實際寫入資料庫")
    print(f"{'='*60}\n")
    
    for idx, survey_data in enumerate(survey_data_list, 1):
        user_id = survey_data["user_id"]
        
        try:
            if dry_run:
                print(f"[{idx}/{len(survey_data_list)}] 測試模式 - User ID: {user_id}")
                print(f"  資料: {json.dumps(survey_data, indent=2, ensure_ascii=False)[:200]}...")
                success_count += 1
            else:
                # 檢查是否已存在該 user_id 的問卷記錄
                existing = supabase.table('career_survey').select('survey_id').eq('user_id', user_id).execute()
                
                if existing.data:
                    # 更新現有記錄（更新所有欄位）
                    survey_id = existing.data[0]['survey_id']
                    update_data = {
                        "questionnaire_response": survey_data["questionnaire_response"],
                        "completed_at": survey_data["completed_at"],
                        "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    # 只更新有值的欄位
                    if "career_preference" in survey_data:
                        update_data["career_preference"] = survey_data["career_preference"]
                    if "skill_self_assessment" in survey_data:
                        update_data["skill_self_assessment"] = survey_data["skill_self_assessment"]
                    if "career_motivation" in survey_data:
                        update_data["career_motivation"] = survey_data["career_motivation"]
                    
                    result = supabase.table('career_survey').update(update_data).eq('survey_id', survey_id).execute()
                    print(f"[{idx}/{len(survey_data_list)}] ✓ 更新 User ID {user_id} (survey_id: {survey_id})")
                else:
                    # 插入新記錄
                    result = supabase.table('career_survey').insert(survey_data).execute()
                    survey_id = result.data[0]['survey_id'] if result.data else None
                    print(f"[{idx}/{len(survey_data_list)}] ✓ 插入 User ID {user_id} (survey_id: {survey_id})")
                
                success_count += 1
                
        except Exception as e:
            fail_count += 1
            error_msg = f"User ID {user_id}: {str(e)}"
            errors.append(error_msg)
            print(f"[{idx}/{len(survey_data_list)}] ✗ 失敗 User ID {user_id}: {e}")
    
    return success_count, fail_count, errors


def main():
    parser = argparse.ArgumentParser(
        description='將問卷資料寫入 Supabase CAREER_SURVEY 表',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  # 使用預設檔案 (converted_input.json)
  python write_to_database.py
  
  # 指定輸入檔案
  python write_to_database.py --input converted_input.json
  
  # 測試模式（不會實際寫入）
  python write_to_database.py --dry-run
        """
    )
    
    parser.add_argument(
        '--input',
        type=str,
        default='converted_input.json',
        help='輸入的 JSON 檔案路徑（預設: converted_input.json）'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='測試模式：不會實際寫入資料庫，只顯示準備寫入的資料'
    )
    
    args = parser.parse_args()
    
    # 載入資料
    print(f"正在讀取檔案: {args.input}")
    try:
        survey_data_list = load_survey_data(args.input)
        print(f"✓ 成功載入 {len(survey_data_list)} 筆資料\n")
    except Exception as e:
        print(f"✗ 載入檔案失敗: {e}")
        sys.exit(1)
    
    # 準備資料
    print("正在準備資料...")
    prepared_data = []
    for idx, data in enumerate(survey_data_list, 1):
        try:
            prepared = prepare_survey_data(data)
            prepared_data.append(prepared)
            user_id = data.get("user_id", "unknown")
            print(f"  [{idx}/{len(survey_data_list)}] ✓ User {user_id}")
        except Exception as e:
            print(f"  [{idx}/{len(survey_data_list)}] ✗ 準備資料失敗: {e}")
            continue
    
    if not prepared_data:
        print("\n✗ 沒有可寫入的資料")
        sys.exit(1)
    
    # 連接資料庫（如果不是測試模式）
    if not args.dry_run:
        try:
            print("\n正在連接 Supabase...")
            supabase = connect_to_supabase(test_connection=False)
        except Exception as e:
            print(f"✗ 連接資料庫失敗: {e}")
            sys.exit(1)
    else:
        supabase = None
    
    # 寫入資料
    try:
        success_count, fail_count, errors = write_surveys_to_database(
            prepared_data, 
            supabase, 
            dry_run=args.dry_run
        )
        
        # 顯示結果摘要
        print(f"\n{'='*60}")
        print("寫入結果摘要")
        print(f"{'='*60}")
        print(f"總共處理: {len(prepared_data)} 筆")
        print(f"成功: {success_count} 筆")
        if fail_count > 0:
            print(f"失敗: {fail_count} 筆")
            print("\n錯誤詳情:")
            for error in errors:
                print(f"  - {error}")
        print(f"{'='*60}\n")
        
        if args.dry_run:
            print("⚠️  這是測試模式，資料並未實際寫入資料庫")
            print("   移除 --dry-run 參數以實際寫入資料\n")
        
    except Exception as e:
        print(f"\n✗ 寫入過程發生錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

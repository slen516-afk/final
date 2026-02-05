# update_location_fields.py
"""
更新現有 job_posting 資料的 location 欄位

此腳本會：
1. 讀取 job_posting_rows.csv（資料庫 export 的資料）
2. 讀取 clear_data_rows.csv（原始 CSV）
3. 使用 job_title + company_name 匹配
4. 更新 location（設為 NULL 刪除）、city, district, full_address 欄位
5. 其他資料會保留不變

更新邏輯：
- location = NULL（刪除，避免與 full_address 重複）
- full_address = clear_data_rows.csv 的 location（原始完整地址）
- city = 從 full_address 拆分出來
- district = 從 full_address 拆分出來
"""

import pandas as pd
import re
from supabase_connection import connect_to_supabase

# 定義清理函數（從 cleaner.ipynb 複製）
def clean_text(text):
    """清理文字：移除多餘空白、換行符、特殊字元"""
    if pd.isna(text) or text is None:
        return None
    text = str(text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    text = re.sub(r'<[^>]+>', '', text)
    return text if text else None

def parse_location_to_city_district(full_address):
    """從完整地址拆分出 city 和 district"""
    if pd.isna(full_address) or not str(full_address).strip():
        return (None, None)
    
    address = str(full_address).strip()
    
    cities = [
        '台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市',
        '基隆市', '新竹市', '嘉義市',
        '新竹縣', '苗栗縣', '彰化縣', '南投縣', '雲林縣', 
        '嘉義縣', '屏東縣', '宜蘭縣', '花蓮縣', '台東縣', '澎湖縣', '金門縣', '連江縣'
    ]
    
    city = None
    district = None
    
    for c in cities:
        if address.startswith(c):
            city = c
            remaining = address[len(c):]
            district_match = re.match(r'^([^區鄉鎮市]*[區鄉鎮市])', remaining)
            if district_match:
                district = district_match.group(1)
            break
    
    return (city, district)

def main():
    print("=" * 60)
    print("更新現有 job_posting 的 location 欄位")
    print("=" * 60)
    
    # 1. 連線到 Supabase
    print("\n【步驟 1】連線到 Supabase...")
    print("-" * 60)
    try:
        supabase = connect_to_supabase()
        print("✓ Supabase 連線成功")
    except Exception as e:
        print(f"✗ 連線失敗: {e}")
        return
    
    # 2. 讀取 job_posting_rows.csv（資料庫 export 的資料）
    print("\n【步驟 2】讀取 job_posting_rows.csv（資料庫 export 的資料）...")
    print("-" * 60)
    try:
        existing_jobs = pd.read_csv('job_posting_rows.csv')
        print(f"✓ 已讀取 {len(existing_jobs)} 筆資料庫資料")
        
        # 讀取 company_info 建立 company_id -> company_name 對應表
        companies_result = supabase.table('company_info').select('company_id, company_name').execute()
        company_id_to_name = {row['company_id']: row['company_name'] for row in companies_result.data}
        print(f"✓ 已建立 {len(company_id_to_name)} 家公司的 ID 對應表")
        
        # 將 company_id 轉換為 company_name（用於匹配）
        existing_jobs['company_name'] = existing_jobs['company_id'].map(company_id_to_name)
        
    except Exception as e:
        print(f"✗ 讀取資料失敗: {e}")
        return
    
    # 3. 讀取 clear_data_rows.csv（原始 CSV）
    print("\n【步驟 3】讀取 clear_data_rows.csv（原始 CSV）...")
    print("-" * 60)
    try:
        df = pd.read_csv('clear_data_rows.csv')
        print(f"✓ 已讀取 {len(df)} 筆原始資料")
    except Exception as e:
        print(f"✗ 讀取 CSV 失敗: {e}")
        return
    
    # 4. 處理原始 CSV 的 location 資料
    print("\n【步驟 4】處理原始 CSV 的 location 資料...")
    print("-" * 60)
    
    # 清理 CSV 中的公司名稱和職缺名稱（用於匹配）
    df['company_name_clean'] = df['company_name'].apply(clean_text)
    df['job_title_clean'] = df['job_name'].apply(clean_text)
    
    # 處理 location：保留原始 CSV 的 location 作為 full_address
    # full_address = clear_data_rows.csv 的 location（原始完整地址，不清理）
    df['full_address'] = df['location'].astype(str)
    
    # 從 full_address 拆分出 city 和 district
    location_parsed = df['full_address'].apply(parse_location_to_city_district)
    df['city'] = location_parsed.apply(lambda x: x[0] if x else None)
    df['district'] = location_parsed.apply(lambda x: x[1] if x else None)
    
    print(f"✓ 已處理 {len(df)} 筆原始資料的 location 資訊")
    print(f"  - 有 city 的資料: {df['city'].notna().sum()} 筆")
    print(f"  - 有 district 的資料: {df['district'].notna().sum()} 筆")
    
    # 5. 建立匹配表（使用 job_title + company_name 匹配）
    print("\n【步驟 5】建立匹配表（使用 job_title + company_name）...")
    print("-" * 60)
    
    csv_location_map = {}
    for idx, row in df.iterrows():
        key = (row['job_title_clean'], row['company_name_clean'])
        csv_location_map[key] = {
            'city': row['city'] if pd.notna(row['city']) else None,
            'district': row['district'] if pd.notna(row['district']) else None,
            'full_address': row['full_address'] if pd.notna(row['full_address']) and str(row['full_address']) != 'nan' else None
        }
    
    print(f"✓ 已建立 {len(csv_location_map)} 筆匹配資料")
    
    # 6. 匹配並更新 location 資料
    print("\n【步驟 6】匹配並更新 location 資料...")
    print("-" * 60)
    print("⚠️  注意：此步驟會更新現有資料的 location 相關欄位")
    print("   更新邏輯：")
    print("   - location = NULL（刪除，避免與 full_address 重複）")
    print("   - full_address = clear_data_rows.csv 的 location（原始完整地址）")
    print("   - city = 從 full_address 拆分出來")
    print("   - district = 從 full_address 拆分出來")
    print("   其他欄位（如 job_title, job_description 等）會保留不變")
    
    updated_count = 0
    not_found_count = 0
    error_count = 0
    
    for idx, job in existing_jobs.iterrows():
        job_id = job['job_id']
        job_title = job['job_title']
        company_name = job['company_name']
        
        # 清理用於匹配
        job_title_clean = clean_text(job_title) if pd.notna(job_title) else None
        company_name_clean = clean_text(company_name) if pd.notna(company_name) else None
        
        if not job_title_clean or not company_name_clean:
            not_found_count += 1
            continue
        
        # 嘗試匹配
        key = (job_title_clean, company_name_clean)
        if key in csv_location_map:
            location_data = csv_location_map[key]
            
            # 更新資料庫（只更新 location 相關欄位，其他欄位保留）
            # location 設為 NULL（刪除，避免與 full_address 重複）
            try:
                update_data = {
                    'location': None,  # 設為 NULL，刪除原先的 location
                    'city': location_data['city'],
                    'district': location_data['district'],
                    'full_address': location_data['full_address']
                }
                
                result = supabase.table('job_posting').update(update_data).eq('job_id', job_id).execute()
                updated_count += 1
                
                if updated_count % 100 == 0:
                    print(f"  已更新 {updated_count} 筆...")
                    
            except Exception as e:
                error_count += 1
                print(f"  ✗ 更新 job_id {job_id} 失敗: {e}")
        else:
            not_found_count += 1
    
    print(f"\n✓ 更新完成！")
    print(f"  - 成功更新: {updated_count} 筆")
    print(f"  - 找不到匹配: {not_found_count} 筆")
    print(f"  - 更新錯誤: {error_count} 筆")
    
    # 7. 驗證更新結果
    print("\n【步驟 7】驗證更新結果...")
    print("-" * 60)
    
    try:
        result = supabase.table('job_posting').select('location, city, district, full_address').limit(1000).execute()
        sample_df = pd.DataFrame(result.data)
        
        print(f"✓ 取樣 {len(sample_df)} 筆資料統計：")
        print(f"  - location 為 NULL: {sample_df['location'].isna().sum()} ({sample_df['location'].isna().sum()/len(sample_df)*100:.1f}%)")
        print(f"  - 有 city 的職缺: {sample_df['city'].notna().sum()} ({sample_df['city'].notna().sum()/len(sample_df)*100:.1f}%)")
        print(f"  - 有 district 的職缺: {sample_df['district'].notna().sum()} ({sample_df['district'].notna().sum()/len(sample_df)*100:.1f}%)")
        print(f"  - 有 full_address 的職缺: {sample_df['full_address'].notna().sum()} ({sample_df['full_address'].notna().sum()/len(sample_df)*100:.1f}%)")
        
        # 顯示前 3 筆範例
        print(f"\n【前 3 筆更新後的資料範例】")
        for idx, row in sample_df.head(3).iterrows():
            print(f"  {idx + 1}. location: {row['location']} (應為 NULL)")
            print(f"     city: {row['city']}, district: {row['district']}")
            print(f"     full_address: {row['full_address']}")
            
    except Exception as e:
        print(f"✗ 驗證失敗: {e}")
    
    print("\n" + "=" * 60)
    print("✓ 更新完成！location 欄位已更新")
    print("=" * 60)

if __name__ == "__main__":
    main()
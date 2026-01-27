# 開發環境 Setup

大家直接用 VS Code 的 Dev Containers 開這個專案。往後有甚麼需要自己改動的再麻煩各位自己弄。

**步驟：**
1. 確保 Docker 有開。
2. VS Code 左下角 `><` 點下去 -> `Reopen in Container`。
3. 選單建議選 **Backend**。

**重點設定：**
* Erd圖位置: 在 資料夾內, 有含說明文件。
* 連線 supabase 需 copy .env_example 成 .env 檔案 
    然後手動輸入 project_url =    - > 哪裡找 : SUPABASE首頁專案裡面 最左邊 project settings  -> Data API -> Project_URL
                service_role_key =  - > 哪裡找 : SUPABASE首頁專案裡面 最左邊 project settings  -> API Keys -> Secret_keys


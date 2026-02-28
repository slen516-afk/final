# 專案簡介 :CareerPilot 【職星領航員】
本專案建構了涵蓋「能力評估、缺口分析、技能補強、職缺媒合、履歷優化」的完整職涯支援閉環。
旨在解決求職過程中缺乏量化依據的認知偏差，並針對「客製化履歷與求職信」的高耗時痛點，預計將申請準備時間大幅縮短 50%。
本平台不只是求職工具，更致力於降低用戶在職涯選擇中的盲目性，支持用戶持續成長，具備「高實用價值」的智慧決策體系。

# 開發環境 Setup
- git clone本專案後，透過VS Code Dev containers連線進個別容器內，如有追加套件應維護至requirements.txt

**Docker啟用方式：**

方式一:
   * 1.開啟 Docker ，確認Docker Desktop已下載並開啟。
   * 2.點選 VS Code 左下角 `><`  -> 選擇 `Reopen in Container`。
   * 3.於選單中選擇對應容器(Backend / Frontend)再開始開發，如果是初次啟動，Docker會在此時建置容器，因為內含torch等大型套件所以初次下載會比較久，建議電腦效能要達到一定程度且網路要穩定或甚至是快速。。
    
方式二:
   * 1.Terminal輸入:`docker compose up -d`啟動Docker Compose。
   * 2.按下F1選擇 `Attach to Running Container` -> 選擇想要進入的容器。
   * 3.進入容器介面後選擇Open Folder , 如果路徑顯示`/root` , 點擊`..` , 將路徑重新選擇到 `/app`。

**重要資訊：**
* Erd圖位置: 在 資料夾內, 有含說明文件。
* 連線 supabase 需 copy .env_example 成 .env 檔案
    然後手動輸入 project_url =    - > 哪裡找 : SUPABASE首頁專案裡面 最左邊 project settings  -> Data API -> Project_URL
                service_role_key =  - > 哪裡找 : SUPABASE首頁專案裡面 最左邊 project settings  -> API Keys -> Secret_keys
* 前端啟用: 進入前端容器後輸入npm run dev開啟前端連線，輸入ctrl + c以關閉連線
* API測試與開發: 開兩個視窗Visual Studio Code視窗分別進入前、後端容器，後端Flask必須維持開啟著前端才可以做測試，後端Flask開啟方式 : Terminal輸入python main.py

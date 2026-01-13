# 開發環境 Setup

大家直接用 VS Code 的 Dev Containers 開這個專案。往後有甚麼需要自己改動的再麻煩各位自己弄。

**步驟：**
1. 確保 Docker 有開。
2. VS Code 左下角 `><` 點下去 -> `Reopen in Container`。
3. 選單建議選 **Backend**。

**重點設定：**
* **目前環境是空的**：進去後自己 pip install 需要的東西。
* **資料庫 (MySQL)**：Port 是 **3307** (不是 3306)，帳密 `user`/`password`。
* **匯入資料**：把舊的 sql/csv 丟進 `database` 資料夾就會自動匯入。


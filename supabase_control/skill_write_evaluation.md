# 技能寫入 skill_master 評估說明（職缺推薦 / 課程推薦）

## 評估準則

寫入 DB 的技能以**職缺推薦、課程推薦**為目標，因此：

1. **建議寫入**：可對應課程或明確學習路徑、職缺常出現、對推薦有區分度。
2. **建議僅當同義詞**：職缺常寫的名稱，但 skill_master 已有對應主項（例如 MS SQL → SQL Server），只須在既有項目加 synonym，不新增一筆。
3. **建議不寫入**：
   - 非「可學習技能」：如中文打字 20~50、英文打字…（條件描述）
   - 特定廠商/產品且難對應通用課程：如鼎新、正航、文中系統、天心資訊
   - 行銷/平台名稱而非技能：如 Line、Facebook、Instagram、短影音
   - 出現次數極低（如 count &lt; 20）：對推薦覆蓋率幫助小，可後續再擴充

---

## 您提到的項目

- **Linux**：**強烈建議寫入**。職缺 1950 筆、與 DevOps/後端/嵌入式高度相關，且易對應課程與學習路徑，對職缺/課程推薦都很重要。

---

## 建議「新增一筆」寫入 DB（WRITE_NEW）

以下為建議**新增**至 `skill_master` 的項目（已排除僅作同義詞者），並建議 `skill_category` 與 `synonyms`。

| skill_name | count | suggested_category | synonyms 建議 |
|------------|------:|--------------------|----------------|
| Linux | 1950 | Tool | ["linux", "LINUX"] |
| C# | 2641 | Programming | ["c#", "C#", "C Sharp"] |
| HTML | 2066 | Programming | ["html", "HTML5"] |
| CSS | 1796 | Programming | ["css", "CSS3"] |
| C | 1633 | Programming | ["c", "C language"] |
| Excel | 2014 | Tool | ["excel", "Microsoft Excel"] |
| Shell | 270 | Tool | ["shell", "bash", "Shell Script"] |
| PyTorch | 277 | Tool | ["pytorch", "PyTorch"] |
| TensorFlow | 217 | Tool | ["tensorflow", "tensor flow"] |
| R | 102 | Programming | ["r", "R language"] |
| Flutter | 124 | Framework | ["flutter"] |
| Android | 446 | Tool | ["android", "Android SDK"] |
| iOS | 309 | Tool | ["ios", "iOS"] |
| jQuery | 1246 | Framework | ["jquery", "jQuery"] |
| ASP.NET | 1290 | Framework | ["asp.net", "ASP.NET"] |
| Spring | 487 | Framework | ["spring", "Spring Framework"]（與既有 Spring Boot 可合併或分開） |
| Power BI | 262 | Tool | ["power bi", "PowerBI"] |
| Tableau | 214 | Tool | ["tableau"] |
| ETL | 210 | Tool | ["etl"] |
| Figma | 201 | Tool | ["figma"] |
| Matlab | 196 | Tool | ["matlab", "MATLAB"] |
| Sass | 196 | Programming | ["sass", "SCSS"] |
| VueJS | 914 | （已有 Vue，見下方「僅同義詞」） | — |
| ReactJS | 647 | （已有 React，見下方「僅同義詞」） | — |
| LLM | 348 | Tool | ["llm", "Large Language Model"] |
| NLP | 123 | Tool | ["nlp", "Natural Language Processing"] |
| scikit-learn | 67 | Tool | ["scikit-learn", "sklearn"] |
| JIRA | 115 | Tool | ["jira", "Jira"] |
| Vmware | 114 | Tool | ["vmware", "VMware", "ESXi"] |
| RDBMS | 133 | Tool | ["rdbms", "關聯式資料庫"] |
| PL/SQL | 269 | Tool | ["pl/sql", "PLSQL"] |
| JSP | 202 | Framework | ["jsp", "Java Server Pages"] |
| Visual Studio | 502 | Tool | ["visual studio", "VS"] |
| Git 相關 | 822 | （已有 Git，見下方「僅同義詞」） | — |
| Oracle | 已有 | — | — |
| MySQL / PostgreSQL / AWS / Azure | 已有 | — | — |

*Spring 若已有 Spring Boot，可選擇：將 "Spring" 當作 Spring Boot 的同義詞，或另建一筆 "Spring"（Framework）。*

---

## 建議「僅當既有 skill 的同義詞」（不新增一筆）

職缺常寫這些名稱，但 DB 已有對應主項，建議只在既有 skill 的 `synonyms` 裡加入下列名稱，**不要**再新增一筆 skill。

| 職缺常見名稱 | 對應既有 skill_master | 建議動作 |
|--------------|------------------------|----------|
| MS SQL | SQL Server | 在 SQL Server 的 synonyms 加入 "MS SQL", "MSSQL" |
| Github | Git | 在 Git 的 synonyms 加入 "Github", "GitHub" |
| ReactJS | React | 已有 "ReactJS" | 
| VueJS | Vue | 已有 "VueJS" |
| Microsoft Azure | Azure | 在 Azure 的 synonyms 加入 "Microsoft Azure" |
| AngularJS | Angular | 在 Angular 的 synonyms 加入 "AngularJS" |

（若目前 synonyms 已含上述，則無須重複新增。）

---

## 建議不寫入（EXCLUDE）範例與原因

| 類型 | 範例 | 原因 |
|------|------|------|
| 打字/條件描述 | 中文打字20~50、英文打字50~75、中文打字75~100 | 非「技能名稱」，是條件描述，難對應單一課程 |
| 特定 ERP/系統 | 鼎新、正航、文中系統、天心資訊、鼎基 ERP、德安… | 廠商/產品名，難對應通用課程，對推薦區分度低 |
| 平台/行銷 | Line、Facebook、Instagram、短影音 | 行銷管道，非可學習「技能」 |
| 過於細版本 | Windows 10、Windows 7、Windows Server 2019 | 可考慮只收「Windows」「Windows Server」大類再對應職缺 |
| 出現極少 | count &lt; 20 且非核心技能 | 對覆蓋率幫助小，可後續再擴充 |

---

## 實作建議

1. **第一波寫入**：以「建議新增」表中 **count ≥ 100** 且與課程/職缺高度相關者優先（含 **Linux、C#、HTML、CSS、C、Excel、Shell、PyTorch、TensorFlow、R、Flutter、Android、iOS、jQuery、ASP.NET、Power BI、Tableau、ETL、Figma、LLM、JIRA、Vmware** 等）。
2. **同義詞**：檢查並更新既有 40 筆的 `synonyms`（MS SQL→SQL Server、Github→Git、Microsoft Azure→Azure 等）。
3. **後續**：再依推薦效果逐步加入 count 較低但仍有課程可對應的項目（如 Scrum、VBA、UNIX、R、SAP 等）。

以上清單已輸出為 `skill_master_recommended_to_write.csv`，欄位含：`skill_name, count, action, suggested_category, synonyms, note`，可直接作為寫入 DB 的依據。

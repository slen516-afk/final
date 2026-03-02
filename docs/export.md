# E-01 匯出履歷文件 API

## Endpoint

```http
GET /api/resumes/{resume_id}/export?format={pdf|docx|json}
```

## 認證

需要 Bearer Token（`Authorization: Bearer <token>`）

## Query Parameters

| 參數       | 必填 | 預設    | 說明                                  |
| ---------- | ---- | ------- | ------------------------------------- |
| `format` | 否   | `pdf` | 匯出格式：`pdf`、`docx`、`json` |
| `version` | 否   |         | 指定優化版本（如 `1.0`、`2.0`），未帶則取最新版本 |

## Response

### `format=pdf`

- **Content-Type**: `application/pdf`
- **Content-Disposition**: `attachment; filename=resume_{id}.pdf`
- 回傳 PDF 二進位串流

### `format=docx`

- **Content-Type**: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- **Content-Disposition**: `attachment; filename=resume_{id}.docx`
- 回傳 DOCX 二進位串流

### `format=json`

```json
{
  "resume_id": 203,
  "optimization_version": "1.0",
  "format": "json",
  "data": { "...整份 resume_optimization row..." }
}
```

## 錯誤

| HTTP Code | 情境                         |
| --------- | ---------------------------- |
| `400`   | 不支援的 format              |
| `401`   | 未登入 / Token 失效          |
| `404`   | 找不到履歷 或 不屬於該使用者 |
| `500`   | 伺服器錯誤                   |

---

## 前端串接範例

### 下載 PDF

```javascript
async function exportResume(resumeId, format = 'pdf') {
  const token = localStorage.getItem('access_token');

  const res = await fetch(
    `/api/resume/${resumeId}/export?format=${format}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error);
  }

  // format=json → 直接拿 JSON
  if (format === 'json') {
    return await res.json();
  }

  // format=pdf|docx → 觸發瀏覽器下載
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `resume_${resumeId}.${format}`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
```

### React 元件範例

```jsx
function ExportButtons({ resumeId }) {
  const handleExport = (format) => {
    exportResume(resumeId, format).catch(err => alert(err.message));
  };

  return (
    <div>
      <button onClick={() => handleExport('pdf')}>匯出 PDF</button>
      <button onClick={() => handleExport('docx')}>匯出 DOCX</button>
      <button onClick={() => handleExport('json')}>匯出 JSON</button>
    </div>
  );
}
```

### Postman 測試

1. **取得 Token（先登入）**

   - `POST http://localhost:5000/api/auth/login`
   - Body (JSON): `{ "email": "...", "password": "..." }`
   - 複製回傳的 `access_token`
2. **設定 Authorization**

   - 在 export 請求的 **Authorization** tab → Type: `Bearer Token` → 貼上 token
3. **發送 Export 請求**

   - Method: **GET**
   - URL: `http://localhost:5000/api/resumes/203/export?format=pdf`
   - 把 `format` 換成 `docx` 或 `json` 即可切換格式
4. **下載檔案（PDF / DOCX）**

   - 收到回應後點 **Save Response → Save to a file**，直接存成 `.pdf` 或 `.docx`
   - `json` 格式則直接在 Body 顯示

> **注意**：不要在 Headers 手動加 `Accept`，讓 Postman 自動處理即可。

### cURL 測試

```bash
# PDF
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:5000/api/resumes/203/export?format=pdf" \
  -o resume_203.pdf

# DOCX
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:5000/api/resumes/203/export?format=docx" \
  -o resume_203.docx

# JSON
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:5000/api/resumes/203/export?format=json"
```

---

## PDF / DOCX 內容區塊

兩種格式產出的履歷包含以下區塊（依 `structured_data` 內容自動渲染）：

| 區塊            | `structured_data` 欄位                                   | 格式說明 |
| --------------- | ---------------------------------------------------------- | -------- |
| 個人資料 Header | `personal_info.name`, `email`, `phone`, `location` | |
| Summary         | `summary`                                                | str |
| Work Experience | `work_experience[]` 或 `experience[]`                  | `List[str]`（模型輸出）或 `List[dict]` |
| Education       | `education[]`                                            | `List[str]`（模型輸出）或 `List[dict]` |
| Skills          | `skills[]`                                               | `List[str]` |
| Projects        | `projects[]`                                             | `List[str]`（模型輸出）或 `List[dict]` |
| Certifications  | `certifications[]` 或 `certificates[]`                 | `List[str]` 或 `List[dict]` |

> **注意**: `work_experience`、`education`、`projects` 欄位在模型輸出時為 `List[str]`（每筆是完整字串），
> PDF/DOCX builder 同時支援 `List[dict]` legacy 格式。

## 相依套件

- `fpdf2` — PDF 生成
- `python-docx` — DOCX 生成

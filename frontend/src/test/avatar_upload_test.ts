import fs from 'fs';
import path from 'path';

// 注意：此腳本為純 Node.js 環境下的快速測試腳本，用來確保 API 端點運作正常。
// 但由於 fetch API 在 Node 18 之前不完全支援 FormData 傳遞檔案 (需要額外的第三方套件、或者特殊構造)
// 此測試會準備一個模擬的前端請求。

// 您需要替換成您在系統中取得的測試用 JWT Token
const TEST_TOKEN = 'YOUR_TEST_JWT_TOKEN_HERE';
const API_URL = 'http://localhost:5000/api/auth/upload-avatar'; // 請根據後端真實 Port 調整

async function testAvatarUpload() {
    console.log('--- 測試 Avatar Upload API ---');

    if (TEST_TOKEN === 'YOUR_TEST_JWT_TOKEN_HERE') {
        console.error('❌ 請先將檔案中的 TEST_TOKEN 替換為真實有效的 JWT Token');
        return;
    }

    // 1. 準備模擬的照片檔案
    const imagePath = path.resolve(__dirname, '../../assets/logocat.png');

    if (!fs.existsSync(imagePath)) {
        console.error(`❌ 找不到測試用圖片：${imagePath}`);
        return;
    }

    const fileBuffer = fs.readFileSync(imagePath);

    // 由於 Node.js 原生的 fetch 對於 FormData 使用較為複雜
    // 這裡我們直接自己建構 multipart/form-data 的 body
    const boundary = '----WebKitFormBoundary' + Math.random().toString(36).substring(2);
    const crlf = '\r\n';

    // 構造頭部
    const headPrefix =
        `--${boundary}${crlf}` +
        `Content-Disposition: form-data; name="file"; filename="test_avatar.png"${crlf}` +
        `Content-Type: image/png${crlf}${crlf}`;

    const headBuffer = Buffer.from(headPrefix, 'utf-8');
    const tailBuffer = Buffer.from(`${crlf}--${boundary}--${crlf}`, 'utf-8');

    const multipartBody = Buffer.concat([headBuffer, fileBuffer, tailBuffer]);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${TEST_TOKEN}`,
                'Content-Type': `multipart/form-data; boundary=${boundary}`
            },
            body: multipartBody
        });

        console.log(`📡 回應狀態碼: ${response.status}`);

        if (!response.ok) {
            const text = await response.text();
            throw new Error(`上傳失敗: ${response.statusText} - ${text}`);
        }

        const data = await response.json();
        console.log('✅ 測試成功! 回應資料:', data);

        if (data.avatar_url) {
            console.log(`🌐 取得的公開網址: ${data.avatar_url}`);
        }
    } catch (error) {
        console.error('❌ 測試發生錯誤:', error);
    }
}

testAvatarUpload();

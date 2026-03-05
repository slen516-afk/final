import { createClient } from '@supabase/supabase-js';

// 這裡假設你是使用 Vite 開發，環境變數前綴是 VITE_
// 如果你是用 Create React App，請把 VITE_ 換成 REACT_APP_
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
    console.warn('⚠️ 找不到 Supabase 環境變數，請檢查前端的 .env 檔案！');
}

// 建立並匯出 Supabase 客戶端實體
export const supabase = createClient(
    supabaseUrl || '',
    supabaseAnonKey || ''
);
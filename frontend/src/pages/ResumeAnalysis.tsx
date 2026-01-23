import React from "react";
import { ResumeUploader } from "../components/ResumeUploader.tsx"; // 確保路徑正確
import { ArrowLeft } from "lucide-react"; // 如果沒有這個圖示，可以先拿掉
import { Link } from "react-router-dom";

const ResumeAnalysis = () => {
    return (
        // 1. 背景色：這裡改成了綠色系的背景 (bg-emerald-50/50)
        <div className="min-h-screen bg-[#F0FDF9] flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8">

            {/* 頂部導覽或返回按鈕 (選擇性) */}
            <div className="w-full max-w-3xl mb-8">
                <Link to="/" className="inline-flex items-center text-emerald-600 hover:text-emerald-700 font-medium">
                    ← 返回首頁
                </Link>
            </div>

            {/* 2. 頂部 Badge (那個綠色的小膠囊) */}
            <div className="mb-6 inline-flex items-center rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-800">
                ✨ AI 智能履歷分析
            </div>

            {/* 3. 大標題 */}
            <h1 className="mb-4 text-center text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
                讓你的才華
                <span className="block text-emerald-600">被世界精準對焦</span>
            </h1>

            {/* 4. 副標題 */}
            <p className="mb-10 max-w-2xl text-center text-lg text-gray-600">
                結合 AI 技術，輔助打造專屬職涯藍圖，精準匹配理想職缺，提升面試成功率。
            </p>

            {/* 5. 核心元件：這裡放你的上傳區塊 */}
            <div className="w-full max-w-xl">
                <ResumeUploader />
            </div>

        </div>
    );
};

export default ResumeAnalysis;
import { useState, useMemo, useEffect } from "react"; // 👈 1. 記得引入 useEffect
import { useNavigate } from "react-router-dom";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { FileDown, Globe, FileText, Briefcase, AlertTriangle, GraduationCap, Loader2 } from "lucide-react";

const languages = [
  { value: "zh-TW", label: "繁體中文", locked: false },
  { value: "en", label: "English", locked: false },
  { value: "ja", label: "日本語", locked: true },
  { value: "de", label: "Deutsch", locked: true },
  { value: "fr", label: "Français", locked: true },
];

const defaultResume = `# 個人履歷

## 基本資訊
- 姓名：王小明
- 職稱：資深前端工程師
- 經驗：5年

## 技能
- React, TypeScript, Next.js
- Node.js, PostgreSQL
- AWS, Docker`;

// 設定後端 API 網址 (如果你的 .env 有設 VITE_API_URL 就用它，沒有就預設 localhost)
const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

export default function Dashboard() {
  const navigate = useNavigate();
  const [resumeContent, setResumeContent] = useState(defaultResume);
  const [jdContent, setJdContent] = useState("");
  const [language, setLanguage] = useState("zh-TW");
  const [isLoggedIn] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false); // 分析中的狀態

  const hasJD = jdContent.trim().length > 0;

  // 💡 2. 這裡改成 State，不再是寫死的資料
  const [analysisResult, setAnalysisResult] = useState({
    missing: [],
    matching: [],
    score: 0
  });

  // 💡 3. 自動呼叫後端 API (防抖動機制)
  useEffect(() => {
    // 如果沒有 JD，就不分析
    if (!jdContent.trim() || !resumeContent.trim()) return;

    // 設定計時器：使用者停止打字 1 秒後才發送請求
    const timer = setTimeout(async () => {
      setIsAnalyzing(true);
      console.log("🚀 發送分析請求...");

      try {
        const response = await fetch(`${API_BASE}/api/analyze`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            resume_content: resumeContent,
            jd_content: jdContent
          })
        });

        const res = await response.json();

        if (res.status === "success") {
          console.log("✅ 收到分析結果:", res.data);
          setAnalysisResult({
            missing: res.data.missing_skills || [],
            matching: res.data.matching_skills || [],
            score: res.data.score || 0
          });
        }
      } catch (error) {
        console.error("❌ 分析失敗:", error);
      } finally {
        setIsAnalyzing(false);
      }
    }, 1000); // 1000ms = 1秒

    return () => clearTimeout(timer); // 如果使用者還在打字，就取消上一次的計時
  }, [jdContent, resumeContent]); // 當這兩個內容改變時觸發

  // Markdown 預覽轉換
  const previewHtml = useMemo(() => {
    return resumeContent
      .replace(/^### (.+)$/gm, '<h3 class="text-lg font-semibold mt-4 mb-2 text-foreground">$1</h3>')
      .replace(/^## (.+)$/gm, '<h2 class="text-xl font-bold mt-6 mb-3 text-foreground border-b border-border pb-2">$1</h2>')
      .replace(/^# (.+)$/gm, '<h1 class="text-2xl font-bold mb-4 text-primary">$1</h1>')
      .replace(/^- (.+)$/gm, '<li class="ml-4 text-muted-foreground">$1</li>')
      .replace(/\n\n/g, '<br/><br/>');
  }, [resumeContent]);

  return (
    <DashboardLayout>
      <div className="h-screen flex flex-col">
        {/* Toolbar */}
        <header className="px-6 py-4 border-b border-border bg-card/50 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold text-foreground">分析編輯器</h1>
            <Select value={language} onValueChange={setLanguage}>
              <SelectTrigger className="w-40">
                <Globe className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {languages.map((lang) => (
                  <SelectItem key={lang.value} value={lang.value} disabled={lang.locked && !isLoggedIn}>
                    {lang.label} {lang.locked && !isLoggedIn && " 🔒"}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="secondary" onClick={() => navigate("/course-search")} className="gap-2">
              <GraduationCap className="w-4 h-4" /> 找課程
            </Button>
            <Button onClick={() => alert("PDF 匯出功能開發中...")} variant="outline">
              <FileDown className="w-4 h-4 mr-2" /> 匯出 PDF
            </Button>
          </div>
        </header>

        {/* Main Content */}
        <div className="flex-1 flex overflow-hidden">

          {/* 左側：編輯器 */}
          <div className="w-1/2 flex flex-col border-r border-border bg-gray-50/50">
            {/* 履歷區 */}
            <div className="flex-1 flex flex-col p-4 overflow-hidden">
              <div className="flex items-center gap-2 mb-3">
                <FileText className="w-5 h-5 text-primary" />
                <h2 className="font-semibold text-foreground">履歷內容 (Markdown)</h2>
              </div>
              <Textarea
                value={resumeContent}
                onChange={(e) => setResumeContent(e.target.value)}
                className="flex-1 font-mono text-sm resize-none border-2 border-slate-200 bg-white p-4 focus:border-primary shadow-sm"
                placeholder="請輸入或貼上您的 Markdown 履歷..."
              />
            </div>

            {/* JD 區 */}
            <div className="h-64 border-t-2 border-slate-200 p-4 bg-slate-100/50 shadow-inner">
              <div className="flex items-center gap-2 mb-3">
                <Briefcase className="w-5 h-5 text-indigo-600" />
                <h2 className="font-semibold text-slate-800">
                  職缺描述
                  {isAnalyzing && <span className="ml-2 text-xs text-indigo-500 animate-pulse">(AI 分析中...)</span>}
                </h2>
              </div>
              <Textarea
                value={jdContent}
                onChange={(e) => setJdContent(e.target.value)}
                className="h-32 text-sm resize-none border-2 border-slate-300 bg-white p-3 focus:border-indigo-500"
                placeholder="試試看！輸入：'需要熟悉 Python 和 AI 相關技術'..."
              />
            </div>
          </div>

          {/* 右側：分析結果 */}
          <div className="w-1/2 flex flex-col overflow-hidden">
            <div className="flex-1 p-6 overflow-y-auto bg-card">
              <div className="max-w-2xl mx-auto">
                <div
                  className="prose prose-sm max-w-none"
                  dangerouslySetInnerHTML={{ __html: previewHtml }}
                />
              </div>
            </div>

            {/* 分析面板 */}
            <div className="h-64 border-t border-border p-4 bg-muted/20 overflow-y-auto">
              <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                {hasJD ? (
                  <><AlertTriangle className="w-5 h-5 text-amber-500" /> 差距分析</>
                ) : (
                  <><Briefcase className="w-5 h-5 text-primary" /> 職缺推薦</>
                )}
              </h3>

              {hasJD ? (
                <div className="space-y-4">
                  {/* 分數條 - 連動 state */}
                  <div className="p-4 rounded-lg bg-card border border-border">
                    <h4 className="font-medium text-foreground mb-2">技能差距分數</h4>
                    <div className="flex items-center gap-3">
                      <div className="flex-1 h-3 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-red-400 via-amber-400 to-green-400 transition-all duration-1000"
                          style={{ width: `${analysisResult.score}%` }}
                        />
                      </div>
                      <span className="text-sm font-semibold text-foreground">{analysisResult.score}%</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    {/* 🟥 缺少技能 - 修改後的按鈕邏輯 */}
                    <div className="p-3 rounded-lg bg-red-50 dark:bg-red-950/20 border border-red-200">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="text-sm font-medium text-red-700">
                          {isAnalyzing ? "分析中..." : "缺少的技能"}
                        </h4>

                        {/* 👇 修改這裡：一次傳送所有缺少的技能 (限制最多前 3 個，避免請求過多) */}
                        {analysisResult.missing.length > 0 && (
                          <button
                            onClick={() => navigate("/course-search", {
                              state: {
                                // 這裡不拿 [0]，而是拿整個陣列，但為了效能我們取前 3 個
                                autoSearchKeywords: analysisResult.missing.slice(0, 3)
                              }
                            })}
                            className="text-xs flex items-center gap-1 text-red-600 hover:underline font-medium"
                          >
                            <GraduationCap className="w-3 h-3" /> 去補強
                          </button>
                        )}
                      </div>

                      {/* 下面的列表顯示保持不變 */}
                      {isAnalyzing ? (
                        <div className="flex justify-center py-2"><Loader2 className="w-4 h-4 animate-spin text-red-400" /></div>
                      ) : (
                        <ul className="text-xs space-y-1 text-red-600">
                          {analysisResult.missing.length > 0 ? (
                            analysisResult.missing.map(skill => <li key={skill} className="capitalize">• {skill}</li>)
                          ) : (
                            <li>沒有缺少的技能！</li>
                          )}
                        </ul>
                      )}
                    </div>

                    {/* 🟩 匹配技能 - 真實資料 */}
                    <div className="p-3 rounded-lg bg-green-50 dark:bg-green-950/20 border border-green-200">
                      <h4 className="text-sm font-medium text-green-700 mb-2">匹配的技能</h4>
                      {isAnalyzing ? (
                        <div className="flex justify-center py-2"><Loader2 className="w-4 h-4 animate-spin text-green-400" /></div>
                      ) : (
                        <ul className="text-xs space-y-1 text-green-600">
                          {analysisResult.matching.length > 0 ? (
                            analysisResult.matching.map(skill => <li key={skill} className="capitalize">• {skill}</li>)
                          ) : (
                            <li>暫無匹配技能</li>
                          )}
                        </ul>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-sm text-muted-foreground p-2">
                  👈 請在左側輸入職缺描述，AI 將自動分析技能差距。
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
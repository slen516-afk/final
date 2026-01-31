import { useState, useRef } from "react";
// 1. 新增了一些圖標來讓介面更漂亮
import {
    Upload, FileText, Sparkles, CheckCircle2, AlertCircle,
    Briefcase, Code, BookOpen, Trophy, Target
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const ResumeUploader = () => {
    const [file, setFile] = useState<File | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    const inputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            setFile(selectedFile);
            setResult(null);
        }
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const droppedFile = e.dataTransfer.files?.[0];
        if (droppedFile) {
            setFile(droppedFile);
            setResult(null);
        }
    };

    const handleClick = () => {
        inputRef.current?.click();
    };

    const handleAnalyze = async () => {
        if (!file) return;

        setLoading(true);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            // 注意：這裡使用你設定好的環境變數
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/upload-resume`, {
                method: 'POST',
                headers: {
                    'Bypass-Tunnel-Reminder': 'true',
                },
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                setResult(data);
                console.log("分析成功:", data);
            } else {
                alert("上傳失敗: " + (data.error || "未知錯誤"));
            }
        } catch (error: any) {
            console.error("連線錯誤:", error);
            alert("錯誤: " + error.message);
        } finally {
            setLoading(false);
        }
    };


    // 修改後的 renderSuggestionContent (防崩潰版)
    const renderSuggestionContent = () => {
        if (!result?.suggestion) return null;

        // 🛑 1. 攔截錯誤物件 (解決 "Objects are not valid" 的關鍵！)
        // 如果後端回傳 { error: "..." }，我們把它抓出來顯示成紅字
        if (result.suggestion.error) {
            return (
                <div className="p-4 bg-red-50 text-red-600 rounded-lg border border-red-200 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5" />
                    <div>
                        <h4 className="font-bold">分析過程發生錯誤</h4>
                        <p className="text-sm">{result.suggestion.error}</p>
                    </div>
                </div>
            );
        }

        // 🛑 2. 攔截純字串 (非結構化回應)
        if (typeof result.suggestion === 'string') {
            return (
                <div className="p-4 bg-yellow-50 text-yellow-800 rounded-lg whitespace-pre-wrap border border-yellow-200">
                    <h4 className="font-bold mb-2">⚠️ 原始回應 (非結構化數據)：</h4>
                    {result.suggestion}
                </div>
            );
        }

        // ✅ 3. 正常結構化資料 (解構賦值)
        // 加上預設值 {}，防止 undefined 報錯
        const {
            analysis = {},
            job_recommendations = [],
            project_recommendations = [],
            learning_path = []
        } = result.suggestion || {};

        return (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">

                {/* A. 綜合評分區 */}
                <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2">
                            <Trophy className="w-6 h-6 text-yellow-500" />
                            <h3 className="text-xl font-bold text-gray-800">履歷健檢分數</h3>
                        </div>
                        <span className={cn(
                            "text-3xl font-black",
                            (analysis?.score || 0) >= 80 ? "text-green-600" :
                                (analysis?.score || 0) >= 60 ? "text-orange-500" : "text-red-500"
                        )}>
                            {analysis?.score || 0} <span className="text-sm font-normal text-gray-400">/ 100</span>
                        </span>
                    </div>
                    <p className="text-gray-600 italic border-l-4 border-primary pl-3 mb-4">
                        {analysis?.overall_comment || "暫無評語"}
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-green-50 p-3 rounded-lg">
                            <h4 className="font-semibold text-green-700 mb-2">✅ 優勢亮點</h4>
                            <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                                {analysis?.strengths?.length > 0
                                    ? analysis.strengths.map((s: string, i: number) => <li key={i}>{s}</li>)
                                    : <li className="text-gray-400">未偵測到明顯優勢</li>}
                            </ul>
                        </div>
                        <div className="bg-red-50 p-3 rounded-lg">
                            <h4 className="font-semibold text-red-700 mb-2">⚠️ 待加強</h4>
                            <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                                {analysis?.weaknesses?.length > 0
                                    ? analysis.weaknesses.map((w: string, i: number) => <li key={i}>{w}</li>)
                                    : <li className="text-gray-400">未偵測到明顯弱點</li>}
                            </ul>
                        </div>
                    </div>
                </div>

                {/* B. 職缺推薦區 */}
                {job_recommendations?.length > 0 && (
                    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                        <div className="flex items-center gap-2 mb-4">
                            <Briefcase className="w-6 h-6 text-blue-600" />
                            <h3 className="text-xl font-bold text-gray-800">推薦職位方向</h3>
                        </div>
                        <div className="grid gap-3">
                            {job_recommendations.map((job: any, i: number) => (
                                <div key={i} className="p-4 border rounded-lg hover:bg-blue-50/50 transition-colors">
                                    <div className="flex justify-between items-start">
                                        <h4 className="font-bold text-lg text-primary">{job.title || "未知職稱"}</h4>
                                    </div>
                                    <p className="text-sm text-gray-600 mt-1">{job.reason || "無推薦理由"}</p>
                                    {job.missing_skills?.length > 0 && (
                                        <div className="mt-2 flex flex-wrap gap-2">
                                            <span className="text-xs font-semibold text-red-500">缺少技能:</span>
                                            {job.missing_skills.map((skill: string, idx: number) => (
                                                <span key={idx} className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full">
                                                    {skill}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* C. Side Project 推薦區 */}
                {project_recommendations?.length > 0 && (
                    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                        <div className="flex items-center gap-2 mb-4">
                            <Code className="w-6 h-6 text-purple-600" />
                            <h3 className="text-xl font-bold text-gray-800">Side Project 練功建議</h3>
                        </div>
                        <div className="grid gap-4 md:grid-cols-2">
                            {project_recommendations.map((proj: any, i: number) => (
                                <div key={i} className="p-4 bg-gray-50 rounded-lg border border-gray-200 flex flex-col h-full">
                                    <div className="flex justify-between items-start mb-2">
                                        <h4 className="font-bold text-gray-900">{proj.name || "專案名稱"}</h4>
                                        <span className="text-xs px-2 py-1 bg-gray-200 rounded text-gray-600">
                                            難度: {proj.difficulty || "未知"}
                                        </span>
                                    </div>
                                    <p className="text-xs text-purple-600 font-mono mb-2">{proj.tech_stack || "未指定技術"}</p>
                                    <p className="text-sm text-gray-600 flex-grow">{proj.description || "無描述"}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* D. 學習路徑區 */}
                {learning_path?.length > 0 && (
                    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                        <div className="flex items-center gap-2 mb-4">
                            <BookOpen className="w-6 h-6 text-green-600" />
                            <h3 className="text-xl font-bold text-gray-800">學習資源推薦</h3>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left">
                                <thead className="text-xs text-gray-500 uppercase bg-gray-50">
                                    <tr>
                                        <th className="px-4 py-2">主題</th>
                                        <th className="px-4 py-2">推薦資源</th>
                                        <th className="px-4 py-2">優先級</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {learning_path.map((item: any, i: number) => (
                                        <tr key={i} className="border-b">
                                            <td className="px-4 py-3 font-medium">{item.topic || "未知主題"}</td>
                                            <td className="px-4 py-3 text-blue-600">
                                                <a href={item.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                                                    {item.resource || "無連結"}
                                                </a>
                                            </td>
                                            <td className="px-4 py-3">
                                                <span className={cn(
                                                    "px-2 py-1 rounded text-xs",
                                                    item.priority === "高" ? "bg-red-100 text-red-700" :
                                                        item.priority === "中" ? "bg-yellow-100 text-yellow-700" :
                                                            "bg-green-100 text-green-700"
                                                )}>
                                                    {item.priority || "一般"}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        );
    };
    return (
        <div className="w-full max-w-3xl mx-auto mb-20"> {/* 把寬度加大 max-w-3xl，讓卡片更好看 */}
            <div
                className={cn(
                    "relative bg-card rounded-2xl p-8 shadow-card transition-all duration-300",
                    isDragging && "ring-2 ring-primary ring-offset-2"
                )}
            >
                {/* Upload Area */}
                <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={cn(
                        "border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 cursor-pointer",
                        isDragging
                            ? "border-primary bg-accent/50"
                            : "border-border hover:border-primary/50 hover:bg-accent/30",
                        file && "border-primary/30 bg-accent/20"
                    )}
                    onClick={handleClick}
                >
                    <input
                        ref={inputRef}
                        type="file"
                        accept=".pdf,.doc,.docx,.png,.jpg,.jpeg"
                        onChange={handleFileChange}
                        className="hidden"
                    />

                    <div className="flex flex-col items-center gap-4">
                        <div className={cn(
                            "w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300",
                            file ? "bg-primary/10" : "bg-accent"
                        )}>
                            {file ? (
                                <CheckCircle2 className="w-8 h-8 text-primary" />
                            ) : (
                                <Upload className="w-8 h-8 text-primary" />
                            )}
                        </div>

                        <div>
                            <h3 className="text-lg font-semibold text-foreground mb-1">
                                {file ? "檔案已選擇" : "上傳你的履歷"}
                            </h3>
                            <p className="text-sm text-muted-foreground">
                                {file ? file.name : "拖放檔案或點擊選擇"}
                            </p>
                        </div>

                        {!file && (
                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                <FileText className="w-3 h-3" />
                                <span>支援 PDF、Word、圖片格式</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* File Selected State */}
                {file && (
                    <div className="mt-4 p-3 bg-accent/50 rounded-lg flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                            <FileText className="w-5 h-5 text-primary" />
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-foreground truncate">{file.name}</p>
                            <p className="text-xs text-muted-foreground">
                                {(file.size / 1024).toFixed(1)} KB
                            </p>
                        </div>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                                e.stopPropagation();
                                setFile(null);
                                setResult(null);
                            }}
                            className="text-muted-foreground hover:text-foreground"
                        >
                            移除
                        </Button>
                    </div>
                )}

                {/* Analyze Button */}
                <Button
                    onClick={handleAnalyze}
                    disabled={!file || loading}
                    className="w-full mt-6 h-12 text-base font-semibold shadow-button hover:shadow-lg transition-all duration-300"
                >
                    <Sparkles className={cn("w-5 h-5 mr-2", loading && "animate-spin")} />
                    {loading ? "AI 正在分析中..." : "開始 AI 分析"}
                </Button>

                {/* 結果顯示區 */}
                {result && (
                    <div className="mt-8 pt-8 border-t border-gray-100">
                        {/* 這裡呼叫我們新寫的渲染函式 */}
                        {renderSuggestionContent()}

                        {/* OCR 文字內容 (保留在最下方當參考) */}
                        <div className="mt-8">
                            <details className="text-xs text-gray-400 cursor-pointer">
                                <summary className="mb-2 hover:text-gray-600">查看原始辨識文字 (Debug用)</summary>
                                <div className="p-4 bg-gray-50 rounded text-gray-500 font-mono text-xs whitespace-pre-wrap">
                                    {result.text}
                                </div>
                            </details>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ResumeUploader;
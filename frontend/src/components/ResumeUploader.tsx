import { useState, useRef } from "react";
import { Upload, FileText, Sparkles, CheckCircle2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const ResumeUploader = () => {
    const [file, setFile] = useState<File | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    // 1. 新增：用來存後端回傳的結果
    const [result, setResult] = useState<any>(null);
    // 2. 新增：用來控制按鈕轉圈圈的狀態
    const [loading, setLoading] = useState(false);

    const inputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            setFile(selectedFile);
            setResult(null); // 選新檔案時，清空舊結果
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

    // 3. 修改：這裡是核心！連接後端的邏輯
    const handleAnalyze = async () => {
        if (!file) return;

        setLoading(true);
        setResult(null); // 清空上次結果

        const formData = new FormData();
        formData.append('file', file);

        try {
            // 呼叫後端 API
            // 請確認是使用反引號 ` 和 ${} 語法
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/upload-resume`, {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                setResult(data); // 成功！存入結果
                console.log("分析成功:", data);
            } else {
                alert("上傳失敗: " + (data.error || "未知錯誤"));
            }
        } catch (error) {
            console.error("連線錯誤:", error);
            alert("無法連接後端，請確認 main.py 有沒有在跑 (Port 5000)！");
        } finally {
            setLoading(false); // 結束讀取狀態
        }
    };

    return (
        <div className="w-full max-w-lg mx-auto">
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
                    disabled={!file || loading} // 讀取中也要鎖住按鈕
                    className="w-full mt-6 h-12 text-base font-semibold shadow-button hover:shadow-lg transition-all duration-300"
                >
                    <Sparkles className={cn("w-5 h-5 mr-2", loading && "animate-spin")} />
                    {loading ? "AI 正在分析中..." : "開始 AI 分析"}
                </Button>

                {/* 4. 新增：結果顯示區 (原本沒有這段，所以就算分析完你也看不到) */}
                {result && (
                    <div className="mt-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="p-4 rounded-xl bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-900">
                            <div className="flex items-center gap-2 mb-3">
                                <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-400" />
                                <h3 className="font-bold text-green-700 dark:text-green-400">分析完成！</h3>
                            </div>

                            <div className="space-y-4">
                                <div>
                                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">辨識內容</p>
                                    <p className="text-sm text-foreground bg-white dark:bg-black/20 p-3 rounded-md border border-border whitespace-pre-wrap">
                                        {result.text || "無內容"}
                                    </p>
                                </div>

                                <div>
                                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">AI 建議</p>
                                    <p className="text-sm text-foreground bg-white dark:bg-black/20 p-3 rounded-md border border-border whitespace-pre-wrap">
                                        {result.suggestion || "無建議"}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ResumeUploader;
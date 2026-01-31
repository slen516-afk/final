import { useState } from "react";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Lightbulb, Rocket, Loader2, Star, Sparkles, UploadCloud, FileText, X } from "lucide-react";

// 設定你的 API 路徑
const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

const SideProjectGenerator = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null); // 儲存使用者選的檔案
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);

  // 處理檔案選擇
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
    }
  };

  // 移除已選檔案
  const clearFile = () => {
    setSelectedFile(null);
  };

  // 發送檔案給後端 (OCR + AI)
  const handleGenerate = async () => {
    if (!selectedFile) {
        alert("請先選擇履歷檔案 (PDF 或 圖片)！");
        return;
    }

    setLoading(true);
    setSuggestions([]); 

    try {
      // 1. 建構 FormData 物件 (這是上傳檔案的關鍵)
      const formData = new FormData();
      formData.append('file', selectedFile); // 'file' 對應後端接收的參數名稱
      // 如果有額外參數也可以 append，例如: formData.append('user_level', 'Junior');

      // 2. 發送請求
      // 注意：使用 FormData 時，不要手動設定 Content-Type header，瀏覽器會自動處理 boundary
      const response = await fetch(`${API_BASE}/api/projects/suggestions`, {
        method: "POST",
        body: formData, 
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // 3. 處理回傳資料 (假設後端回傳結構是 { suggestions: [...] })
      const resultList = data.suggestions || data || [];
      
      if (Array.isArray(resultList)) {
        setSuggestions(resultList);
      } else {
        console.error("格式錯誤:", data);
      }
    } catch (error) {
      console.error("API Error:", error);
      alert("分析失敗，請稍後再試或確認檔案格式。");
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="p-8 max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2 text-indigo-600">
            <Rocket className="h-8 w-8" />
            AI 履歷專案顧問
          </h1>
          <p className="text-muted-foreground text-lg">
            直接上傳你的履歷 (PDF/圖片)，AI 將自動分析並推薦適合你的 Side Project。
          </p>
        </div>

        {/* Upload Section */}
        <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 text-center">
            
            {!selectedFile ? (
                // 狀態 A: 還沒選檔案
                <div className="border-2 border-dashed border-slate-300 rounded-lg p-10 flex flex-col items-center justify-center gap-4 hover:bg-slate-50 transition-colors cursor-pointer relative">
                    <input 
                        type="file" 
                        accept=".pdf,.png,.jpg,.jpeg"
                        onChange={handleFileChange}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    />
                    <div className="p-4 bg-indigo-50 rounded-full text-indigo-600">
                        <UploadCloud className="w-8 h-8" />
                    </div>
                    <div>
                        <p className="text-lg font-medium text-slate-700">點擊上傳或拖放履歷檔案</p>
                        <p className="text-sm text-slate-500">支援 PDF, PNG, JPG, PDF (最大 5MB)</p>
                    </div>
                </div>
            ) : (
                // 狀態 B: 已經選了檔案
                <div className="flex flex-col items-center gap-6">
                    <div className="flex items-center gap-3 p-4 bg-indigo-50 border border-indigo-100 rounded-lg text-indigo-700">
                        <FileText className="w-6 h-6" />
                        <span className="font-medium text-lg">{selectedFile.name}</span>
                        <button onClick={clearFile} className="ml-2 hover:bg-indigo-200 p-1 rounded-full transition">
                            <X className="w-4 h-4" />
                        </button>
                    </div>

                    <Button size="lg" className="h-12 px-8 bg-indigo-600 hover:bg-indigo-700 text-white text-lg shadow-md" onClick={handleGenerate} disabled={loading}>
                        {loading ? (
                            <>
                                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                                AI 正在讀取並分析履歷中...
                            </>
                        ) : (
                            <>
                                <Sparkles className="mr-2 h-5 w-5" />
                                開始 AI 分析與推薦
                            </>
                        )}
                    </Button>
                </div>
            )}
        </div>

        {/* Results Section */}
        {suggestions.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {suggestions.map((project: any, index: number) => (
                <Card key={index} className="flex flex-col hover:shadow-xl transition-all border-t-4 border-t-indigo-500 bg-white group">
                <CardHeader>
                    <div className="flex justify-between items-start mb-2">
                    <Badge variant="outline" className="bg-indigo-50 text-indigo-700 group-hover:bg-indigo-100 transition-colors">
                        {project.difficulty || "推薦"}
                    </Badge>
                    <div className="flex text-yellow-400">
                        {[...Array(4)].map((_, i) => <Star key={i} className="w-3 h-3 fill-current" />)}
                    </div>
                    </div>
                    <CardTitle className="text-xl text-slate-900 group-hover:text-indigo-600 transition-colors">
                    {project.title || project.project_name || "未命名專案"}
                    </CardTitle>
                </CardHeader>
                
                <CardContent className="flex-1 space-y-4">
                    <p className="text-slate-600 line-clamp-4 leading-relaxed">
                        {project.reason || project.description}
                    </p>
                    <div className="flex flex-wrap gap-2 pt-2">
                    {(project.tech_keywords || project.tech_stack || []).map((tech: string, i: number) => (
                        <Badge key={i} variant="secondary" className="bg-slate-100 text-slate-700 hover:bg-slate-200">
                            {tech}
                        </Badge>
                    ))}
                    </div>
                </CardContent>

                <CardFooter className="pt-4 border-t bg-slate-50/50 text-xs text-slate-500 flex justify-between items-center">
                    <span>AI 匹配度: 高</span>
                    <Button variant="ghost" size="sm" className="text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 p-0 h-auto font-medium">
                        查看詳情 &rarr;
                    </Button>
                </CardFooter>
                </Card>
            ))}
            </div>
        )}

        {/* Empty State / Hints */}
        {!loading && suggestions.length === 0 && !selectedFile && (
          <div className="text-center py-10 opacity-60">
            <Lightbulb className="w-12 h-12 mx-auto mb-2 text-slate-300" />
            <p>不知道該做什麼 Side Project 嗎？上傳履歷試試看！</p>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default SideProjectGenerator;
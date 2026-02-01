import { useState } from "react";
import { Header } from "@/components/Header"; // 確保你有這個元件
import { Footer } from "@/components/Footer"; // 確保你有這個元件
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Rocket, Loader2, Star, Sparkles, UploadCloud,
  FileText, X, Lightbulb, ArrowRight
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

// 設定你的 API 路徑
const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

const SideProjectGenerator = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<any[]>([]);

  // 處理檔案選擇
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
    }
  };

  // 移除已選檔案
  const clearFile = () => {
    setSelectedFile(null);
    setSuggestions([]); // 清除檔案時順便清除建議，重置狀態
  };

  // 發送檔案給後端
  const handleGenerate = async () => {
    if (!selectedFile) {
      alert("請先選擇履歷檔案 (PDF 或 圖片)！");
      return;
    }

    setLoading(true);
    setSuggestions([]);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch(`${API_BASE}/api/projects/suggestions`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
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
    // 1. 最外層套用 Hero Gradient 背景，取代原本的 DashboardLayout
    <div className="min-h-screen flex flex-col bg-gradient-hero font-sans text-foreground">

      <Header />

      <main className="flex-1 container mx-auto px-4 pt-24 pb-12">

        {/* 2. 標題區塊動畫 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-3xl mx-auto text-center mb-10"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary mb-4 border border-primary/20 backdrop-blur-sm">
            <Sparkles className="w-4 h-4" />
            <span className="text-sm font-medium">AI 驅動職涯加速器</span>
          </div>

          <h1 className="text-3xl md:text-5xl font-bold text-foreground mb-6 leading-tight">
            AI 履歷專案顧問
          </h1>
          <p className="text-muted-foreground text-lg md:text-xl max-w-2xl mx-auto">
            直接上傳你的履歷 (PDF/圖片)，AI 將自動分析並推薦<br className="hidden md:block" />
            量身打造的 Side Project，讓你的作品集脫穎而出。
          </p>
        </motion.div>

        {/* 3. 上傳區塊：使用 glass-strong 樣式 */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="max-w-4xl mx-auto mb-16"
        >
          <div className="glass-strong rounded-3xl p-8 md:p-12 shadow-elevated border border-white/20 relative overflow-hidden">

            {/* 裝飾背景球 */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-3xl -mr-32 -mt-32 pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl -ml-32 -mb-32 pointer-events-none" />

            <div className="relative z-10">
              {!selectedFile ? (
                // --- 狀態 A: 尚未選擇檔案 ---
                <div className="border-2 border-dashed border-primary/20 bg-white/40 hover:bg-white/60 transition-colors rounded-2xl p-10 flex flex-col items-center justify-center gap-4 cursor-pointer relative group">
                  <input
                    type="file"
                    accept=".pdf,.png,.jpg,.jpeg"
                    onChange={handleFileChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20"
                  />
                  <div className="p-5 bg-white rounded-full text-primary shadow-sm group-hover:scale-110 transition-transform duration-300">
                    <UploadCloud className="w-8 h-8" />
                  </div>
                  <div className="text-center">
                    <p className="text-xl font-semibold text-foreground mb-2">點擊上傳或拖放檔案</p>
                    <p className="text-sm text-muted-foreground">支援 PDF, PNG, JPG (最大 5MB)</p>
                  </div>
                </div>
              ) : (
                // --- 狀態 B: 已選擇檔案 ---
                <div className="flex flex-col items-center gap-8 py-4">
                  <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="flex items-center gap-4 p-4 pl-6 pr-4 bg-white/60 border border-white/50 backdrop-blur-md rounded-2xl shadow-sm w-full max-w-md justify-between"
                  >
                    <div className="flex items-center gap-3 overflow-hidden">
                      <div className="p-2 bg-primary/10 rounded-lg text-primary">
                        <FileText className="w-6 h-6" />
                      </div>
                      <span className="font-medium text-lg truncate text-foreground">{selectedFile.name}</span>
                    </div>
                    <button
                      onClick={clearFile}
                      className="p-2 hover:bg-red-50 text-muted-foreground hover:text-red-500 rounded-full transition-colors"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </motion.div>

                  <Button
                    size="lg"
                    className="h-14 px-10 rounded-full text-lg shadow-glow hover:shadow-glow-hover transition-all duration-300"
                    variant="hero"
                    onClick={handleGenerate}
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                        AI 深度分析中...
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-5 w-5" />
                        生成專案建議
                      </>
                    )}
                  </Button>
                </div>
              )}
            </div>
          </div>
        </motion.div>

        {/* 4. 結果區塊：使用 Grid 排版顯示卡片 */}
        <AnimatePresence>
          {suggestions.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto"
            >
              {suggestions.map((project: any, index: number) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="h-full flex flex-col hover:shadow-xl hover:-translate-y-1 transition-all duration-300 border-white/40 bg-white/60 backdrop-blur-sm group overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-purple-500 transform origin-left scale-x-0 group-hover:scale-x-100 transition-transform duration-300" />

                    <CardHeader>
                      <div className="flex justify-between items-start mb-3">
                        <Badge variant="outline" className="bg-primary/5 text-primary border-primary/20">
                          {project.difficulty || "推薦"}
                        </Badge>
                        <div className="flex text-yellow-400">
                          {[...Array(4)].map((_, i) => <Star key={i} className="w-3 h-3 fill-current" />)}
                        </div>
                      </div>
                      <CardTitle className="text-xl text-foreground group-hover:text-primary transition-colors line-clamp-2">
                        {project.title || project.project_name || "未命名專案"}
                      </CardTitle>
                    </CardHeader>

                    <CardContent className="flex-1 space-y-4">
                      <p className="text-muted-foreground line-clamp-4 leading-relaxed text-sm">
                        {project.reason || project.description}
                      </p>
                      <div className="flex flex-wrap gap-2 pt-2">
                        {(project.tech_keywords || project.tech_stack || []).map((tech: string, i: number) => (
                          <Badge key={i} variant="secondary" className="bg-white text-slate-600 border border-slate-100">
                            {tech}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>

                    <CardFooter className="pt-4 border-t border-slate-100 bg-white/50 flex justify-between items-center">
                      <span className="text-xs font-medium text-muted-foreground flex items-center gap-1">
                        <Sparkles className="w-3 h-3 text-primary" />
                        AI 匹配度: 高
                      </span>
                      <Button variant="ghost" size="sm" className="text-primary hover:text-primary/80 hover:bg-primary/5 p-0 h-auto font-medium gap-1">
                        查看詳情 <ArrowRight className="w-3 h-3" />
                      </Button>
                    </CardFooter>
                  </Card>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* 5. 空狀態提示 */}
        {!loading && suggestions.length === 0 && !selectedFile && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-center py-12 opacity-60"
          >
            <Lightbulb className="w-12 h-12 mx-auto mb-4 text-slate-300" />
            <p className="text-muted-foreground">不知道該做什麼 Side Project 嗎？上傳履歷試試看！</p>
          </motion.div>
        )}

      </main>

      <Footer />
    </div>
  );
};

export default SideProjectGenerator;
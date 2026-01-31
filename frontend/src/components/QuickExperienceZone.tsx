import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
    Upload, FileText, Plus, X, Sparkles, Loader2, Link as LinkIcon, 
    Image as ImageIcon, CheckCircle2, AlertCircle,
    Trophy, Briefcase, Code, BookOpen, Target
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { cn } from "@/lib/utils"; // 記得確認你的專案有這個 utils

interface JobDescription {
  id: number;
  content: string;
  url: string;
  image: File | null;
  previewUrl?: string;
  isUrlValid?: boolean;
}

export function QuickExperienceZone() {
  const reportSectionRef = useRef<HTMLDivElement>(null);
  
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobDescriptions, setJobDescriptions] = useState<JobDescription[]>([
    { id: 1, content: "", url: "", image: null, isUrlValid: true },
  ]);
  
  const [result, setResult] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
  
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > MAX_FILE_SIZE) {
        toast.error("檔案大小不能超過 5MB");
        return;
      }
      setResumeFile(file);
      setResult(null); 
      toast.success("履歷上傳成功");
    }
  };

  const updateJobDescription = (id: number, field: keyof JobDescription, value: any) => {
    setJobDescriptions(prev => prev.map(jd => {
      if (jd.id !== id) return jd;
      let updates: Partial<JobDescription> = { [field]: value };

      if (field === "url") {
        const urlPattern = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/;
        updates.isUrlValid = value === "" || urlPattern.test(value);
      }

      if (field === "image") {
        const file = value as File | null;
        if (file && file.size > MAX_FILE_SIZE) {
          toast.error("截圖大小不能超過 5MB");
          return jd;
        }
        if (jd.previewUrl) URL.revokeObjectURL(jd.previewUrl);
        updates.previewUrl = file ? URL.createObjectURL(file) : undefined;
      }
      return { ...jd, ...updates };
    }));
  };

  useEffect(() => {
    return () => {
      jobDescriptions.forEach(jd => jd.previewUrl && URL.revokeObjectURL(jd.previewUrl));
    };
  }, []);

  const addJobDescription = () => {
    if (jobDescriptions.length < 5) {
      setJobDescriptions([
        ...jobDescriptions,
        { id: Date.now(), content: "", url:"", image: null, isUrlValid: true }
      ]);
    } else {
      toast.info("最多可添加 5 個職位描述");
    }
  };
  
  const removeJobDescription = (id: number) => {
    if (jobDescriptions.length > 1) {
      const target = jobDescriptions.find(jd => jd.id === id);
      if (target?.previewUrl) URL.revokeObjectURL(target.previewUrl);
      setJobDescriptions(jobDescriptions.filter((jd) => jd.id !== id));
    }
  };

  const handleAnalyze = async () => {
    if (!resumeFile) {
      toast.error("請先上傳您的履歷");
      return;
    }
    
    setIsAnalyzing(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', resumeFile);

    try {
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
        toast.success("分析完成！");

        setTimeout(() => {
            if (reportSectionRef.current) {
                reportSectionRef.current.scrollIntoView({ 
                    behavior: "smooth", 
                    block: "start" 
                });
            }
        }, 100);
      } else {
        // 即使失敗，也要把錯誤訊息存起來顯示，不要讓畫面壞掉
        setResult({ suggestion: { error: data.error || "未知錯誤" } });
        toast.error("分析失敗: " + (data.error || "未知錯誤"));
      }
    } catch (error: any) {
      console.error("連線錯誤:", error);
      setResult({ suggestion: { error: "無法連接後端: " + error.message } });
      toast.error("無法連接後端");
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 核心渲染邏輯 (把 JSON 變成漂亮卡片)
  const renderSuggestionContent = () => {
    if (!result?.suggestion) return null;

    // 1. 攔截錯誤
    if (result.suggestion.error) {
         return (
            <div className="p-6 bg-red-50 text-red-600 rounded-xl border border-red-200 flex items-start gap-3">
                <AlertCircle className="w-6 h-6 flex-shrink-0 mt-0.5" />
                <div>
                    <h4 className="font-bold text-lg mb-1">分析過程發生錯誤</h4>
                    <p className="text-sm opacity-90">{result.suggestion.error}</p>
                </div>
            </div>
        );
    }

    // 2. 攔截純字串
    if (typeof result.suggestion === 'string') {
        return (
            <div className="p-6 bg-yellow-50 text-yellow-800 rounded-xl whitespace-pre-wrap border border-yellow-200">
                <h4 className="font-bold mb-2 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5"/> 原始回應 (非結構化數據)
                </h4>
                {result.suggestion}
            </div>
        );
    }

    // 3. 正常結構化資料
    const { 
        analysis = {}, 
        job_recommendations = [], 
        project_recommendations = [], 
        learning_path = [] 
    } = result.suggestion || {};

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            
            {/* A. 綜合評分區 */}
            <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-green-100 shadow-lg">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-yellow-100 rounded-lg">
                            <Trophy className="w-6 h-6 text-yellow-600" />
                        </div>
                        <h3 className="text-xl font-bold text-slate-800">履歷健檢分數</h3>
                    </div>
                    <div className="flex items-baseline gap-1">
                        <span className={cn(
                            "text-4xl font-black",
                            (analysis?.score || 0) >= 80 ? "text-green-600" : 
                            (analysis?.score || 0) >= 60 ? "text-orange-500" : "text-red-500"
                        )}>
                            {analysis?.score || 0}
                        </span>
                        <span className="text-gray-400 font-medium">/ 100</span>
                    </div>
                </div>
                
                <p className="text-slate-600 italic border-l-4 border-primary pl-4 py-1 mb-6 bg-slate-50 rounded-r-lg">
                    {analysis?.overall_comment || "暫無評語"}
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-green-50/80 p-4 rounded-xl border border-green-100">
                        <h4 className="font-bold text-green-800 mb-3 flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4"/> 優勢亮點
                        </h4>
                        <ul className="space-y-2">
                            {analysis?.strengths?.length > 0 
                                ? analysis.strengths.map((s: string, i: number) => (
                                    <li key={i} className="flex items-start gap-2 text-sm text-green-700">
                                        <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-green-500 flex-shrink-0"/>
                                        {s}
                                    </li>
                                ))
                                : <li className="text-gray-400 text-sm">未偵測到明顯優勢</li>}
                        </ul>
                    </div>
                    <div className="bg-red-50/80 p-4 rounded-xl border border-red-100">
                        <h4 className="font-bold text-red-800 mb-3 flex items-center gap-2">
                            <AlertCircle className="w-4 h-4"/> 待加強
                        </h4>
                        <ul className="space-y-2">
                            {analysis?.weaknesses?.length > 0
                                ? analysis.weaknesses.map((w: string, i: number) => (
                                    <li key={i} className="flex items-start gap-2 text-sm text-red-700">
                                        <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-red-500 flex-shrink-0"/>
                                        {w}
                                    </li>
                                ))
                                : <li className="text-gray-400 text-sm">未偵測到明顯弱點</li>}
                        </ul>
                    </div>
                </div>
            </div>

            {/* B. 職缺推薦區 */}
            {job_recommendations?.length > 0 && (
                <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-blue-100 shadow-lg">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 bg-blue-100 rounded-lg">
                            <Briefcase className="w-6 h-6 text-blue-600" />
                        </div>
                        <h3 className="text-xl font-bold text-slate-800">推薦職位方向</h3>
                    </div>
                    <div className="grid gap-4 md:grid-cols-2">
                        {job_recommendations.map((job: any, i: number) => (
                            <div key={i} className="p-5 border border-slate-200 rounded-xl hover:shadow-md hover:border-blue-200 transition-all bg-white group">
                                <div className="flex justify-between items-start mb-2">
                                    <h4 className="font-bold text-lg text-slate-800 group-hover:text-blue-600 transition-colors">
                                        {job.title || "未知職稱"}
                                    </h4>
                                </div>
                                <p className="text-sm text-slate-600 mb-4 leading-relaxed">
                                    {job.reason || "無推薦理由"}
                                </p>
                                {job.missing_skills?.length > 0 && (
                                    <div className="flex flex-wrap gap-2 pt-3 border-t border-slate-100">
                                        <span className="text-[10px] font-bold text-red-500 uppercase tracking-wider mt-0.5">Missing:</span>
                                        {job.missing_skills.map((skill: string, idx: number) => (
                                            <span key={idx} className="px-2 py-0.5 bg-red-50 text-red-600 text-xs rounded-full font-medium">
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

            {/* C. Side Project & Learning */}
            <div className="grid md:grid-cols-2 gap-6">
                {/* Side Projects */}
                {project_recommendations?.length > 0 && (
                    <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-purple-100 shadow-lg h-full">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="p-2 bg-purple-100 rounded-lg">
                                <Code className="w-6 h-6 text-purple-600" />
                            </div>
                            <h3 className="text-xl font-bold text-slate-800">練功專案</h3>
                        </div>
                        <div className="space-y-4">
                            {project_recommendations.map((proj: any, i: number) => (
                                <div key={i} className="p-4 bg-purple-50/50 rounded-xl border border-purple-100">
                                    <div className="flex justify-between items-start mb-2">
                                        <h4 className="font-bold text-slate-800">{proj.name}</h4>
                                        <span className="text-xs px-2 py-1 bg-white border border-purple-200 rounded-full text-purple-700 font-medium shadow-sm">
                                            {proj.difficulty}
                                        </span>
                                    </div>
                                    <p className="text-xs font-mono text-purple-600 mb-2 bg-purple-100/50 inline-block px-2 py-0.5 rounded">
                                        {proj.tech_stack}
                                    </p>
                                    <p className="text-sm text-slate-600 leading-relaxed">
                                        {proj.description}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Learning Path */}
                {learning_path?.length > 0 && (
                    <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-cyan-100 shadow-lg h-full">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="p-2 bg-cyan-100 rounded-lg">
                                <BookOpen className="w-6 h-6 text-cyan-600" />
                            </div>
                            <h3 className="text-xl font-bold text-slate-800">學習資源</h3>
                        </div>
                        <div className="space-y-3">
                            {learning_path.map((item: any, i: number) => (
                                <div key={i} className="flex items-center gap-3 p-3 rounded-xl hover:bg-cyan-50 transition-colors group">
                                    <div className={cn(
                                        "w-2 h-2 rounded-full flex-shrink-0",
                                        item.priority === "高" ? "bg-red-500" :
                                        item.priority === "中" ? "bg-yellow-500" : "bg-green-500"
                                    )} />
                                    <div className="flex-1 min-w-0">
                                        <div className="font-medium text-slate-800 truncate">{item.topic}</div>
                                        <a href="#" className="text-xs text-cyan-600 hover:underline truncate block">
                                            {item.resource}
                                        </a>
                                    </div>
                                    <span className="text-[10px] text-slate-400 font-medium px-2 py-1 bg-slate-100 rounded">
                                        {item.priority}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
  };
  
  return (
    <>
    <section id="quick-experience" className="py-24 bg-background relative">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-secondary text-secondary-foreground text-sm font-medium mb-4">
            <Sparkles className="w-4 h-4" />
            免登入快速體驗區
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            履歷優化服務
          </h2>
          <p className="text-muted-foreground max-w-xl mx-auto">
            上傳您的履歷，即刻體驗 AI 深度分析與精準職缺匹配
          </p>
        </motion.div>

        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="glass rounded-3xl p-8 shadow-elevated"
          >
            <div className="grid md:grid-cols-2 gap-8">
              {/* Resume Upload */}
              <div>
                <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                  <FileText className="w-5 h-5 text-primary" />
                  上傳履歷
                </h3>
                <label
                  htmlFor="resume-upload"
                  className={`
                    relative flex flex-col items-center justify-center p-8 rounded-2xl border-2 border-dashed
                    transition-all duration-300 cursor-pointer
                    ${resumeFile
                      ? "border-primary bg-primary/5"
                      : "border-border hover:border-primary/50 hover:bg-accent"
                    }
                  `}
                >
                  {resumeFile ? (
                    <>
                      <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                        <FileText className="w-8 h-8 text-primary" />
                      </div>
                      <p className="font-medium text-foreground">{resumeFile.name}</p>
                      <p className="text-sm text-muted-foreground mt-1">點擊更換檔案</p>
                    </>
                  ) : (
                    <>
                      <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
                        <Upload className="w-8 h-8 text-muted-foreground" />
                      </div>
                      <p className="font-medium text-foreground">拖曳或點擊上傳</p>
                      <p className="text-sm text-muted-foreground mt-1">支援 PDF / 圖片格式</p> 
                    </>
                  )}
                  <input
                    id="resume-upload"
                    type="file"
                    accept=".pdf,.png,.jpg,.jpeg"
                    onChange={handleFileUpload}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                </label>
              </div>

              {/* Job Descriptions (Optional) */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-primary" />
                    上傳職缺資訊 <span className="text-sm font-normal text-muted-foreground">(選填)</span>
                  </h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={addJobDescription}
                    disabled={jobDescriptions.length >= 5}
                    className="text-primary"
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    新增
                  </Button>
                </div>
                <div className="space-y-4 max-h-[350px] overflow-y-auto pr-2 custom-scrollbar">
                    <AnimatePresence>
                      {jobDescriptions.map((jd, index) => (
                        <motion.div key={jd.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="relative p-4 rounded-xl border border-border/50 bg-background/50 space-y-3">
                          <div className="flex items-center gap-2">
                            <LinkIcon className="w-3.5 h-3.5 text-muted-foreground" />
                            <Input 
                              placeholder="可輸入網址" 
                              value={jd.url}
                              onChange={(e) => updateJobDescription(jd.id, "url", e.target.value)}
                              className={`h-7 text-xs bg-transparent ${!jd.isUrlValid ? "border-destructive" : ""}`}
                            />
                        </div>
                        <Textarea
                          placeholder={`職缺描述 ${index + 1}...`}
                          value={jd.content}
                          onChange={(e) => updateJobDescription(jd.id, "content", e.target.value)}
                          className="min-h-[80px] pr-8 resize-none rounded-xl bg-background/50 border-border/50 focus:border-primary"
                        />
                          <div className="flex items-center justify-between">
                            <label className="flex items-center gap-2 cursor-pointer text-[10px] text-muted-foreground hover:text-primary">
                              <ImageIcon className="w-3.5 h-3.5" />
                              <span>{jd.image ? "更換截圖" : "上傳截圖"}</span>
                              <input type="file" accept="image/*" className="hidden" onChange={(e) => updateJobDescription(jd.id, "image", e.target.files?.[0])} />
                            </label>
                            {jd.previewUrl && (
                              <div className="relative w-8 h-8 rounded border overflow-hidden">
                                <img src={jd.previewUrl} className="w-full h-full object-cover" />
                                <button onClick={() => updateJobDescription(jd.id, "image", null)} className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                                  <X className="w-3 h-3 text-white" />
                                </button>
                              </div>
                            )}
                          </div>
                          {jobDescriptions.length > 1 && (
                            <button onClick={() => removeJobDescription(jd.id)} className="absolute -top-1 -right-1 p-1 bg-background border rounded-full shadow-sm"><X className="w-2.5 h-2.5" /></button>
                          )}
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>
                </div>
              </div>

              <div className="mt-8 flex justify-center">
                <Button variant="default" size="lg" onClick={handleAnalyze} disabled={isAnalyzing} className="min-w-[200px] shadow-lg shadow-primary/20">
                  {isAnalyzing ? <><Loader2 className="animate-spin mr-2 h-5 w-5" /> AI 分析中...</> : "開始分析"}
                </Button>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* 分析結果顯示區 (Result Section) */}
      <div ref={reportSectionRef} id="file-search-anchor" className="scroll-mt-20 container mx-auto px-4 pb-20">
        <AnimatePresence>
            {result && (
                <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="max-w-4xl mx-auto"
                >
                    <div className="mb-6 flex items-center justify-between">
                         <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center shadow-sm">
                                <CheckCircle2 className="w-6 h-6 text-green-600" />
                            </div>
                            <h3 className="text-2xl font-bold text-slate-800">分析報告完成</h3>
                        </div>
                        <Button variant="outline" size="sm" onClick={() => setResult(null)}>
                            清空結果
                        </Button>
                    </div>

                    {/* 呼叫渲染函式 */}
                    {renderSuggestionContent()}

                    {/* 除錯用：顯示原始辨識文字 (可選) */}
                    {result.text && (
                        <div className="mt-8 text-center">
                            <details className="text-xs text-gray-400 cursor-pointer inline-block">
                                <summary className="hover:text-gray-600 transition-colors">查看 OCR 原始文字 (Debug)</summary>
                                <div className="mt-4 p-4 bg-slate-50 rounded-xl text-left border border-slate-100 max-h-60 overflow-y-auto font-mono">
                                    {result.text}
                                </div>
                            </details>
                        </div>
                    )}
                </motion.div>
            )}
        </AnimatePresence>
      </div>
    </>
  );
}
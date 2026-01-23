import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, Plus, X, Sparkles, ArrowRight, Loader2, Link as LinkIcon, Image as ImageIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { useRef } from "react";

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
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  //驗證用戶是否登入 
  const [isLoggedIn] = useState(false);

  const MAX_FILE_SIZE = 5 * 1024 *1024; // 5MB
  
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.type !== "application/pdf") {
        toast.error("請上傳 PDF 格式檔案");
        return;
      }
      if (file.size > MAX_FILE_SIZE) {
        toast.error("檔案大小不能超過 5MB");
        return;
      }
      setResumeFile(file);
      toast.success("履歷上傳成功");
    }
  };

  const updateJobDescription = (id: number, field: keyof JobDescription, value: any) => {
    setJobDescriptions(prev => prev.map(jd => {
      if (jd.id !== id) return jd;
      let updates: Partial<JobDescription> = { [field]: value };

      // URL 驗證邏輯
      if (field === "url") {
        const urlPattern = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/;
        updates.isUrlValid = value === "" || urlPattern.test(value);
      }

      // 圖片處理與預覽
      if (field === "image") {
        const file = value as File | null;
        if (file && file.size > MAX_FILE_SIZE) {
          toast.error("截圖大小不能超過 5MB");
          return jd;
        }

        // 若已有舊預覽則釋放
        if (jd.previewUrl) URL.revokeObjectURL(jd.previewUrl);
        updates.previewUrl = file ? URL.createObjectURL(file) : undefined;
      }
      return { ...jd, ...updates };
    }));

  };

  // 清除預覽網址
  useEffect(() => {
    return () => {
      jobDescriptions.forEach(jd => jd.previewUrl && URL.revokeObjectURL(jd.previewUrl));
    };
  }, []);

    const addJobDescription = () => {
    if (jobDescriptions.length < 5) {
      setJobDescriptions([
        ...jobDescriptions,
        { id: Date.now(), content: "" , url:"", image: null, isUrlValid: true}]);
    }else{
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

 const handleAnalyze = () => {
    if (!resumeFile) {
      toast.error("請先上傳您的履歷");
      return;
    }
    setIsAnalyzing(true);

    setTimeout(() => {
      setIsAnalyzing(false);
      toast.success("分析完成！");

      // 用戶有登入的情況下，自動傳進報告區塊
      if (isLoggedIn && reportSectionRef.current) {
        reportSectionRef.current.scrollIntoView({ 
          behavior: "smooth", 
          block: "start" 
        });
      }
    }, 2000);
  };

  useEffect(() => {
    return () => {
      jobDescriptions.forEach(jd => jd.previewUrl && URL.revokeObjectURL(jd.previewUrl));
    };
  }, []);
  
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
                      ? "border-primary bg-mint-50"
                      : "border-border hover:border-primary/50 hover:bg-accent"
                    }
                  `}
                >
                  {resumeFile ? (
                    <>
                      <div className="w-16 h-16 rounded-full bg-mint-100 flex items-center justify-center mb-4">
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
                      <p className="text-sm text-muted-foreground mt-1">支援 PDF / DOC格式</p> 
                      {/* 後端邏輯未加入DOC格式 */}
                    </>
                  )}
                  <input
                    id="resume-upload"
                    type="file"
                    accept=".md"
                    onChange={handleFileUpload}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                </label>
              </div>

              {/* Job Descriptions */}
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
                  onChange={(e) => updateJobDescription(jd.id, e.target.value)}
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
                <Button variant="hero" size="xl" onClick={handleAnalyze} disabled={isAnalyzing} className="min-w-[200px]">
                  {isAnalyzing ? <><Loader2 className="animate-spin mr-2 h-5 w-5" /> 分析中...</> : "開始分析"}
                </Button>
              </div>
            </motion.div>
          </div>
        </div>
      </section>
      {/*關聯至目標滾動區域:FileSearch，待補PATH*/}
      <div ref={reportSectionRef} id="file-search-anchor" className="scroll-mt-20">
      </div>
    </>
  );
}

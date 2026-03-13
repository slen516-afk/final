import { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { getJobDetailAPI, fetchUserResumesAPI, generateCoverLetterAPI } from '@/services/api';
import { useAsyncTask } from '@/hooks/useAsyncTask';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import { useAppState } from '@/contexts/AppContext';
import AuthModal from '@/components/auth/AuthModal';
import RightDrawer from '@/components/panels/RightDrawer';
import { AILoadingSpinner } from '@/components/loading/LoadingStates';
import JobDetailHeader from '@/components/jobs/detail/JobDetailHeader';
import JobDetailContent from '@/components/jobs/detail/JobDetailContent';
import JobDetailUserAnalysis from '@/components/jobs/detail/JobDetailUserAnalysis';
import JobDetailSkeleton from '@/components/jobs/detail/JobDetailSkeleton';
import type { RecommendedJobDetail } from '@/types/job';
import { mockCoverLetter, getMockRecommendedJobDetail } from '@/mocks/jobs';
import {
  ChevronLeft,
  Copy,
  CheckCircle2,
  ListFilter
} from 'lucide-react';
import { Button } from '@/components/ui/button';

const JobDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  // 🌟 1. 從全域狀態拿到你的真實 user 資料
  const { isLoggedIn, user, isMockMode } = useAppState();
  // 🛡️ 防護：相容不同開發人員定義的欄位名 (user_id 或 id)
  const realUserId = user?.user_id || user?.id;

  const [isLoading, setIsLoading] = useState(true);
  const [job, setJob] = useState<RecommendedJobDetail | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);

  // 🌟 2. 履歷選擇相關狀態 (新增 isFetching 用來顯示載入中)
  const [userResumes, setUserResumes] = useState<any[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<string>("");
  const [isFetchingResumes, setIsFetchingResumes] = useState(false);

  // Cover letter drawer states
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [letterContent, setLetterContent] = useState<{ subject: string; body: string } | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const [isCopied, setIsCopied] = useState(false);

  // Load job details
  useEffect(() => {
    const fetchJob = async () => {
      if (!id) return;
      setIsLoading(true);
      try {
        // 如果是 Mock 模式，直接拿 Mock 資料
        if (isMockMode && isMockMode()) {
          console.log("🛠️ [JobDetail] Mock Mode 啟動，加載模擬職缺詳情");
          await new Promise(resolve => setTimeout(resolve, 800));
          setJob(getMockRecommendedJobDetail(id));
          setIsLoading(false);
          return;
        }

        const res = await getJobDetailAPI(id);
        const rawData = res.data;
        const stateJob = (location.state as any)?.job;

        // 將後端原始資料對接成 RecommendedJobDetail (後端已標準化，此處僅做防呆)
        const formattedJob: RecommendedJobDetail = {
          ...rawData,
          id: rawData.id || rawData.job_id || id,
          title: rawData.title || rawData.job_name || rawData.job_title || "職缺詳情",
          company: rawData.company || rawData.comp_name || rawData.company_name || "精選企業",
          industry: rawData.industry || rawData.job_category || "產業未提供",
          description: rawData.description || rawData.job_description || "",
          location: rawData.full_address || rawData.location || rawData.city || "地區未提供",
          externalUrl: rawData.externalUrl || rawData.source_url || `https://www.104.com.tw/job/${id}`,
          salary_range: rawData.salary_range || "依公司規定",
          requirements: Array.isArray(rawData.requirements) ? rawData.requirements : (rawData.requirements ? [rawData.requirements] : []),
          // 以下 AI 欄位優先從 Router state (上頁點擊傳遞) 取得，若無則留空
          strengths: stateJob?.strengths || "",
          weaknesses: stateJob?.weaknesses || "",
          interview_tips: stateJob?.interview_tips || ""
        };
        setJob(formattedJob);
      } catch (error) {
        console.error("無法取得職缺詳細資料:", error);
        toast.error('無法載入職缺資訊');

        // 備援方案：出錯也給 Mock 資料
        setJob(getMockRecommendedJobDetail(id));
      } finally {
        setIsLoading(false);
      }
    };
    fetchJob();
  }, [id, isMockMode]);

  // 🌟 3. 當使用者打開側邊欄時，獲取履歷清單
  useEffect(() => {
    const loadMyResumes = async () => {
      console.log("🔍 [JobDetail] loadMyResumes triggered", { isLoggedIn, realUserId, drawerOpen });
      if (isLoggedIn && realUserId) {
        setIsFetchingResumes(true);
        try {
          const data = await fetchUserResumesAPI(realUserId);
          console.log("✅ [JobDetail] Fetched resumes:", data);
          if (Array.isArray(data)) {
            setUserResumes(data);
            if (data.length > 0) {
              const firstId = data[0].resume_id?.toString() || "";
              setSelectedResumeId(firstId);
              console.log("🎯 [JobDetail] Default selected ID:", firstId);
            }
          } else {
            setUserResumes([]);
          }
        } catch (error) {
          console.error("❌ [JobDetail] Fetch resumes failed:", error);
          toast.error("無法載入您的履歷清單");
        } finally {
          setIsFetchingResumes(false);
        }
      } else {
        console.warn("⚠️ [JobDetail] No logged in user or missing ID", { isLoggedIn, realUserId });
      }
    };

    if (drawerOpen) {
      loadMyResumes();
    }
  }, [drawerOpen, isLoggedIn, realUserId]);
  // 🌟 AI Cover Letter 任務監聽
  const { runTask: runGenerateCoverLetter, status: genStatus, result: genResult, progress: genProgress } = useAsyncTask();

  useEffect(() => {
     if (genStatus === 'SUCCESS' && genResult) {
          // 解析內容，後端回傳的是 Markdown 或純文字
          const rawText = genResult;
          let subject = `應徵 ${job?.company} - ${job?.title}`;
          let body = rawText;

          if (rawText.includes("主旨：") || rawText.includes("Subject:")) {
            const parts = rawText.split(/\n/);
            subject = parts[0].replace(/主旨：|Subject:/, "").trim();
            body = parts.slice(1).join("\n").trim();
          }

          setLetterContent({ subject, body });
          toast.success("推薦信生成完成！");
          setIsGenerating(false);
     } else if (genStatus === 'FAILURE') {
          toast.error("推薦信生成失敗，請重試");
          setIsGenerating(false);
     }
  }, [genStatus, genResult, job]);

  const handleStartGeneration = async () => {
    if (!selectedResumeId) {
      toast.error("請先選擇一份履歷");
      return;
    }
    
    // 🌟 依照是否為 mock 模式切換
    if (isMockMode && isMockMode()) {
        console.log("🛠️ [JobDetail] Mock 模式：產生模擬推薦信");
        setIsGenerating(true);
        setLetterContent(null);
        await new Promise(resolve => setTimeout(resolve, 2000));
        setLetterContent(mockCoverLetter(job?.title, job?.company));
        setIsGenerating(false);
        return;
    }

    setIsGenerating(true);
    setLetterContent(null);
    setIsCopied(false);

    console.log("🚀 [JobDetail] 真實模式：呼叫後端 AI 生成推薦信", { 
        job_id: id, 
        resume_id: selectedResumeId 
    });

    // 構建 Payload
    const payload: any = { job_id: id };
    if (selectedResumeId.includes("_opt_")) {
        payload.optimization_id = selectedResumeId;
    } else {
        payload.resume_id = selectedResumeId;
    }

    runGenerateCoverLetter('cover_letter', payload);
  };

  const handleGenerateLetterClick = () => {
    if (!isLoggedIn) {
      setShowAuthModal(true);
      return;
    }
    setDrawerOpen(true);
    setLetterContent(null); // 重置狀態
  };

  // --- 複製與下載功能保留不變 ---
  const handleCopyContent = async () => {
    if (!letterContent) return;
    const fullContent = `主旨：${letterContent.subject}\n\n${letterContent.body}`;
    await navigator.clipboard.writeText(fullContent);
    setIsCopied(true);
    toast.success('已複製到剪貼簿');
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handleDownload = async () => {
    if (!letterContent) return;
    setIsDownloading(true);
    const fullContent = `主旨：${letterContent.subject}\n\n${letterContent.body}`;
    const blob = new Blob([fullContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `推薦信_${job?.company}_${job?.title}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    setIsDownloading(false);
    toast.success('推薦信已下載');
  };

  const handleBack = () => navigate(-1);

  return (
    <>
      <div className="min-h-screen">
        <div className="container py-8 animate-fade-in">
          <div className="max-w-4xl mx-auto">
            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="mb-6">
              <Button variant="ghost" onClick={handleBack} className="gap-2 text-muted-foreground hover:text-foreground">
                <ChevronLeft className="h-4 w-4" /> 返回推薦職缺列表
              </Button>
            </motion.div>

            <AnimatePresence mode="wait">
              {isLoading ? (
                <JobDetailSkeleton />
              ) : job ? (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                  {/* 使用新組件：Header */}
                  <JobDetailHeader
                    job={job}
                    onGenerateLetter={handleGenerateLetterClick}
                  />

                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* 使用新組件：內容描述 (佔 2 欄) */}
                    <div className="lg:col-span-2">
                      <JobDetailContent job={job} />
                    </div>

                    {/* 使用新組件：AI 用戶分析 (佔 1 欄) */}
                    <div className="space-y-6">
                      <JobDetailUserAnalysis job={job} />
                    </div>
                  </div>
                </motion.div>
              ) : (
                <div className="text-center py-12"><p>找不到此職缺資訊</p></div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>

      <RightDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title="AI 推薦信生成"
        subtitle={job?.title}
        showDownload={!!letterContent}
        onDownload={handleDownload}
        isDownloading={isDownloading}
      >
        <AnimatePresence mode="wait">
          {isFetchingResumes ? (
            <AILoadingSpinner message="正在從資料庫同步您的履歷清單..." />
          ) : !letterContent && !isGenerating ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-primary font-medium">
                  <ListFilter className="h-4 w-4" />
                  <span>第一步：選擇您的履歷</span>
                </div>

                {userResumes.length > 0 ? (
                  <div className="grid gap-3">
                    {userResumes.map((resume) => (
                      <div
                        key={resume.resume_id}
                        onClick={() => setSelectedResumeId(resume.resume_id.toString())}
                        className={`p-4 rounded-xl border-2 transition-all cursor-pointer flex items-center gap-3 ${selectedResumeId === resume.resume_id.toString()
                          ? "border-primary bg-primary/5 shadow-sm"
                          : "border-border hover:border-primary/30"
                          }`}
                      >
                        <div className={`h-4 w-4 rounded-full border-2 flex-shrink-0 flex items-center justify-center ${selectedResumeId === resume.resume_id.toString() ? "border-primary" : "border-muted-foreground/30"
                          }`}>
                          {selectedResumeId === resume.resume_id.toString() && <div className="h-2 w-2 rounded-full bg-primary" />}
                        </div>
                        <div className="min-w-0 flex-1">
                          {/* 🌟 欄位名稱對齊資料庫 resume_name */}
                          <p className="text-sm font-medium truncate">{resume.resume_name}</p>
                          <p className="text-[10px] text-muted-foreground uppercase">{resume.resume_type}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg text-amber-700 text-sm">
                    您尚未上傳履歷，請先前往「我的履歷」上傳。
                  </div>
                )}
              </div>
              <Button onClick={handleStartGeneration} className="w-full gradient-primary" disabled={userResumes.length === 0}>
                開始 AI 分析並撰寫
              </Button>
            </motion.div>
          ) : isGenerating ? (
            <div className="space-y-4">
               <AILoadingSpinner message={`正在撰寫個人化推薦信... ${genProgress}%`} />
               <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
                   <motion.div className="h-full bg-primary" initial={{ width: 0 }} animate={{ width: `${genProgress}%` }} />
               </div>
            </div>
          ) : letterContent ? (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
              <div className="bg-primary/5 border border-primary/10 rounded-lg p-3 text-[10px] text-primary flex items-center gap-2">
                <CheckCircle2 className="h-3 w-3" /> 已結合您的真實履歷進行分析
              </div>
              <div className="bg-muted/50 rounded-lg p-4 border">
                <label className="text-xs font-medium text-muted-foreground uppercase">主旨</label>
                <p className="mt-1 font-medium">{letterContent.subject}</p>
              </div>
              <div className="bg-muted/30 rounded-lg p-4 border">
                <label className="text-xs font-medium text-muted-foreground uppercase">內容</label>
                <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">{letterContent.body}</p>
              </div>
              <Button variant="outline" className="w-full gap-2" onClick={handleCopyContent}>
                {isCopied ? <><CheckCircle2 className="h-4 w-4 text-primary" />已複製</> : <><Copy className="h-4 w-4" />複製內容</>}
              </Button>
            </motion.div>
          ) : null}
        </AnimatePresence>
      </RightDrawer>

      <AuthModal open={showAuthModal} onOpenChange={setShowAuthModal} />
    </>
  );
};

export default JobDetail;

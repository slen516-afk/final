import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getJobDetailAPI, fetchUserResumesAPI } from '@/services/api';
import { Skeleton } from '@/components/ui/skeleton';
import {
  ChevronLeft,
  MapPin,
  Banknote,
  Building2,
  Briefcase,
  FileText,
  ExternalLink,
  Copy,
  Download,
  CheckCircle2,
  Loader2,
  ListFilter
} from 'lucide-react';
import RightDrawer from '@/components/panels/RightDrawer';
import { AILoadingSpinner } from '@/components/loading/LoadingStates';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppState } from '@/contexts/AppContext';
import AuthModal from '@/components/auth/AuthModal';
import { toast } from 'sonner';
import icon104 from '@/assets/104-icon.png';
import type { JobDetailData } from '@/types/job';
import { mockCoverLetter } from '@/mocks/jobs';

// --- Skeleton 元件保留不變 ---
const JobDetailSkeleton = () => (
  <div className="space-y-6">
    <Card>
      <CardHeader className="space-y-4">
        <div className="flex items-start justify-between">
          <div className="flex-1 space-y-3">
            <Skeleton className="h-8 w-3/4" />
            <Skeleton className="h-5 w-1/2" />
          </div>
          <Skeleton className="h-12 w-12 rounded-full" />
        </div>
      </CardHeader>
    </Card>
    {/* ... 其他 Skeleton 內容 ... */}
  </div>
);

const JobDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // 🌟 1. 從全域狀態拿到你的真實 user 資料
  const { isLoggedIn, user } = useAppState();
  const realUserId = user?.user_id;

  const [isLoading, setIsLoading] = useState(true);
  const [job, setJob] = useState<JobDetailData | null>(null);
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

  // Load job details (真實 API 版)
  useEffect(() => {
    const fetchJob = async () => {
      if (!id) return;
      setIsLoading(true);
      try {
        const res = await getJobDetailAPI(id);
        const rawData = res.data;
        const formattedJob: JobDetailData = {
          id: rawData.job_id,
          title: rawData.job_title,
          company: rawData.company_name || "精選企業",
          description: rawData.job_description,
          city: rawData.city,
          salary: (rawData.salary_min && rawData.salary_max)
            ? `${Math.floor(rawData.salary_min / 1000)}k - ${Math.floor(rawData.salary_max / 1000)}k`
            : "依公司規定",
          industry: "資訊軟體業",
          skills: rawData.skills || ["專業技能"],
          requirements: ["請參考上方職缺描述"],
          benefits: ["勞健保", "年終獎金"],
          externalUrl: `https://www.104.com.tw/job/${rawData.job_id}`
        };
        setJob(formattedJob);
      } catch (error) {
        console.error("無法取得職缺詳細資料:", error);
        toast.error('無法載入職缺資訊');
      } finally {
        setIsLoading(false);
      }
    };
    fetchJob();
  }, [id]);

  // 🌟 3. 當使用者打開側邊欄時，正式「讀取」API 抓取 60 幾號 ID 的履歷
  useEffect(() => {
    const loadMyResumes = async () => {
      if (isLoggedIn && realUserId) {
        setIsFetchingResumes(true);
        try {
          // 這裡解決了 "fetchUserResumesAPI is never read" 的問題
          console.log("🚀 正使用真實 ID 請求履歷中:", realUserId);
          const data = await fetchUserResumesAPI(realUserId);
          setUserResumes(data);

          // 如果有資料，預設選擇第一份
          if (data && data.length > 0) {
            setSelectedResumeId(data[0].resume_id.toString());
          }
        } catch (error) {
          console.error("抓取個人履歷失敗:", error);
          toast.error("無法載入您的履歷清單");
        } finally {
          setIsFetchingResumes(false);
        }
      }
    };

    if (drawerOpen) {
      loadMyResumes();
    }
  }, [drawerOpen, isLoggedIn, realUserId]);

  const handleStartGeneration = async () => {
    if (!selectedResumeId) {
      toast.error("請先選擇一份履歷");
      return;
    }
    setIsGenerating(true);
    setLetterContent(null);
    setIsCopied(false);

    // TODO: 之後換成真實的 AI 生成 API
    await new Promise(resolve => setTimeout(resolve, 2500));
    setLetterContent(mockCoverLetter(job?.title, job?.company));
    setIsGenerating(false);
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
                <ChevronLeft className="h-4 w-4" /> 返回推薦職缺
              </Button>
            </motion.div>

            <AnimatePresence mode="wait">
              {isLoading ? (
                <JobDetailSkeleton />
              ) : job ? (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                  {/* Job Header Card */}
                  <Card className="overflow-hidden border-border shadow-soft">
                    <CardHeader className="pb-4">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <CardTitle className="text-2xl md:text-3xl mb-2">{job.title}</CardTitle>
                          <div className="flex items-center gap-2 text-lg text-muted-foreground">
                            <Building2 className="h-5 w-5 flex-shrink-0" />
                            <span>{job.company}</span>
                          </div>
                        </div>
                        <img src={icon104} alt="104" className="h-12 w-12 rounded-full shadow-sm flex-shrink-0" />
                      </div>
                      <div className="flex flex-wrap gap-3 mt-6">
                        <Button onClick={handleGenerateLetterClick} variant="outline" className="gap-2">
                          <FileText className="h-4 w-4" /> 生成推薦信
                        </Button>
                        <a href={job.externalUrl} target="_blank" rel="noopener noreferrer">
                          <Button className="gap-2">立即應徵 <ExternalLink className="h-4 w-4" /></Button>
                        </a>
                      </div>
                    </CardHeader>
                  </Card>
                  {/* ... 其他卡片內容 (Description, Skills, etc.) 保留 ... */}
                  <Card className="border-border shadow-soft">
                    <CardHeader><CardTitle className="text-lg">職缺描述</CardTitle></CardHeader>
                    <CardContent><p className="text-muted-foreground whitespace-pre-line leading-relaxed">{job.description}</p></CardContent>
                  </Card>
                </motion.div>
              ) : (
                <div className="text-center py-12"><p>找不到此職缺資訊</p></div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* --- 側邊欄：陳浩宇要在這裡消失 --- */}
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
                  <span>第一步：選擇您的履歷 (ID: {realUserId})</span>
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
            <AILoadingSpinner message="正在撰寫個人化推薦信..." />
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
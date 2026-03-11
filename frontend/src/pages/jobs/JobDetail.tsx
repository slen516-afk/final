import { useState, useEffect, useMemo, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { getJobDetailAPI, generateCoverLetterAPI } from '@/services/api';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import { useAppState } from '@/contexts/AppContext';
import { useResumes } from '@/contexts/ResumeContext';
import AuthModal from '@/components/auth/AuthModal';
import RightDrawer from '@/components/panels/RightDrawer';
import { AILoadingSpinner } from '@/components/loading/LoadingStates';
import JobDetailHeader from '@/components/jobs/detail/JobDetailHeader';
import JobDetailContent from '@/components/jobs/detail/JobDetailContent';
import JobDetailUserAnalysis from '@/components/jobs/detail/JobDetailUserAnalysis';
import JobDetailSkeleton from '@/components/jobs/detail/JobDetailSkeleton';
import type { RecommendedJobDetail } from '@/types/job';
import { mockCoverLetter, getMockRecommendedJobDetail } from '@/mocks/jobs';
import { parseCoverLetterContent } from '@/utils/coverLetterParser';
import {
  ChevronLeft,
  ListFilter,
  Mail,
  Link as LinkIcon,
  User,
} from 'lucide-react';
import { Button } from '@/components/ui/button';

export interface CoverLetterResult {
  subject: string;
  content: string;
}

const JobDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  // 1. 從全域狀態拿到你的真實 user 資料
  const { isLoggedIn, user, isMockMode } = useAppState();

  // 從 Context 取得在推薦頁面選擇的履歷
  const { selectedResumeId } = useResumes();

  const [isLoading, setIsLoading] = useState(true);
  const [job, setJob] = useState<RecommendedJobDetail | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Cover letter drawer states
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [letterContent, setLetterContent] = useState<CoverLetterResult | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);

  const parsed = useMemo(
    () => letterContent ? parseCoverLetterContent(letterContent.content) : null,
    [letterContent]
  );

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
  }, [id, isMockMode, location.state]);

  const handleGenerateLetter = async () => {
    if (!isLoggedIn) {
      setShowAuthModal(true);
      return;
    }

    if (!selectedResumeId) {
      toast.error("您尚未在推薦頁面選擇履歷");
      return;
    }

    setDrawerOpen(true);
    setIsGenerating(true);
    setLetterContent(null);

    if (isMockMode && isMockMode()) {
      setTimeout(() => {
        const mockData = mockCoverLetter(job?.title, job?.company);
        setLetterContent({
          subject: mockData.subject,
          content: mockData.content as string
        });
        setIsGenerating(false);
      }, 2000);
      return;
    }

    try {
      if (!id) throw new Error("缺少職缺 ID");

      // 從 Recommendation 儲存的偏好設定抓出當時選擇的履歷種類
      const savedData = localStorage.getItem('userJobSurvey');
      const surveyPayload = savedData ? JSON.parse(savedData) : null;

      const docId = surveyPayload?.resumeId || selectedResumeId;
      const sourceType = surveyPayload?.sourceType || "RESUME";

      if (!docId) {
        toast.error("找不到原本選擇的履歷 ID，請返回推薦頁面重新選擇");
        setIsGenerating(false);
        return;
      }

      // 根據 sourceType 判斷傳哪個欄位給後端
      const resId = sourceType === "RESUME" ? docId.toString() : "";
      const optId = sourceType === "OPTIMIZATION" ? docId.toString() : "";

      const coverLetterContent = await generateCoverLetterAPI(id, resId, optId);

      let extractedSubject = "推薦信";
      let mainContent = coverLetterContent;

      const subjectMatch = coverLetterContent.match(/主旨[：:\s]+([^\n]+)/);
      if (subjectMatch) {
        extractedSubject = subjectMatch[1].trim();
        mainContent = coverLetterContent.replace(subjectMatch[0], '').trim();
      }

      setLetterContent({
        subject: extractedSubject,
        content: mainContent
      });
      toast.success("推薦信生成成功！");
    } catch (error: any) {
      console.error("生成推薦信失敗:", error);
      toast.error(error.message || "生成失敗，請稍後再試");
    } finally {
      setIsGenerating(false);
    }
  };

  // --- 下載功能保留不變 ---
  const handleDownload = async () => {
    if (!letterContent || !parsed) return;
    setIsDownloading(true);

    const date = new Date().toLocaleDateString('zh-TW', { year: 'numeric', month: 'long', day: 'numeric' });
    const divider = '─'.repeat(40);

    const lines = [
      divider,
      `主旨：${letterContent.subject}`,
      `日期：${date}`,
      divider,
      '',
      ...parsed.bodyParagraphs.map(p => p + '\n'),
      '',
      divider,
      ...(parsed.author ? [`此致，${parsed.author}`] : []),
      ...(parsed.email ? [`Email：${parsed.email}`] : []),
      ...(parsed.portfolio ? [`Portfolio：${parsed.portfolio}`] : []),
      divider,
    ];

    const fullContent = lines.join('\n');
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
            {/* Back navigation */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="mb-6"
            >
              <Button
                variant="link"
                onClick={() => navigate('/jobs/recommendations')}
                className="gap-2 px-0 text-[#8d4903] hover:text-[#8d4903]/80"
              >
                <ChevronLeft className="h-4 w-4" />
                返回推薦職缺列表
              </Button>
            </motion.div>

            <AnimatePresence mode="wait">
              {isLoading ? (
                <motion.div
                  key="skeleton"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <JobDetailSkeleton />
                </motion.div>
              ) : job ? (
                <motion.div
                  key="content"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="space-y-6"
                >
                  <JobDetailHeader job={job} onGenerateLetter={handleGenerateLetter} />
                  <JobDetailContent job={job} />
                  <JobDetailUserAnalysis job={job} />
                </motion.div>
              ) : (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-center py-12"
                >
                  <p className="text-muted-foreground">找不到此職缺資訊</p>
                  <Button onClick={() => navigate('/jobs/recommendations')} className="mt-4">
                    返回推薦職缺列表
                  </Button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Cover Letter Right Drawer */}
      <RightDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title="推薦信生成"
        subtitle="根據職缺內容與您的履歷生成"
        showDownload={!!letterContent}
        onDownload={handleDownload}
        isDownloading={isDownloading}
      >
        <AnimatePresence mode="wait">
          {isGenerating ? (
            <AILoadingSpinner message="正在為您撰寫個人化推薦信..." />
          ) : letterContent && parsed ? (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-5"
            >
              {/* Letter Header — Subject */}
              <div className="rounded-xl p-5 border" style={{ backgroundColor: '#fbf1e8' }}>
                <p className="text-xs text-muted-foreground mb-1 tracking-wider">主旨</p>
                <p className="text-lg font-bold text-[#502D03] leading-snug tracking-tight">
                  {letterContent.subject}
                </p>
              </div>

              {/* Letter Body — Paragraphs */}
              <div className="rounded-xl p-6 border bg-card space-y-4">
                {parsed.bodyParagraphs.map((para, i) => (
                  <p
                    key={i}
                    className="text-sm leading-[1.9] tracking-wide text-foreground/85"
                    style={{ textIndent: '2em' }}
                  >
                    {para}
                  </p>
                ))}
              </div>

              {/* Signature Block */}
              {(parsed.author || parsed.email || parsed.portfolio) && (
                <div className="rounded-xl p-5 border bg-muted/30 space-y-3">
                  {parsed.author && (
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                      <p className="text-sm font-semibold text-foreground">此致，{parsed.author}</p>
                    </div>
                  )}
                  {parsed.email && (
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                      <a
                        href={`mailto:${parsed.email}`}
                        className="text-sm text-[#8d4903] hover:underline"
                      >
                        {parsed.email}
                      </a>
                    </div>
                  )}
                  {parsed.portfolio && (
                    <div className="flex items-center gap-2">
                      <LinkIcon className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                      <a
                        href={parsed.portfolio}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-[#8d4903] hover:underline break-all"
                      >
                        {parsed.portfolio}
                      </a>
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          ) : null}
        </AnimatePresence>
      </RightDrawer>


      <AuthModal open={showAuthModal} onOpenChange={setShowAuthModal} />
    </>
  );
};

export default JobDetail;
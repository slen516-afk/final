import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
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
  Loader2
} from 'lucide-react';
import RightDrawer from '@/components/panels/RightDrawer';
import { AILoadingSpinner } from '@/components/loading/LoadingStates';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppState } from '@/contexts/AppContext';
import AuthModal from '@/components/auth/AuthModal';
import { toast } from 'sonner';
import icon104 from '@/assets/104-icon.png';
import type { JobDetailData } from '@/types/job';
import { getMockJobDetail, mockCoverLetter } from '@/mocks/jobs';

// Skeleton for job detail
const JobDetailSkeleton = () => (
  <div className="space-y-6">
    {/* Header skeleton */}
    <Card>
      <CardHeader className="space-y-4">
        <div className="flex items-start justify-between">
          <div className="flex-1 space-y-3">
            <Skeleton className="h-8 w-3/4" />
            <Skeleton className="h-5 w-1/2" />
          </div>
          <Skeleton className="h-12 w-12 rounded-full" />
        </div>
        <div className="flex flex-wrap gap-3">
          <Skeleton className="h-6 w-24" />
          <Skeleton className="h-6 w-28" />
          <Skeleton className="h-6 w-20" />
        </div>
      </CardHeader>
    </Card>

    {/* Description skeleton */}
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-32" />
      </CardHeader>
      <CardContent className="space-y-3">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-2/3" />
      </CardContent>
    </Card>

    {/* Requirements skeleton */}
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-32" />
      </CardHeader>
      <CardContent className="space-y-2">
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-4 w-full" />
        ))}
      </CardContent>
    </Card>
  </div>
);

const JobDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isLoggedIn } = useAppState();
  
  // Page states
  const [isLoading, setIsLoading] = useState(true);
  const [job, setJob] = useState<JobDetailData | null>(null);
  
  // Auth modal
  const [showAuthModal, setShowAuthModal] = useState(false);
  
  // Cover letter drawer states
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [letterContent, setLetterContent] = useState<{ subject: string; body: string } | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const [isCopied, setIsCopied] = useState(false);

  // Load job details
  useEffect(() => {
    setIsLoading(true);
    // TODO: Replace with API call
    const timer = setTimeout(() => {
      if (id) {
        setJob(getMockJobDetail(id));
      }
      setIsLoading(false);
    }, 1000);
    
    return () => clearTimeout(timer);
  }, [id]);

  const handleGenerateLetter = async () => {
    // Check login status first
    if (!isLoggedIn) {
      setShowAuthModal(true);
      return;
    }
    
    setDrawerOpen(true);
    setIsGenerating(true);
    setLetterContent(null);
    setIsCopied(false);
    
    // TODO: Replace with API call
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    setLetterContent(mockCoverLetter(job?.title, job?.company));
    
    setIsGenerating(false);
  };

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
    await new Promise(resolve => setTimeout(resolve, 500));
    
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

  const handleBack = () => {
    navigate(-1);
  };

  return (
    <>
      <div className="min-h-screen">
        <div className="container py-8 animate-fade-in">
          <div className="max-w-4xl mx-auto">
            {/* Smart Back Navigation */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="mb-6"
            >
              <Button
                variant="ghost"
                onClick={handleBack}
                className="gap-2 text-muted-foreground hover:text-foreground"
              >
                <ChevronLeft className="h-4 w-4" />
                返回推薦職缺
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
                        <img 
                          src={icon104} 
                          alt="104人力銀行" 
                          className="h-12 w-12 rounded-full shadow-sm flex-shrink-0"
                        />
                      </div>
                      
                      {/* Job meta info */}
                      <div className="flex flex-wrap gap-3 mt-4">
                        <Badge variant="secondary" className="flex items-center gap-1 px-3 py-1">
                          <MapPin className="h-3.5 w-3.5" />
                          {job.city}
                        </Badge>
                        <Badge variant="secondary" className="flex items-center gap-1 px-3 py-1">
                          <Banknote className="h-3.5 w-3.5" />
                          {job.salary}
                        </Badge>
                        <Badge variant="outline" className="flex items-center gap-1 px-3 py-1">
                          <Briefcase className="h-3.5 w-3.5" />
                          {job.industry}
                        </Badge>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex flex-wrap gap-3 mt-6">
                        <Button onClick={handleGenerateLetter} variant="outline" className="gap-2">
                          <FileText className="h-4 w-4" />
                          生成推薦信
                        </Button>
                        <a 
                          href={job.externalUrl} 
                          target="_blank" 
                          rel="noopener noreferrer"
                        >
                          <Button className="gap-2">
                            立即應徵
                            <ExternalLink className="h-4 w-4" />
                          </Button>
                        </a>
                      </div>
                    </CardHeader>
                  </Card>

                  {/* Job Description */}
                  <Card className="border-border shadow-soft">
                    <CardHeader>
                      <CardTitle className="text-lg">職缺描述</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-muted-foreground whitespace-pre-line leading-relaxed">
                        {job.description}
                      </p>
                    </CardContent>
                  </Card>

                  {/* Skills */}
                  <Card className="border-border shadow-soft">
                    <CardHeader>
                      <CardTitle className="text-lg">所需技能</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-2">
                        {job.skills.map((skill, index) => (
                          <Badge 
                            key={index} 
                            variant="secondary"
                            className="px-3 py-1"
                          >
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Requirements */}
                  <Card className="border-border shadow-soft">
                    <CardHeader>
                      <CardTitle className="text-lg">工作要求</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {job.requirements.map((req, index) => (
                          <li 
                            key={index} 
                            className="flex items-start gap-3 text-muted-foreground"
                          >
                            <span className="inline-block h-1.5 w-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                            <span>{req}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>

                  {/* Benefits */}
                  <Card className="border-border shadow-soft">
                    <CardHeader>
                      <CardTitle className="text-lg">福利制度</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {job.benefits.map((benefit, index) => (
                          <li 
                            key={index} 
                            className="flex items-start gap-3 text-muted-foreground"
                          >
                            <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                            <span>{benefit}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>

                  {/* Bottom CTA */}
                  <Card className="border-border shadow-soft bg-gradient-to-r from-primary/5 to-primary/10">
                    <CardContent className="py-6">
                      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                        <div>
                          <h3 className="font-semibold text-lg">對這個職位感興趣嗎？</h3>
                          <p className="text-muted-foreground text-sm">立即投遞履歷，開啟您的新職涯旅程</p>
                        </div>
                        <a 
                          href={job.externalUrl} 
                          target="_blank" 
                          rel="noopener noreferrer"
                        >
                          <Button size="lg" className="gap-2">
                            前往應徵
                            <ExternalLink className="h-4 w-4" />
                          </Button>
                        </a>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ) : (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-center py-12"
                >
                  <p className="text-muted-foreground">找不到此職缺資訊</p>
                  <Button onClick={handleBack} className="mt-4">
                    返回職缺列表
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
        title="AI 推薦信生成"
        subtitle="根據職缺內容與您的履歷生成"
        showDownload={!!letterContent}
        onDownload={handleDownload}
        isDownloading={isDownloading}
      >
        <AnimatePresence mode="wait">
          {isGenerating ? (
            <AILoadingSpinner message="正在為您撰寫個人化推薦信..." />
          ) : letterContent ? (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              {/* Subject */}
              <div className="bg-muted/50 rounded-lg p-4 border">
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  主旨
                </label>
                <p className="mt-1 font-medium">{letterContent.subject}</p>
              </div>

              {/* Body */}
              <div className="bg-muted/30 rounded-lg p-4 border">
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  內容
                </label>
                <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
                  {letterContent.body}
                </p>
              </div>

              {/* Copy Button */}
              <Button
                variant="outline"
                className="w-full gap-2"
                onClick={handleCopyContent}
              >
                {isCopied ? (
                  <>
                    <CheckCircle2 className="h-4 w-4 text-primary" />
                    已複製
                  </>
                ) : (
                  <>
                    <Copy className="h-4 w-4" />
                    複製內容
                  </>
                )}
              </Button>
            </motion.div>
          ) : null}
        </AnimatePresence>
      </RightDrawer>

      {/* Auth Modal */}
      <AuthModal
        open={showAuthModal}
        onOpenChange={setShowAuthModal}
      />
    </>
  );
};

export default JobDetail;

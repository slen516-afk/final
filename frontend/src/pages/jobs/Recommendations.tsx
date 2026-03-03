import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  MapPin,
  Building2,
  Banknote,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  Briefcase,
  Star,
  Heart,
  RefreshCw,
} from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Link, useSearchParams } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { useAppState } from "@/contexts/AppContext";
import { AILoadingSpinner } from "@/components/loading/LoadingStates";
import EmbeddedPreferenceSurvey from "@/components/survey/EmbeddedPreferenceSurvey";
import ResumeSelector from "@/components/survey/ResumeSelector";
import AlertModal from "@/components/modals/AlertModal";
import icon104 from "@/assets/104-icon.png";
import type { JobData } from "@/types/job";
import { getJobRecommendationsAPI } from "@/services/api";
import { useResumes } from "@/contexts/ResumeContext";

// Job Card Skeleton
const JobCardSkeleton = () => (
  <Card className="overflow-hidden">
    <CardHeader className="pb-3">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-2">
          <Skeleton className="h-6 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </div>
        <Skeleton className="h-8 w-8 rounded-full flex-shrink-0" />
      </div>
    </CardHeader>
    <CardContent className="space-y-4">
      <Skeleton className="h-4 w-full" />
      <div className="flex flex-wrap gap-2">
        <Skeleton className="h-6 w-20 rounded-full" />
        <Skeleton className="h-6 w-24 rounded-full" />
        <Skeleton className="h-6 w-16 rounded-full" />
      </div>
      <div className="flex gap-3 pt-2">
        <Skeleton className="h-9 w-24" />
        <Skeleton className="h-9 w-24" />
      </div>
    </CardContent>
  </Card>
);

const JobCard = ({ job }: { job: JobData }) => (
  <Card className="overflow-hidden hover:shadow-medium hover:-translate-y-1 transition-all duration-300 group border-border hover:border-primary/30 hover:shadow-[0_8px_30px_rgba(141,73,3,0.12)]">
    <CardHeader className="pb-3">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors truncate">
            {job.title}
          </h3>
          <div className="flex items-center gap-2 mt-1 text-muted-foreground">
            <Building2 className="h-4 w-4 flex-shrink-0" />
            <span className="text-sm truncate">{job.company}</span>
          </div>
        </div>
        <div className="flex-shrink-0">
          <img src={icon104} alt="104人力銀行" className="h-8 w-8 rounded-full shadow-sm" />
        </div>
      </div>
    </CardHeader>
    <CardContent className="space-y-4">
      <p className="text-muted-foreground text-sm line-clamp-2">{job.description}</p>
      <div className="flex flex-wrap gap-2">
        <Badge variant="secondary" className="flex items-center gap-1">
          <MapPin className="h-3 w-3" />
          {job.city}
        </Badge>
        <Badge variant="secondary" className="flex items-center gap-1">
          <Banknote className="h-3 w-3" />
          {job.salary}
        </Badge>
        <Badge variant="outline" className="flex items-center gap-1">
          <Briefcase className="h-3 w-3" />
          {job.industry}
        </Badge>
      </div>
      <div className="flex gap-3 pt-2">
        <Link to={`/jobs/${job.id}`}>
          <Button size="sm" className="gap-1">
            查看詳細
          </Button>
        </Link>
        <a href={job.externalUrl} target="_blank" rel="noopener noreferrer">
          <Button size="sm" variant="outline" className="gap-1">
            立即投遞
            <ExternalLink className="h-3 w-3" />
          </Button>
        </a>
      </div>
    </CardContent>
  </Card>
);


type Stage = "survey" | "loading" | "results";

const Recommendations = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { isJobPreferenceQuizDone, setIsJobPreferenceQuizDone } = useAppState();
  const { selectedResumeId } = useResumes();


  const [stage, setStage] = useState<Stage>(isJobPreferenceQuizDone ? "results" : "survey");
  const [showRefillAlert, setShowRefillAlert] = useState(false);

  // 1. 基礎分頁狀態
  const urlPage = parseInt(searchParams.get("page") || "1", 10);
  const initialPage = isNaN(urlPage) || urlPage < 1 ? 1 : urlPage;
  const [currentPage, setCurrentPage] = useState(initialPage);
  const itemsPerPage = 5;

  // 2. 從 LocalStorage 拿出使用者的搜尋條件
  const savedData = localStorage.getItem('userJobSurvey');
  const surveyPayload = savedData ? JSON.parse(savedData) : null;

  // 🌟 3. React Query 魔法陣！
  const { data: allJobs = [], isLoading: isJobsLoading } = useQuery({
    queryKey: ['jobRecommendations', surveyPayload],
    queryFn: async () => {
      console.log("🚀 真的打 API 囉！(如果有快取，你就不會看到這行)");
      const response = await getJobRecommendationsAPI(surveyPayload);
      const backendJobs = response.recommendations || [];
      return backendJobs.map((bJob: any) => ({
        id: bJob.id,
        title: bJob.title,
        company: bJob.company || "精選企業",
        description: bJob.description,
        city: bJob.location,
        salary: bJob.salary_range,
        industry: "資訊軟體業",
        externalUrl: `https://www.104.com.tw/jobs/search/?keyword=${encodeURIComponent(bJob.title)}`
      }));
    },
    enabled: stage === "results" && !!surveyPayload,
    staleTime: 1000 * 60 * 30, // 30 分鐘保鮮期
  });

  // 4. 數學魔法 (必須放在 allJobs 宣告之後！)
  const calculatedTotalPages = Math.max(1, Math.ceil(allJobs.length / itemsPerPage));
  const displayJobs = allJobs.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // 5. UI 連動 useEffect
  useEffect(() => {
    if (isJobPreferenceQuizDone && stage === "survey") {
      setStage("results");
    }
  }, [isJobPreferenceQuizDone, stage]);

  useEffect(() => {
    const urlPageParam = parseInt(searchParams.get("page") || "1", 10);
    const validPage = isNaN(urlPageParam) || urlPageParam < 1 ? 1 : Math.min(urlPageParam, calculatedTotalPages);
    if (validPage !== currentPage && allJobs.length > 0) {
      setCurrentPage(validPage);
    }
  }, [searchParams, calculatedTotalPages, allJobs.length, currentPage]);

  const handlePageChange = (page: number) => {
    if (page < 1 || page > calculatedTotalPages) return;
    setCurrentPage(page);
    setSearchParams({ page: page.toString() });
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleSurveyComplete = (surveyData: any) => {
    const finalPayload = {
      resumeId: selectedResumeId,
      city: surveyData.city || surveyData.location || "不限地區",
      workMode: surveyData.workMode || "不限",
      minSalary: surveyData.minSalary || 30000,
      maxSalary: surveyData.maxSalary || 200000,
    };

    localStorage.setItem('userJobSurvey', JSON.stringify(finalPayload));
    setStage("loading");
    window.scrollTo({ top: 0, behavior: "smooth" });

    setTimeout(() => {
      setIsJobPreferenceQuizDone(true);
      setStage("results");
      setCurrentPage(1);
      setSearchParams({ page: "1" });
      window.scrollTo({ top: 0, behavior: "smooth" });
    }, 1800);
  };

  const handleRefillConfirm = () => {
    setShowRefillAlert(false);
    setIsJobPreferenceQuizDone(false);
    setStage("survey");
    // 移除了舊的 setAllJobs([]) 避免報錯
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    if (calculatedTotalPages <= 7) {
      for (let i = 1; i <= calculatedTotalPages; i++) pages.push(i);
    } else {
      if (currentPage <= 3) {
        pages.push(1, 2, 3, 4, "...", calculatedTotalPages);
      } else if (currentPage >= calculatedTotalPages - 2) {
        pages.push(1, "...", calculatedTotalPages - 3, calculatedTotalPages - 2, calculatedTotalPages - 1, calculatedTotalPages);
      } else {
        pages.push(1, "...", currentPage - 1, currentPage, currentPage + 1, "...", calculatedTotalPages);
      }
    }
    return pages;
  };

  return (
    <div className="min-h-screen ">
      <div className="container py-8 md:py-12">
        <AnimatePresence mode="wait">
          {/* ─── Stage 1: Survey ─── */}
          {stage === "survey" && (
            <motion.div
              key="survey"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="text-center mb-12">
                <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-6">
                  <Heart className="h-8 w-8 text-primary" />
                </div>
                <h1 className="text-3xl font-bold mb-4">設定您的工作偏好</h1>
                <p className="text-muted-foreground max-w-2xl mx-auto">
                  告訴我們您的工作偏好，我們將為您精準匹配最適合的職缺
                </p>
              </div>
              <div className="max-w-2xl mx-auto space-y-4 md:space-y-6">
                <ResumeSelector />
                <EmbeddedPreferenceSurvey onComplete={handleSurveyComplete} />
              </div>
            </motion.div>
          )}

          {/* ─── Stage 2: Loading ─── */}
          {stage === "loading" && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="flex items-center justify-center min-h-[60vh]"
            >
              <AILoadingSpinner message="正在根據您的偏好為您尋找合適職缺..." />
            </motion.div>
          )}

          {/* ─── Stage 3: Results ─── */}
          {stage === "results" && (
            <motion.div
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              {/* Header */}
              <div className="text-center mb-12">
                <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-6">
                  <Star className="h-8 w-8 text-primary" />
                </div>
                <h1 className="text-3xl font-bold mb-4">推薦職缺</h1>
                <p className="text-muted-foreground max-w-2xl mx-auto">
                  我們根據您的履歷、個性特質與工作偏好，精心挑選最適合您的職位機會
                </p>
              </div>

              <div className="max-w-4xl mx-auto mb-6">
                <Button variant="outline" size="sm" className="gap-2" onClick={() => setShowRefillAlert(true)}>
                  <RefreshCw className="h-4 w-4" />
                  重新填寫工作偏好
                </Button>
              </div>

              <div className="max-w-4xl mx-auto">
                <AnimatePresence mode="wait">
                  {isJobsLoading ? (
                    <motion.div
                      key="skeleton"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="grid gap-4"
                    >
                      {[...Array(5)].map((_, i) => (
                        <JobCardSkeleton key={i} />
                      ))}
                    </motion.div>
                  ) : allJobs.length === 0 ? (
                    null
                  ) : (
                    <motion.div
                      key="content"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="grid gap-4"
                    >
                      {displayJobs.map((job, index) => (
                        <motion.div
                          key={job.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.05 }}
                        >
                          <JobCard job={job} />
                        </motion.div>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>

                {!isJobsLoading && allJobs.length > 0 && (
                  <motion.div
                    className="flex justify-center items-center gap-2 mt-10 pb-8"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                  >
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1}
                      className="gap-1"
                    >
                      <ChevronLeft className="h-4 w-4" />
                      上一頁
                    </Button>
                    <div className="flex gap-1">
                      {getPageNumbers().map((page, idx) =>
                        typeof page === "number" ? (
                          <Button
                            key={idx}
                            variant={currentPage === page ? "default" : "outline"}
                            size="sm"
                            onClick={() => handlePageChange(page)}
                            className="w-10"
                          >
                            {page}
                          </Button>
                        ) : (
                          <span key={idx} className="flex items-center justify-center w-10 text-muted-foreground">
                            {page}
                          </span>
                        ),
                      )}
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage === calculatedTotalPages}
                      className="gap-1"
                    >
                      下一頁
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </motion.div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <AlertModal
        open={showRefillAlert}
        onClose={() => setShowRefillAlert(false)}
        type="warning"
        title="確認重新填寫？"
        message="重新填寫將會更新您的推薦職缺清單，是否確認重新填寫？"
        confirmLabel="確認重新填寫"
        onConfirm={handleRefillConfirm}
        showCancel
      />
    </div>
  );
};

export default Recommendations;
import { useState, useEffect, useCallback, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  Radar,
  FileText,
  BookOpen,
  Lightbulb,
  Target,
  TrendingUp,
  Download,
  Star,
  ExternalLink,
  Info,
  ArrowLeft,
  ScanSearch,
  RefreshCw,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { ContentTransition } from "@/components/loading/LoadingStates";
import { motion, AnimatePresence } from "framer-motion";
import logoImage from "@/assets/logo.png";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Radar as RechartsRadar,
} from "recharts";
import { useResumes } from "@/contexts/ResumeContext";
import { getMyUserId } from "@/services/memberService";
import { generateAnalysis } from "@/services/analysisService";
import type { AnalysisResult } from "@/types/analysis";
// Fallback mock data for download report when no API result yet
import { radarTemplates as mockRadarTemplates, gapAnalysis as mockGapAnalysis, learningResources as mockLearningResources, sideProjects as mockSideProjects } from "@/mocks/analysis";

const ANALYSIS_DONE_KEY = "skills-analysis-done";

const loadingMessages = [
  "正在解析履歷關鍵字...",
  "正在匹配人格特質...",
  "正在比對目標職位需求...",
  "正在計算職能落差...",
  "正在生成個人化建議...",
];

type AnalysisPhase = "idle" | "loading" | "done";

// Skeleton components
const RadarChartSkeleton = () => (
  <div className="space-y-4">
    <Skeleton className="h-8 w-48" />
    <div className="flex items-center justify-center h-80">
      <div className="relative">
        <Skeleton className="h-64 w-64 rounded-full" />
        <Skeleton className="absolute inset-4 h-56 w-56 rounded-full" />
        <Skeleton className="absolute inset-8 h-48 w-48 rounded-full" />
      </div>
    </div>
    <Skeleton className="h-20 w-full rounded-lg" />
  </div>
);

const GapAnalysisSkeleton = () => (
  <div className="space-y-4">
    <Skeleton className="h-8 w-48" />
    <div className="grid grid-cols-2 gap-4">
      <Skeleton className="h-24 w-full rounded-lg" />
      <Skeleton className="h-24 w-full rounded-lg" />
    </div>
    <Skeleton className="h-32 w-full rounded-lg" />
    <div className="space-y-3">
      {[1, 2, 3, 4].map((i) => (
        <Skeleton key={i} className="h-16 w-full rounded-lg" />
      ))}
    </div>
  </div>
);

// ── Sub-view type ──
type SubView = "main" | "learning" | "sideproject";

const ANALYSIS_RESULT_KEY = "skills-analysis-result";

const Skills = () => {
  const navigate = useNavigate();
  const { resumes } = useResumes();

  // Determine initial phase from localStorage
  const [phase, setPhase] = useState<AnalysisPhase>(() =>
    localStorage.getItem(ANALYSIS_DONE_KEY) === "true" ? "done" : "idle"
  );
  const [selectedCareer, setSelectedCareer] = useState<string>("frontend");
  const [subView, setSubView] = useState<SubView>("main");
  const [subViewLoading, setSubViewLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState(loadingMessages[0]);

  // Analysis result state – load persisted result or fall back to mocks
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult>(() => {
    try {
      const saved = localStorage.getItem(ANALYSIS_RESULT_KEY);
      if (saved) return JSON.parse(saved);
    } catch {}
    return {
      radarTemplates: mockRadarTemplates,
      gapAnalysis: mockGapAnalysis,
      learningResources: mockLearningResources,
      sideProjects: mockSideProjects,
    };
  });

  // Derived data from analysis result
  const radarTemplates = analysisResult.radarTemplates;
  const gapAnalysis = analysisResult.gapAnalysis;
  const learningResources = analysisResult.learningResources;
  const sideProjects = analysisResult.sideProjects;
  const careerTypeKeys = Object.keys(radarTemplates);

  // Get latest resume_id (most recent updatedAt)
  const latestResumeId = useMemo(() => {
    if (resumes.length === 0) return null;
    const sorted = [...resumes].sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
    return sorted[0].id;
  }, [resumes]);

  // Branded loading sequence + API call
  const startAnalysis = useCallback(async () => {
    setPhase("loading");

    // Fetch user_id and prepare payload
    const userId = await getMyUserId();
    const resumeId = latestResumeId;

    // Start loading messages animation concurrently with API call
    const animationPromise = (async () => {
      for (let i = 0; i < loadingMessages.length; i++) {
        setLoadingMsg(loadingMessages[i]);
        await new Promise((r) => setTimeout(r, 1200));
      }
    })();

    // API call runs in parallel with animation
    const apiPromise = generateAnalysis({
      user_id: userId,
      resume_id: resumeId ?? 0,
    });

    // Wait for both animation and API to complete
    const [, result] = await Promise.all([animationPromise, apiPromise]);

    // Persist result and update state
    setAnalysisResult(result);
    localStorage.setItem(ANALYSIS_RESULT_KEY, JSON.stringify(result));
    localStorage.setItem(ANALYSIS_DONE_KEY, "true");
    setPhase("done");
  }, [latestResumeId]);

  // Re-analyse
  const handleReAnalyse = useCallback(() => {
    localStorage.removeItem(ANALYSIS_DONE_KEY);
    localStorage.removeItem(ANALYSIS_RESULT_KEY);
    startAnalysis();
  }, [startAnalysis]);

  const currentTemplate = radarTemplates[selectedCareer];

  // Navigate to sub-view with loading
  const openSubView = async (view: SubView) => {
    setSubViewLoading(true);
    setSubView(view);
    await new Promise((resolve) => setTimeout(resolve, 1200));
    setSubViewLoading(false);
  };

  // Download report
  const handleDownloadReport = () => {
    const reportContent = `
職能分析報告
================

一、整體評估
${gapAnalysis.summary}

二、職能雷達圖數據 (${currentTemplate.label})
${currentTemplate.data.map((d) => `- ${d.dimension}: 當前 ${d.user}% / 目標 ${d.target}%`).join("\n")}

三、職能差距分析
- 自評職級: ${gapAnalysis.selfAssessment}
- 評估職級: ${gapAnalysis.aiAssessment}
- 匹配度: ${gapAnalysis.matchPercentage}%
- 目標職位: ${gapAnalysis.targetPosition}

認知偏差說明:
${gapAnalysis.cognitiveBias}

評估說明:
${gapAnalysis.assessmentExplanation}

優先改善項目:
${gapAnalysis.gaps.map((g) => `- ${g.skill}: 當前 ${g.current}% → 目標 ${g.target}% (優先級: ${g.priority})`).join("\n")}

四、推薦學習資源
${learningResources.map((r) => `- ${r.title}: ${r.description}`).join("\n")}

五、推薦 Side Project
${sideProjects.map((p) => `- ${p.name} (技術: ${p.technologies.join(", ")})`).join("\n")}
    `.trim();

    const blob = new Blob([reportContent], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "職能分析報告.txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  // Render difficulty stars
  const renderDifficulty = (level: number) => (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((i) => (
        <Star key={i} className={`h-4 w-4 ${i <= level ? "text-primary fill-primary" : "text-muted-foreground/30"}`} />
      ))}
    </div>
  );

  // ── Learning Resources Sub-view ──
  if (subView === "learning") {
    return (
      <>
        <div className="min-h-screen bg-card">
          <div className="container py-8">
            {/* Top bar */}
            <div className="flex items-center justify-between mb-8">
              <Button
                variant="ghost"
                className="gap-2 text-[#502D03] hover:text-foreground"
                onClick={() => setSubView("main")}
              >
                <ArrowLeft className="h-4 w-4" />
                返回職能圖譜
              </Button>
              <Button variant="ghost" size="icon" onClick={handleDownloadReport}>
                <Download className="h-5 w-5 text-[#502D03]" />
              </Button>
            </div>

            {subViewLoading ? (
              <div className="flex flex-col items-center justify-center py-12">
                <img src={logoImage} alt="載入中" className="h-16 w-16 object-contain animate-pulse" />
                <p className="mt-4 text-[#8d4903] animate-pulse">正在載入學習資源...</p>
              </div>
            ) : (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                <h1 className="text-2xl font-bold text-foreground">學習資源推薦</h1>
                <p className="text-muted-foreground">
                  根據您的職能差距分析，我們為您精選以下學習資源。建議優先完成「高優先」技能的相關課程， 每週投入 5-10
                  小時，預計 3-6 個月內可達成目標職位的技能要求。
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {learningResources.map((resource, index) => (
                    <motion.div
                      key={resource.title}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <Card className="h-full bg-white transition-all duration-300 hover:shadow-medium hover:-translate-y-1 group cursor-pointer">
                        <CardContent className="pt-6 h-full flex flex-col">
                          <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">
                            {resource.title}
                          </h3>
                          <p className="text-sm text-muted-foreground mb-4 flex-grow">{resource.description}</p>
                          <div className="flex items-center justify-between">
                            <div className="flex flex-wrap gap-1">
                              {resource.tags.map((tag) => (
                                <Badge key={tag} variant="secondary" className="text-xs">
                                  {tag}
                                </Badge>
                              ))}
                            </div>
                            <ExternalLink className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </>
    );
  }

  // ── Side Project Sub-view ──
  if (subView === "sideproject") {
    return (
      <>
        
        <div className="min-h-screen bg-card">
          <div className="container py-8">
            {/* Top bar */}
            <div className="flex items-center justify-between mb-8">
              <Button
                variant="ghost"
                className="gap-2 text-[#502D03] hover:text-foreground"
                onClick={() => setSubView("main")}
              >
                <ArrowLeft className="h-4 w-4" />
                返回職能圖譜
              </Button>
              <Button variant="ghost" size="icon" onClick={handleDownloadReport}>
                <Download className="h-5 w-5 text-[#502D03]" />
              </Button>
            </div>

            {subViewLoading ? (
              <div className="flex flex-col items-center justify-center py-12">
                <img src={logoImage} alt="載入中" className="h-16 w-16 object-contain animate-pulse" />
                <p className="mt-4 text-[#8d4903] animate-pulse">正在載入 Side Project 推薦...</p>
              </div>
            ) : (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                <h1 className="text-2xl font-bold text-foreground">Side Project 推薦</h1>
                <p className="text-muted-foreground">
                  實作 Side Project 是提升技術深度最有效的方式。以下專案根據您的職能落差量身推薦，
                  建議從低難度開始逐步挑戰。
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {sideProjects.map((project, index) => (
                    <motion.div
                      key={project.name}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <Card className="h-full bg-white transition-all duration-300 hover:shadow-medium hover:-translate-y-1">
                        <CardContent className="pt-6 h-full flex flex-col">
                          <h3 className="font-semibold text-lg mb-3">{project.name}</h3>
                          <div className="flex flex-wrap gap-1 mb-4">
                            {project.technologies.map((tech) => (
                              <Badge key={tech} variant="outline" className="text-xs">
                                {tech}
                              </Badge>
                            ))}
                          </div>
                          <p className="text-sm text-muted-foreground mb-4 flex-grow">{project.highlights}</p>
                          <div className="flex items-center justify-between pt-3 border-t">
                            <span className="text-sm text-muted-foreground">實作難度</span>
                            {renderDifficulty(project.difficulty)}
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </>
    );
  }

  // ── Pre-Analysis (idle) State ──
  if (phase === "idle") {
    return (
      <div className="min-h-screen">
        <div className="container py-8">
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-6">
              <Radar className="h-8 w-8 text-primary" />
            </div>
            <h1 className="text-3xl font-bold mb-4">職能圖譜</h1>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              深入分析您的技能優勢與發展潛力
            </p>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="flex flex-col items-center justify-center py-16"
          >
            <Card className="max-w-lg w-full shadow-warm">
              <CardContent className="pt-8 pb-8 flex flex-col items-center text-center space-y-6">
                <div className="h-20 w-20 rounded-full bg-[#fbf1e8] flex items-center justify-center">
                  <ScanSearch className="h-10 w-10 text-[#8d4903]" />
                </div>
                <div className="space-y-2">
                  <h2 className="text-xl font-bold">準備分析</h2>
                  <p className="text-muted-foreground text-sm leading-relaxed max-w-sm">
                    系統將根據您的履歷、職涯問卷與人格特質進行綜合分析。
                  </p>
                </div>
                <button
                  onClick={startAnalysis}
                  className="px-8 py-4 rounded-xl font-semibold text-white gradient-primary shadow-medium
                    transition-all duration-300 hover:-translate-y-1 hover:shadow-large
                    hover:brightness-110 flex items-center justify-center gap-3"
                >
                  <Radar className="h-5 w-5" />
                  開始職能深度分析
                </button>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    );
  }

  // ── Loading State ──
  if (phase === "loading") {
    return (
      <div className="min-h-screen">
        <div className="container py-8">
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-6">
              <Radar className="h-8 w-8 text-primary" />
            </div>
            <h1 className="text-3xl font-bold mb-4">職能圖譜</h1>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              深入分析您的技能優勢與發展潛力
            </p>
          </div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center py-20 space-y-8"
          >
            <motion.img
              src={logoImage}
              alt="分析中"
              className="h-24 w-24 object-contain"
              animate={{ scale: [1, 1.08, 1] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            />
            <AnimatePresence mode="wait">
              <motion.p
                key={loadingMsg}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
                className="text-lg font-medium text-[#8d4903]"
              >
                {loadingMsg}
              </motion.p>
            </AnimatePresence>
            <div className="w-64 h-2 rounded-full bg-[#fbf1e8] overflow-hidden">
              <motion.div
                className="h-full rounded-full"
                style={{ background: "linear-gradient(90deg, #8d4903, #c4742b)" }}
                initial={{ width: "0%" }}
                animate={{ width: "100%" }}
                transition={{ duration: loadingMessages.length * 1.2, ease: "linear" }}
              />
            </div>
          </motion.div>
        </div>
      </div>
    );
  }

  // ── Main View (phase === "done") ──
  return (
    <>
      <div className="min-h-screen">
        {/* Header */}
        <div className="container py-8">
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-6">
              <Radar className="h-8 w-8 text-primary" />
            </div>
            <h1 className="text-3xl font-bold mb-4">職能圖譜</h1>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              深入分析您的技能優勢與發展潛力
            </p>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" className="gap-2" onClick={handleReAnalyse}>
              <RefreshCw className="h-4 w-4" />
              重新分析
            </Button>
            <Button className="gradient-primary gap-2 hidden sm:flex" onClick={handleDownloadReport}>
              <FileText className="h-4 w-4" />
              下載分析報告
            </Button>
          </div>
        </div>

        {/* Full-width main content */}
        <div className="container py-8 space-y-16">
          {/* Section 1: Radar Chart */}
          <section id="radar" className="scroll-mt-32">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg flex items-center justify-center bg-background">
                    <Radar className="h-5 w-5 text-primary" />
                  </div>
                  <h2 className="text-xl font-bold">職能雷達圖</h2>
                </div>

                {/* Career type selector */}
                <div className="flex flex-wrap gap-2">
                  {careerTypeKeys.map((key) => (
                    <Button
                      key={key}
                      variant={selectedCareer === key ? "default" : "outline"}
                      size="sm"
                      onClick={() => setSelectedCareer(key)}
                      className={selectedCareer === key ? "gradient-primary" : ""}
                    >
                      {radarTemplates[key].label}
                    </Button>
                  ))}
                </div>

                <Card className="transition-all duration-300 hover:shadow-medium">
                  <CardContent className="pt-6">
                    <div className="flex flex-row items-center gap-4 md:gap-8">
                      {/* Radar chart - always takes priority */}
                      <div className="h-64 sm:h-80 flex-1 min-w-0">
                        <ResponsiveContainer width="100%" height="100%">
                          <RadarChart data={currentTemplate.data}>
                            <PolarGrid stroke="#dabea8" />
                            <PolarAngleAxis
                              dataKey="dimension"
                              tick={{ fill: "hsl(var(--foreground))", fontSize: 12 }}
                            />

                            <PolarRadiusAxis
                              angle={30}
                              domain={[0, 100]}
                              tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
                            />

                            <RechartsRadar
                              name="目標職缺"
                              dataKey="target"
                              stroke="#dabea8"
                              fill="#dabea8"
                              fillOpacity={0.25}
                              strokeWidth={2}
                              strokeDasharray="5 5"
                            />

                            <RechartsRadar
                              name="您的職能"
                              dataKey="user"
                              stroke="#8d4903"
                              fill="#8d4903"
                              fillOpacity={0.45}
                              strokeWidth={3}
                            />

                            <Legend />
                          </RadarChart>
                        </ResponsiveContainer>
                      </div>

                      {/* Mascot - beside radar, shrinks on mobile */}
                      <div className="shrink-0 flex flex-col items-center gap-2 w-20 sm:w-32 md:w-48">
                        <img
                          src={currentTemplate.mascot}
                          alt={currentTemplate.label}
                          className="w-20 h-20 sm:w-32 sm:h-32 md:w-48 md:h-48 object-contain"
                        />

                        <span className="text-xs sm:text-sm font-semibold text-muted-foreground text-center">{currentTemplate.label}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Global Summary Callout */}
                <Card className="shadow-warm">
                  <CardContent className="pt-6">
                    <div className="p-5 rounded-xl bg-sidebar" style={{ backgroundColor: "#fbf1e8" }}>
                      <div className="flex items-start gap-3">
                        <div className="h-10 w-10 rounded-full flex items-center justify-center shrink-0 bg-primary">
                          <TrendingUp className="h-5 w-5 text-[#fbf2e9]" />
                        </div>
                        <div>
                          <p className="font-semibold text-foreground mb-1 bg-white/0">整體評估結果</p>
                          <p className="text-[#675143] leading-relaxed">{gapAnalysis.summary}</p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
           </section>

          {/* Section 2: Gap Analysis (落差分析報告) */}
          <section id="gap" className="scroll-mt-32">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15 }}
                className="space-y-6"
              >
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <Target className="h-5 w-5 text-primary" />
                  </div>
                  <h2 className="text-xl font-bold">職能差距分析</h2>
                </div>

                {/* Assessment Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card className="transition-all duration-300 hover:shadow-medium hover:-translate-y-1">
                    <CardContent className="pt-6">
                      <p className="text-sm text-muted-foreground mb-2">自評職級</p>
                      <p className="text-2xl font-bold text-foreground">{gapAnalysis.selfAssessment}</p>
                    </CardContent>
                  </Card>
                  <Card className="transition-all duration-300 hover:shadow-medium hover:-translate-y-1 border-primary/30 shadow-warm">
                    <CardContent className="pt-6">
                      <div className="p-4 rounded-lg" style={{ backgroundColor: "#fbf1e8" }}>
                        <p className="text-sm text-[#675143] mb-2">評估職級</p>
                        <p className="text-2xl font-bold text-primary">{gapAnalysis.aiAssessment}</p>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* 評估說明 */}
                <Card className="shadow-warm">
                  <CardContent className="pt-6">
                    <div className="p-5 rounded-xl" style={{ backgroundColor: "#FFFBF5" }}>
                      <div className="flex items-start gap-3">
                        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0 mt-0.5">
                          <Info className="h-4 w-4 text-primary" />
                        </div>
                        <div>
                          <p className="font-semibold text-foreground mb-2">評估說明</p>
                          <p className="text-sm text-[#675143] leading-relaxed">{gapAnalysis.assessmentExplanation}</p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Match Percentage & Target */}
                <Card className="transition-all duration-300 hover:shadow-medium">
                  <CardContent className="pt-6 space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">目標職位</p>
                        <p className="text-lg font-semibold">{gapAnalysis.targetPosition}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-muted-foreground">匹配度</p>
                        <p className="text-3xl font-bold text-primary">{gapAnalysis.matchPercentage}%</p>
                      </div>
                    </div>
                    <Progress value={gapAnalysis.matchPercentage} className="h-3" />

                    <div className="p-4 bg-muted/30 rounded-lg">
                      <p className="text-sm font-medium mb-1">認知偏差說明</p>
                      <p className="text-sm text-muted-foreground">{gapAnalysis.cognitiveBias}</p>
                    </div>
                  </CardContent>
                </Card>

                {/* Gap Details */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">落差分析報告</CardTitle>
                    <CardDescription>依優先級排序的技能提升項目</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {gapAnalysis.gaps.map((gap, index) => (
                      <motion.div
                        key={gap.skill}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="p-4 rounded-lg border bg-card hover:shadow-soft transition-all duration-300"
                      >
                        <div className="flex items-center justify-between mb-3">
                          <span className="font-medium">{gap.skill}</span>
                          <Badge variant={gap.priority === "高" ? "default" : "secondary"}>{gap.priority}優先</Badge>
                        </div>
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm text-muted-foreground">
                            <span>當前: {gap.current}%</span>
                            <span>目標: {gap.target}%</span>
                          </div>
                          <div className="relative h-2 bg-muted rounded-full overflow-hidden">
                            <div
                              className="absolute h-full bg-primary/30 rounded-full"
                              style={{ width: `${gap.target}%` }}
                            />

                            <div
                              className="absolute h-full bg-primary rounded-full"
                              style={{ width: `${gap.current}%` }}
                            />
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </CardContent>
                </Card>
              </motion.div>
          </section>

          {/* Section 3: 推薦行動計畫 (below 目標職位) */}
          <section id="action-plan" className="scroll-mt-32">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="space-y-6"
              >
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <BookOpen className="h-5 w-5 text-primary" />
                  </div>
                  <h2 className="text-xl font-bold">推薦行動計畫</h2>
                </div>

                <Card className="ui-white shadow-warm">
                  <CardContent className="pt-6">
                    <div className="p-5 rounded-xl" style={{ backgroundColor: "#fbf1e8" }}>
                      <p className="text-[#675143] leading-relaxed">
                        根據您的職能差距分析，我們為您精選以下學習資源。建議優先完成「高優先」技能的相關課程， 每週投入
                        5-10 小時，預計 3-6 個月內可達成目標職位的技能要求。
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
          </section>

          {/* Section 4: Bottom Action Buttons */}
            <section className="pb-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="flex flex-col sm:flex-row items-center justify-center gap-4"
              >
                <button
                  onClick={() => openSubView("learning")}
                  className="w-full sm:w-auto max-w-xs px-8 py-4 rounded-xl font-semibold text-white gradient-primary shadow-medium
                    transition-all duration-300 hover:-translate-y-1 hover:shadow-large
                    hover:brightness-110 flex items-center justify-center gap-3"
                >
                  <BookOpen className="h-5 w-5" />
                  學習資源推薦
                </button>
                <button
                  onClick={() => openSubView("sideproject")}
                  className="w-full sm:w-auto max-w-xs px-8 py-4 rounded-xl font-semibold text-white gradient-primary shadow-medium
                    transition-all duration-300 hover:-translate-y-1 hover:shadow-large
                    hover:brightness-110 flex items-center justify-center gap-3"
                >
                  <Lightbulb className="h-5 w-5" />
                  Side Project 推薦
                </button>
              </motion.div>
            </section>

          {/* Mobile Download Button */}
            <div className="sm:hidden pt-4">
              <Button className="w-full gradient-primary gap-2" onClick={handleDownloadReport}>
                <Download className="h-4 w-4" />
                下載分析報告
              </Button>
            </div>
        </div>
      </div>
    </>
  );
};

export default Skills;

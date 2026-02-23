import { useState, useEffect } from "react";
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
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { AILoadingSpinner, ContentTransition } from "@/components/loading/LoadingStates";
import { motion } from "framer-motion";
import { useAppState } from "@/contexts/AppContext";
import AuthModal from "@/components/auth/AuthModal";
import GatekeeperOverlay from "@/components/gatekeeper/GatekeeperOverlay";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Radar as RechartsRadar,
} from "recharts";
import { radarTemplates, gapAnalysis, learningResources, sideProjects } from "@/mocks/analysis";

// All mock data imported from src/mocks/analysis.ts

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

const careerTypeKeys = Object.keys(radarTemplates) as Array<keyof typeof radarTemplates>;

// ── Sub-view type ──
type SubView = "main" | "learning" | "sideproject";

const Skills = () => {
  const navigate = useNavigate();
  const { isLoggedIn, isResumeUploaded, isPersonalityQuizDone } = useAppState();

  const [isLoading, setIsLoading] = useState(true);
  const [selectedCareer, setSelectedCareer] = useState<string>("frontend");
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showGatekeeper, setShowGatekeeper] = useState(false);
  const [subView, setSubView] = useState<SubView>("main");
  const [subViewLoading, setSubViewLoading] = useState(false);

  // Access control check
  useEffect(() => {
    if (!isLoggedIn) {
      setShowAuthModal(true);
    } else if (!isResumeUploaded || !isPersonalityQuizDone) {
      setShowGatekeeper(true);
    } else {
      const loadData = async () => {
        setIsLoading(true);
        await new Promise((resolve) => setTimeout(resolve, 2000));
        setIsLoading(false);
      };
      loadData();
    }
  }, [isLoggedIn, isResumeUploaded, isPersonalityQuizDone]);

  const handleAuthModalClose = (open: boolean) => {
    setShowAuthModal(open);
    if (!open && !isLoggedIn) {
      navigate(-1);
    }
  };

  const handleGatekeeperClose = (open: boolean) => {
    setShowGatekeeper(open);
  };

  const handleGatekeeperLoginClick = () => {
    setShowGatekeeper(false);
    setShowAuthModal(true);
  };

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
        <AuthModal open={showAuthModal} onOpenChange={handleAuthModalClose} />
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
              <AILoadingSpinner message="正在載入學習資源..." />
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
        <AuthModal open={showAuthModal} onOpenChange={handleAuthModalClose} />
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
              <AILoadingSpinner message="正在載入 Side Project 推薦..." />
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

  // ── Main View ──
  return (
    <>
      <AuthModal open={showAuthModal} onOpenChange={handleAuthModalClose} />
      <GatekeeperOverlay
        open={showGatekeeper}
        onOpenChange={handleGatekeeperClose}
        onLoginClick={handleGatekeeperLoginClick}
      />

      <div className="min-h-screen">
        {/* Header */}
        <div className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-30">
          <div className="container py-6">
            <div className="flex flex-col items-center text-center gap-2">
              <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-6">
                <Radar className="h-8 w-8 text-primary" />
              </div>
              <h1 className="text-3xl font-bold mb-4">職能圖譜</h1>
              <p className="text-muted-foreground max-w-2xl mx-auto">深入分析您的技能優勢與發展潛力</p>
            </div>
            <div className="flex justify-end mt-4">
              {!isLoading && (
                <Button className="gradient-primary gap-2 hidden sm:flex" onClick={handleDownloadReport}>
                  <FileText className="h-4 w-4" />
                  下載分析報告
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Full-width main content */}
        <div className="container py-8 space-y-16">
          {/* Section 1: Radar Chart */}
          <section id="radar" className="scroll-mt-32">
            <ContentTransition isLoading={isLoading} skeleton={<RadarChartSkeleton />}>
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
                    <div className="flex flex-col md:flex-row items-center gap-8">
                      {/* Radar chart */}
                      <div className="h-80 w-full md:flex-1">
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

                      {/* Mascot - right side */}
                      <div className="shrink-0 flex flex-col items-center gap-3 md:w-48">
                        <img
                          src={currentTemplate.mascot}
                          alt={currentTemplate.label}
                          className="w-48 h-48 object-contain"
                        />

                        <span className="text-sm font-semibold text-muted-foreground">{currentTemplate.label}</span>
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
            </ContentTransition>
          </section>

          {/* Section 2: Gap Analysis (落差分析報告) */}
          <section id="gap" className="scroll-mt-32">
            <ContentTransition isLoading={isLoading} skeleton={<GapAnalysisSkeleton />}>
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
            </ContentTransition>
          </section>

          {/* Section 3: 推薦行動計畫 (below 目標職位) */}
          <section id="action-plan" className="scroll-mt-32">
            <ContentTransition
              isLoading={isLoading}
              skeleton={
                <div className="space-y-4">
                  <Skeleton className="h-8 w-48" />
                  <Skeleton className="h-24 w-full rounded-lg" />
                </div>
              }
            >
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
            </ContentTransition>
          </section>

          {/* Section 4: Bottom Action Buttons */}
          {!isLoading && (
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
          )}

          {/* Mobile Download Button */}
          {!isLoading && (
            <div className="sm:hidden pt-4">
              <Button className="w-full gradient-primary gap-2" onClick={handleDownloadReport}>
                <Download className="h-4 w-4" />
                下載分析報告
              </Button>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default Skills;

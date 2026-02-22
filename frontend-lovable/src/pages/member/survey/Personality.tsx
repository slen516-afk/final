import { useState, useEffect, useCallback } from 'react';
import { Brain, BarChart3, RefreshCw, ArrowLeft, ArrowRight, Zap, BookOpen } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useAppState } from '@/contexts/AppContext';
import { useNavigate } from 'react-router-dom';
import { AILoadingSpinner, ContentTransition } from '@/components/loading/LoadingStates';
import AlertModal from '@/components/modals/AlertModal';
import { motion } from 'framer-motion';
import LoginRequired from '@/components/gatekeeper/LoginRequired';
import { surveyModules, type SurveyModule } from '@/data/surveyQuestions';
import RadioQuestion from '@/components/survey/questions/RadioQuestion';
import CheckboxQuestion from '@/components/survey/questions/CheckboxQuestion';
import RankQuestion from '@/components/survey/questions/RankQuestion';
import TextQuestion from '@/components/survey/questions/TextQuestion';
import CategorizedSkillSelector from '@/components/survey/questions/CategorizedSkillSelector';

const STORAGE_KEY = 'career-survey-progress';

interface SurveyProgress {
  hasSkillBase: boolean | null;
  answers: Record<string, any>;
  currentStep: number;
}

const loadProgress = (): SurveyProgress => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) return JSON.parse(saved);
  } catch {}
  return { hasSkillBase: null, answers: {}, currentStep: 0 };
};

const saveProgress = (progress: SurveyProgress) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
};

const clearProgress = () => {
  localStorage.removeItem(STORAGE_KEY);
};

const RESULT_KEY = 'career-survey-done';

const Personality = () => {
  const { isPersonalityQuizDone, setIsPersonalityQuizDone } = useAppState();
  const navigate = useNavigate();

  const [progress, setProgress] = useState<SurveyProgress>(loadProgress);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showIncompleteAlert, setShowIncompleteAlert] = useState(false);
  // Restore result view if already completed
  const [showResult, setShowResult] = useState(() => {
    if (isPersonalityQuizDone) return true;
    try { return localStorage.getItem(RESULT_KEY) === 'true'; } catch { return false; }
  });
  const [invalidIds, setInvalidIds] = useState<Set<string>>(new Set());

  const { hasSkillBase, answers, currentStep } = progress;

  // Determine active modules
  const activeModules: SurveyModule[] = (() => {
    if (hasSkillBase) return surveyModules;
    // No skill base: skip module_A & module_B, prepend Q15 into module_C
    const moduleC = surveyModules.find((m) => m.id === 'module_C')!;
    const moduleB = surveyModules.find((m) => m.id === 'module_B')!;
    const q15 = moduleB.questions.find((q) => q.id === 'Q15')!;
    const moduleCWithQ15: SurveyModule = {
      ...moduleC,
      questions: [q15, ...moduleC.questions],
    };
    return [moduleCWithQ15, ...surveyModules.filter((m) => m.id === 'module_D')];
  })();

  const totalSteps = activeModules.length;
  const currentModule = activeModules[currentStep] as SurveyModule | undefined;

  // Persist on change
  useEffect(() => {
    saveProgress(progress);
  }, [progress]);

  const updateProgress = useCallback((partial: Partial<SurveyProgress>) => {
    setProgress((prev) => ({ ...prev, ...partial }));
  }, []);

  const setAnswer = useCallback((questionId: string, value: any) => {
    setProgress((prev) => ({
      ...prev,
      answers: { ...prev.answers, [questionId]: value },
    }));
    // Clear red border when user answers
    setInvalidIds((prev) => {
      if (!prev.has(questionId)) return prev;
      const next = new Set(prev);
      next.delete(questionId);
      return next;
    });
  }, []);

  // Check if a single question is invalid
  const isQuestionInvalid = (q: any): boolean => {
    if (!q.required) return false;
    const ans = answers[q.id];
    if (ans === undefined || ans === null || ans === '') return true;
    if (q.type === 'checkbox' && (!Array.isArray(ans) || ans.length === 0)) return true;
    if (q.type === 'rank' && (!Array.isArray(ans) || ans.length < (q as any).validation.max_selection)) return true;
    if (q.type === 'categorized_skill_selector' && (!Array.isArray(ans) || ans.length === 0)) return true;
    return false;
  };

  // Validate current module and return invalid IDs
  const validateCurrentModule = (): boolean => {
    if (!currentModule) return false;
    const newInvalid = new Set<string>();
    for (const q of currentModule.questions) {
      if (isQuestionInvalid(q)) newInvalid.add(q.id);
    }
    setInvalidIds(newInvalid);
    return newInvalid.size === 0;
  };

  const handleNext = () => {
    if (!validateCurrentModule()) {
      setShowIncompleteAlert(true);
      return;
    }
    if (currentStep < totalSteps - 1) {
      updateProgress({ currentStep: currentStep + 1 });
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      updateProgress({ currentStep: currentStep - 1 });
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleSubmit = async () => {
    if (!validateCurrentModule()) {
      setShowIncompleteAlert(true);
      return;
    }

    setIsAnalyzing(true);

    // Build final data: fill Q1-Q7 with 0 if skipped
    const finalAnswers = { ...answers };
    if (!hasSkillBase) {
      for (let i = 1; i <= 7; i++) {
        finalAnswers[`Q${i}`] = finalAnswers[`Q${i}`] ?? 0;
      }
      if (!finalAnswers['Q8']) finalAnswers['Q8'] = '';
    }

    // Simulate analysis
    await new Promise((resolve) => setTimeout(resolve, 1500));

    setIsAnalyzing(false);
    setShowResult(true);
    setIsPersonalityQuizDone(true);
    localStorage.setItem(RESULT_KEY, 'true');
  };

  const handleReset = () => {
    clearProgress();
    setProgress({ hasSkillBase: null, answers: {}, currentStep: 0 });
    setShowResult(false);
    setIsPersonalityQuizDone(false);
    localStorage.removeItem(RESULT_KEY);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Choose path
  const handleChoosePath = (withSkills: boolean) => {
    updateProgress({ hasSkillBase: withSkills, currentStep: 0, answers: {} });
  };

  const progressPercent = totalSteps > 0 ? ((currentStep + 1) / totalSteps) * 100 : 0;

  // Render question by type
  const renderQuestion = (q: any) => {
    switch (q.type) {
      case 'categorized_skill_selector':
        return (
          <CategorizedSkillSelector
            key={q.id}
            question={q}
            value={answers[q.id] || []}
            onChange={(val) => setAnswer(q.id, val)}
          />
        );
      case 'radio':
        return (
          <RadioQuestion
            key={q.id}
            question={q}
            value={answers[q.id]}
            onChange={(val) => setAnswer(q.id, val)}
          />
        );
      case 'checkbox':
        return (
          <CheckboxQuestion
            key={q.id}
            question={q}
            value={answers[q.id] || []}
            onChange={(val) => setAnswer(q.id, val)}
          />
        );
      case 'rank':
        return (
          <RankQuestion
            key={q.id}
            question={q}
            value={answers[q.id] || []}
            onChange={(val) => setAnswer(q.id, val)}
          />
        );
      case 'text':
        return (
          <TextQuestion
            key={q.id}
            question={q}
            value={answers[q.id] || ''}
            onChange={(val) => setAnswer(q.id, val)}
          />
        );
      default:
        return null;
    }
  };

  return (
    <LoginRequired>
      <div className="container py-8 md:py-12 animate-fade-in">
        {/* Header */}
        <div className="text-center mb-8 md:mb-10">
          <div className="inline-flex items-center justify-center h-14 w-14 md:h-16 md:w-16 rounded-full bg-primary/10 mb-4">
            <Brain className="h-7 w-7 md:h-8 md:w-8 text-primary" />
          </div>
          <h1 className="text-2xl md:text-3xl font-bold mb-2">職涯問卷</h1>
          <p className="text-muted-foreground text-sm md:text-base max-w-2xl mx-auto">
            全方位評估您的硬實力、軟實力、職涯定位與價值觀
          </p>
        </div>

        <div className="max-w-2xl mx-auto">
          <ContentTransition
            isLoading={isAnalyzing}
            skeleton={<AILoadingSpinner message="正在分析您的職涯傾向..." />}
          >
            {/* ─── Result View ─── */}
            {showResult ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-5"
              >
                <Card className="border-primary/20 bg-primary/5">
                  <CardContent className="p-6 md:p-8 text-center">
                    <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-4">
                      <BarChart3 className="h-8 w-8 text-primary" />
                    </div>
                    <h2 className="text-xl md:text-2xl font-bold mb-2">問卷已完成！</h2>
                    <p className="text-muted-foreground text-sm md:text-base">
                      您的職涯分析報告已生成，可前往職能圖譜查看完整結果
                    </p>
                  </CardContent>
                </Card>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <Button
                    onClick={() => navigate('/analysis/skills')}
                    className="gradient-primary h-12"
                  >
                    <BarChart3 className="h-4 w-4 mr-2" />
                    查看職能圖譜
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleReset}
                    className="h-12 border-primary/40 text-primary hover:bg-primary/5"
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    重新填寫職涯問卷
                  </Button>
                </div>
              </motion.div>
            ) : hasSkillBase === null ? (
              /* ─── Entry Card ─── */
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-4"
              >
                <Card>
                  <CardContent className="p-6 md:p-8">
                    <h2 className="text-lg md:text-xl font-bold mb-2 text-center">開始之前</h2>
                    <p className="text-muted-foreground text-sm text-center mb-6">
                      請選擇最符合您目前狀況的選項，我們將為您安排合適的問卷路徑
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <button
                        onClick={() => handleChoosePath(true)}
                        className="group p-5 rounded-xl border-2 border-border hover:border-primary/50 hover:bg-primary/5 hover:shadow-[0_0_12px_hsl(var(--primary)/0.12)] transition-all text-left"
                      >
                        <Zap className="h-6 w-6 text-primary mb-2" />
                        <p className="font-semibold text-sm md:text-base">我有相關技能基礎</p>
                      </button>
                      <button
                        onClick={() => handleChoosePath(false)}
                        className="group p-5 rounded-xl border-2 border-border hover:border-primary/50 hover:bg-primary/5 hover:shadow-[0_0_12px_hsl(var(--primary)/0.12)] transition-all text-left"
                      >
                        <BookOpen className="h-6 w-6 text-primary mb-2" />
                        <p className="font-semibold text-sm md:text-base">我目前沒有技能基礎</p>
                      </button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ) : (
              /* ─── Module Step ─── */
              <motion.div
                key={currentStep}
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
                className="space-y-5"
              >
                {/* Back to path selection */}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleReset}
                  className="gap-1.5 text-xs"
                  style={{ color: '#675143' }}
                >
                  <ArrowLeft className="h-3.5 w-3.5" />
                  返回選擇有無技能基礎
                </Button>

                {/* Progress bar */}
                <div>
                  <div className="flex items-center justify-between text-xs md:text-sm text-muted-foreground mb-2">
                    <span>Step {currentStep + 1} / {totalSteps}</span>
                    <span>{currentModule?.title.replace(/^模組\s*[A-Z][\s：:]*/, '')}</span>
                  </div>
                  <Progress value={progressPercent} className="h-2" />
                </div>

                {/* Module description */}
                <p className="text-xs text-muted-foreground">{currentModule?.description}</p>

                {/* Questions — one card per question */}
                <div className="space-y-4">
                  {currentModule?.questions.map((q) => (
                    <Card
                      key={q.id}
                      className={`transition-all ${
                        invalidIds.has(q.id)
                          ? 'border-destructive shadow-[0_0_8px_hsl(var(--destructive)/0.25)]'
                          : ''
                      }`}
                    >
                      <CardContent className="p-5 md:p-6">
                        {renderQuestion(q)}
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {/* Navigation */}
                <div className="flex justify-between gap-3">
                  <Button
                    variant="outline"
                    onClick={handlePrev}
                    disabled={currentStep === 0}
                    className="flex-1 sm:flex-none"
                  >
                    <ArrowLeft className="h-4 w-4 mr-1" />
                    上一步
                  </Button>
                  {currentStep === totalSteps - 1 ? (
                    <Button onClick={handleSubmit} className="gradient-primary flex-1 sm:flex-none">
                      提交問卷
                    </Button>
                  ) : (
                    <Button onClick={handleNext} className="gradient-primary flex-1 sm:flex-none">
                      下一步
                      <ArrowRight className="h-4 w-4 ml-1" />
                    </Button>
                  )}
                </div>
              </motion.div>
            )}
          </ContentTransition>
        </div>

        <AlertModal
          open={showIncompleteAlert}
          onClose={() => setShowIncompleteAlert(false)}
          type="warning"
          title="請完成所有必填題目"
          message="請先回答當前頁面的所有必填問題後再繼續"
          confirmLabel="了解"
        />
      </div>
    </LoginRequired>
  );
};

export default Personality;

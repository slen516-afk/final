import { useState, useEffect, useCallback } from 'react';
import { Sparkles, BarChart3, RefreshCw, ArrowLeft, ArrowRight } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { useAppState } from '@/contexts/AppContext';
import { useNavigate } from 'react-router-dom';
import { AILoadingSpinner, ContentTransition } from '@/components/loading/LoadingStates';
import AlertModal from '@/components/modals/AlertModal';
import { motion } from 'framer-motion';
import LoginRequired from '@/components/gatekeeper/LoginRequired';
import { personalityTestModules, type PTModule } from '@/data/personalityTestQuestions';
import { computePersonalityResult, type PersonalityResult } from '@/data/personalityScoring';
import { MOCK_RESULTS } from '@/data/mockPersonalityResults';
import PersonalityTestResult from '@/components/personality/PersonalityTestResult';

const STORAGE_KEY = 'personality-test-progress';
const RESULT_KEY = 'personality-test-result';

interface TestProgress {
  answers: Record<string, string>;
  currentStep: number;
}

const loadProgress = (): TestProgress => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) return JSON.parse(saved);
  } catch {}
  return { answers: {}, currentStep: 0 };
};

const saveProgress = (progress: TestProgress) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
};

const clearProgress = () => {
  localStorage.removeItem(STORAGE_KEY);
};

const PersonalityTest = () => {
  const { isPersonalityTestDone, setIsPersonalityTestDone } = useAppState();
  const navigate = useNavigate();

  const [progress, setProgress] = useState<TestProgress>(loadProgress);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showIncompleteAlert, setShowIncompleteAlert] = useState(false);
  const [invalidIds, setInvalidIds] = useState<Set<string>>(new Set());

  // Restore persisted result
  const [result, setResult] = useState<PersonalityResult | null>(() => {
    try {
      const saved = localStorage.getItem(RESULT_KEY);
      if (saved) return JSON.parse(saved);
    } catch {}
    return null;
  });
  const [showResult, setShowResult] = useState(() => {
    if (isPersonalityTestDone) return true;
    try { return localStorage.getItem(RESULT_KEY) !== null; } catch { return false; }
  });

  const { answers, currentStep } = progress;
  const modules = personalityTestModules;
  const totalSteps = modules.length;
  const currentModule = modules[currentStep] as PTModule | undefined;

  useEffect(() => {
    saveProgress(progress);
  }, [progress]);


  const updateProgress = useCallback((partial: Partial<TestProgress>) => {
    setProgress((prev) => ({ ...prev, ...partial }));
  }, []);

  const setAnswer = useCallback((questionId: string, value: string) => {
    setProgress((prev) => ({
      ...prev,
      answers: { ...prev.answers, [questionId]: value },
    }));
    setInvalidIds((prev) => {
      if (!prev.has(questionId)) return prev;
      const next = new Set(prev);
      next.delete(questionId);
      return next;
    });
  }, []);

  const validateCurrentModule = (): boolean => {
    if (!currentModule) return false;
    const newInvalid = new Set<string>();
    for (const q of currentModule.questions) {
      if (!answers[q.id]) newInvalid.add(q.id);
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
    await new Promise((resolve) => setTimeout(resolve, 1500));
    const computed = computePersonalityResult(answers);
    setResult(computed);
    localStorage.setItem(RESULT_KEY, JSON.stringify(computed));
    setIsAnalyzing(false);
    setShowResult(true);
    setIsPersonalityTestDone(true);
    clearProgress();
  };

  const handleReset = () => {
    clearProgress();
    localStorage.removeItem(RESULT_KEY);
    setProgress({ answers: {}, currentStep: 0 });
    setShowResult(false);
    setResult(null);
    setIsPersonalityTestDone(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const progressPercent = totalSteps > 0 ? ((currentStep + 1) / totalSteps) * 100 : 0;

  return (
    <LoginRequired>
      <div className="container py-8 md:py-12 animate-fade-in">
        {/* Header */}
        <div className="text-center mb-8 md:mb-10">
          <div className="inline-flex items-center justify-center h-14 w-14 md:h-16 md:w-16 rounded-full bg-primary/10 mb-4">
            <Sparkles className="h-7 w-7 md:h-8 md:w-8 text-primary" />
          </div>
          <h1 className="text-2xl md:text-3xl font-bold mb-2">人格特質問卷</h1>
          <p className="text-muted-foreground text-sm md:text-base max-w-2xl mx-auto">
            探索您的認知風格與決策偏好，幫助我們提供更精準的職涯建議
          </p>
          {/* Dev shortcut */}
          {!showResult && (
            <button
              onClick={() => {
                setResult(MOCK_RESULTS.STRUCTURE_ARCHITECT);
                setShowResult(true);
              }}
              className="mt-3 px-3 py-1 rounded border-2 border-dashed border-primary/30 text-xs text-primary hover:bg-primary/5 transition-colors"
            >
              🔧 DEV: 直接預覽結果頁
            </button>
          )}
        </div>

        <div className="max-w-2xl mx-auto">
          <ContentTransition
            isLoading={isAnalyzing}
            skeleton={<AILoadingSpinner message="正在分析您的人格特質..." />}
          >
            {/* Result View */}
            {showResult && result ? (
              <PersonalityTestResult result={result} onReset={handleReset} />
            ) : showResult ? (
              <PersonalityTestResult
                result={{ rawScores: { structure: 0, ambiguity: 0, decision: 0, learning: 0, transfer: 0 }, scaledScores: { structure: 0, ambiguity: 0, decision: 0, learning: 0, transfer: 0 }, archetypes: [{ id: 'GENERALIST', name: '綜合型' }] }}
                onReset={handleReset}
              />
            ) : (
              /* Module Step */
              <motion.div
                key={currentStep}
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
                className="space-y-5"
              >
                {/* Progress bar */}
                <div>
                  <div className="flex items-center justify-between text-xs md:text-sm text-muted-foreground mb-2">
                    <span>第 {currentStep + 1} / {totalSteps} 頁</span>
                    <span>{Math.round(progressPercent)}%</span>
                  </div>
                  <Progress value={progressPercent} className="h-2" />
                </div>

                {/* Questions */}
                <div className="space-y-5">
                  {currentModule?.questions.map((q, idx) => {
                    const globalIndex = currentStep * 2 + idx + 1;
                    return (
                      <Card
                        key={q.id}
                        className={`rounded-2xl border-0 bg-white shadow-[0_4px_20px_rgba(150,105,73,0.08)] transition-all ${
                          invalidIds.has(q.id)
                            ? 'ring-2 ring-destructive/50 shadow-[0_4px_20px_rgba(150,105,73,0.08),0_0_8px_hsl(var(--destructive)/0.25)]'
                            : ''
                        }`}
                      >
                        <CardContent className="p-6 md:p-8">
                          <div className="space-y-4">
                            <p className="font-semibold text-sm md:text-base text-foreground">
                              <span className="text-destructive mr-1">*</span>
                              {globalIndex}. {q.question}
                              <span className="text-xs text-muted-foreground ml-1.5 font-normal">(單選)</span>
                            </p>
                            <RadioGroup
                              value={answers[q.id] || ''}
                              onValueChange={(v) => setAnswer(q.id, v)}
                              className="space-y-2.5"
                            >
                              {q.options.map((opt) => (
                                <div
                                  key={opt.key}
                                  className={`flex items-start space-x-3 p-3.5 rounded-xl border transition-all cursor-pointer hover:bg-muted/40 ${
                                    answers[q.id] === opt.key
                                      ? 'border-primary/60 bg-primary/5 shadow-[0_0_8px_hsl(var(--primary)/0.15)]'
                                      : 'border-border/60'
                                  }`}
                                >
                                  <RadioGroupItem value={opt.key} id={`${q.id}-${opt.key}`} className="mt-0.5" />
                                  <Label htmlFor={`${q.id}-${opt.key}`} className="flex-1 cursor-pointer text-sm md:text-base leading-relaxed">
                                    {opt.key}. {opt.text}
                                  </Label>
                                </div>
                              ))}
                            </RadioGroup>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
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

export default PersonalityTest;

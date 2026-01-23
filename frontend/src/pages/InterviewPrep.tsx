import { useState } from "react";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MessageSquare, Users, Briefcase, RefreshCw, CheckCircle2, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Interview Prep Page
 * 
 * Supabase tables required:
 * 
 * Table: interview_questions
 * - id: UUID
 * - user_id: UUID (foreign key)
 * - resume_id: UUID (foreign key)
 * - jd_id: UUID (foreign key, nullable)
 * - question_type: TEXT ('hr' | 'manager')
 * - question_text: TEXT
 * - suggested_answer: TEXT (AI-generated)
 * - difficulty: TEXT ('easy' | 'medium' | 'hard')
 * - is_practiced: BOOLEAN
 * - created_at: TIMESTAMP
 * 
 * Table: interview_sessions
 * - id: UUID
 * - user_id: UUID
 * - session_type: TEXT ('practice' | 'mock')
 * - questions_completed: INTEGER
 * - score: FLOAT (if mock interview)
 * - feedback: JSONB
 * - created_at: TIMESTAMP
 */

interface Question {
  id: string;
  type: "hr" | "manager";
  question: string;
  difficulty: "easy" | "medium" | "hard";
  isPracticed: boolean;
}

const sampleQuestions: Question[] = [
  // HR Questions
  { id: "hr1", type: "hr", question: "請簡單介紹一下你自己", difficulty: "easy", isPracticed: false },
  { id: "hr2", type: "hr", question: "你為什麼想離開現在的公司？", difficulty: "medium", isPracticed: false },
  { id: "hr3", type: "hr", question: "你的職涯目標是什麼？五年後你希望達成什麼？", difficulty: "medium", isPracticed: false },
  { id: "hr4", type: "hr", question: "描述一次你與同事發生衝突的經驗，你如何處理？", difficulty: "hard", isPracticed: false },
  { id: "hr5", type: "hr", question: "你期望的薪資範圍是多少？", difficulty: "hard", isPracticed: false },
  // Manager Questions
  { id: "mgr1", type: "manager", question: "請說明你在 React 專案中如何處理狀態管理？", difficulty: "medium", isPracticed: false },
  { id: "mgr2", type: "manager", question: "你如何確保程式碼品質？有什麼具體的實踐？", difficulty: "medium", isPracticed: false },
  { id: "mgr3", type: "manager", question: "描述一個你解決過最困難的技術問題", difficulty: "hard", isPracticed: false },
  { id: "mgr4", type: "manager", question: "你如何在緊迫的 deadline 下做出技術決策？", difficulty: "hard", isPracticed: false },
  { id: "mgr5", type: "manager", question: "如果要你重構一個遺留系統，你會怎麼規劃？", difficulty: "hard", isPracticed: false },
];

const difficultyColors = {
  easy: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  medium: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  hard: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

const difficultyLabels = {
  easy: "簡單",
  medium: "中等",
  hard: "困難",
};

export default function InterviewPrep() {
  const [questions, setQuestions] = useState<Question[]>(sampleQuestions);
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);
  const [userAnswer, setUserAnswer] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);

  const hrQuestions = questions.filter((q) => q.type === "hr");
  const managerQuestions = questions.filter((q) => q.type === "manager");

  const handleRegenerate = () => {
    setIsGenerating(true);
    // Placeholder for AI regeneration
    setTimeout(() => {
      setIsGenerating(false);
    }, 1500);
  };

  const handleMarkPracticed = (id: string) => {
    setQuestions((prev) =>
      prev.map((q) => (q.id === id ? { ...q, isPracticed: true } : q))
    );
  };

  const practiceCount = questions.filter((q) => q.isPracticed).length;

  return (
    <DashboardLayout>
      <div className="h-screen flex flex-col">
        {/* Header */}
        <header className="px-6 py-4 border-b border-border bg-card/50 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-foreground">面試準備</h1>
            <p className="text-sm text-muted-foreground">
              根據履歷與職缺自動生成面試問題
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-sm text-muted-foreground">
              已練習：<span className="font-semibold text-primary">{practiceCount}</span> / {questions.length}
            </div>
            <Button onClick={handleRegenerate} disabled={isGenerating}>
              <RefreshCw className={cn("w-4 h-4 mr-2", isGenerating && "animate-spin")} />
              重新生成
            </Button>
          </div>
        </header>

        <div className="flex-1 flex overflow-hidden">
          {/* Questions List */}
          <div className="w-1/2 border-r border-border overflow-y-auto p-6 space-y-6">
            {/* HR Questions */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Users className="w-5 h-5 text-blue-500" />
                  HR 面試問題
                  <Badge variant="secondary" className="ml-auto">
                    5 題
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {hrQuestions.map((q, index) => (
                  <div
                    key={q.id}
                    onClick={() => setSelectedQuestion(q)}
                    className={cn(
                      "p-3 rounded-lg border cursor-pointer transition-all",
                      selectedQuestion?.id === q.id
                        ? "border-primary bg-primary/5"
                        : "border-border hover:border-primary/50 hover:bg-muted/50"
                    )}
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-sm font-medium text-muted-foreground shrink-0">
                        {index + 1}.
                      </span>
                      <div className="flex-1">
                        <p className="text-sm text-foreground">{q.question}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <span className={cn("px-2 py-0.5 text-xs rounded-full", difficultyColors[q.difficulty])}>
                            {difficultyLabels[q.difficulty]}
                          </span>
                          {q.isPracticed && (
                            <span className="flex items-center gap-1 text-xs text-green-600">
                              <CheckCircle2 className="w-3 h-3" />
                              已練習
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Manager Questions */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Briefcase className="w-5 h-5 text-purple-500" />
                  主管面試問題
                  <Badge variant="secondary" className="ml-auto">
                    5 題
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {managerQuestions.map((q, index) => (
                  <div
                    key={q.id}
                    onClick={() => setSelectedQuestion(q)}
                    className={cn(
                      "p-3 rounded-lg border cursor-pointer transition-all",
                      selectedQuestion?.id === q.id
                        ? "border-primary bg-primary/5"
                        : "border-border hover:border-primary/50 hover:bg-muted/50"
                    )}
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-sm font-medium text-muted-foreground shrink-0">
                        {index + 1}.
                      </span>
                      <div className="flex-1">
                        <p className="text-sm text-foreground">{q.question}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <span className={cn("px-2 py-0.5 text-xs rounded-full", difficultyColors[q.difficulty])}>
                            {difficultyLabels[q.difficulty]}
                          </span>
                          {q.isPracticed && (
                            <span className="flex items-center gap-1 text-xs text-green-600">
                              <CheckCircle2 className="w-3 h-3" />
                              已練習
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Practice Area */}
          <div className="w-1/2 flex flex-col">
            {selectedQuestion ? (
              <>
                <div className="p-6 border-b border-border bg-muted/30">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant={selectedQuestion.type === "hr" ? "default" : "secondary"}>
                      {selectedQuestion.type === "hr" ? "HR" : "主管"}
                    </Badge>
                    <span className={cn("px-2 py-0.5 text-xs rounded-full", difficultyColors[selectedQuestion.difficulty])}>
                      {difficultyLabels[selectedQuestion.difficulty]}
                    </span>
                  </div>
                  <h2 className="text-lg font-semibold text-foreground">
                    {selectedQuestion.question}
                  </h2>
                </div>

                <div className="flex-1 p-6 flex flex-col gap-4">
                  <div className="flex-1">
                    <label className="text-sm font-medium text-muted-foreground mb-2 block">
                      你的回答
                    </label>
                    <Textarea
                      value={userAnswer}
                      onChange={(e) => setUserAnswer(e.target.value)}
                      placeholder="在這裡練習你的回答..."
                      className="h-full min-h-[200px] resize-none"
                    />
                  </div>

                  <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles className="w-4 h-4 text-primary" />
                      <h3 className="font-medium text-foreground">AI 建議回答方向</h3>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {selectedQuestion.type === "hr"
                        ? "運用 STAR 法則（情境、任務、行動、結果）來組織你的回答，並結合具體的數據和成果來增強說服力。"
                        : "從技術深度和實際經驗出發，說明你的決策過程和考量因素。如果可能，請附上具體的技術細節和成效指標。"}
                    </p>
                  </div>

                  <div className="flex gap-3">
                    <Button
                      variant="outline"
                      className="flex-1"
                      onClick={() => {
                        setUserAnswer("");
                        setSelectedQuestion(null);
                      }}
                    >
                      返回列表
                    </Button>
                    <Button
                      className="flex-1"
                      onClick={() => handleMarkPracticed(selectedQuestion.id)}
                      disabled={selectedQuestion.isPracticed}
                    >
                      {selectedQuestion.isPracticed ? (
                        <>
                          <CheckCircle2 className="w-4 h-4 mr-2" />
                          已完成練習
                        </>
                      ) : (
                        <>
                          <CheckCircle2 className="w-4 h-4 mr-2" />
                          標記為已練習
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-muted-foreground">
                <div className="text-center">
                  <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>選擇一個問題開始練習</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

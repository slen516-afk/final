import { useState } from "react";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Mail, MessageCircle, Copy, RefreshCw, Sparkles, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";

/**
 * Thank-you Letter Generator
 * 
 * Supabase tables required:
 * 
 * Table: thank_you_letters
 * - id: UUID
 * - user_id: UUID (foreign key)
 * - interview_id: UUID (foreign key, optional)
 * - format_type: TEXT ('email' | 'chat')
 * - interviewer_name: TEXT
 * - company_name: TEXT
 * - position_title: TEXT
 * - interview_notes: TEXT
 * - generated_content: TEXT
 * - is_sent: BOOLEAN
 * - created_at: TIMESTAMP
 * 
 * Table: interview_notes
 * - id: UUID
 * - user_id: UUID (foreign key)
 * - company_name: TEXT
 * - interviewer_name: TEXT
 * - interview_date: DATE
 * - key_points: TEXT[]
 * - questions_asked: TEXT[]
 * - topics_discussed: TEXT[]
 * - follow_up_items: TEXT[]
 * - created_at: TIMESTAMP
 */

export default function ThankYouLetter() {
  const [interviewerName, setInterviewerName] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [positionTitle, setPositionTitle] = useState("");
  const [interviewNotes, setInterviewNotes] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedEmail, setGeneratedEmail] = useState("");
  const [generatedChat, setGeneratedChat] = useState("");
  const [copied, setCopied] = useState<"email" | "chat" | null>(null);

  const handleGenerate = () => {
    if (!interviewerName || !companyName || !positionTitle) {
      toast.error("請填寫面試官姓名、公司名稱和職位名稱");
      return;
    }

    setIsGenerating(true);

    // Placeholder AI generation
    setTimeout(() => {
      setGeneratedEmail(`親愛的 ${interviewerName}：

感謝您今天撥冗與我進行 ${positionTitle} 職位的面試。

非常榮幸有機會更深入了解 ${companyName} 的團隊文化和發展方向。${interviewNotes ? `特別是我們討論到的${interviewNotes.slice(0, 50)}...相關內容，讓我對這個職位有了更清晰的認識。` : ""}

通過今天的交流，我更加確信我的技能和經驗能夠為團隊帶來價值。我對這個機會充滿期待，希望有機會成為 ${companyName} 的一員。

如有任何需要補充的資訊，請隨時與我聯繫。再次感謝您的時間和考慮。

祝好，
[您的姓名]`);

      setGeneratedChat(`${interviewerName} 您好！

謝謝您今天的面試 🙏 和您聊 ${companyName} 的 ${positionTitle} 機會很開心！

${interviewNotes ? `特別是您分享的${interviewNotes.slice(0, 30)}相關經驗很有收穫 💡` : "今天的對話讓我對團隊有更多了解！"}

期待有機會加入團隊一起打拼 💪

有任何問題隨時找我～`);

      setIsGenerating(false);
    }, 1500);
  };

  const handleCopy = (type: "email" | "chat") => {
    const content = type === "email" ? generatedEmail : generatedChat;
    navigator.clipboard.writeText(content);
    setCopied(type);
    toast.success("已複製到剪貼簿");
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <DashboardLayout>
      <div className="h-screen flex flex-col">
        {/* Header */}
        <header className="px-6 py-4 border-b border-border bg-card/50">
          <h1 className="text-xl font-bold text-foreground">感謝信生成器</h1>
          <p className="text-sm text-muted-foreground">
            根據面試筆記自動生成專業的感謝信
          </p>
        </header>

        <div className="flex-1 flex overflow-hidden">
          {/* Input Form */}
          <div className="w-2/5 border-r border-border p-6 overflow-y-auto">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-primary" />
                  面試資訊
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="interviewer">面試官姓名</Label>
                  <Input
                    id="interviewer"
                    value={interviewerName}
                    onChange={(e) => setInterviewerName(e.target.value)}
                    placeholder="例如：王經理"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="company">公司名稱</Label>
                  <Input
                    id="company"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    placeholder="例如：ABC 科技"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="position">應徵職位</Label>
                  <Input
                    id="position"
                    value={positionTitle}
                    onChange={(e) => setPositionTitle(e.target.value)}
                    placeholder="例如：資深前端工程師"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="notes">面試筆記 (選填)</Label>
                  <Textarea
                    id="notes"
                    value={interviewNotes}
                    onChange={(e) => setInterviewNotes(e.target.value)}
                    placeholder="記錄面試中討論的重點、特別印象深刻的對話等..."
                    className="min-h-[150px]"
                  />
                </div>

                <Button
                  className="w-full"
                  onClick={handleGenerate}
                  disabled={isGenerating}
                >
                  {isGenerating ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      生成中...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      生成感謝信
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Output Area */}
          <div className="flex-1 p-6 overflow-y-auto">
            {generatedEmail || generatedChat ? (
              <Tabs defaultValue="email" className="h-full flex flex-col">
                <TabsList className="self-start mb-4">
                  <TabsTrigger value="email" className="flex items-center gap-2">
                    <Mail className="w-4 h-4" />
                    Email 格式
                  </TabsTrigger>
                  <TabsTrigger value="chat" className="flex items-center gap-2">
                    <MessageCircle className="w-4 h-4" />
                    即時通訊格式
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="email" className="flex-1 flex flex-col">
                  <Card className="flex-1 flex flex-col">
                    <CardHeader className="pb-3 flex-row items-center justify-between">
                      <CardTitle className="text-lg">Email 感謝信</CardTitle>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleCopy("email")}
                      >
                        {copied === "email" ? (
                          <>
                            <CheckCircle2 className="w-4 h-4 mr-2 text-green-500" />
                            已複製
                          </>
                        ) : (
                          <>
                            <Copy className="w-4 h-4 mr-2" />
                            複製
                          </>
                        )}
                      </Button>
                    </CardHeader>
                    <CardContent className="flex-1">
                      <div className="h-full p-4 rounded-lg bg-muted/50 border border-border">
                        <pre className="whitespace-pre-wrap text-sm text-foreground font-sans">
                          {generatedEmail}
                        </pre>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="chat" className="flex-1 flex flex-col">
                  <Card className="flex-1 flex flex-col">
                    <CardHeader className="pb-3 flex-row items-center justify-between">
                      <CardTitle className="text-lg">即時通訊版本</CardTitle>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleCopy("chat")}
                      >
                        {copied === "chat" ? (
                          <>
                            <CheckCircle2 className="w-4 h-4 mr-2 text-green-500" />
                            已複製
                          </>
                        ) : (
                          <>
                            <Copy className="w-4 h-4 mr-2" />
                            複製
                          </>
                        )}
                      </Button>
                    </CardHeader>
                    <CardContent className="flex-1">
                      <div className="h-full p-4 rounded-lg bg-muted/50 border border-border">
                        <pre className="whitespace-pre-wrap text-sm text-foreground font-sans">
                          {generatedChat}
                        </pre>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            ) : (
              <div className="h-full flex items-center justify-center text-muted-foreground">
                <div className="text-center">
                  <Mail className="w-16 h-16 mx-auto mb-4 opacity-30" />
                  <h3 className="text-lg font-medium mb-2">尚未生成感謝信</h3>
                  <p className="text-sm">填寫左側表單後點擊「生成感謝信」</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

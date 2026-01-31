import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Trophy, Send, X, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

/**
 * Achievement Logger - Floating Chat Widget
 * 
 * Supabase table: achievements
 * Required fields:
 * - id: UUID (primary key)
 * - user_id: UUID (foreign key to auth.users)
 * - content: TEXT (natural language description)
 * - parsed_skills: TEXT[] (AI-extracted skills)
 * - parsed_metrics: JSONB (quantified achievements)
 * - project_name: TEXT (optional project association)
 * - achievement_date: DATE
 * - created_at: TIMESTAMP
 */

interface Message {
  id: string;
  type: "user" | "assistant";
  content: string;
}

export function AchievementLogger() {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "assistant",
      content: "嗨！我是你的成就記錄助手 ✨ 隨時告訴我你完成了什麼專案或達成了什麼里程碑，我會幫你整理成專業的履歷素材！",
    },
  ]);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: input,
    };

    // Placeholder AI response
    const aiResponse: Message = {
      id: (Date.now() + 1).toString(),
      type: "assistant",
      content: `已記錄！我從你的描述中提取了以下重點：\n\n📌 專案：${input.slice(0, 20)}...\n💡 技能：待AI分析\n📊 量化指標：待AI分析\n\n這個成就已加入你的職涯資料庫！`,
    };

    setMessages((prev) => [...prev, userMessage, aiResponse]);
    setInput("");
  };

  return (
    <>
      {/* Floating Button */}
      <motion.button
        onClick={() => setIsOpen(true)}
        className={cn(
          "fixed bottom-6 right-24 z-40 w-14 h-14 rounded-full shadow-elevated",
          "bg-gradient-to-br from-amber-400 to-orange-500 text-white",
          "flex items-center justify-center hover:scale-110 transition-transform",
          isOpen && "hidden"
        )}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
      >
        <Trophy className="w-6 h-6" />
      </motion.button>

      {/* Chat Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-6 right-24 z-50 w-96 h-[500px] rounded-2xl shadow-elevated overflow-hidden flex flex-col bg-card border border-border"
          >
            {/* Header */}
            <div className="px-4 py-3 bg-gradient-to-r from-amber-400 to-orange-500 text-white flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Trophy className="w-5 h-5" />
                <span className="font-semibold">成就記錄器</span>
                <Sparkles className="w-4 h-4" />
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="text-white hover:bg-white/20 h-8 w-8"
                onClick={() => setIsOpen(false)}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    "max-w-[85%] rounded-2xl px-4 py-2.5 text-sm",
                    message.type === "user"
                      ? "ml-auto bg-primary text-primary-foreground"
                      : "bg-muted text-foreground"
                  )}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>
              ))}
            </div>

            {/* Input */}
            <div className="p-3 border-t border-border">
              <div className="flex gap-2">
                <Textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="描述你的成就，例如：完成了電商平台的搜尋功能優化，提升了30%的搜尋準確率..."
                  className="min-h-[60px] resize-none text-sm"
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                />
                <Button
                  onClick={handleSend}
                  size="icon"
                  className="shrink-0 self-end"
                  disabled={!input.trim()}
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

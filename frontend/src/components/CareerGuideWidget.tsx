import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence, useDragControls } from "framer-motion";
import { MessageCircle, X, Sparkles, ChevronRight, Lightbulb, Target, FileText, GraduationCap } from "lucide-react";
import { Button } from "@/components/ui/button";

interface GuideStep {
  id: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  action?: string;
}

const guideSteps: GuideStep[] = [
  {
    id: "welcome",
    icon: <Sparkles className="w-5 h-5" />,
    title: "歡迎來到 CareerPilot！",
    description: "我是你的專屬職涯領航員 ✨ 讓我帶你快速了解這個平台！",
    action: "開始導覽",
  },
  {
    id: "upload",
    icon: <FileText className="w-5 h-5" />,
    title: "AI履歷優化",
    description: "首先，你可以上傳你的PDF / DOC 格式履歷，讓 AI 幫你突顯特長！",
    action: "下一步",
  },
  {
    id: "match",
    icon: <Target className="w-5 h-5" />,
    title: "職缺匹配",
    description: "輸入目標職位的網址或描述，系統會精準分析你與職位的契合度。",
    action: "下一步",
  },
  {
    id: "grow",
    icon: <GraduationCap className="w-5 h-5" />,
    title: "持續成長",
    description: "註冊帳號可以解鎖更多功能：職涯地圖、面試輔助、感謝信生成、成就記錄等！",
    action: "結束導覽",
  },
];

export function CareerGuideWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const constraintsRef = useRef<HTMLDivElement>(null);
  const dragControls = useDragControls();

  useEffect(() => {
    // Show widget after a delay
    const timer = setTimeout(() => {
      setIsOpen(true);
    }, 2000);
    return () => clearTimeout(timer);
  }, []);

  const handleNext = () => {
    if (currentStep < guideSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      setIsOpen(false);
      setCurrentStep(0);
    }
  };

  const currentGuide = guideSteps[currentStep];

  return (
    <>
      {/* Drag constraints container */}
      <div ref={constraintsRef} className="fixed inset-0 pointer-events-none z-40" />

      {/* Widget */}
      <motion.div
        drag
        dragControls={dragControls}
        dragConstraints={constraintsRef}
        dragElastic={0.1}
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 1, type: "spring", stiffness: 200, damping: 20 }}
        className="fixed bottom-6 right-6 z-50 pointer-events-auto"
        style={{ touchAction: "none" }}
      >
        <AnimatePresence mode="wait">
          {isOpen ? (
            <motion.div
              key="panel"
              initial={{ opacity: 0, scale: 0.8, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8, y: 20 }}
              className="relative"
            >
              {/* RPG-style panel */}
              <div className="w-80 glass-strong rounded-2xl shadow-elevated overflow-hidden">
                {/* Header */}
                <div className="relative bg-gradient-cta p-4 cursor-grab active:cursor-grabbing">
                  <button
                    onClick={() => setIsOpen(false)}
                    className="absolute top-3 right-3 p-1 rounded-full bg-primary-foreground/20 hover:bg-primary-foreground/30 transition-colors"
                  >
                    <X className="w-4 h-4 text-primary-foreground" />
                  </button>
                  <div className="flex items-center gap-3">
                    {/* Character avatar */}
                    <div className="w-14 h-14 rounded-full bg-primary-foreground/20 flex items-center justify-center animate-bounce-gentle">
                      <div className="w-12 h-12 rounded-full bg-primary-foreground flex items-center justify-center">
                        <Lightbulb className="w-6 h-6 text-primary" />
                      </div>
                    </div>
                    <div>
                      <h3 className="font-bold text-primary-foreground">職星接待員</h3>
                      <p className="text-xs text-primary-foreground/80">Career Guide</p>
                    </div>
                  </div>
                </div>

                {/* Content */}
                <div className="p-5">
                  {/* Progress dots */}
                  <div className="flex justify-center gap-2 mb-4">
                    {guideSteps.map((_, index) => (
                      <div
                        key={index}
                        className={`w-2 h-2 rounded-full transition-colors ${
                          index === currentStep
                            ? "bg-primary"
                            : index < currentStep
                            ? "bg-mint-300"
                            : "bg-border"
                        }`}
                      />
                    ))}
                  </div>

                  {/* Step content */}
                  <motion.div
                    key={currentStep}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="text-center"
                  >
                    <div className="w-12 h-12 rounded-full bg-mint-100 flex items-center justify-center mx-auto mb-3 text-primary">
                      {currentGuide.icon}
                    </div>
                    <h4 className="font-semibold text-foreground mb-2">
                      {currentGuide.title}
                    </h4>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {currentGuide.description}
                    </p>
                  </motion.div>

                  {/* Action button */}
                  <Button
                    variant="hero"
                    size="sm"
                    onClick={handleNext}
                    className="w-full mt-5"
                  >
                    {currentGuide.action}
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>

                {/* RPG-style decorative border */}
                <div className="absolute inset-x-4 bottom-0 h-1 bg-gradient-to-r from-transparent via-primary/30 to-transparent" />
              </div>

              {/* Speech bubble tail */}
              <div className="absolute -bottom-2 right-8 w-4 h-4 bg-card rotate-45 border-r border-b border-border/50" />
            </motion.div>
          ) : (
            <motion.button
              key="button"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsOpen(true)}
              className="w-16 h-16 rounded-full bg-gradient-cta shadow-glow flex items-center justify-center group"
            >
              <div className="relative">
                <Lightbulb className="w-7 h-7 text-primary-foreground" />
                <span className="absolute -top-1 -right-1 w-3 h-3 bg-destructive rounded-full animate-pulse" />
              </div>
            </motion.button>
          )}
        </AnimatePresence>
      </motion.div>
    </>
  );
}
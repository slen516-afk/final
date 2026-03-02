import { useState, forwardRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { X, MessageCircle, Star, ChevronLeft, ChevronRight } from 'lucide-react';

const CareerGuide = forwardRef<HTMLDivElement>((_, ref) => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentSlide, setCurrentSlide] = useState(0);

  const slides = [
    {
      icon: '✨',
      title: '歡迎來到職星領航員！',
      description: '我是你的專屬職涯接待員 🚀 讓我帶你快速了解平台的使用流程吧！'
    },
    {
      icon: '📄',
      title: '步驟一：上傳履歷',
      description: '首先上傳你的履歷，系統會自動解析你的技能、經歷等關鍵資訊，作為後續分析的基礎。'
    },
    {
      icon: '🧠',
      title: '步驟二：人格特質問卷',
      description: '透過人格特質測驗，了解你的職場性格與工作偏好，幫助系統更精準地為你推薦方向。'
    },
    {
      icon: '🎯',
      title: '步驟三：職涯問卷',
      description: '填寫職涯偏好問卷，讓系統掌握你的求職意向、期望產業與地區等條件。'
    },
    {
      icon: '💎',
      title: '步驟四：履歷優化',
      description: '根據分析結果，系統會自動生成優化建議，幫你打造更具競爭力的履歷。'
    },
    {
      icon: '📊',
      title: '步驟五：職能圖譜',
      description: '查看你的技能雷達圖與職能落差分析，了解自身優勢與需要補強的方向。'
    },
    {
      icon: '💼',
      title: '步驟六：推薦職缺',
      description: '最後，系統會根據你的技能與偏好，推薦最適合的職缺，助你找到理想工作！'
    }
  ];


  const nextSlide = () => {
    if (currentSlide < slides.length - 1) {
      setCurrentSlide((prev) => prev + 1);
    }
  };

  const prevSlide = () => {
    if (currentSlide > 0) {
      setCurrentSlide((prev) => prev - 1);
    }
  };

  return (
    <>
      {/* FAB Button */}
      <motion.button
        className="fixed bottom-6 right-6 z-50 h-14 w-14 rounded-full gradient-primary shadow-large flex items-center justify-center text-primary-foreground hover:scale-110 transition-transform bg-[#896e5d]"
        onClick={() => setIsOpen(true)}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 260, damping: 20 }}>

        <MessageCircle className="h-6 w-6" />
      </motion.button>

      {/* Guide Window */}
      <AnimatePresence>
        {isOpen &&
          <motion.div
            className="fixed bottom-24 right-6 z-50 w-80 md:w-96"
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            transition={{ type: 'spring', stiffness: 300, damping: 25 }}>

            <div className="ui-white rounded-2xl border overflow-hidden">
              {/* Header */}
              <div className="bg-primary p-4 flex items-center justify-between text-primary-foreground">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-primary-foreground/20 flex items-center justify-center">
                    <Star className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold">職星接待員</h3>
                    <p className="text-xs opacity-80">Career Guide</p>
                  </div>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="h-8 w-8 rounded-full hover:bg-primary-foreground/20 flex items-center justify-center transition-colors">

                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* Pagination Dots */}
              <div className="flex justify-center gap-1.5 py-3 bg-muted/30">
                {slides.map((_, index) =>
                  <button
                    key={index}
                    onClick={() => setCurrentSlide(index)}
                    className={`h-2 rounded-full transition-all ${index === currentSlide ?
                        'w-6 bg-primary' :
                        'w-2 bg-muted-foreground/30 hover:bg-muted-foreground/50'}`
                    } />

                )}
              </div>

              {/* Content */}
              <div className="p-6">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={currentSlide}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                    className="text-center">

                    <div className="text-4xl mb-4">{slides[currentSlide].icon}</div>
                    <h4 className="text-lg font-semibold mb-2">
                      {slides[currentSlide].title}
                    </h4>
                    <p className="text-muted-foreground text-sm">
                      {slides[currentSlide].description}
                    </p>
                  </motion.div>
                </AnimatePresence>
              </div>

              {/* Actions */}
              <div className="p-4 border-t bg-muted/20">
                <div className="flex items-center justify-between gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={prevSlide}
                    disabled={currentSlide === 0}
                    className="gap-1">

                    <ChevronLeft className="h-4 w-4" />
                    上一步
                  </Button>

                  {currentSlide < slides.length - 1 ?
                    <Button
                      size="sm"
                      className="gradient-primary gap-1"
                      onClick={nextSlide}>

                      {currentSlide === 0 ? '開始導覽' : '下一步'}
                      <ChevronRight className="h-4 w-4" />
                    </Button> :

                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setIsOpen(false)}>

                      完成
                    </Button>
                  }
                </div>
              </div>
            </div>
          </motion.div>
        }
      </AnimatePresence>
    </>);

});

CareerGuide.displayName = 'CareerGuide';

export default CareerGuide;
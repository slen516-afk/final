import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { HelpCircle } from 'lucide-react';

const FAQ = () => {
  const faqs = [
    {
      question: '如何開始使用職涯智慧平台？',
      answer: '請先註冊帳號，完成個人資料填寫後，即可開始使用各項功能。',
    },
    {
      question: '履歷優化功能如何運作？',
      answer: '系統會深入分析您的履歷內容，提供專業建議與優化方向。',
    },
    {
      question: '如何取得職缺推薦？',
      answer: '完成技能評估與偏好問卷後，系統會根據您的條件推薦合適職缺。',
    },
    {
      question: '平台服務是否收費？',
      answer: '基本功能免費使用，進階功能請參考付費方案。',
    },
  ];

  return (
    <div className="container py-12 animate-fade-in">
      <div className="text-center mb-12">
        <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-6">
          <HelpCircle className="h-8 w-8 text-primary" />
        </div>
        <h1 className="text-3xl font-bold mb-4">常見問題</h1>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          找到您需要的答案
        </p>
      </div>
      
      <div className="max-w-2xl mx-auto">
        <Accordion type="single" collapsible className="w-full">
          {faqs.map((faq, index) => (
            <AccordionItem key={index} value={`item-${index}`}>
              <AccordionTrigger className="text-left">
                {faq.question}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {faq.answer}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </div>
  );
};

export default FAQ;

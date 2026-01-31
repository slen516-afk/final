import { motion } from "framer-motion";
import { 
  FileSearch, 
  Target, 
  Map, 
  MessageSquare, 
  Mail, 
  Trophy,
  ArrowRight
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

const services = [
  {
    icon: FileSearch,
    title: "AI履歷優化",
    description: " 經由 AI 深度分析您的履歷，提供專業建議協助您突顯強項",
    color: "bg-mint-100 text-primary",
  },
  {
    icon: Target,
    title: "職缺匹配",
    description: "智慧比對您的技能與職位需求，為您精準推薦最適合的工作機會",
    color: "bg-mint-100 text-primary",
  },
  {
    icon: Map,
    title: "職涯地圖",
    description: "基於大數據進行職涯路徑匹配，提供客觀市場分析與預期親資區間，探索嶄新可能性",
    color: "bg-mint-100 text-primary",
  },
  {
    icon: MessageSquare,
    title: "面試輔助",
    description: "彙整投遞回覆狀態及面試排程，提供即時面談策略諮詢，助您自信應對",
    color: "bg-mint-100 text-primary",
  },
  {
    icon: Mail,
    title: "感謝信生成",
    description: "AI將根據您的回覆內容自動生成個人化、有溫度的面試後感謝信，為您增添好印象",
    color: "bg-mint-100 text-primary",
  },
  {
    icon: Trophy,
    title: "成就記錄",
    description: "轉職前不必再埋頭苦思，日常動態追蹤記錄您的職涯成就與里程碑，為您打造專屬職涯檔案",
    color: "bg-mint-100 text-primary",
  },
];

export function ServicesSection() {
  return (
    <section className="py-24 bg-muted/30 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-mint-100/50 to-transparent pointer-events-none" />
      
      <div className="container mx-auto px-4 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            一站式智慧職涯導航平台
          </h2>
          <p className="text-muted-foreground max-w-xl mx-auto">
            利用AI與大數據，將傳統瑣碎的求職流程，整合為智慧化的舒適體驗。
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((service, index) => (
            <motion.div
              key={service.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="group"
            >
              <div className="h-full glass rounded-2xl p-6 shadow-soft hover:shadow-elevated transition-all duration-300 hover:-translate-y-1">
                <div className={`w-14 h-14 rounded-xl ${service.color} flex items-center justify-center mb-5 group-hover:scale-110 transition-transform`}>
                  <service.icon className="w-7 h-7" />
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-3">
                  {service.title}
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  {service.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-center mt-12"
        >
          <Button variant="hero" size="lg" asChild className="group">
            <Link to="/services">
              探索更多服務
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </Button>
        </motion.div>
      </div>
    </section>
  );
}
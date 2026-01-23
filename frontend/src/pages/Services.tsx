import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ServicesSection } from "@/components/ServicesSection";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

const Services = () => {
  return (
    <div className="min-h-screen">
      <Header />
      <main className="pt-20">
        {/* Hero */}
        <section className="py-24 bg-gradient-hero">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-center max-w-3xl mx-auto"
            >
              <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-6">
                服務項目
              </h1>
              <p className="text-lg text-muted-foreground leading-relaxed">
                從履歷優化到面試準備，我們提供全方位的 AI 職涯服務，
                助您在職場上脫穎而出
              </p>
            </motion.div>
          </div>
        </section>

        <ServicesSection />

        {/* CTA */}
        <section className="py-24">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="glass rounded-3xl p-12 text-center shadow-elevated max-w-3xl mx-auto"
            >
              <h2 className="text-3xl font-bold text-foreground mb-4">
                準備好開始了嗎？
              </h2>
              <p className="text-muted-foreground mb-8 max-w-lg mx-auto">
                立即註冊，解鎖所有 AI 職涯服務，讓我們一起打造您的理想職涯
              </p>
              <Button variant="hero" size="xl" asChild className="group">
                <Link to="/register">
                  免費開始使用
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
              </Button>
            </motion.div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
};

export default Services;
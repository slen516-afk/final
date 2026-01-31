import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { motion } from "framer-motion";
import { Users, Target, Award, Heart } from "lucide-react";

const values = [
  {
    icon: Target,
    title: "精準匹配",
    description: "運用先進 AI 技術，為每位求職者找到最適合的職位機會",
  },
  {
    icon: Users,
    title: "用戶至上",
    description: "以用戶需求為核心，持續優化產品體驗",
  },
  {
    icon: Award,
    title: "專業可靠",
    description: "結合人力資源專家與技術團隊，提供專業服務",
  },
  {
    icon: Heart,
    title: "真誠關懷",
    description: "關心每位用戶的職涯發展，陪伴成長每一步",
  },
];

const About = () => {
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
                關於 CareerAI
              </h1>
              <p className="text-lg text-muted-foreground leading-relaxed">
                我們相信每個人都值得擁有理想的職涯。透過 AI 技術的力量，
                我們致力於讓求職者與企業之間的連結更加精準、高效。
              </p>
            </motion.div>
          </div>
        </section>

        {/* Mission */}
        <section className="py-24">
          <div className="container mx-auto px-4">
            <div className="grid md:grid-cols-2 gap-16 items-center">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
              >
                <h2 className="text-3xl font-bold text-foreground mb-6">
                  我們的使命
                </h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                  CareerAI 成立於 2024 年，由一群熱愛技術與人力資源的專業人士創立。
                  我們看到傳統求職過程中的痛點：履歷石沉大海、職位描述與實際工作不符、
                  面試準備無從下手。
                </p>
                <p className="text-muted-foreground leading-relaxed">
                  因此，我們打造了這個 AI 驅動的職涯平台，希望透過智能分析與精準匹配，
                  讓每一份才華都能被世界看見，讓每一個夢想職位都觸手可及。
                </p>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
                className="glass rounded-3xl p-8 shadow-elevated"
              >
                <div className="grid grid-cols-2 gap-8">
                  {[
                    { value: "50K+", label: "活躍用戶" },
                    { value: "200+", label: "合作企業" },
                    { value: "95%", label: "匹配準確率" },
                    { value: "10K+", label: "成功就職" },
                  ].map((stat, index) => (
                    <div key={index} className="text-center">
                      <p className="text-3xl font-bold text-primary">{stat.value}</p>
                      <p className="text-sm text-muted-foreground">{stat.label}</p>
                    </div>
                  ))}
                </div>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Values */}
        <section className="py-24 bg-muted/30">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="text-center mb-16"
            >
              <h2 className="text-3xl font-bold text-foreground mb-4">
                我們的核心價值
              </h2>
            </motion.div>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {values.map((value, index) => (
                <motion.div
                  key={value.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="glass rounded-2xl p-6 text-center shadow-soft"
                >
                  <div className="w-14 h-14 rounded-xl bg-mint-100 flex items-center justify-center mx-auto mb-4">
                    <value.icon className="w-7 h-7 text-primary" />
                  </div>
                  <h3 className="font-semibold text-foreground mb-2">{value.title}</h3>
                  <p className="text-sm text-muted-foreground">{value.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
};

export default About;
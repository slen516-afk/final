import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Link } from "react-router-dom";
import { useState } from "react";
import { toast } from "sonner";
import { Eye, EyeOff, Sparkles, Check } from "lucide-react";

const Register = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      toast.info("註冊功能需要連接 Supabase");
    }, 1000);
  };

  const benefits = [
    "完整 AI 履歷分析報告",
    "無限職位匹配",
    "個人化職涯地圖",
    "面試準備與模擬",
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 flex items-center justify-center pt-20 py-12 bg-gradient-hero">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-8 items-center">
            {/* Benefits */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              className="hidden md:block"
            >
              <h2 className="text-3xl font-bold text-foreground mb-6">
                開啟您的職涯新篇章
              </h2>
              <p className="text-muted-foreground mb-8">
                註冊即可解鎖所有 AI 驅動的職涯服務，讓專業技術助您一臂之力
              </p>
              <ul className="space-y-4">
                {benefits.map((benefit, index) => (
                  <motion.li
                    key={benefit}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: 0.2 + index * 0.1 }}
                    className="flex items-center gap-3"
                  >
                    <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                      <Check className="w-4 h-4 text-primary-foreground" />
                    </div>
                    <span className="text-foreground">{benefit}</span>
                  </motion.li>
                ))}
              </ul>
            </motion.div>

            {/* Form */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="glass-strong rounded-3xl p-8 shadow-elevated">
                <div className="text-center mb-8">
                  <Link to="/" className="inline-flex items-center gap-2 mb-6">
                    <div className="w-12 h-12 rounded-xl bg-gradient-cta flex items-center justify-center">
                      <Sparkles className="w-6 h-6 text-primary-foreground" />
                    </div>
                  </Link>
                  <h1 className="text-2xl font-bold text-foreground mb-2">
                    免費註冊
                  </h1>
                  <p className="text-muted-foreground">
                    立即創建帳戶，開始使用 CareerAI
                  </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      姓名
                    </label>
                    <Input
                      type="text"
                      placeholder="請輸入您的姓名"
                      required
                      className="rounded-xl"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      電子郵件
                    </label>
                    <Input
                      type="email"
                      placeholder="your@email.com"
                      required
                      className="rounded-xl"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      密碼
                    </label>
                    <div className="relative">
                      <Input
                        type={showPassword ? "text" : "password"}
                        placeholder="至少 8 個字元"
                        required
                        className="rounded-xl pr-10"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div className="flex items-start gap-2">
                    <input type="checkbox" required className="rounded border-border mt-1" />
                    <span className="text-sm text-muted-foreground">
                      我同意 CareerAI 的{" "}
                      <Link to="/terms" className="text-primary hover:underline">
                        服務條款
                      </Link>{" "}
                      與{" "}
                      <Link to="/privacy" className="text-primary hover:underline">
                        隱私政策
                      </Link>
                    </span>
                  </div>

                  <Button
                    type="submit"
                    variant="hero"
                    size="lg"
                    className="w-full"
                    disabled={isLoading}
                  >
                    {isLoading ? "註冊中..." : "免費註冊"}
                  </Button>
                </form>

                <div className="mt-6 text-center text-sm text-muted-foreground">
                  已有帳戶？{" "}
                  <Link to="/login" className="text-primary font-medium hover:underline">
                    立即登入
                  </Link>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Register;
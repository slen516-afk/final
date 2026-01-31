import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Mail, Phone, MapPin, Send } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

const Contact = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      toast.success("訊息已送出，我們會盡快與您聯繫！");
    }, 1500);
  };

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
                聯繫我們
              </h1>
              <p className="text-lg text-muted-foreground leading-relaxed">
                有任何問題或建議？我們很樂意聆聽您的聲音
              </p>
            </motion.div>
          </div>
        </section>

        {/* Contact Form */}
        <section className="py-24">
          <div className="container mx-auto px-4">
            <div className="grid md:grid-cols-2 gap-16 max-w-5xl mx-auto">
              {/* Info */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
              >
                <h2 className="text-2xl font-bold text-foreground mb-6">
                  與我們取得聯繫
                </h2>
                <p className="text-muted-foreground mb-8">
                  無論是產品諮詢、合作洽談還是技術支援，
                  我們的團隊隨時準備為您服務。
                </p>

                <div className="space-y-6">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-mint-100 flex items-center justify-center flex-shrink-0">
                      <Mail className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-foreground mb-1">電子郵件</h3>
                      <p className="text-muted-foreground">contact@careerai.com</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-mint-100 flex items-center justify-center flex-shrink-0">
                      <Phone className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-foreground mb-1">聯絡電話</h3>
                      <p className="text-muted-foreground">+886 2 1234 5678</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-mint-100 flex items-center justify-center flex-shrink-0">
                      <MapPin className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-foreground mb-1">辦公地址</h3>
                      <p className="text-muted-foreground">
                        台北市信義區信義路五段7號
                      </p>
                    </div>
                  </div>
                </div>
              </motion.div>

              {/* Form */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
              >
                <form onSubmit={handleSubmit} className="glass rounded-3xl p-8 shadow-elevated">
                  <div className="space-y-5">
                    <div>
                      <label className="block text-sm font-medium text-foreground mb-2">
                        姓名
                      </label>
                      <Input placeholder="請輸入您的姓名" required className="rounded-xl" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-foreground mb-2">
                        電子郵件
                      </label>
                      <Input type="email" placeholder="請輸入您的電子郵件" required className="rounded-xl" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-foreground mb-2">
                        主旨
                      </label>
                      <Input placeholder="請輸入訊息主旨" required className="rounded-xl" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-foreground mb-2">
                        訊息內容
                      </label>
                      <Textarea
                        placeholder="請輸入您的訊息..."
                        required
                        className="min-h-[120px] rounded-xl resize-none"
                      />
                    </div>
                    <Button
                      type="submit"
                      variant="hero"
                      size="lg"
                      className="w-full"
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? "送出中..." : (
                        <>
                          送出訊息
                          <Send className="w-4 h-4" />
                        </>
                      )}
                    </Button>
                  </div>
                </form>
              </motion.div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
};

export default Contact;
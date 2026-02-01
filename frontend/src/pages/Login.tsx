import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
// 修正 1: 移除重複的 import，合併寫在一起
import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { toast } from "sonner";
import { Eye, EyeOff, Sparkles } from "lucide-react";

const Login = () => {
  // 修正 2: 新增這兩個 State 來儲存使用者輸入的資料
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // 假設你的後端是 5000 port
      const response = await fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // 修正 3: 這裡不再是寫死的字串，而是傳入上面的 state 變數
        body: JSON.stringify({
          email: email,      // 對應 const [email...]
          password: password // 對應 const [password...]
        }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('accessToken', data.access_token);
        // 這裡可以選擇性存 email，看你之後要不要顯示 "Hi, xxx"
        if (data.email) localStorage.setItem('userEmail', data.email);

        toast.success("登入成功！");
        navigate("/");
      } else {
        toast.error(data.message || "登入失敗，請檢查帳號密碼");
      }
    } catch (error) {
      console.error(error);
      toast.error("連線錯誤，請確認後端是否有開，或網址是否正確");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 flex items-center justify-center pt-20 py-12 bg-gradient-hero">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="max-w-md mx-auto"
          >
            <div className="glass-strong rounded-3xl p-8 shadow-elevated">
              <div className="text-center mb-8">
                <Link to="/" className="inline-flex items-center gap-2 mb-6">
                  <div className="w-12 h-12 rounded-xl bg-gradient-cta flex items-center justify-center">
                    <Sparkles className="w-6 h-6 text-primary-foreground" />
                  </div>
                </Link>
                <h1 className="text-2xl font-bold text-foreground mb-2">
                  歡迎回來
                </h1>
                <p className="text-muted-foreground">
                  登入您的帳戶繼續使用 CareerAI
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    電子郵件
                  </label>
                  {/* 修正 4: 綁定 value 和 onChange，這樣輸入框打字才會有效 */}
                  <Input
                    type="email"
                    placeholder="your@email.com"
                    required
                    className="rounded-xl"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    密碼
                  </label>
                  <div className="relative">
                    {/* 修正 5: 綁定密碼欄位的 value 和 onChange */}
                    <Input
                      type={showPassword ? "text" : "password"}
                      placeholder="請輸入密碼"
                      required
                      className="rounded-xl pr-10"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
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

                <div className="flex items-center justify-between text-sm">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" className="rounded border-border" />
                    <span className="text-muted-foreground">記住我</span>
                  </label>
                  <Link to="/forgot-password" className="text-primary hover:underline">
                    忘記密碼？
                  </Link>
                </div>

                <Button
                  type="submit"
                  variant="hero"
                  size="lg"
                  className="w-full"
                  disabled={isLoading}
                >
                  {isLoading ? "登入中..." : "登入"}
                </Button>
              </form>

              <div className="mt-6 text-center text-sm text-muted-foreground">
                還沒有帳戶？{" "}
                <Link to="/register" className="text-primary font-medium hover:underline">
                  立即註冊
                </Link>
              </div>
            </div>
          </motion.div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Login;
import { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom"; // 1. 補上 useNavigate, useLocation
import { Button } from "@/components/ui/button";
import { Menu, X, Sparkles, LayoutDashboard, LogOut, User } from "lucide-react"; // 2. 補上新 icon
import { motion, AnimatePresence } from "framer-motion";

const navLinks = [
  { name: "首頁", href: "/" },
  { name: "關於我們", href: "/about" },
  { name: "服務項目", href: "/services" },
  { name: "聯繫我們", href: "/contact" },
];

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  // 3. 新增狀態與 Hook
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userEmail, setUserEmail] = useState("");
  const navigate = useNavigate();
  const location = useLocation(); // 用來監聽網址變化

  // 4. 監聽路由變化，自動檢查 Token
  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    const email = localStorage.getItem("userEmail");

    if (token) {
      setIsLoggedIn(true);
      setUserEmail(email || "User");
    } else {
      setIsLoggedIn(false);
    }
  }, [location]); // 只要換頁就會重新檢查

  // 5. 登出功能
  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("userEmail");
    setIsLoggedIn(false);
    navigate("/login"); // 登出後踢回登入頁
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 glass-strong">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16 md:h-20">
          {/* Logo (保持不變) */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-cta flex items-center justify-center shadow-soft group-hover:shadow-glow transition-shadow duration-300">
              <Sparkles className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold text-foreground">
              職星領航員 <span className="text-primary">Career Pilot</span>
            </span>
          </Link>

          {/* Desktop Navigation (保持不變) */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                to={link.href}
                className="px-4 py-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent transition-all duration-200 font-medium"
              >
                {link.name}
              </Link>
            ))}
          </nav>

          {/* Desktop Auth Buttons (這裡做了修改！) */}
          <div className="hidden md:flex items-center gap-3">
            {isLoggedIn ? (
              // === 情況 A: 已登入 (顯示儀表板 + 登出) ===
              <>
                <span className="text-sm text-muted-foreground mr-2 hidden lg:inline-block">
                  {userEmail}
                </span>
                <Button variant="ghost" asChild>
                  <Link to="/dashboard" className="flex items-center gap-2">
                    <LayoutDashboard className="w-4 h-4" />
                    儀表板
                  </Link>
                </Button>
                <Button
                  variant="ghost"
                  onClick={handleLogout}
                  className="text-red-500 hover:text-red-600 hover:bg-red-50"
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  登出
                </Button>
              </>
            ) : (
              // === 情況 B: 未登入 (顯示原本的按鈕) ===
              <>
                <Button variant="ghost" asChild>
                  <Link to="/login">登入</Link>
                </Button>
                <Button variant="hero" asChild>
                  <Link to="/register">免費註冊</Link>
                </Button>
              </>
            )}
          </div>

          {/* Mobile Menu Button (保持不變) */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-accent transition-colors"
            aria-label="Toggle menu"
          >
            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu (這裡也做了修改！) */}
      <AnimatePresence>
        {isMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden glass-strong border-t border-border"
          >
            <nav className="container mx-auto px-4 py-4 flex flex-col gap-2">
              {navLinks.map((link) => (
                <Link
                  key={link.name}
                  to={link.href}
                  onClick={() => setIsMenuOpen(false)}
                  className="px-4 py-3 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent transition-all duration-200 font-medium"
                >
                  {link.name}
                </Link>
              ))}

              <div className="flex flex-col gap-2 mt-4 pt-4 border-t border-border">
                {isLoggedIn ? (
                  // === 手機版：已登入 ===
                  <>
                    <div className="px-4 py-2 text-sm text-muted-foreground flex items-center gap-2">
                      <User className="w-4 h-4" />
                      {userEmail}
                    </div>
                    <Button variant="outline" asChild className="w-full justify-start">
                      <Link to="/dashboard" onClick={() => setIsMenuOpen(false)}>
                        <LayoutDashboard className="w-4 h-4 mr-2" />
                        前往儀表板
                      </Link>
                    </Button>
                    <Button
                      variant="ghost"
                      onClick={() => { handleLogout(); setIsMenuOpen(false); }}
                      className="w-full justify-start text-red-500 hover:text-red-600 hover:bg-red-50"
                    >
                      <LogOut className="w-4 h-4 mr-2" />
                      登出
                    </Button>
                  </>
                ) : (
                  // === 手機版：未登入 ===
                  <>
                    <Button variant="outline" asChild className="w-full">
                      <Link to="/login" onClick={() => setIsMenuOpen(false)}>登入</Link>
                    </Button>
                    <Button variant="hero" asChild className="w-full">
                      <Link to="/register" onClick={() => setIsMenuOpen(false)}>免費註冊</Link>
                    </Button>
                  </>
                )}
              </div>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
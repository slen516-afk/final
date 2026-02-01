import { Header } from "@/components/Header";
import { HeroSection } from "@/components/HeroSection";
import { QuickExperienceZone } from "@/components/QuickExperienceZone";
import { ServicesSection } from "@/components/ServicesSection";
import { Footer } from "@/components/Footer";
import { CareerGuideWidget } from "@/components/CareerGuideWidget";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, LayoutDashboard } from "lucide-react"; // 引入一些漂亮的 icon

const Index = () => {
  // 1. 設定狀態來存登入資訊
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userEmail, setUserEmail] = useState("");

  // 2. 畫面載入時檢查 localStorage
  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    const email = localStorage.getItem("userEmail");

    if (token) {
      setIsLoggedIn(true);
      if (email) setUserEmail(email);
    }
  }, []);

  return (
    <div className="min-h-screen flex flex-col"> {/* flex-col 確保 footer 在最下面 */}
      <Header />

      <main className="flex-1">

        {/* === 3. 新增這裡：如果已登入，顯示歡迎橫幅 === */}
        {isLoggedIn && (
          <div className="bg-blue-50 border-b border-blue-100">
            <div className="container mx-auto px-4 py-4 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-2 text-blue-900">
                <span className="font-medium">👋 歡迎回來，{userEmail}！</span>
                <span className="text-sm text-blue-600 hidden sm:inline">準備好繼續你的職涯規劃了嗎？</span>
              </div>

              <Link to="/dashboard">
                <button className="flex items-center gap-2 bg-blue-600 text-white px-6 py-2.5 rounded-full hover:bg-blue-700 transition-all shadow-sm font-medium text-sm">
                  <LayoutDashboard className="w-4 h-4" />
                  前往儀表板
                  <ArrowRight className="w-4 h-4" />
                </button>
              </Link>
            </div>
          </div>
        )}
        {/* =========================================== */}

        <HeroSection />
        <QuickExperienceZone />
        <ServicesSection />
      </main>

      <Footer />
      <CareerGuideWidget />
    </div>
  );
};

export default Index;
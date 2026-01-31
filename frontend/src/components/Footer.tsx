import { Link } from "react-router-dom";
import { Sparkles, Mail, Phone, MapPin } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-foreground text-background py-16">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-12">
          {/* Brand */}
          <div className="md:col-span-1">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold">
                Career<span className="text-primary">AI</span>
              </span>
            </Link>
            <p className="text-background/70 text-sm leading-relaxed">
              讓你的才華，被世界精準對焦。
              讓 AI 輔助您打造專屬個人品牌。
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-semibold mb-4">快速連結</h4>
            <ul className="space-y-3">
              {["首頁", "關於我們", "服務項目", "聯繫我們"].map((link) => (
                <li key={link}>
                  <Link
                    to={link === "首頁" ? "/" : `/${link}`}
                    className="text-background/70 hover:text-primary transition-colors text-sm"
                  >
                    {link}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Services */}
          <div>
            <h4 className="font-semibold mb-4">服務項目</h4>
            <ul className="space-y-3">
              {["履歷分析", "職位匹配", "面試準備", "職涯地圖"].map((service) => (
                <li key={service}>
                  <span className="text-background/70 text-sm">{service}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-semibold mb-4">聯繫方式</h4>
            <ul className="space-y-3">
              <li className="flex items-center gap-2 text-background/70 text-sm">
                <Mail className="w-4 h-4 text-primary" />
                contact@careerpilot.com
              </li>
              <li className="flex items-center gap-2 text-background/70 text-sm">
                <Phone className="w-4 h-4 text-primary" />
                +886 2 1234 5678
              </li>
              <li className="flex items-start gap-2 text-background/70 text-sm">
                <MapPin className="w-4 h-4 text-primary mt-0.5" />
                台北市信義區信義路五段7號
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-background/10 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-background/50 text-sm">
            © 2024 Career Pilot. All rights reserved.
          </p>
          <div className="flex gap-6">
            <Link to="/privacy" className="text-background/50 hover:text-primary transition-colors text-sm">
              隱私政策
            </Link>
            <Link to="/terms" className="text-background/50 hover:text-primary transition-colors text-sm">
              服務條款
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
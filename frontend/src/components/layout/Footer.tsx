import { Link } from "react-router-dom";
import { Mail, Phone, MapPin } from "lucide-react";
import logoImage from "@/assets/logo.png";

const Footer = () => {
  const quickLinks = [
    { to: "/", label: "首頁" },
    { to: "/team", label: "關於我們" },
    { to: "/faq", label: "常見問題" },
  ];

  const serviceLinks = [
    { to: "/jobs/skill-search", label: "職缺核心技能查詢" },
    { to: "/resume/optimize", label: "履歷優化" },
    { to: "/jobs/recommendations", label: "推薦職缺" },
    { to: "/analysis/skills", label: "職能圖譜" },
  ];

  return (
    <footer className="footer-bg">
      <div className="container py-12 md:py-16 bg-[#4f2d03]">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="space-y-4">
            <Link to="/" className="flex items-center gap-3">
              <img
                src={logoImage}
                alt="職星領航員 Logo"
                className="h-14 w-14 object-contain opacity-90 brightness-125"
              />
              <div className="flex flex-col leading-none">
                <span className="text-lg font-bold text-white">職星領航員</span>
                <span className="text-xs text-white/60">Career Pilot</span>
              </div>
            </Link>
            <p className="text-sm text-white/70 leading-relaxed">運用 AI 技術，為您打造最佳職涯發展路徑。</p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-semibold mb-4 text-white">快速連結</h4>
            <ul className="space-y-2">
              {quickLinks.map((link) => (
                <li key={link.to}>
                  <Link to={link.to} className="text-sm text-white/70 hover:text-white transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Services */}
          <div>
            <h4 className="font-semibold mb-4 text-white">服務項目</h4>
            <ul className="space-y-2">
              {serviceLinks.map((link) => (
                <li key={link.to}>
                  <Link to={link.to} className="text-sm text-white/70 hover:text-white transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact Info - icons use light color on dark bg */}
          <div>
            <h4 className="font-semibold mb-4 text-white">聯絡資訊</h4>
            <ul className="space-y-3">
              <li className="flex items-center gap-2 text-sm text-white/70">
                <Mail className="h-4 w-4 text-icon-light" />
                <span>service@careerpilot.com</span>
              </li>
              <li className="flex items-center gap-2 text-sm text-white/70">
                <Phone className="h-4 w-4 text-icon-light" />
                <span>https://reurl.cc/jmA301</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Copyright */}
        <div className="border-t border-white/10 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-white/60">© 2026 Career Pilot 職星領航員. All rights reserved.</p>
          <div className="flex gap-6">
            <Link to="#" className="text-sm text-white/60 hover:text-white transition-colors">
              隱私政策
            </Link>
            <Link to="#" className="text-sm text-white/60 hover:text-white transition-colors">
              服務條款
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

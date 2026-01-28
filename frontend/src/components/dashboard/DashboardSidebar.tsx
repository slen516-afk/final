import { useState } from "react";
import { NavLink } from "@/components/NavLink";
import { useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  History,
  Compass,
  Map,
  MessageSquare,
  Mail,
  Trophy,
  ChevronLeft,
  ChevronRight,
  Star,
  Rocket, // 👈 1. 新增 Rocket 圖示引入
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

/**
 * Dashboard Sidebar Navigation
 * * Supabase fields required:
 * - user_id: UUID (from auth.users)
 * - subscription_tier: TEXT (free/premium for feature gating)
 * - preferred_language: TEXT (user's language preference)
 */

const navItems = [
  { 
    title: "分析編輯器", 
    titleEn: "Analysis Editor",
    url: "/dashboard", 
    icon: LayoutDashboard 
  },
  // 👇👇👇 2. 新增這個「AI 專案推薦」按鈕
  { 
    title: "AI 專案推薦", 
    titleEn: "Project Ideas",
    url: "/dashboard/side-projects", 
    icon: Rocket 
  },
  { 
    title: "歷史分析", 
    titleEn: "Historical Analysis",
    url: "/dashboard/history", 
    icon: History 
  },
  { 
    title: "職涯推薦", 
    titleEn: "Job Recommendations",
    url: "/dashboard/recommendations", 
    icon: Compass 
  },
  { 
    title: "職涯地圖", 
    titleEn: "Career Map",
    url: "/dashboard/career-map", 
    icon: Map 
  },
  { 
    title: "面試準備", 
    titleEn: "Interview Prep",
    url: "/dashboard/interview-prep", 
    icon: MessageSquare 
  },
  { 
    title: "感謝信生成", 
    titleEn: "Thank-you Letter",
    url: "/dashboard/thank-you", 
    icon: Mail 
  },
  { 
    title: "成就記錄", 
    titleEn: "Achievement Logger",
    url: "/dashboard/achievements", 
    icon: Trophy 
  },
];

export function DashboardSidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  return (
    <aside
      className={cn(
        "h-screen sticky top-0 bg-sidebar-background border-r border-sidebar-border transition-all duration-300 flex flex-col",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Logo / Brand */}
      <div className="p-4 border-b border-sidebar-border flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center shrink-0">
          <Star className="w-5 h-5 text-primary-foreground" />
        </div>
        {!collapsed && (
          <span className="font-semibold text-sidebar-foreground whitespace-nowrap">
            職涯助手
          </span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = location.pathname === item.url;
          return (
            <NavLink
              key={item.url}
              to={item.url}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group",
                isActive
                  ? "bg-sidebar-accent text-sidebar-primary font-medium"
                  : "text-sidebar-foreground hover:bg-sidebar-accent/50"
              )}
            >
              <item.icon
                className={cn(
                  "w-5 h-5 shrink-0 transition-colors",
                  isActive ? "text-sidebar-primary" : "text-muted-foreground group-hover:text-sidebar-primary"
                )}
              />
              {!collapsed && (
                <span className="truncate">{item.title}</span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Collapse Toggle */}
      <div className="p-3 border-t border-sidebar-border">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setCollapsed(!collapsed)}
          className="w-full justify-center"
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <>
              <ChevronLeft className="w-4 h-4 mr-2" />
              <span>收合</span>
            </>
          )}
        </Button>
      </div>
    </aside>
  );
}
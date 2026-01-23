import { ReactNode } from "react";
import { DashboardSidebar } from "./DashboardSidebar";
import { AchievementLogger } from "./AchievementLogger";

interface DashboardLayoutProps {
  children: ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="flex min-h-screen w-full bg-background">
      <DashboardSidebar />
      <main className="flex-1 overflow-auto">
        {children}
      </main>
      <AchievementLogger />
    </div>
  );
}

import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Trophy, Calendar, Tag, TrendingUp } from "lucide-react";

/**
 * Achievements Page - Full view of logged achievements
 * 
 * This page displays all achievements logged via the AchievementLogger widget.
 * See AchievementLogger.tsx for the Supabase table schema.
 */

const sampleAchievements = [
  {
    id: "1",
    date: "2024-01-15",
    content: "完成了電商平台的搜尋功能優化",
    skills: ["Elasticsearch", "React", "Performance"],
    metrics: { improvement: "30%", metric: "搜尋準確率" },
    project: "電商平台",
  },
  {
    id: "2",
    date: "2024-01-10",
    content: "主導建立前端元件庫，統一團隊開發規範",
    skills: ["Storybook", "Design System", "Documentation"],
    metrics: { improvement: "40%", metric: "開發效率" },
    project: "內部工具",
  },
  {
    id: "3",
    date: "2024-01-05",
    content: "完成用戶分析儀表板的資料視覺化模組",
    skills: ["D3.js", "React", "Data Visualization"],
    metrics: { improvement: "15", metric: "個新圖表類型" },
    project: "Analytics Dashboard",
  },
];

export default function Achievements() {
  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Trophy className="w-6 h-6 text-amber-500" />
            成就記錄
          </h1>
          <p className="text-muted-foreground mt-1">
            您的專案成就和職涯里程碑
          </p>
        </div>

        <div className="grid gap-4">
          {sampleAchievements.map((achievement) => (
            <Card key={achievement.id}>
              <CardContent className="p-4">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shrink-0">
                    <Trophy className="w-6 h-6 text-white" />
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                      <Calendar className="w-4 h-4" />
                      <span>{achievement.date}</span>
                      <Badge variant="outline">{achievement.project}</Badge>
                    </div>

                    <p className="text-foreground font-medium mb-3">
                      {achievement.content}
                    </p>

                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-1">
                        <Tag className="w-4 h-4 text-muted-foreground" />
                        <div className="flex gap-1">
                          {achievement.skills.map((skill) => (
                            <Badge key={skill} variant="secondary" className="text-xs">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      <div className="flex items-center gap-1 text-sm">
                        <TrendingUp className="w-4 h-4 text-green-500" />
                        <span className="font-semibold text-green-600">
                          {achievement.metrics.improvement}
                        </span>
                        <span className="text-muted-foreground">
                          {achievement.metrics.metric}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}

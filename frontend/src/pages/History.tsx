import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { History as HistoryIcon, FileText, Eye, Trash2, Calendar } from "lucide-react";

/**
 * Historical Analysis Page
 * 
 * Supabase tables required:
 * 
 * Table: analysis_history
 * - id: UUID
 * - user_id: UUID (foreign key)
 * - resume_id: UUID (foreign key)
 * - jd_id: UUID (foreign key, nullable)
 * - analysis_type: TEXT ('gap' | 'recommendation')
 * - skill_gap_score: FLOAT (for gap analysis)
 * - result_summary: JSONB
 * - created_at: TIMESTAMP
 */

const sampleHistory = [
  {
    id: "1",
    date: "2024-01-15",
    type: "gap",
    resumeTitle: "前端工程師履歷 v3",
    jdTitle: "Google - Staff Engineer",
    score: 78,
  },
  {
    id: "2",
    date: "2024-01-10",
    type: "recommendation",
    resumeTitle: "前端工程師履歷 v2",
    jdTitle: null,
    matchCount: 12,
  },
  {
    id: "3",
    date: "2024-01-05",
    type: "gap",
    resumeTitle: "前端工程師履歷 v1",
    jdTitle: "Meta - Frontend Engineer",
    score: 65,
  },
];

export default function History() {
  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <HistoryIcon className="w-6 h-6 text-primary" />
            歷史分析紀錄
          </h1>
          <p className="text-muted-foreground mt-1">
            查看過去的履歷分析和職缺匹配結果
          </p>
        </div>

        <div className="space-y-4">
          {sampleHistory.map((item) => (
            <Card key={item.id}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                      <FileText className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-medium text-foreground">
                        {item.resumeTitle}
                      </h3>
                      {item.jdTitle && (
                        <p className="text-sm text-muted-foreground">
                          對比：{item.jdTitle}
                        </p>
                      )}
                      <div className="flex items-center gap-2 mt-1">
                        <Calendar className="w-3 h-3 text-muted-foreground" />
                        <span className="text-xs text-muted-foreground">{item.date}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    {item.type === "gap" ? (
                      <Badge variant={item.score >= 70 ? "default" : "secondary"}>
                        匹配度 {item.score}%
                      </Badge>
                    ) : (
                      <Badge variant="outline">
                        {item.matchCount} 個推薦職缺
                      </Badge>
                    )}
                    <div className="flex gap-2">
                      <Button variant="ghost" size="icon">
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="icon">
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
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

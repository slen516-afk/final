import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Compass, MapPin, Building2, ExternalLink, Bookmark } from "lucide-react";

/**
 * Recommendations Page
 * 
 * Supabase tables required:
 * 
 * Table: job_recommendations
 * - id: UUID
 * - user_id: UUID (foreign key)
 * - resume_id: UUID (foreign key)
 * - job_title: TEXT
 * - company_name: TEXT
 * - location: TEXT
 * - match_score: FLOAT
 * - matching_skills: TEXT[]
 * - external_url: TEXT
 * - is_saved: BOOLEAN
 * - created_at: TIMESTAMP
 */

const sampleRecommendations = [
  {
    id: "1",
    title: "Staff Frontend Engineer",
    company: "Google",
    location: "台北 / Remote",
    matchScore: 95,
    matchingSkills: ["React", "TypeScript", "System Design"],
    salary: "NTD 3.5M - 4.5M",
  },
  {
    id: "2",
    title: "Senior Software Engineer",
    company: "Meta",
    location: "新加坡",
    matchScore: 88,
    matchingSkills: ["React", "GraphQL", "Testing"],
    salary: "SGD 180K - 220K",
  },
  {
    id: "3",
    title: "前端架構師",
    company: "Shopify",
    location: "Remote",
    matchScore: 85,
    matchingSkills: ["Architecture", "React", "Performance"],
    salary: "USD 150K - 180K",
  },
  {
    id: "4",
    title: "技術主管",
    company: "LINE Taiwan",
    location: "台北",
    matchScore: 82,
    matchingSkills: ["Leadership", "React", "Node.js"],
    salary: "NTD 2.8M - 3.5M",
  },
];

export default function Recommendations() {
  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Compass className="w-6 h-6 text-primary" />
            職涯推薦
          </h1>
          <p className="text-muted-foreground mt-1">
            基於您的履歷技能推薦的最佳職缺
          </p>
        </div>

        <div className="grid gap-4">
          {sampleRecommendations.map((job) => (
            <Card key={job.id} className="overflow-hidden">
              <CardContent className="p-0">
                <div className="flex">
                  {/* Match Score Bar */}
                  <div
                    className="w-2 shrink-0"
                    style={{
                      background: `linear-gradient(to bottom, hsl(var(--primary)), hsl(var(--primary) / 0.5))`,
                    }}
                  />

                  <div className="flex-1 p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="text-lg font-semibold text-foreground">
                          {job.title}
                        </h3>
                        <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Building2 className="w-4 h-4" />
                            {job.company}
                          </span>
                          <span className="flex items-center gap-1">
                            <MapPin className="w-4 h-4" />
                            {job.location}
                          </span>
                        </div>
                        <p className="text-sm font-medium text-primary mt-2">
                          {job.salary}
                        </p>
                      </div>

                      <div className="text-right">
                        <div className="text-2xl font-bold text-primary">
                          {job.matchScore}%
                        </div>
                        <p className="text-xs text-muted-foreground">匹配度</p>
                      </div>
                    </div>

                    <div className="flex items-center justify-between mt-4">
                      <div className="flex flex-wrap gap-2">
                        {job.matchingSkills.map((skill) => (
                          <Badge key={skill} variant="secondary">
                            {skill}
                          </Badge>
                        ))}
                      </div>

                      <div className="flex gap-2">
                        <Button variant="ghost" size="icon">
                          <Bookmark className="w-4 h-4" />
                        </Button>
                        <Button size="sm">
                          <ExternalLink className="w-4 h-4 mr-2" />
                          查看職缺
                        </Button>
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

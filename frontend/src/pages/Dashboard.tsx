import { useState, useMemo } from "react";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { FileDown, Globe, FileText, Briefcase, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Analysis Editor (Dashboard Main Page)
 * 
 * Supabase tables required:
 * 
 * Table: resumes
 * - id: UUID
 * - user_id: UUID (foreign key)
 * - content: TEXT (markdown content)
 * - parsed_skills: TEXT[] (extracted skills)
 * - years_experience: INTEGER
 * - job_titles: TEXT[] (historical titles)
 * - languages: TEXT[] (unlocked languages based on metadata)
 * - created_at: TIMESTAMP
 * - updated_at: TIMESTAMP
 * 
 * Table: job_descriptions
 * - id: UUID
 * - user_id: UUID (foreign key)
 * - resume_id: UUID (foreign key)
 * - content: TEXT
 * - company_name: TEXT
 * - job_title: TEXT
 * - required_skills: TEXT[]
 * - created_at: TIMESTAMP
 * 
 * Table: gap_analyses
 * - id: UUID
 * - resume_id: UUID (foreign key)
 * - jd_id: UUID (foreign key)
 * - skill_gap_score: FLOAT (0-1, degree of gap)
 * - missing_skills: TEXT[]
 * - matching_skills: TEXT[]
 * - recommendations: JSONB
 * - created_at: TIMESTAMP
 */

const defaultResume = `# 個人履歷

## 基本資訊
- 姓名：王小明
- 職稱：資深前端工程師
- 經驗：5年

## 技能
- React, TypeScript, Next.js
- Node.js, PostgreSQL
- AWS, Docker

## 工作經歷
### ABC科技公司 | 資深前端工程師 | 2021-現在
- 主導電商平台重構，提升頁面載入速度40%
- 建立前端元件庫，減少開發時間30%

### XYZ新創 | 前端工程師 | 2019-2021
- 開發SaaS產品前端架構
- 實作即時協作功能
`;

const languages = [
  { value: "zh-TW", label: "繁體中文", locked: false },
  { value: "en", label: "English", locked: false },
  { value: "ja", label: "日本語", locked: true },
  { value: "de", label: "Deutsch", locked: true },
  { value: "fr", label: "Français", locked: true },
];

export default function Dashboard() {
  const [resumeContent, setResumeContent] = useState(defaultResume);
  const [jdContent, setJdContent] = useState("");
  const [language, setLanguage] = useState("zh-TW");
  const [isLoggedIn] = useState(false); // Placeholder for auth state

  const hasJD = jdContent.trim().length > 0;

  // Simple markdown to HTML conversion for preview
  const previewHtml = useMemo(() => {
    return resumeContent
      .replace(/^### (.+)$/gm, '<h3 class="text-lg font-semibold mt-4 mb-2 text-foreground">$1</h3>')
      .replace(/^## (.+)$/gm, '<h2 class="text-xl font-bold mt-6 mb-3 text-foreground border-b border-border pb-2">$1</h2>')
      .replace(/^# (.+)$/gm, '<h1 class="text-2xl font-bold mb-4 text-primary">$1</h1>')
      .replace(/^- (.+)$/gm, '<li class="ml-4 text-muted-foreground">$1</li>')
      .replace(/\n\n/g, '<br/><br/>');
  }, [resumeContent]);

  const handleExportPDF = () => {
    // Placeholder for PDF export
    console.log("Exporting to PDF...");
    alert("PDF 匯出功能開發中...");
  };

  return (
    <DashboardLayout>
      <div className="h-screen flex flex-col">
        {/* Toolbar */}
        <header className="px-6 py-4 border-b border-border bg-card/50 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold text-foreground">分析編輯器</h1>
            <Select value={language} onValueChange={setLanguage}>
              <SelectTrigger className="w-40">
                <Globe className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {languages.map((lang) => (
                  <SelectItem
                    key={lang.value}
                    value={lang.value}
                    disabled={lang.locked && !isLoggedIn}
                  >
                    {lang.label}
                    {lang.locked && !isLoggedIn && " 🔒"}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button onClick={handleExportPDF} variant="outline">
            <FileDown className="w-4 h-4 mr-2" />
            匯出 PDF
          </Button>
        </header>

        {/* Main Content - Split View */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left: Editor */}
          <div className="w-1/2 flex flex-col border-r border-border">
            {/* Resume Editor */}
            <div className="flex-1 flex flex-col p-4 overflow-hidden">
              <div className="flex items-center gap-2 mb-3">
                <FileText className="w-5 h-5 text-primary" />
                <h2 className="font-semibold text-foreground">履歷內容 (Markdown)</h2>
              </div>
              <Textarea
                value={resumeContent}
                onChange={(e) => setResumeContent(e.target.value)}
                className="flex-1 font-mono text-sm resize-none"
                placeholder="請輸入或貼上您的 Markdown 履歷..."
              />
            </div>

            {/* JD Input */}
            <div className="h-48 border-t border-border p-4 bg-muted/30">
              <div className="flex items-center gap-2 mb-3">
                <Briefcase className="w-5 h-5 text-primary" />
                <h2 className="font-semibold text-foreground">職缺描述 (選填)</h2>
              </div>
              <Textarea
                value={jdContent}
                onChange={(e) => setJdContent(e.target.value)}
                className="h-24 text-sm resize-none"
                placeholder="貼上職缺 JD，系統將進行差距分析..."
              />
            </div>
          </div>

          {/* Right: Preview & Analysis */}
          <div className="w-1/2 flex flex-col overflow-hidden">
            {/* Markdown Preview */}
            <div className="flex-1 p-6 overflow-y-auto bg-card">
              <div className="max-w-2xl mx-auto">
                <div
                  className="prose prose-sm max-w-none"
                  dangerouslySetInnerHTML={{ __html: previewHtml }}
                />
              </div>
            </div>

            {/* Analysis Panel */}
            <div className="h-64 border-t border-border p-4 bg-muted/20 overflow-y-auto">
              <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                {hasJD ? (
                  <>
                    <AlertTriangle className="w-5 h-5 text-amber-500" />
                    差距分析
                  </>
                ) : (
                  <>
                    <Briefcase className="w-5 h-5 text-primary" />
                    職缺推薦
                  </>
                )}
              </h3>

              {hasJD ? (
                // Gap Analysis View
                <div className="space-y-4">
                  <div className="p-4 rounded-lg bg-card border border-border">
                    <h4 className="font-medium text-foreground mb-2">技能差距分數</h4>
                    <div className="flex items-center gap-3">
                      <div className="flex-1 h-3 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-red-400 via-amber-400 to-green-400"
                          style={{ width: "72%" }}
                        />
                      </div>
                      <span className="text-sm font-semibold text-foreground">72%</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 rounded-lg bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900">
                      <h4 className="text-sm font-medium text-red-700 dark:text-red-400 mb-2">
                        缺少的技能
                      </h4>
                      <ul className="text-xs space-y-1 text-red-600 dark:text-red-300">
                        <li>• Kubernetes</li>
                        <li>• GraphQL</li>
                        <li>• CI/CD Pipeline</li>
                      </ul>
                    </div>
                    <div className="p-3 rounded-lg bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-900">
                      <h4 className="text-sm font-medium text-green-700 dark:text-green-400 mb-2">
                        匹配的技能
                      </h4>
                      <ul className="text-xs space-y-1 text-green-600 dark:text-green-300">
                        <li>• React</li>
                        <li>• TypeScript</li>
                        <li>• Node.js</li>
                      </ul>
                    </div>
                  </div>
                </div>
              ) : (
                // Recommendations View
                <div className="grid grid-cols-1 gap-3">
                  {[
                    { title: "技術主管", company: "Google", match: "95%" },
                    { title: "Staff Engineer", company: "Meta", match: "88%" },
                    { title: "前端架構師", company: "Shopify", match: "85%" },
                  ].map((job, i) => (
                    <div
                      key={i}
                      className="p-3 rounded-lg bg-card border border-border flex items-center justify-between hover:border-primary/50 transition-colors cursor-pointer"
                    >
                      <div>
                        <h4 className="font-medium text-foreground">{job.title}</h4>
                        <p className="text-sm text-muted-foreground">{job.company}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-primary">{job.match}</span>
                        <Button size="sm" variant="outline">
                          查看
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

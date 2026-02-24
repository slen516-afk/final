import { useState, useCallback } from "react";
import { Search, Code, Layers } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { AILoadingSpinner, ContentTransition } from "@/components/loading/LoadingStates";
import { Skeleton } from "@/components/ui/skeleton";
import { motion } from "framer-motion";
import type { SkillCard } from "@/types/job";
import { JOB_CATEGORIES, ICON_NAME_MAP } from "@/mocks/jobs";

// ── Icon helper ──────────────────────────────────────────────────

const getIconFileName = (skillName: string): string => {
  if (ICON_NAME_MAP[skillName]) return ICON_NAME_MAP[skillName];
  return skillName;
};

const SkillIcon = ({ skillName }: { skillName: string }) => {
  const [imgError, setImgError] = useState(false);
  const iconPath = `/icons/${getIconFileName(skillName)}_icon.png`;

  if (imgError) {
    const hash = skillName.charCodeAt(0);
    return hash % 2 === 0 ? <Code className="h-8 w-8 text-primary" /> : <Layers className="h-8 w-8 text-primary" />;
  }

  return (
    <img
      src={iconPath}
      alt={`${skillName} icon`}
      className="h-8 w-8 object-contain"
      onError={() => setImgError(true)}
    />
  );
};

// ── Skeleton for skill grid ──────────────────────────────────────

const SkillGridSkeleton = () => (
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
    {Array.from({ length: 6 }).map((_, i) => (
      <div key={i} className="rounded-xl border bg-card p-5 space-y-3">
        <div className="flex items-center gap-3">
          <Skeleton className="h-10 w-10 rounded-lg" />
          <Skeleton className="h-5 w-24" />
        </div>
        <Skeleton className="h-4 w-full" />
        <div className="flex gap-2">
          <Skeleton className="h-5 w-14 rounded-full" />
          <Skeleton className="h-5 w-16 rounded-full" />
        </div>
      </div>
    ))}
  </div>
);

// ── Main Component ───────────────────────────────────────────────

const SkillSearch = () => {
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [selectedSub, setSelectedSub] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [results, setResults] = useState<SkillCard[]>([]);

  // Derived data
  const currentCategory = JOB_CATEGORIES.find((c) => c.label === selectedCategory);
  const subcategories = currentCategory?.subcategories ?? [];

  // Reset subcategory when category changes
  const handleCategoryChange = (value: string) => {
    setSelectedCategory(value);
    setSelectedSub("");
    setHasSearched(false);
    setResults([]);
  };

  const handleSearch = useCallback(async () => {
    if (!selectedCategory || !selectedSub) return;

    setIsLoading(true);
    setHasSearched(true);

    // TODO: Replace with API call
    await new Promise((resolve) => setTimeout(resolve, 1000));

    const sub = subcategories.find((s) => s.label === selectedSub);
    setResults(sub?.skills ?? []);
    setIsLoading(false);
  }, [selectedCategory, selectedSub, subcategories]);

  return (
    <div className="container py-12 animate-fade-in">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-6">
          <Search className="h-8 w-8 text-primary" />
        </div>
        <h1 className="text-3xl font-bold mb-4">職類核心技能查詢</h1>
        <p className="text-muted-foreground max-w-2xl mx-auto">選擇您感興趣的職務類別，探索所需的核心技能</p>
      </div>

      {/* Search Controls */}
      <div className="max-w-3xl mx-auto mb-12">
        <div className="flex flex-col sm:flex-row gap-3">
          <Select value={selectedCategory} onValueChange={handleCategoryChange}>
            <SelectTrigger className="flex-1 bg-card">
              <SelectValue placeholder="選擇職務大類" />
            </SelectTrigger>
            <SelectContent className="bg-popover border z-50">
              {JOB_CATEGORIES.map((cat) => (
                <SelectItem key={cat.label} value={cat.label}>
                  {cat.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={selectedSub} onValueChange={setSelectedSub} disabled={!selectedCategory}>
            <SelectTrigger className="flex-1 bg-card">
              <SelectValue placeholder={selectedCategory ? "選擇細分項目" : "請先選擇職務大類"} />
            </SelectTrigger>
            <SelectContent className="bg-popover border z-50">
              {subcategories.map((sub) => (
                <SelectItem key={sub.label} value={sub.label}>
                  {sub.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Button
            className="gradient-primary min-w-[100px]"
            onClick={handleSearch}
            disabled={isLoading || !selectedCategory || !selectedSub}
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <span className="h-4 w-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                搜尋中
              </span>
            ) : (
              <>
                <Search className="h-4 w-4" />
                搜尋
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Results */}
      <div className="max-w-6xl mx-auto">
        <ContentTransition
          isLoading={isLoading}
          skeleton={
            <div className="space-y-4">
              <AILoadingSpinner message="正在為您分析相關技能..." />
              <SkillGridSkeleton />
            </div>
          }
        >
          {hasSearched && results.length > 0 ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <p className="text-sm text-muted-foreground mb-6">
                {selectedSub} — 共 {results.length} 項核心技能
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {results.map((skill, index) => (
                  <motion.div
                    key={skill.name}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.06 }}
                  >
                    <Card className="group relative overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-medium hover:ring-1 hover:ring-primary/40 hover:shadow-[0_0_16px_hsl(152_69%_45%/0.15)]">
                      <CardHeader className="pb-2">
                        <div className="flex items-center gap-3">
                          <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-primary/10 shrink-0">
                            <SkillIcon skillName={skill.name} />
                          </div>
                          <CardTitle className="text-base">{skill.name}</CardTitle>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-muted-foreground mb-3 line-clamp-2">{skill.description}</p>
                        <div className="flex flex-wrap gap-1.5">
                          {skill.tags.map((tag) => (
                            <Badge key={tag} variant="secondary" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          ) : hasSearched ? (
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-muted-foreground">沒有找到相關技能，請嘗試其他類別</p>
              </CardContent>
            </Card>
          ) : (
            <Card className="border-dashed">
              <CardContent className="py-16 text-center">
                <div className="inline-flex items-center justify-center h-12 w-12 rounded-full bg-muted mb-4">
                  <Search className="h-6 w-6 text-muted-foreground" />
                </div>
                <p className="text-muted-foreground">請選擇職務類別並按下搜尋</p>
              </CardContent>
            </Card>
          )}
        </ContentTransition>
      </div>
    </div>
  );
};

export default SkillSearch;

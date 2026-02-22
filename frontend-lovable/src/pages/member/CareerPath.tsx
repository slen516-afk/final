import { useState, useEffect } from 'react';
import { Map, ChevronRight, Star, FileText, Calendar } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import RightDrawer from '@/components/panels/RightDrawer';
import LoginRequired from '@/components/gatekeeper/LoginRequired';
import CareerLadder from '@/components/career-path/CareerLadder';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { useIsMobile } from '@/hooks/use-mobile';
import type { AnalysisHistoryItem } from '@/types/analysis';
import { analysisHistory } from '@/mocks/analysis';

const AnalysisListSkeleton = () => (
  <div className="space-y-3 md:space-y-4">
    {[1, 2, 3].map((i) => (
      <div key={i} className="p-3 md:p-4 rounded-lg border">
        <div className="flex items-start justify-between">
          <div className="space-y-1.5 md:space-y-2 flex-1">
            <Skeleton className="w-24 md:w-32 h-3 md:h-4" />
            <Skeleton className="w-36 md:w-48 h-4 md:h-5" />
            <Skeleton className="w-full h-3 md:h-4" />
          </div>
          <Skeleton className="w-4 h-4 md:w-5 md:h-5 shrink-0" />
        </div>
      </div>
    ))}
  </div>
);

const DrawerContentSkeleton = () => (
  <div className="space-y-4 md:space-y-6">
    <div>
      <Skeleton className="w-20 md:w-24 h-4 md:h-5 mb-2" />
      <Skeleton className="w-full h-3 md:h-4" />
    </div>
    <div>
      <Skeleton className="w-16 md:w-20 h-4 md:h-5 mb-2 md:mb-3" />
      <div className="space-y-2">
        <Skeleton className="w-full h-7 md:h-8 rounded-full" />
        <Skeleton className="w-4/5 h-7 md:h-8 rounded-full" />
      </div>
    </div>
  </div>
);

const CareerPath = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedAnalysis, setSelectedAnalysis] = useState<typeof analysisHistory[0] | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const isMobile = useIsMobile();

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1200);
    return () => clearTimeout(timer);
  }, []);

  const handleAnalysisClick = (analysis: typeof analysisHistory[0]) => {
    setDrawerLoading(true);
    setSelectedAnalysis(analysis);
    setDrawerOpen(true);
    setTimeout(() => setDrawerLoading(false), 800);
  };

  const handleDownload = () => {
    setIsDownloading(true);
    setTimeout(() => setIsDownloading(false), 1500);
  };


  return (
    <LoginRequired>
      <div className="container py-6 md:py-8 animate-fade-in max-w-full overflow-x-hidden">
        {/* Page Header */}
        <div className="text-center mb-6 md:mb-8">
          <div className="inline-flex items-center justify-center h-14 w-14 md:h-16 md:w-16 rounded-full bg-primary/10 mb-3 md:mb-4">
            <Map className="h-7 w-7 md:h-8 md:w-8 text-primary" />
          </div>
          <h1 className="text-2xl md:text-3xl font-bold mb-1.5 md:mb-2">職涯地圖</h1>
          <p className="text-muted-foreground text-sm md:text-base">掌握您的職涯發展藍圖與歷史分析紀錄</p>
        </div>



        {/* Main Content - Full Width */}
        <div className="w-full">
          <main className="space-y-6 md:space-y-8 overflow-hidden">
            {/* Career Ladder Section */}
            <section className="overflow-hidden">
              <CareerLadder isLoading={isLoading} />
            </section>

            {/* Analysis History Section */}
            <section>
              <Card>
                <CardHeader className="pb-2 md:pb-4">
                  <CardTitle className="flex items-center gap-2 text-base md:text-lg">
                    <FileText className="h-4 w-4 md:h-5 md:w-5 text-primary" />
                    職涯分析結果
                  </CardTitle>
                  <CardDescription className="text-xs md:text-sm">
                    點擊查看詳細分析內容，可下載完整報告
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <AnalysisListSkeleton />
                  ) : (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.5, delay: 0.2 }}
                      className="space-y-3 md:space-y-4"
                    >
                      {analysisHistory.map((analysis, index) => (
                        <motion.div
                          key={analysis.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className="p-3 md:p-4 rounded-lg border hover:bg-muted/50 transition-colors cursor-pointer group"
                          onClick={() => handleAnalysisClick(analysis)}
                        >
                          <div className="flex items-start justify-between">
                            <div className="space-y-0.5 md:space-y-1 flex-1 min-w-0">
                              <div className="flex items-center gap-1.5 md:gap-2 text-xs md:text-sm text-muted-foreground">
                                <Calendar className="h-3.5 w-3.5 md:h-4 md:w-4 shrink-0" />
                                {analysis.date}
                              </div>
                              <h4 className="font-semibold text-sm md:text-base truncate">{analysis.title}</h4>
                              <p className="text-xs md:text-sm text-muted-foreground line-clamp-2">{analysis.summary}</p>
                            </div>
                            <ChevronRight className="h-4 w-4 md:h-5 md:w-5 text-muted-foreground group-hover:text-primary transition-colors mt-1 shrink-0 ml-2" />
                          </div>
                        </motion.div>
                      ))}
                    </motion.div>
                  )}
                </CardContent>
              </Card>
            </section>
          </main>
        </div>

        {/* Right Drawer */}
        <RightDrawer
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          title={selectedAnalysis?.title || ''}
          subtitle={selectedAnalysis?.date || ''}
          showDownload
          onDownload={handleDownload}
          isDownloading={isDownloading}
        >
          {drawerLoading ? (
            <DrawerContentSkeleton />
          ) : selectedAnalysis && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4 md:space-y-6">
              <div>
                <h4 className="font-medium mb-1.5 md:mb-2 text-sm md:text-base">分析摘要</h4>
                <p className="text-muted-foreground text-xs md:text-sm">{selectedAnalysis.summary}</p>
              </div>
              <div>
                <h4 className="font-medium mb-2 md:mb-3 flex items-center gap-1.5 md:gap-2 text-sm md:text-base">
                  <Star className="h-3.5 w-3.5 md:h-4 md:w-4 text-primary" />
                  優勢亮點
                </h4>
                <div className="flex flex-wrap gap-1.5 md:gap-2">
                  {selectedAnalysis.content.strengths.map((item, idx) => (
                    <span key={idx} className="px-2.5 py-1 md:px-3 md:py-1.5 bg-primary/10 text-primary rounded-full text-xs md:text-sm">{item}</span>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="font-medium mb-2 md:mb-3 text-sm md:text-base">待加強項目</h4>
                <ul className="space-y-1.5 md:space-y-2">
                  {selectedAnalysis.content.improvements.map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-xs md:text-sm text-muted-foreground">
                      <span className="h-1.5 w-1.5 rounded-full bg-amber-500 mt-1.5 md:mt-2 shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="font-medium mb-2 md:mb-3 text-sm md:text-base">發展建議</h4>
                <ul className="space-y-1.5 md:space-y-2">
                  {selectedAnalysis.content.recommendations.map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-xs md:text-sm text-muted-foreground">
                      <span className="h-1.5 w-1.5 rounded-full bg-primary mt-1.5 md:mt-2 shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </motion.div>
          )}
        </RightDrawer>
      </div>
    </LoginRequired>
  );
};

export default CareerPath;

import { useState } from 'react';
import { FileText, Download, Trash2, Eye } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import RightDrawer from '@/components/panels/RightDrawer';
import { motion } from 'framer-motion';
import LoginRequired from '@/components/gatekeeper/LoginRequired';
import { useResumes, type ResumeItem } from '@/contexts/ResumeContext';

const MyResumes = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedResume, setSelectedResume] = useState<ResumeItem | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const { resumes } = useResumes();

  const handlePreview = (resume: ResumeItem) => {
    setSelectedResume(resume);
    setDrawerOpen(true);
  };

  const handleDownload = async () => {
    if (!selectedResume) return;
    
    setIsDownloading(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const blob = new Blob([selectedResume.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = selectedResume.name;
    a.click();
    URL.revokeObjectURL(url);
    
    setIsDownloading(false);
  };

  return (
    <LoginRequired>
      <div className="container py-8 md:py-12 animate-fade-in">
        <div className="text-center mb-8 md:mb-12">
          <div className="inline-flex items-center justify-center h-14 w-14 md:h-16 md:w-16 rounded-full bg-primary/10 mb-4 md:mb-6">
            <FileText className="h-7 w-7 md:h-8 md:w-8 text-primary" />
          </div>
          <h1 className="text-2xl md:text-3xl font-bold mb-3 md:mb-4">我的履歷</h1>
          <p className="text-muted-foreground text-sm md:text-base max-w-2xl mx-auto">
            管理您已上傳的履歷檔案
          </p>
        </div>

        <div className="max-w-3xl mx-auto">
          <div className="flex justify-end mb-4 md:mb-6">
            <Link to="/member/upload-resume">
              <Button className="gradient-primary text-sm md:text-base">上傳新履歷</Button>
            </Link>
          </div>

          <div className="space-y-3 md:space-y-4">
            {resumes.map((resume, index) => (
              <motion.div
                key={resume.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="hover:shadow-medium transition-shadow">
                  <CardContent className="flex flex-col sm:flex-row items-start sm:items-center justify-between py-3 md:py-4 gap-3">
                    <div className="flex items-center gap-3 md:gap-4 w-full sm:w-auto">
                      <div className="h-9 w-9 md:h-10 md:w-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                        <FileText className="h-4 w-4 md:h-5 md:w-5 text-primary" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="font-medium text-sm md:text-base truncate">{resume.name}</p>
                        <p className="text-xs md:text-sm text-muted-foreground">更新於 {resume.updatedAt}</p>
                      </div>
                    </div>
                    <div className="flex gap-1 md:gap-2 w-full sm:w-auto justify-end">
                      <Button variant="ghost" size="icon" onClick={() => handlePreview(resume)} className="h-8 w-8 md:h-9 md:w-9">
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-8 w-8 md:h-9 md:w-9">
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" className="text-destructive h-8 w-8 md:h-9 md:w-9">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>

        <RightDrawer
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          title="履歷預覽"
          subtitle={selectedResume?.name}
          showDownload
          onDownload={handleDownload}
          isDownloading={isDownloading}
        >
          {selectedResume && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="whitespace-pre-wrap text-xs md:text-sm leading-relaxed bg-muted/30 p-3 md:p-4 rounded-lg font-mono"
            >
              {selectedResume.content}
            </motion.div>
          )}
        </RightDrawer>
      </div>
    </LoginRequired>
  );
};

export default MyResumes;

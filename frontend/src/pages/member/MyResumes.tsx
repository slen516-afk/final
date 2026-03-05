import { useState, useEffect } from 'react';
import { FileText, Download, Trash2, Eye, AlertCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import RightDrawer from '@/components/panels/RightDrawer';
import { motion, AnimatePresence } from 'framer-motion';
import LoginRequired from '@/components/gatekeeper/LoginRequired';

// 引入 Supabase client
import { supabase } from '@/utils/supabaseClient';
// 引入 API 函式
import { getResumes, type ResumeItem } from '@/mocks/resumes';

const MyResumes = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedResume, setSelectedResume] = useState<ResumeItem | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);

  const [resumes, setResumes] = useState<ResumeItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // 👉 新增：用來控制「自訂刪除彈窗」的狀態
  const [resumeToDelete, setResumeToDelete] = useState<ResumeItem | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const fetchCloudData = async () => {
      setIsLoading(true);
      const data = await getResumes();
      setResumes(data);
      setIsLoading(false);
    };
    fetchCloudData();
  }, []);

  const handlePreview = async (resume: ResumeItem) => {
    setSelectedResume({ ...resume, content: '⏳ 正在為您讀取履歷詳細內容...\n請稍候...' });
    setDrawerOpen(true);

    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      const mockDetailText = `【模擬的詳細履歷內容】\n\n這份資料是從遠端動態加載回來的！\n\n📌 履歷名稱：${resume.name}\n🕒 建立時間：${resume.updatedAt}\n\n這裡未來可以換成從你的 Flask 後端分析出來的 JSON，或者是你存在 Storage 的完整自傳與經歷。`;
      setSelectedResume((prev) => prev ? { ...prev, content: mockDetailText } : null);
    } catch (err) {
      setSelectedResume((prev) => prev ? { ...prev, content: '❌ 無法載入詳細資料' } : null);
    }
  };

  // 🗑️ 按下垃圾桶時，不直接刪除，而是「打開自訂彈窗」
  const handleDeleteClick = (resume: ResumeItem) => {
    setResumeToDelete(resume); // 把這筆資料存進狀態，彈窗就會跳出來
  };

  // ⚠️ 彈窗裡的「確定刪除」按下去後，才執行這段真實刪除邏輯
  const confirmDelete = async () => {
    if (!resumeToDelete) return;

    setIsDeleting(true); // 按鈕顯示載入中
    try {
      const tableName = resumeToDelete.sourceType === 'RESUME' ? 'resume' : 'resume_optimization';
      const idField = resumeToDelete.sourceType === 'RESUME' ? 'resume_id' : 'optimization_id';

      const { error } = await supabase
        .from(tableName)
        .delete()
        .eq(idField, resumeToDelete.id);

      if (error) throw error;

      // 成功刪除後，即時更新前端畫面
      setResumes((prevResumes) =>
        prevResumes.filter((r) => !(r.id === resumeToDelete.id && r.sourceType === resumeToDelete.sourceType))
      );

      // 關閉彈窗
      setResumeToDelete(null);

    } catch (err) {
      console.error('❌ Supabase 刪除報錯:', err);
      alert('刪除失敗！請檢查資料庫權限或網路連線。');
    } finally {
      setIsDeleting(false); // 恢復按鈕狀態
    }
  };

  const handleDownload = async () => {
    if (!selectedResume) return;
    setIsDownloading(true);
    try {
      const { exportHtmlToPdf, buildResumeContentHtml } = await import('@/utils/pdfExport');
      await exportHtmlToPdf({
        filename: `${selectedResume.name.replace(/\.[^.]+$/, '')}.pdf`,
        htmlContent: buildResumeContentHtml(selectedResume.name, selectedResume.content),
      });
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <LoginRequired>
      <div className="container py-8 md:py-12 animate-fade-in relative">
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

          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              <p>正在從雲端載入履歷中...</p>
            </div>
          ) : (
            <div className="space-y-3 md:space-y-4">
              <AnimatePresence>
                {resumes.map((resume, index) => (
                  <motion.div
                    key={`${resume.sourceType}-${resume.id}`}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.2 } }} // 被刪除時的縮小消失動畫
                    transition={{ delay: index * 0.1 }}
                  >
                    <Card className="hover:shadow-medium transition-shadow">
                      <CardContent className="flex flex-col sm:flex-row items-start sm:items-center justify-between py-3 md:py-4 gap-3">
                        <div className="flex items-center gap-3 md:gap-4 w-full sm:w-auto">
                          <div className="h-9 w-9 md:h-10 md:w-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                            <FileText className="h-4 w-4 md:h-5 md:w-5 text-primary" />
                          </div>
                          <div className="min-w-0 flex-1">
                            <p className="font-medium text-sm md:text-base truncate">
                              {resume.name}
                              <span className="ml-2 text-xs text-primary/60">
                                ({resume.sourceType === 'OPTIMIZATION' ? '已優化' : '一般'})
                              </span>
                            </p>
                            <p className="text-xs md:text-sm text-muted-foreground">更新於 {resume.updatedAt}</p>
                          </div>
                        </div>

                        <div className="flex gap-1 md:gap-2 w-full sm:w-auto justify-end">
                          <Button variant="ghost" size="icon" onClick={() => handlePreview(resume)} className="h-8 w-8 md:h-9 md:w-9">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon" onClick={handleDownload} className="h-8 w-8 md:h-9 md:w-9">
                            <Download className="h-4 w-4" />
                          </Button>
                          {/* 👉 改成呼叫 handleDeleteClick */}
                          <Button
                            variant="ghost"
                            size="icon"
                            className="text-destructive hover:bg-destructive/10 h-8 w-8 md:h-9 md:w-9"
                            onClick={() => handleDeleteClick(resume)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </AnimatePresence>

              {resumes.length === 0 && (
                <div className="text-center py-8 text-muted-foreground bg-muted/30 rounded-lg">
                  <p>您還沒有上傳任何履歷喔！</p>
                </div>
              )}
            </div>
          )}
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

        {/* ✨ 超美自訂刪除確認彈窗 ✨ */}
        <AnimatePresence>
          {resumeToDelete && (
            <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm px-4">
              <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 10 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 10 }}
                className="bg-background rounded-xl shadow-xl max-w-sm w-full p-6 border border-border"
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="h-10 w-10 rounded-full bg-destructive/10 flex items-center justify-center shrink-0">
                    <AlertCircle className="h-5 w-5 text-destructive" />
                  </div>
                  <h3 className="text-lg font-bold text-foreground">確定要刪除？</h3>
                </div>

                <p className="text-muted-foreground text-sm mb-6 leading-relaxed">
                  您即將徹底刪除「<span className="font-semibold text-foreground">{resumeToDelete.name}</span>」。<br />此動作無法復原，請確認是否繼續？
                </p>

                <div className="flex justify-end gap-3">
                  <Button
                    variant="outline"
                    onClick={() => setResumeToDelete(null)}
                    disabled={isDeleting}
                    className="w-20"
                  >
                    取消
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={confirmDelete}
                    disabled={isDeleting}
                    className="w-24"
                  >
                    {isDeleting ? '刪除中...' : '確定刪除'}
                  </Button>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>

      </div>
    </LoginRequired>
  );
};

export default MyResumes;
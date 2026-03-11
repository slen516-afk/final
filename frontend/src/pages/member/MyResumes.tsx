import { useState, useEffect } from 'react';
import { FileText, Download, Trash2, Eye, Loader2, AlertTriangle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import LoginRequired from '@/components/gatekeeper/LoginRequired';
import { useAppState } from '@/contexts/AppContext';
import apiClient from '@/services/api';

const MyResumes = () => {
  const { user } = useAppState();
  const realUserId = user?.user_id;

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedResume, setSelectedResume] = useState<any | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);

  const [resumes, setResumes] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // 🌟 控制漂亮彈窗的 State
  const [resumeToDelete, setResumeToDelete] = useState<any | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    if (realUserId) {
      setIsLoading(true);
      loadResumes();
    } else {
      setIsLoading(false);
    }
  }, [realUserId]);

  const loadResumes = async () => {
    try {
      const response = await apiClient.get(`/resume_process/list/${realUserId}`);

      let finalData: any[] = [];
      const rawData = response.data;

      if (Array.isArray(rawData)) {
        finalData = rawData;
      } else if (rawData?.data && Array.isArray(rawData.data)) {
        finalData = rawData.data;
      } else if (rawData?.resumes && Array.isArray(rawData.resumes)) {
        finalData = rawData.resumes;
      }

      setResumes(finalData);
    } catch (err) {
      console.error('❌ [我的履歷] 載入失敗:', err);
      setResumes([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePreview = (resume: any) => {
    const content = typeof resume.structured_data === 'string'
      ? resume.structured_data
      : JSON.stringify(resume.structured_data, null, 2);

    setSelectedResume({
      ...resume,
      content: content
    });
    setDrawerOpen(true);
  };

  // 🌟 1. 點擊卡片上的垃圾桶時，只負責開啟漂亮彈窗
  const handleDeleteClick = (resume: any) => {
    setResumeToDelete(resume);
    setShowDeleteModal(true);
  };

  // 🌟 在彈窗按下「確定刪除」時：
  const confirmDelete = async () => {
    if (!resumeToDelete) return;
    setIsDeleting(true);

    try {
      // 🛑 絕對不要在這裡 split！直接把原本的 ID (例如 129 或是 129_opt_1) 原封不動傳過去！
      const targetId = resumeToDelete.resume_id;
      console.log(`🚀 [前端] 準備發送刪除請求，送出的完整 ID 是: ${targetId}`);

      // 呼叫 API
      const response = await apiClient.delete(`/resume_process/delete/${targetId}`);

      const resData = response.data || response;
      if (response.status === 200 || resData.status === 'success') {
        setShowDeleteModal(false);
        await loadResumes(); // 畫面重整
      } else {
        throw new Error(resData.message || '未知錯誤');
      }
    } catch (err) {
      console.error('❌ 刪除失敗詳細原因:', err);
      alert('刪除失敗，請打開 F12 Console 查看原因！');
    } finally {
      setIsDeleting(false);
      if (!showDeleteModal) setResumeToDelete(null);
    }
  };

  const handleDownload = async () => {
    if (!selectedResume) return;
    setIsDownloading(true);
    try {
      const { exportHtmlToPdf, buildResumeContentHtml } = await import('@/utils/pdfExport');
      await exportHtmlToPdf({
        filename: `${selectedResume.resume_name}.pdf`,
        htmlContent: buildResumeContentHtml(selectedResume.resume_name, selectedResume.content),
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
            管理您已上傳的履歷檔案 (User ID: {realUserId || '未登入'})
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
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-2" />
              <p>正在從資料庫載入您的履歷...</p>
            </div>
          ) : (
            <div className="space-y-3 md:space-y-4">
              <AnimatePresence>
                {resumes.map((resume) => (
                  <motion.div
                    key={resume.resume_id}
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0, marginBottom: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Card className="hover:shadow-md transition-shadow">
                      <CardContent className="flex flex-col sm:flex-row items-start sm:items-center justify-between py-3 md:py-4 gap-3">

                        <div className="flex items-center gap-3 md:gap-4 w-full sm:w-auto">
                          <div className="h-9 w-9 md:h-10 md:w-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                            <FileText className="h-4 w-4 md:h-5 md:w-5 text-primary" />
                          </div>
                          <div className="min-w-0 flex-1">
                            <p className="font-medium text-sm md:text-base truncate">
                              {resume.is_optimized ? `${resume.resume_name}` : resume.resume_name || resume.name || '未命名履歷'}
                              <span className="ml-2 text-[10px] px-1.5 py-0.5 bg-primary/10 text-primary rounded capitalize">
                                {resume.resume_type === 'OPTIMIZATION' || resume.is_optimized ? '優化版' : '原版'}
                              </span>
                            </p>
                            <p className="text-xs text-muted-foreground mt-0.5">
                              建立於 {resume.created_at ? new Date(resume.created_at).toLocaleString('zh-TW') : '剛剛'}
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-1 sm:gap-2 w-full sm:w-auto mt-3 sm:mt-0 justify-end sm:justify-start">
                          <Button variant="ghost" size="sm" className="h-8 md:h-9 px-2 md:px-3 text-muted-foreground hover:text-primary transition-colors" onClick={() => handlePreview(resume)}>
                            <Eye className="h-4 w-4 md:mr-1.5" />
                            <span className="hidden md:inline">預覽</span>
                          </Button>

                          <Button variant="ghost" size="sm" className="h-8 md:h-9 px-2 md:px-3 text-muted-foreground hover:text-primary transition-colors" onClick={() => { setSelectedResume(resume); setTimeout(handleDownload, 0); }} disabled={isDownloading && selectedResume?.resume_id === resume.resume_id}>
                            {isDownloading && selectedResume?.resume_id === resume.resume_id ? <Loader2 className="h-4 w-4 animate-spin md:mr-1.5" /> : <Download className="h-4 w-4 md:mr-1.5" />}
                            <span className="hidden md:inline">下載</span>
                          </Button>

                          <Button variant="ghost" size="sm" className="h-8 md:h-9 px-2 md:px-3 text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors" onClick={() => handleDeleteClick(resume)}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </AnimatePresence>

              {resumes.length === 0 && (
                <div className="text-center py-12 text-muted-foreground bg-muted/20 rounded-xl border-2 border-dashed">
                  <p>您目前還沒有任何履歷資料</p>
                  <Link to="/member/upload-resume" className="text-primary hover:underline text-sm mt-2 block">
                    立即去上傳第一份履歷吧！
                  </Link>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* 🌟 美型自訂刪除確認彈窗 */}
      <AnimatePresence>
        {showDeleteModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/50 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-xl shadow-lg w-full max-w-md overflow-hidden"
            >
              <div className="p-6">
                <div className="flex items-center gap-3 text-red-600 mb-4">
                  <div className="p-2 bg-red-100 rounded-full">
                    <AlertTriangle size={24} />
                  </div>
                  <h3 className="text-lg font-bold">確定要刪除履歷嗎？</h3>
                </div>
                <p className="text-gray-600 mb-2">
                  您即將刪除 <span className="font-bold text-gray-900">{resumeToDelete?.resume_name || '此份履歷'}</span>。
                </p>
                <p className="text-sm text-gray-500">
                  ⚠️ 刪除原版履歷將會一併清空與其相關的「AI 優化紀錄」，此動作無法復原。
                </p>
              </div>
              <div className="bg-gray-50 px-6 py-4 flex justify-end gap-3">
                <Button variant="outline" onClick={() => setShowDeleteModal(false)} disabled={isDeleting}>
                  取消
                </Button>
                <Button variant="destructive" onClick={confirmDelete} disabled={isDeleting}>
                  {isDeleting ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> 刪除中</> : '確定刪除'}
                </Button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </LoginRequired>
  );
};

export default MyResumes;
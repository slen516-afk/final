import { useState, useEffect } from 'react';
import { FileText, Download, Trash2, Eye, AlertCircle, Loader2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import RightDrawer from '@/components/panels/RightDrawer';
import { motion, AnimatePresence } from 'framer-motion';
import LoginRequired from '@/components/gatekeeper/LoginRequired';
import { supabase } from '@/utils/supabaseClient';
// 🌟 1. 引入 AppContext 拿到真實 user_id
import { useAppState } from '@/contexts/AppContext';
// 🌟 2. 改為引入真實的 API 函式 (稍後在下一步定義)
import apiClient, { fetchUserResumesAPI } from '@/services/api';

const MyResumes = () => {
  const { user, setIsPersonalityQuizDone } = useAppState();
  // 🌟 3. 取得目前登入者的真實 ID
  const realUserId = user?.user_id;
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedResume, setSelectedResume] = useState<any | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);

  const [resumes, setResumes] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const [resumeToDelete, setResumeToDelete] = useState<any | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // 🌟 4. 當 realUserId 變化時才抓資料
  // 🌟 4. 當 realUserId 變化時才抓資料
  useEffect(() => {
    if (realUserId) {
      setIsLoading(true); // 💡 確保每次抓取前，畫面一定會先轉圈圈
      loadResumes();
    } else {
      setIsLoading(false);
    }
  }, [realUserId]);

  const loadResumes = async () => {
    try {
      console.log(`🚀 [我的履歷] 開始向後端請求 ID: ${realUserId} 的資料...`);

      // 💡 暴力破解法：直接用 apiClient 呼叫，不經過原本會亂丟資料的舊函式
      const response = await apiClient.get(`/resume_process/list/${realUserId}`);
      console.log("📥 [我的履歷] 後端回傳的原始資料:", response.data);

      // 💡 智慧拆包邏輯：不管 Flask 後端包裝成什麼樣子，我們都把它挖出來！
      let finalData: any[] = [];
      const rawData = response.data;

      if (Array.isArray(rawData)) {
        finalData = rawData;
      } else if (rawData?.data && Array.isArray(rawData.data)) {
        finalData = rawData.data;
      } else if (rawData?.resumes && Array.isArray(rawData.resumes)) {
        finalData = rawData.resumes;
      }

      console.log("✅ [我的履歷] 最終要渲染在畫面的陣列:", finalData);
      setResumes(finalData);

    } catch (err) {
      console.error('❌ [我的履歷] 載入失敗:', err);
      setResumes([]); // 失敗就給空陣列
    } finally {
      setIsLoading(false);
    }
  };

  const handlePreview = (resume: any) => {
    // 🌟 6. 預覽時直接顯示 structured_data 裡的內容
    const content = typeof resume.structured_data === 'string'
      ? resume.structured_data
      : JSON.stringify(resume.structured_data, null, 2);

    setSelectedResume({
      ...resume,
      content: content
    });
    setDrawerOpen(true);
  };

  const handleDeleteClick = (resume: any) => {
    setResumeToDelete(resume);
  };

  const confirmDelete = async () => {
    if (!resumeToDelete) return;

    setIsDeleting(true);
    try {
      // 🌟 7. 根據資料庫實體欄位刪除 (resume_id)
      const { error } = await supabase
        .from('resume')
        .delete()
        .eq('resume_id', resumeToDelete.resume_id);

      if (error) throw error;

      setResumes((prev) => prev.filter((r) => r.resume_id !== resumeToDelete.resume_id));
      setResumeToDelete(null);
    } catch (err) {
      console.error('刪除失敗:', err);
      alert('刪除失敗！');
    } finally {
      setIsDeleting(false);
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
                {/* 找到 resumes.map 的地方，修改顯示欄位 */}
                {resumes.map((resume, index) => (
                  <motion.div key={resume.resume_id}>
                    <Card className="hover:shadow-md transition-shadow">
                      <CardContent className="flex flex-col sm:flex-row items-start sm:items-center justify-between py-3 md:py-4 gap-3">
                        <div className="flex items-center gap-3 md:gap-4 w-full sm:w-auto">
                          <div className="h-9 w-9 md:h-10 md:w-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                            <FileText className="h-4 w-4 md:h-5 md:w-5 text-primary" />
                          </div>
                          <div className="min-w-0 flex-1">
                            <p className="font-medium text-sm md:text-base truncate">
                              {/* 🌟 防呆：如果沒有 resume_name，就找 name，再沒有就顯示未命名 */}
                              {resume.resume_name || resume.name || '未命名履歷'}

                              <span className="ml-2 text-[10px] px-1.5 py-0.5 bg-primary/10 text-primary rounded capitalize">
                                {resume.resume_type || '一般'}
                              </span>
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {/* 🌟 防呆：確保有時間資料才轉換，不然就顯示剛剛 */}
                              建立於 {resume.created_at ? new Date(resume.created_at).toLocaleString('zh-TW') : '剛剛'}
                            </p>
                          </div>
                        </div>
                        {/* ... 按鈕部分保持不變 ... */}
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

        {/* 預覽與彈窗邏輯維持不變... */}
      </div>
    </LoginRequired>
  );
};

export default MyResumes;
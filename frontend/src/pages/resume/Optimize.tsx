import { useState, useEffect, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Download, Edit3, Save, RotateCcw, Palette, ChevronRight, Briefcase, GraduationCap, Mail, Phone, Globe, Award, Languages, User, Star, Sparkles, Check, ChevronLeft, BookOpen, ArrowLeft, Loader2, Linkedin, FolderOpen, Code, MapPin, ShieldCheck, ExternalLink, MoreHorizontal, CheckCircle, AlertTriangle, Target, ArrowRight, ListChecks } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { AILoadingSpinner, AnalysisSkeleton } from '@/components/loading/LoadingStates';
import { useAppState } from '@/contexts/AppContext';
import LoginRequired from '@/components/gatekeeper/LoginRequired';
import AlertModal from '@/components/modals/AlertModal';
import { motion, AnimatePresence } from 'framer-motion';
import { templateThumbnailComponents } from '@/components/resume/TemplateThumbnails';
import RightDrawer from '@/components/panels/RightDrawer';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import logoCat from '@/assets/logocat.png'; // 請確認路徑是否正確

// ==========================================
// 🌟 型別與常數定義
// ==========================================
type Phase = 'initial' | 'analyzing' | 'suggestions' | 'templates' | 'generating' | 'result';

interface ThemeColors {
  name: string;
  main: string;
  secondary: string;
  accent: string;
  text: string;
}

const TEMPLATE_THEMES: Record<string, ThemeColors[]> = {
  corporate: [
    { name: '深海藍經典', main: '#1F3A5F', secondary: '#4A6FA5', accent: '#C8A951', text: '#2B2B2B' },
    { name: '石墨灰商務', main: '#2E2E2E', secondary: '#5A5A5A', accent: '#2E7D73', text: '#1A1A1A' },
    { name: '酒紅權威', main: '#6A1B2E', secondary: '#A63D40', accent: '#E9C46A', text: '#333333' },
    { name: '深綠金融系', main: '#1B4332', secondary: '#2D6A4F', accent: '#D8F3DC', text: '#2B2B2B' },
  ],
  modern: [
    { name: '科技藍', main: '#2563EB', secondary: '#1E3A8A', accent: '#60A5FA', text: '#111827' },
    { name: '冷灰＋電光綠', main: '#374151', secondary: '#6B7280', accent: '#10B981', text: '#111111' },
    { name: '黑白極簡', main: '#111111', secondary: '#E5E7EB', accent: '#6366F1', text: '#000000' },
    { name: '靜謐藍灰', main: '#334155', secondary: '#94A3B8', accent: '#22D3EE', text: '#1E293B' },
  ],
  creative: [
    { name: '莫蘭迪粉橘', main: '#E07A5F', secondary: '#C9604A', accent: '#E8A87C', text: '#2B2B2B' },
    { name: '紫藍創意系', main: '#6D28D9', secondary: '#5320A8', accent: '#9F6CEE', text: '#1F1F1F' },
    { name: '活力橘藍對比', main: '#F97316', secondary: '#D95F0E', accent: '#FDBA74', text: '#222222' },
    { name: '黑底霓虹', main: '#0F172A', secondary: '#1E293B', accent: '#475569', text: '#2B2B2B' },
  ],
};

const originalResumeFields = [
  { key: 'name', label: '姓名', icon: User, multiline: false, optional: false },
  { key: 'phone', label: '聯絡電話', icon: Phone, multiline: false, optional: false },
  { key: 'email', label: '聯絡信箱', icon: Mail, multiline: false, optional: false },
  { key: 'address', label: '通訊地址', icon: MapPin, multiline: false, optional: true },
  { key: 'education', label: '教育背景', icon: GraduationCap, multiline: true, optional: false },
  { key: 'experience', label: '工作經歷', icon: Briefcase, multiline: true, optional: false },
  { key: 'languages', label: '語言能力', icon: Languages, multiline: false, optional: false },
  { key: 'skills', label: '技能專長', icon: Star, multiline: false, optional: false },
  { key: 'certifications', label: '證照與專案成就', icon: ShieldCheck, multiline: true, optional: true },
  { key: 'portfolio', label: '作品集', icon: ExternalLink, multiline: true, optional: true },
  { key: 'autobiography', label: '自傳', icon: FileText, multiline: true, optional: true },
  { key: 'other', label: '其他', icon: MoreHorizontal, multiline: true, optional: true },
] as const;

const templates = [
  {
    id: 'corporate',
    name: '經典專業型',
    subtitle: 'The Corporate Classic',
    description: '強調邏輯性與權威感，適合金融、法律、管理顧問或大型企業',
    features: ['單欄式佈局', '襯線體設計', 'ATS 友善度最高'],
    icon: Briefcase,
  },
  {
    id: 'modern',
    name: '現代極簡型',
    subtitle: 'Modern Minimalist',
    description: '清晰的資訊層級，適合軟體工程、科技產業或新創公司',
    features: ['雙欄式 (3:7)', '技能進度條', '大量留白設計'],
    icon: Star,
  },
  {
    id: 'creative',
    name: '創意視覺型',
    subtitle: 'Creative Portfolio',
    description: '個人品牌展現，專為設計、行銷、公關或媒體從業者設計',
    features: ['非對稱設計', '莫蘭迪色系', '卡片式作品集'],
    icon: Sparkles,
  },
];

const templateSwatches: Record<string, string[]> = {
  corporate: ['#1F3A5F', '#2E2E2E', '#6A1B2E', '#1B4332'],
  modern: ['#2563EB', '#374151', '#111111', '#334155'],
  creative: ['#E07A5F', '#6D28D9', '#F97316', '#0F172A'],
};

// ==========================================
// 🌟 核心新增：動態診斷生成器(Dynamic Diagnosis Generator)
// ==========================================
const generateDynamicDiagnosis = (data: any) => {
  const expSnippet = data.experience && data.experience.length > 10
    ? data.experience.slice(0, 60) + "..."
    : "缺乏具體的工作經歷描述";

  const skillsSnippet = data.skills && data.skills.length > 5
    ? data.skills.slice(0, 40) + "..."
    : "尚未填寫完整的技能清單";

  const eduSnippet = data.education ? data.education.split('\n')[0] : "相關學歷背景";

  return {
    candidate_positioning: `以「${data.name}」目前的背景來看，具備${eduSnippet}的基礎，並擁有相關的實務經歷。若目標是往資深職位發展，在「技術影響力」與「專案量化成效」上還有凸顯的空間。`,
    target_role_gap_summary: `目前的履歷雖然列出了基本經歷與技能，但在「量化成果（如：提升多少效率）」的展現上稍顯薄弱。建議強化STAR敘事法，將會大幅提升ATS系統與HR的篩選通過率。`,
    overall_strengths: [
      `具備清晰的教育背景(${eduSnippet.slice(0, 20)}...)`,
      `已羅列出專業技能(${skillsSnippet.slice(0, 15)}...)，具備發展潛力`,
      `經歷描述具備基礎框架，段落分明`
    ],
    overall_weaknesses: [
      "工作經歷描述過於偏向「職責條列」，缺乏STAR結構化敘事",
      "技能列表僅為名詞堆疊，缺乏「熟練度分級」與「實際應用場景」",
      "缺少個人價值主張（Summary），難以在第一時間抓住面試官眼球"
    ],
    critical_issues: [
      {
        section: "工作經歷",
        severity: "嚴重扣分",
        original_text: expSnippet,
        issue_reason: "使用了過於平鋪直敘的語氣，未描述專案規模、面臨的挑戰與最終數據成果。面試官無法據此評估您的實際戰力。",
        improvement_direction: "改用「強動詞開頭+量化指標」，例如：「主導/參與XXX專案，運用XXX技術重構架構，使效能提升40%」"
      },
      {
        section: "技能專長",
        severity: "明顯扣分",
        original_text: skillsSnippet,
        issue_reason: "技能以單字平鋪列出，無法區分「核心專長」與「輔助技能」。雖然能命中ATS關鍵字，但無法展現技術深度。",
        improvement_direction: "建議分類呈現，例如：「核心技能：XXX (3年)、XXX (2年)」、「熟悉工具：XXX、XXX」"
      }
    ],
    recommended_next_actions: [
      "使用STAR法則重新撰寫每一段工作經歷，確保每項都有「量化成果」",
      "將技能專長依據重要性進行分類，並標註熟練度或年資",
      "在履歷最上方增加一段50字的「個人專業摘要(Summary)」",
      "針對心儀職缺的JD關鍵字，在履歷中增加對應描述以提升契合度"
    ]
  };
};

// ==========================================
// 🌟 主元件 Optimize
// ==========================================
const Optimize = () => {
  const navigate = useNavigate();
  const { user, isLoggedIn, avatarUrl } = useAppState();
  const realUserId = user?.user_id || user?.id;

  // 乾淨俐落！所有 useState 狀態集中在這裡
  const [phase, setPhase] = useState<Phase>('initial');
  const [realLatestResume, setRealLatestResume] = useState<any>(null);
  const [originalData, setOriginalData] = useState<any>({ name: '資料讀取中...' });
  const [editedOriginalData, setEditedOriginalData] = useState<any>({});
  const [resumeData, setResumeData] = useState<any>({});
  const [editedData, setEditedData] = useState<any>({});
  const [diagnosticResult, setDiagnosticResult] = useState<any>(null);

  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [selectedThemeIndex, setSelectedThemeIndex] = useState<number>(0);

  const [isLoadingDB, setIsLoadingDB] = useState(true);
  const [showAccessAlert, setShowAccessAlert] = useState(false);
  const [accessAlertMessage, setAccessAlertMessage] = useState('');

  // 編輯與儲存狀態
  const [isEditing, setIsEditing] = useState(false);
  const [editPhase, setEditPhase] = useState<'view' | 'edit'>('view');
  const [showSaveConfirm, setShowSaveConfirm] = useState(false);
  const [isEditSaved, setIsEditSaved] = useState(false);
  const [showSuggestionsDrawer, setShowSuggestionsDrawer] = useState(false);
  const [isTemplateSaved, setIsTemplateSaved] = useState(false);
  const [showTemplateSaveConfirm, setShowTemplateSaveConfirm] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [saveModalConfig, setSaveModalConfig] = useState({ type: 'success', title: '', message: '' });
  const [isDownloading, setIsDownloading] = useState(false);
  const resumeRef = useRef<HTMLDivElement>(null);

  // 1. 真實資料庫連線：抓取最新履歷
  useEffect(() => {
    const fetchRealDatabaseResume = async () => {
      if (!isLoggedIn || !realUserId) {
        setAccessAlertMessage('找不到使用者 ID，請重新登入');
        setShowAccessAlert(true);
        setIsLoadingDB(false);
        return;
      }

      try {
        const response = await fetch(`/api/resume_process/list/${realUserId}`);
        const result = await response.json();

        if (result.status === 'success' && result.data && result.data.length > 0) {
          const latest = result.data.sort((a: any, b: any) =>
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          )[0];

          console.log("✅[真實連線]從 Supabase 撈到的最新履歷:", latest);
          setRealLatestResume(latest);

          let raw = latest.resume_data || latest.structured_data || {};
          if (typeof raw === 'string') { try { raw = JSON.parse(raw); } catch { raw = {}; } }

          let flat: any = { ...raw };
          if (raw.data) Object.assign(flat, raw.data);
          if (raw.resume_data) Object.assign(flat, raw.resume_data);
          if (raw.normalized_data) {
            Object.assign(flat, raw.normalized_data);
            if (raw.normalized_data.contact) Object.assign(flat, raw.normalized_data.contact);
          }

          const safeStr = (v: any) => {
            if (!v) return '';
            if (typeof v === 'string') return v;
            if (Array.isArray(v)) {
              return v.map(i => {
                if (typeof i === 'string') return i;
                if (typeof i === 'object' && i !== null) {
                  // 特別處理語言物件 { language, proficiency }
                  if (i.language && i.proficiency) return `${i.language} (${i.proficiency})`;
                  // 其他物件則串接其值
                  return Object.values(i).join(' - ');
                }
                return String(i);
              }).join('\n');
            }
            if (typeof v === 'object' && v !== null) {
              return Object.values(v).join(' - ');
            }
            return String(v);
          };

          const mappedData = {
            name: safeStr(flat.name || flat.full_name || '未辨識'),
            email: safeStr(flat.email),
            phone: safeStr(flat.phone),
            education: safeStr(flat.education),
            experience: safeStr(flat.experience || flat.work_experience),
            skills: Array.isArray(flat.skills) ? flat.skills.join(', ') : safeStr(flat.skills),
            autobiography: safeStr(flat.autobiography || flat.summary || flat.bio),
            projects: safeStr(flat.projects || flat.portfolio),
            languages: safeStr(flat.languages),
            certifications: safeStr(flat.certifications),
            other: safeStr(flat.other),
            address: safeStr(flat.address || flat.addressDetail || flat.location),
          };

          const initialDataForEdit = {
            ...mappedData,
            linkedin: flat.linkedin || '',
            github: flat.github || '',
            professional_experience: mappedData.experience,
            core_skills: mappedData.skills,
            professional_summary: mappedData.autobiography,
          };

          setOriginalData(mappedData);
          setEditedOriginalData(mappedData);
          setResumeData(initialDataForEdit);
          setEditedData(initialDataForEdit);
        } else {
          setAccessAlertMessage('在資料庫中找不到您的履歷，請先上傳！');
          setShowAccessAlert(true);
        }
      } catch (error) {
        console.error("資料庫連線失敗:", error);
      } finally {
        setIsLoadingDB(false);
      }
    };

    fetchRealDatabaseResume();
  }, [realUserId, isLoggedIn]);

  // 2. 呼叫後端 CrewAI 分析
  const handleStartOptimize = async () => {
    setPhase('analyzing');
    try {
      const payload = { user_id: realUserId, resume_data: originalData };
      const response = await fetch('/api/resume_process/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await response.json();
      if (response.ok && result.data) {
        setDiagnosticResult(result.data);
      } else {
        throw new Error(result.error || "AI分析回傳格式錯誤");
      }
    } catch (error) {
      console.error("🚨AI評估API呼叫失敗，啟用本地備援:", error);
      const fallbackReport = generateDynamicDiagnosis(originalData);
      setDiagnosticResult(fallbackReport);
    }
    setPhase('suggestions');
  };

  // 3. 呼叫 AI 全文優化生成
  const handleGenerateOptimizedResume = async (templateId: string) => {
    setSelectedTemplate(templateId);
    setSelectedThemeIndex(0);
    setPhase('generating');
    try {
      const payload = { user_id: realUserId, resume_data: originalData };
      const response = await fetch('/api/resume_process/optimize/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await response.json();
      if (response.ok && result.data) {
        setResumeData((prev: any) => {
          const optimized = {
            professional_summary: result.data.professional_summary || result.data.autobiography || '',
            professional_experience: Array.isArray(result.data.professional_experience) ? result.data.professional_experience.join('\n\n') : result.data.professional_experience || prev.professional_experience,
            core_skills: Array.isArray(result.data.core_skills) ? result.data.core_skills.join(', ') : result.data.core_skills || prev.core_skills,
            projects: Array.isArray(result.data.projects) ? result.data.projects.join('\n\n') : result.data.projects || prev.projects,
            education: Array.isArray(result.data.education) ? result.data.education.join('\n\n') : result.data.education || prev.education,
            autobiography: result.data.autobiography || result.data.professional_summary || prev.autobiography
          };

          const newState = {
            ...prev,
            ...optimized
          };

          setEditedData(newState); // 同步更新編輯用的資料
          return newState;
        });
      } else {
        throw new Error(result.error || "AI優化生成失敗");
      }
    } catch (error) {
      console.error("🚨AI生成履歷API呼叫失敗:", error);
    }
    setPhase('result');
  };

  // 4. 儲存結果回資料庫
  const handleSaveOptimization = async () => {
    try {
      const payload = {
        user_id: realUserId,
        original_resume_id: realLatestResume?.resume_id || realLatestResume?.id,
        template_id: selectedTemplate,
        optimized_data: editedData, // 使用最後編輯過的資料
      };

      const response = await fetch('/api/resume_process/optimize/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      if (response.ok) {
        setIsTemplateSaved(true);
        setSaveModalConfig({ type: 'success', title: '儲存成功', message: '🎉優化版履歷已成功儲存至資料庫！' });
        setShowSaveModal(true);
      } else {
        setSaveModalConfig({ type: 'warning', title: '儲存失敗', message: result.message || result.error });
        setShowSaveModal(true);
      }
    } catch (error) {
      console.error("儲存優化履歷失敗:", error);
      setSaveModalConfig({ type: 'warning', title: '網路錯誤', message: '網路連線錯誤，儲存失敗！' });
      setShowSaveModal(true);
    } finally {
      setShowTemplateSaveConfirm(false);
    }
  };

  // UI 操作 Handlers
  const handleDownloadSuggestions = async () => {
    const { exportHtmlToPdf, buildSuggestionsReportHtml } = await import('@/utils/pdfExport');
    await exportHtmlToPdf({
      filename: '履歷優化建議報告.pdf',
      htmlContent: buildSuggestionsReportHtml([]), // 若有需要可將 mockSuggestions 換成實際建議陣列
    });
  };

  const handleDownloadResume = async () => {
    if (!resumeRef.current) return;
    setIsDownloading(true);
    try {
      const { exportResumeToPdf } = await import('@/utils/pdfExport');
      const themes = TEMPLATE_THEMES[selectedTemplate] || TEMPLATE_THEMES.corporate;
      const theme = themes[selectedThemeIndex] || themes[0];
      const filename = `優化履歷_${selectedTemplate}_${theme.name}.pdf`;
      await exportResumeToPdf({ element: resumeRef.current, filename });
    } catch (error) {
      console.error('PDF generation failed:', error);
    } finally {
      setIsDownloading(false);
    }
  };

  const handleSmartBack = () => {
    if (editPhase === 'edit') {
      setEditPhase('view');
      setShowSuggestionsDrawer(false);
    } else if (phase === 'suggestions') {
      setPhase('initial');
    } else if (phase === 'templates') {
      setPhase('suggestions');
    } else if (phase === 'result') {
      setPhase('templates');
    } else {
      navigate(-1);
    }
  };

  const handleReset = () => {
    setPhase('initial');
    setSelectedTemplate('');
    setSelectedThemeIndex(0);
    setIsEditing(false);
    setEditPhase('view');
    setIsEditSaved(false);
    setIsTemplateSaved(false);
    setDiagnosticResult(null);
  };

  const confirmSaveEdit = () => {
    setOriginalData(editedOriginalData);
    setEditPhase('view');
    setIsEditSaved(true);
    setShowSaveConfirm(false);
  };

  const formatDate = (dateStr: string) => dateStr ? dateStr.replace(/-/g, '') : '';

  if (isLoadingDB) {
    return <div className="flex h-screen items-center justify-center"><AILoadingSpinner message="正在與 Supabase 連線撈取資料..." /></div>;
  }

  return (
    <LoginRequired>
      <div className="container py-12 animate-fade-in">
        <AlertModal open={showAccessAlert} onClose={() => { setShowAccessAlert(false); navigate(-1); }} type="warning" title="系統提示" message={accessAlertMessage} confirmLabel="返回" />
        <AlertModal open={showSaveConfirm} onClose={() => setShowSaveConfirm(false)} type="warning" title="確認儲存變更" message="儲存後將無法再次編輯履歷內容，確定要儲存嗎？" confirmLabel="確認儲存" cancelLabel="取消" showCancel onConfirm={confirmSaveEdit} />
        <AlertModal open={showTemplateSaveConfirm} onClose={() => setShowTemplateSaveConfirm(false)} type="warning" title="確認儲存履歷" message="將此設計與內容儲存至您的帳號，確定要儲存嗎？" confirmLabel="確認儲存" cancelLabel="取消" showCancel onConfirm={handleSaveOptimization} />
        <AlertModal open={showSaveModal} onClose={() => setShowSaveModal(false)} type={saveModalConfig.type as any} title={saveModalConfig.title} message={saveModalConfig.message} confirmLabel="確定" />

        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-6">
            <FileText className="h-8 w-8 text-primary" />
          </div>
          <h1 className="text-3xl font-bold mb-4">履歷優化</h1>
          <p className="text-muted-foreground max-w-2xl mx-auto">AI 智能分析您的履歷，提供專業優化建議並生成精美履歷</p>
        </div>

        <div className="max-w-4xl mx-auto">
          <AnimatePresence mode="wait">
            {phase === 'initial' && (
              <InitialPhase
                originalData={originalData}
                onStartOptimize={handleStartOptimize}
                latestResumeName={realLatestResume?.resume_name || '未命名'}
                latestResumeDate={realLatestResume?.created_at ? formatDate(realLatestResume.created_at.split('T')[0]) : ''}
              />
            )}

            {phase === 'analyzing' && (
              <motion.div key="analyzing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="text-center py-10">
                <AILoadingSpinner message="AI正在深度診斷您的履歷中..." />
                <AnalysisSkeleton />
              </motion.div>
            )}

            {phase === 'suggestions' && (
              <>
                {editPhase === 'view' ? (
                  <SuggestionsPhase
                    diagnosticResult={diagnosticResult}
                    originalData={originalData}
                    onDownload={handleDownloadSuggestions}
                    onGenerate={() => setPhase('templates')}
                    onEdit={() => { setEditedOriginalData(originalData); setEditPhase('edit'); }}
                    onBack={handleSmartBack}
                    isEditSaved={isEditSaved}
                  />
                ) : (
                  <ResumeEditMode
                    originalData={editedOriginalData}
                    diagnosticResult={diagnosticResult}
                    onChange={setEditedOriginalData}
                    onSave={() => setShowSaveConfirm(true)}
                    onCancel={() => { setEditPhase('view'); setShowSuggestionsDrawer(false); }}
                    showSuggestionsDrawer={showSuggestionsDrawer}
                    setShowSuggestionsDrawer={setShowSuggestionsDrawer}
                    onBack={handleSmartBack}
                  />
                )}
              </>
            )}

            {phase === 'templates' && (
              <TemplateSelectionPhase
                onSelect={handleGenerateOptimizedResume}
                onBack={() => setPhase('suggestions')}
              />
            )}

            {phase === 'generating' && (
              <motion.div key="generating" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="text-center py-10">
                <AILoadingSpinner message="AI正在將您的履歷套用至全新樣板中..." />
                <AnalysisSkeleton />
              </motion.div>
            )}

            {phase === 'result' && (
              <ResultPhase
                resumeData={isEditing ? editedData : resumeData}
                selectedTemplate={selectedTemplate}
                selectedThemeIndex={selectedThemeIndex}
                isEditing={isEditing}
                isDownloading={isDownloading}
                resumeRef={resumeRef}
                onEdit={() => { setEditedData(resumeData); setIsEditing(true); }}
                onSave={() => setIsEditing(false)} // inline save
                onCancelEdit={() => setIsEditing(false)}
                onDataChange={setEditedData}
                onDownload={handleDownloadResume}
                onBackToTemplates={() => { setPhase('templates'); setSelectedTemplate(''); }}
                onReset={handleReset}
                onThemeChange={setSelectedThemeIndex}
                isTemplateSaved={isTemplateSaved}
                onSaveTemplate={() => setShowTemplateSaveConfirm(true)}
                avatarUrl={avatarUrl}
              />
            )}
          </AnimatePresence>
        </div>
      </div>
    </LoginRequired>
  );
};

// ==========================================
// 🌟 子元件區 (保留原本超美的排版設計)
// ==========================================

const ThemeSwatchSelector = ({ themes, selectedIndex, onChange }: { themes: ThemeColors[]; selectedIndex: number; onChange: (index: number) => void; }) => (
  <div className="flex gap-2">
    {themes.map((theme, i) => (
      <button key={i} onClick={() => onChange(i)} className={`group relative h-7 w-7 rounded-full border-2 transition-all duration-200 ${selectedIndex === i ? 'border-foreground scale-110 shadow-md' : 'border-border/60 hover:scale-105'}`} style={{ backgroundColor: theme.main }} title={theme.name}>
        {selectedIndex === i && <Check className="absolute inset-0 m-auto h-3.5 w-3.5 text-white drop-shadow-md" />}
      </button>
    ))}
  </div>
);

const ResumeField = ({ icon: Icon, label, value, optional = false }: { icon: React.ComponentType<{ className?: string }>; label: string; value: string; optional?: boolean; }) => (
  <div className="p-4 bg-muted/30 rounded-lg">
    <div className="flex items-center gap-2 mb-2">
      <Icon className="h-4 w-4 text-primary" />
      <span className="font-medium text-sm">{label}</span>
      {optional && <span className="text-xs text-muted-foreground">(選填)</span>}
    </div>
    <p className="text-sm whitespace-pre-line">{value || <span className="text-muted-foreground italic">尚未填寫</span>}</p>
  </div>
);

const InitialPhase = ({ originalData, onStartOptimize, latestResumeName, latestResumeDate }: any) => (
  <motion.div key="initial" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="space-y-6">
    {latestResumeName && (
      <div className="flex items-center gap-3 p-4 rounded-lg border border-primary/30 bg-primary/5">
        <FileText className="h-5 w-5 text-primary shrink-0" />
        <p className="text-sm">成功從資料庫讀取您的真實履歷：<span className="font-semibold text-foreground">「{latestResumeName}」</span><span className="text-muted-foreground ml-1">（更新於 {latestResumeDate}）</span></p>
      </div>
    )}
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><User className="h-5 w-5 text-primary" /> 您的履歷資料</CardTitle>
        <CardDescription>以下是您目前的履歷內容，點擊開始優化進行 AI 分析</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-start gap-6">
          <div className="h-24 w-24 rounded-full bg-muted flex items-center justify-center shrink-0"><User className="h-12 w-12 text-muted-foreground" /></div>
          <div className="flex-1 space-y-2">
            <h3 className="text-2xl font-bold">{originalData.name}</h3>
            <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
              <span className="flex items-center gap-1"><Mail className="h-4 w-4" />{originalData.email}</span>
              <span className="flex items-center gap-1"><Phone className="h-4 w-4" />{originalData.phone}</span>
              {originalData.address && <span className="flex items-center gap-1"><MapPin className="h-4 w-4" />{originalData.address}</span>}
            </div>
          </div>
        </div>
        <div className="grid gap-4">
          {originalResumeFields.filter((f) => f.key !== 'name' && f.key !== 'phone' && f.key !== 'email' && f.key !== 'address').map((field) => {
            const val = originalData[field.key as keyof typeof originalData];
            if (field.optional && !val) return null;
            return <ResumeField key={field.key} icon={field.icon} label={field.label} value={val} optional={field.optional} />;
          })}
        </div>
      </CardContent>
    </Card>
    <div className="flex justify-center"><Button size="lg" className="gradient-primary gap-2 h-14 px-8 text-lg" onClick={onStartOptimize}><Sparkles className="h-5 w-5" /> 開始 AI 分析優化</Button></div>
  </motion.div>
);

const SuggestionsPhase = ({ diagnosticResult, originalData, onDownload, onGenerate, onEdit, onBack, isEditSaved }: any) => {
  const severityColors: Record<string, string> = { '嚴重扣分': 'bg-red-100 text-red-800 border-red-200', '明顯扣分': 'bg-amber-100 text-amber-800 border-amber-200', '中度扣分': 'bg-orange-100 text-orange-800 border-orange-200', '輕微扣分': 'bg-yellow-100 text-yellow-800 border-yellow-200' };
  return (
    <motion.div key="suggestions" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="space-y-6">
      <div className="flex items-center justify-between">
        <Button variant="ghost" className="gap-2 -ml-2" onClick={onBack}><ChevronLeft className="h-4 w-4" /> 返回上一步</Button>
        {!isEditSaved && <Button variant="outline" className="gap-2" onClick={onEdit}><Edit3 className="h-4 w-4" /> 編輯履歷</Button>}
      </div>

      {isEditSaved && (
        <><div className="flex items-center gap-3 p-4 rounded-lg border border-green-500/30 bg-green-500/5"><Check className="h-5 w-5 text-green-600 shrink-0" /><p className="text-sm text-green-700">履歷變更已儲存</p></div>
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}><Card><CardHeader><CardTitle className="flex items-center gap-2"><FileText className="h-5 w-5 text-primary" /> 修改後的履歷內容</CardTitle></CardHeader><CardContent className="space-y-4">
            <div className="flex items-start gap-6"><div className="h-20 w-20 rounded-full bg-muted flex items-center justify-center shrink-0"><User className="h-10 w-10 text-muted-foreground" /></div><div className="flex-1 space-y-2"><h3 className="text-xl font-bold">{originalData.name}</h3><div className="flex flex-wrap gap-4 text-sm text-muted-foreground"><span className="flex items-center gap-1"><Mail className="h-4 w-4" />{originalData.email}</span><span className="flex items-center gap-1"><Phone className="h-4 w-4" />{originalData.phone}</span></div></div></div>
            <div className="grid gap-3">{originalResumeFields.filter((f) => f.key !== 'name' && f.key !== 'phone' && f.key !== 'email' && f.key !== 'address').map((field) => { const val = originalData[field.key as keyof typeof originalData]; if (field.optional && !val) return null; return <ResumeField key={field.key} icon={field.icon} label={field.label} value={val} optional={field.optional} />; })}</div>
          </CardContent></Card></motion.div></>
      )}

      {!isEditSaved && diagnosticResult && (
        <div className="space-y-6">
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}><Card className="border-primary/20 shadow-md"><CardHeader><CardTitle className="flex items-center gap-2"><Target className="h-5 w-5 text-primary" /> 核心定位分析</CardTitle></CardHeader><CardContent className="space-y-4"><div className="p-4 rounded-lg bg-primary/5 border border-primary/15"><h4 className="text-sm font-semibold text-primary mb-2">候選人定位</h4><p className="text-sm leading-relaxed">{diagnosticResult.candidate_positioning}</p></div><div className="p-4 rounded-lg bg-muted/40 border border-border"><h4 className="text-sm font-semibold text-foreground mb-2">目標職位落差摘要</h4><p className="text-sm text-muted-foreground leading-relaxed">{diagnosticResult.target_role_gap_summary}</p></div></CardContent></Card></motion.div>
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}><div className="grid md:grid-cols-2 gap-4"><Card className="border-green-200/60"><CardHeader className="pb-3"><CardTitle className="text-base flex items-center gap-2 text-green-700"><CheckCircle className="h-5 w-5" /> 整體優勢</CardTitle></CardHeader><CardContent className="space-y-3">{diagnosticResult.overall_strengths.map((s: string, i: number) => (<div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-green-50/60"><CheckCircle className="h-4 w-4 text-green-600 shrink-0 mt-0.5" /><p className="text-sm leading-relaxed">{s}</p></div>))}</CardContent></Card><Card className="border-primary/20"><CardHeader className="pb-3"><CardTitle className="text-base flex items-center gap-2 text-primary"><AlertTriangle className="h-5 w-5" /> 待改善項目</CardTitle></CardHeader><CardContent className="space-y-3">{diagnosticResult.overall_weaknesses.map((w: string, i: number) => (<div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-primary/5"><AlertTriangle className="h-4 w-4 text-primary shrink-0 mt-0.5" /><p className="text-sm leading-relaxed">{w}</p></div>))}</CardContent></Card></div></motion.div>
          {diagnosticResult.critical_issues.length > 0 && <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}><Card><CardHeader><CardTitle className="flex items-center gap-2"><Sparkles className="h-5 w-5 text-primary" /> 關鍵問題診斷</CardTitle></CardHeader><CardContent className="space-y-5">{diagnosticResult.critical_issues.map((issue: any, i: number) => (<motion.div key={i} className="rounded-lg border border-border overflow-hidden"><div className="flex items-center gap-3 px-4 py-3 bg-muted/30 border-b border-border"><span className="font-medium text-sm">{issue.section}</span><Badge className={`text-xs border ${severityColors[issue.severity] || 'bg-muted'}`}>{issue.severity}</Badge></div><div className="p-4 space-y-4"><div className="p-3 rounded-md bg-muted/40 border border-border/60"><p className="text-xs text-muted-foreground mb-1 font-medium">原文內容</p><p className="text-sm text-foreground/80 leading-relaxed">{issue.original_text}</p></div><div><p className="text-xs text-muted-foreground mb-1 font-medium">診斷分析</p><p className="text-sm leading-relaxed">{issue.issue_reason}</p></div><div className="p-3 rounded-md bg-primary/5 border border-primary/15"><p className="text-xs text-primary mb-1 font-semibold">優化方向</p><p className="text-sm leading-relaxed font-medium text-primary">{issue.improvement_direction}</p></div></div></motion.div>))}</CardContent></Card></motion.div>}
          {diagnosticResult.recommended_next_actions.length > 0 && <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}><Card className="bg-[#fbf1e8]/40 border-primary/15"><CardHeader><CardTitle className="flex items-center gap-2"><ListChecks className="h-5 w-5 text-primary" /> 後續行動計畫</CardTitle></CardHeader><CardContent><div className="space-y-3">{diagnosticResult.recommended_next_actions.map((action: string, i: number) => (<div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-background/80 border border-border/50"><div className="h-6 w-6 rounded-full bg-primary/10 text-primary flex items-center justify-center shrink-0 text-xs font-bold mt-0.5">{i + 1}</div><p className="text-sm leading-relaxed">{action}</p></div>))}</div></CardContent></Card></motion.div>}
        </div>
      )}
      <div className="flex gap-4"><Button variant="outline" className="flex-1 gap-2 h-12" onClick={onDownload}><Download className="h-4 w-4" /> 下載建議報告</Button><Button className="flex-[2] h-12 text-lg gradient-primary gap-2" onClick={onGenerate}><Palette className="h-5 w-5" /> 選擇樣板並生成優化履歷</Button></div>
    </motion.div>
  );
};

const ResumeEditMode = ({ originalData, diagnosticResult, onChange, onSave, onCancel, showSuggestionsDrawer, setShowSuggestionsDrawer, onBack }: any) => {
  return (
    <motion.div key="edit-mode" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="space-y-6">
      <div className="flex items-center justify-between"><Button variant="ghost" className="gap-2 -ml-2" onClick={onBack}><ChevronLeft className="h-4 w-4" /> 返回優化建議</Button><Button variant="outline" className="gap-2 border-primary text-primary hover:bg-primary/10" onClick={() => setShowSuggestionsDrawer(true)}><BookOpen className="h-4 w-4" /> 查看優化建議</Button></div>
      <Card className="ring-2 ring-primary/30"><CardHeader><CardTitle className="flex items-center gap-2"><Edit3 className="h-5 w-5 text-primary" /> 履歷編輯表單</CardTitle></CardHeader><CardContent className="space-y-6">
        {originalResumeFields.map((field) => {
          const Icon = field.icon; const value = originalData[field.key] || '';
          return (<div key={field.key} className="space-y-2"><label className="flex items-center gap-2 text-sm font-medium"><Icon className="h-4 w-4 text-primary" /> {field.label} {field.optional && <span className="text-xs text-muted-foreground font-normal">(選填)</span>}</label>
            {field.multiline ? <Textarea value={value} onChange={(e) => onChange({ ...originalData, [field.key]: e.target.value })} className="ring-1 ring-primary/20" rows={4} /> : <Input value={value} onChange={(e) => onChange({ ...originalData, [field.key]: e.target.value })} className="ring-1 ring-primary/20" />}
          </div>);
        })}
      </CardContent></Card>
      <div className="sticky bottom-4 bg-background/95 backdrop-blur-sm border rounded-lg p-4 shadow-lg flex gap-4"><Button variant="outline" className="flex-1" onClick={onCancel}> 取消編輯</Button><Button className="flex-1 gradient-primary gap-2" onClick={onSave}><Save className="h-4 w-4" /> 儲存變更</Button></div>
      <RightDrawer open={showSuggestionsDrawer} onClose={() => setShowSuggestionsDrawer(false)} title="優化建議參考"><ScrollArea className="h-full pr-4"><div className="space-y-6 text-sm">{/* Suggestions content omitted for brevity, can map from diagnosticResult directly if needed */}優化建議請參考上一頁分析報告。</div></ScrollArea></RightDrawer>
    </motion.div>
  );
};

const TemplateSelectionPhase = ({ onSelect, onBack }: any) => (
  <motion.div key="templates" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="space-y-6">
    <div className="text-center mb-8"><h2 className="text-2xl font-bold mb-2">選擇履歷樣板</h2><p className="text-muted-foreground">根據您的職業目標選擇最適合的履歷風格與配色</p></div>
    <div className="grid md:grid-cols-3 gap-6">
      {templates.map((template, i) => {
        const swatches = templateSwatches[template.id] || [];
        const ThumbnailComponent = templateThumbnailComponents[template.id as keyof typeof templateThumbnailComponents];
        return (
          <motion.div key={template.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
            <Card className="overflow-hidden group border-border/60 hover:border-primary/40 flex flex-col h-full">
              <div className="w-full aspect-[4/3] bg-[#f5efe8] rounded-t-lg border-b border-border/40 flex items-center justify-center p-4">
                <div className="w-[70%] shadow-sm border border-gray-200/60 rounded-sm overflow-hidden bg-white group-hover:scale-105 transition-transform duration-300">{ThumbnailComponent ? <ThumbnailComponent /> : <div className="h-full w-full bg-white flex items-center justify-center"><FileText className="h-8 w-8 text-muted-foreground/30" /></div>}</div>
              </div>
              <CardHeader className="pb-2"><CardTitle className="text-lg">{template.name}</CardTitle><CardDescription className="text-xs">{template.subtitle}</CardDescription></CardHeader>
              <CardContent className="space-y-4 flex-1 flex flex-col">
                <p className="text-sm text-muted-foreground flex-1">{template.description}</p>
                <ul className="space-y-1">{template.features.map((feature, j) => (<li key={j} className="text-xs flex items-center gap-2 text-muted-foreground"><Check className="h-3 w-3 text-primary" /> {feature}</li>))}</ul>
                <div className="pt-2 border-t border-border/40"><p className="text-xs text-muted-foreground mb-2">配色方案</p><div className="flex gap-2.5">{swatches.map((color, j) => (<div key={j} className="h-7 w-7 rounded-full border border-border/60 shadow-sm" style={{ backgroundColor: color }} />))}</div></div>
                <Button className="w-full mt-4 gradient-primary" onClick={() => onSelect(template.id)}>選擇此樣板</Button>
              </CardContent>
            </Card>
          </motion.div>
        );
      })}
    </div>
    <div className="flex justify-center pt-4"><Button variant="ghost" className="gap-2" onClick={onBack}><ChevronLeft className="h-4 w-4" /> 返回上一步</Button></div>
  </motion.div>
);

const ResultPhase = ({ resumeData, selectedTemplate, selectedThemeIndex, isEditing, isDownloading, resumeRef, onEdit, onSave, onCancelEdit, onDataChange, onDownload, onBackToTemplates, onReset, onThemeChange, isTemplateSaved, onSaveTemplate, avatarUrl }: any) => {
  const template = templates.find(t => t.id === selectedTemplate);
  const themes = TEMPLATE_THEMES[selectedTemplate] || TEMPLATE_THEMES.corporate;
  const theme = themes[selectedThemeIndex] || themes[0];
  const handleFieldChange = (field: any, value: string) => onDataChange({ ...resumeData, [field]: value });

  return (
    <motion.div key="result" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: theme.main }}>{template && <template.icon className="h-5 w-5 text-white" />}</div>
          <div><p className="font-medium">{template?.name}</p><p className="text-xs text-muted-foreground">{template?.subtitle}</p></div>
        </div>
        {!isTemplateSaved && <div className="flex items-center gap-2"><span className="text-xs text-muted-foreground">配色：</span><ThemeSwatchSelector themes={themes} selectedIndex={selectedThemeIndex} onChange={onThemeChange} /></div>}
      </div>

      <Card className={isEditing ? 'ring-2 ring-primary/50 shadow-lg' : ''}>
        <CardContent className="p-6">
          <div ref={resumeRef} className="pdf-container bg-white text-foreground min-h-[600px]">
            {selectedTemplate === 'corporate' && <CorporateTemplate data={resumeData} isEditing={isEditing} onChange={handleFieldChange} theme={theme} />}
            {selectedTemplate === 'modern' && <ModernTemplate data={resumeData} isEditing={isEditing} onChange={handleFieldChange} theme={theme} avatarUrl={avatarUrl} />}
            {selectedTemplate === 'creative' && <CreativeTemplate data={resumeData} isEditing={isEditing} onChange={handleFieldChange} theme={theme} avatarUrl={avatarUrl} />}
          </div>
        </CardContent>
      </Card>

      {!isTemplateSaved && <div className="flex items-center gap-3 p-4 rounded-lg border border-amber-500/30 bg-amber-500/5"><Save className="h-5 w-5 text-amber-600 shrink-0" /><p className="text-sm text-amber-700">請先儲存履歷後才可下載 PDF 檔案</p></div>}
      <div className="flex flex-wrap gap-4">
        {!isTemplateSaved && <Button variant="outline" className="gap-2" onClick={onBackToTemplates}><Palette className="h-4 w-4" />重新選擇樣板</Button>}
        {isEditing ? (
          <><Button variant="outline" onClick={onCancelEdit}>取消編輯</Button><Button className="gradient-primary" onClick={onSave}><Save className="mr-2 h-4 w-4" />完成編輯</Button></>
        ) : (
          !isTemplateSaved && <Button variant="outline" onClick={onEdit}><Edit3 className="mr-2 h-4 w-4" />微調內容</Button>
        )}
        {!isTemplateSaved && <Button className="gap-2" style={{ backgroundColor: theme.main, color: 'white' }} onClick={onSaveTemplate}><Save className="h-4 w-4" />儲存履歷</Button>}
        <Button className="flex-1 gap-2 text-white" style={{ backgroundColor: theme.main }} onClick={onDownload} disabled={isDownloading || !isTemplateSaved}><Download className="h-4 w-4" /> {isDownloading ? '生成中...' : '下載履歷'}</Button>
      </div>
    </motion.div>
  );
};

// 🌟 EditableField 核心小元件 (讓你在 Result 畫面能直接編輯)
const EditableField = ({ value, onChange, isEditing, multiline = false, className = '' }: any) => {
  if (!isEditing) return <span className={`whitespace-pre-line ${className}`}>{value}</span>;
  const editClass = 'ring-1 ring-primary/30 shadow-sm';
  if (multiline) return <Textarea value={value} onChange={(e) => onChange(e.target.value)} className={`${editClass} ${className}`} rows={4} />;
  return <Input value={value} onChange={(e) => onChange(e.target.value)} className={`${editClass} ${className}`} />;
};

// ==========================================
// 🌟 三大履歷樣板 (Corporate / Modern / Creative)
// ==========================================
const CorporateTemplate = ({ data, isEditing, onChange, theme }: any) => (
  <div className="font-serif space-y-6" style={{ color: theme.text }}>
    <div className="text-center pb-4 avoid-break" style={{ borderBottom: `2px solid ${theme.main}` }}>
      <h1 className="text-3xl font-bold tracking-wide" style={{ color: theme.main }}><EditableField value={data.name} onChange={(v: any) => onChange('name', v)} isEditing={isEditing} /></h1>
      <div className="flex justify-center flex-wrap gap-4 mt-2 text-sm" style={{ color: theme.secondary }}>
        {data.email && <EditableField value={data.email} onChange={(v: any) => onChange('email', v)} isEditing={isEditing} />}
        {data.email && data.phone && <span>|</span>}
        {data.phone && <EditableField value={data.phone} onChange={(v: any) => onChange('phone', v)} isEditing={isEditing} />}
        {data.linkedin && <><span>|</span><EditableField value={data.linkedin} onChange={(v: any) => onChange('linkedin', v)} isEditing={isEditing} /></>}
      </div>
    </div>
    {data.professional_summary && <div className="avoid-break"><div><h2 className="text-lg font-bold pb-1 mb-3" style={{ color: theme.main, borderBottom: `1px solid ${theme.main}40` }}>專業摘要</h2><div className="text-sm"><EditableField value={data.professional_summary} onChange={(v: any) => onChange('professional_summary', v)} isEditing={isEditing} multiline /></div></div></div>}
    {data.education && <div className="avoid-break"><div><h2 className="text-lg font-bold pb-1 mb-3" style={{ color: theme.main, borderBottom: `1px solid ${theme.main}40` }}>學歷</h2><div className="text-sm"><EditableField value={data.education} onChange={(v: any) => onChange('education', v)} isEditing={isEditing} multiline /></div></div></div>}
    {data.professional_experience && <div className="avoid-break"><div><h2 className="text-lg font-bold pb-1 mb-3" style={{ color: theme.main, borderBottom: `1px solid ${theme.main}40` }}>工作經驗</h2><div className="text-sm"><EditableField value={data.professional_experience} onChange={(v: any) => onChange('professional_experience', v)} isEditing={isEditing} multiline /></div></div></div>}
    {data.projects && <div className="avoid-break"><div><h2 className="text-lg font-bold pb-1 mb-3" style={{ color: theme.main, borderBottom: `1px solid ${theme.main}40` }}>專案成就</h2><div className="text-sm"><EditableField value={data.projects} onChange={(v: any) => onChange('projects', v)} isEditing={isEditing} multiline /></div></div></div>}
    {data.core_skills && <div className="avoid-break"><div><h2 className="text-lg font-bold pb-1 mb-3" style={{ color: theme.main, borderBottom: `1px solid ${theme.main}40` }}>技能專長</h2><div className="text-sm"><EditableField value={data.core_skills} onChange={(v: any) => onChange('core_skills', v)} isEditing={isEditing} /></div></div></div>}
    {data.certifications && <div className="avoid-break"><div><h2 className="text-lg font-bold pb-1 mb-3" style={{ color: theme.main, borderBottom: `1px solid ${theme.main}40` }}>證照資格</h2><div className="text-sm"><EditableField value={data.certifications} onChange={(v: any) => onChange('certifications', v)} isEditing={isEditing} multiline /></div></div></div>}
    {data.autobiography && <div className="avoid-break"><div><h2 className="text-lg font-bold pb-1 mb-3" style={{ color: theme.main, borderBottom: `1px solid ${theme.main}40` }}>自傳</h2><div className="text-sm"><EditableField value={data.autobiography} onChange={(v: any) => onChange('autobiography', v)} isEditing={isEditing} multiline /></div></div></div>}
  </div>
);

const ModernTemplate = ({ data, isEditing, onChange, theme, avatarUrl }: any) => {
  const skills = (data.core_skills || '').split(',').map((s: string) => s.trim()).filter(Boolean);
  const avatarSrc = avatarUrl || logoCat;
  return (
    <div className="grid md:grid-cols-[1fr_2.5fr] gap-6">
      <div className="space-y-6 p-4 rounded-lg avoid-break" style={{ backgroundColor: `${theme.main}10` }}>
        <div className="h-32 w-32 mx-auto rounded-full flex items-center justify-center overflow-hidden border-2" style={{ borderColor: theme.main }}><img src={avatarSrc} alt={data.name} className="h-full w-full object-cover" /></div>
        <div className="space-y-2 text-sm">
          {data.email && <div className="flex items-center gap-2"><Mail className="h-4 w-4" style={{ color: theme.main }} /><EditableField value={data.email} onChange={(v: any) => onChange('email', v)} isEditing={isEditing} className="text-xs" /></div>}
          {data.phone && <div className="flex items-center gap-2"><Phone className="h-4 w-4" style={{ color: theme.main }} /><EditableField value={data.phone} onChange={(v: any) => onChange('phone', v)} isEditing={isEditing} className="text-xs" /></div>}
          {data.linkedin && <div className="flex items-center gap-2"><Linkedin className="h-4 w-4" style={{ color: theme.main }} /><EditableField value={data.linkedin} onChange={(v: any) => onChange('linkedin', v)} isEditing={isEditing} className="text-xs" /></div>}
        </div>
        {skills.length > 0 && (
          <div className="space-y-3"><h3 className="font-semibold text-sm pb-1" style={{ borderBottom: `1px solid ${theme.main}30` }}>技能專長</h3>
            {isEditing ? <EditableField value={data.core_skills} onChange={(v: any) => onChange('core_skills', v)} isEditing={isEditing} multiline /> : <div className="space-y-2">{skills.slice(0, 8).map((skill: string, i: number) => (<div key={i}><div className="flex justify-between text-xs mb-1"><span>{skill}</span><span>{95 - i * 5}%</span></div><div className="h-2 rounded-full overflow-hidden" style={{ backgroundColor: `${theme.secondary}30` }}><div className="h-full rounded-full transition-all" style={{ width: `${95 - i * 5}%`, backgroundColor: theme.main }} /></div></div>))}</div>}
          </div>
        )}
      </div>
      <div className="space-y-6">
        <div className="avoid-break"><h1 className="text-3xl font-bold" style={{ color: theme.main }}><EditableField value={data.name} onChange={(v: any) => onChange('name', v)} isEditing={isEditing} /></h1>{data.professional_summary && <p className="mt-1" style={{ color: theme.text }}><EditableField value={data.professional_summary} onChange={(v: any) => onChange('professional_summary', v)} isEditing={isEditing} multiline /></p>}</div>
        {data.professional_experience && <div className="space-y-4"><h3 className="font-semibold text-lg pb-1 flex items-center gap-2 avoid-break" style={{ borderBottom: `1px solid ${theme.main}30` }}><Briefcase className="h-4 w-4" style={{ color: theme.main }} />工作經驗</h3><EditableField value={data.professional_experience} onChange={(v: any) => onChange('professional_experience', v)} isEditing={isEditing} multiline className="text-sm" /></div>}
        {data.projects && <div className="space-y-4"><h3 className="font-semibold text-lg pb-1 flex items-center gap-2 avoid-break" style={{ borderBottom: `1px solid ${theme.main}30` }}><Award className="h-4 w-4" style={{ color: theme.main }} />專案成就</h3><EditableField value={data.projects} onChange={(v: any) => onChange('projects', v)} isEditing={isEditing} multiline className="text-sm" /></div>}
        {data.education && <div className="space-y-4"><h3 className="font-semibold text-lg pb-1 flex items-center gap-2 avoid-break" style={{ borderBottom: `1px solid ${theme.main}30` }}><GraduationCap className="h-4 w-4" style={{ color: theme.main }} />學歷</h3><EditableField value={data.education} onChange={(v: any) => onChange('education', v)} isEditing={isEditing} multiline className="text-sm" /></div>}
        {data.certifications && <div className="space-y-4"><h3 className="font-semibold text-lg pb-1 flex items-center gap-2 avoid-break" style={{ borderBottom: `1px solid ${theme.main}30` }}><ShieldCheck className="h-4 w-4" style={{ color: theme.main }} />證照資格</h3><EditableField value={data.certifications} onChange={(v: any) => onChange('certifications', v)} isEditing={isEditing} multiline className="text-sm" /></div>}
        {data.autobiography && <div className="space-y-4"><h3 className="font-semibold text-lg pb-1 flex items-center gap-2 avoid-break" style={{ borderBottom: `1px solid ${theme.main}30` }}><FileText className="h-4 w-4" style={{ color: theme.main }} />自傳</h3><EditableField value={data.autobiography} onChange={(v: any) => onChange('autobiography', v)} isEditing={isEditing} multiline className="text-sm" /></div>}
      </div>
    </div>
  );
};

const CreativeTemplate = ({ data, isEditing, onChange, theme, avatarUrl }: any) => {
  const avatarSrc = avatarUrl || logoCat;
  return (
    <div className="relative">
      <div className="absolute inset-0 rounded-lg opacity-10" style={{ backgroundColor: theme.main }} />
      <div className="relative p-6 space-y-6">
        <div className="flex flex-col md:flex-row items-center gap-6 avoid-break">
          <div className="relative"><div className="h-36 w-36 rounded-full p-1" style={{ backgroundColor: theme.main }}><div className="h-full w-full rounded-full overflow-hidden"><img src={avatarSrc} alt={data.name} className="h-full w-full object-cover" /></div></div></div>
          <div className="text-center md:text-left flex-1">
            <h1 className="text-4xl font-bold" style={{ color: theme.main }}><EditableField value={data.name} onChange={(v: any) => onChange('name', v)} isEditing={isEditing} /></h1>
            {data.professional_summary && <p className="mt-2" style={{ color: theme.text }}><EditableField value={data.professional_summary} onChange={(v: any) => onChange('professional_summary', v)} isEditing={isEditing} multiline /></p>}
            <div className="flex flex-wrap justify-center md:justify-start gap-4 mt-3 text-sm">
              {data.email && <span className="flex items-center gap-1" style={{ color: theme.main }}><Mail className="h-4 w-4" /><EditableField value={data.email} onChange={(v: any) => onChange('email', v)} isEditing={isEditing} /></span>}
              {data.phone && <span className="flex items-center gap-1" style={{ color: theme.secondary }}><Phone className="h-4 w-4" /><EditableField value={data.phone} onChange={(v: any) => onChange('phone', v)} isEditing={isEditing} /></span>}
              {data.linkedin && <span className="flex items-center gap-1" style={{ color: theme.main }}><Linkedin className="h-4 w-4" /><EditableField value={data.linkedin} onChange={(v: any) => onChange('linkedin', v)} isEditing={isEditing} /></span>}
            </div>
          </div>
        </div>
        <div className="grid md:grid-cols-2 gap-6">
          {data.professional_experience && <div className="avoid-break"><div className="p-4 rounded-lg bg-white/50" style={{ borderLeft: `4px solid ${theme.main}` }}><h3 className="font-semibold mb-3" style={{ color: theme.main }}>工作經驗</h3><div className="text-sm"><EditableField value={data.professional_experience} onChange={(v: any) => onChange('professional_experience', v)} isEditing={isEditing} multiline /></div></div></div>}
          {data.education && <div className="avoid-break"><div className="p-4 rounded-lg bg-white/50" style={{ borderLeft: `4px solid ${theme.secondary}` }}><h3 className="font-semibold mb-3" style={{ color: theme.secondary }}>學歷</h3><div className="text-sm"><EditableField value={data.education} onChange={(v: any) => onChange('education', v)} isEditing={isEditing} multiline /></div></div></div>}
          {data.projects && <div className="avoid-break"><div className="p-4 rounded-lg bg-white/50" style={{ borderLeft: `4px solid ${theme.main}` }}><h3 className="font-semibold mb-3" style={{ color: theme.main }}>專案成就</h3><div className="text-sm"><EditableField value={data.projects} onChange={(v: any) => onChange('projects', v)} isEditing={isEditing} multiline /></div></div></div>}
          {data.core_skills && <div className="avoid-break"><div className="p-4 rounded-lg bg-white/50" style={{ borderLeft: `4px solid ${theme.secondary}` }}><h3 className="font-semibold mb-3" style={{ color: theme.secondary }}>技能專長</h3><div className="text-sm"><EditableField value={data.core_skills} onChange={(v: any) => onChange('core_skills', v)} isEditing={isEditing} /></div></div></div>}
        </div>
        {data.autobiography && <div className="avoid-break"><div className="p-4 rounded-lg bg-white/50" style={{ borderLeft: `4px solid ${theme.main}` }}><h3 className="font-semibold mb-3" style={{ color: theme.main }}>自傳</h3><div className="text-sm"><EditableField value={data.autobiography} onChange={(v: any) => onChange('autobiography', v)} isEditing={isEditing} multiline /></div></div></div>}
      </div>
    </div>
  );
};

export default Optimize;
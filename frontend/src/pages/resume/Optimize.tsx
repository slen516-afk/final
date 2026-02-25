import { useState, useEffect, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Download, Edit3, Save, RotateCcw, Palette, ChevronRight, Briefcase, GraduationCap, Mail, Phone, Globe, Award, Languages, User, Star, Sparkles, Check, ChevronLeft, BookOpen, ArrowLeft, Loader2, Linkedin, FolderOpen, Code, MapPin, ShieldCheck, ExternalLink, MoreHorizontal } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AILoadingSpinner, AnalysisSkeleton } from '@/components/loading/LoadingStates';
import { useAppState } from '@/contexts/AppContext';
import { useResumes } from '@/contexts/ResumeContext';
import LoginRequired from '@/components/gatekeeper/LoginRequired';
import AlertModal from '@/components/modals/AlertModal';
import { motion, AnimatePresence } from 'framer-motion';
import { templateThumbnailComponents } from '@/components/resume/TemplateThumbnails';
import html2pdf from 'html2pdf.js';
import RightDrawer from '@/components/panels/RightDrawer';
import { ScrollArea } from '@/components/ui/scroll-area';
import type { OriginalResumeData, ResumeData, Suggestion } from '@/types/resume';
import { mockOriginalResumeData, mockResumeData, mockSuggestions } from '@/mocks/resumes';

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
    { name: '莫蘭迪粉橘', main: '#E07A5F', secondary: '#F2CC8F', accent: '#3D405B', text: '#2B2B2B' },
    { name: '紫藍創意系', main: '#6D28D9', secondary: '#A78BFA', accent: '#F472B6', text: '#1F1F1F' },
    { name: '活力橘藍對比', main: '#F97316', secondary: '#2563EB', accent: '#FACC15', text: '#222222' },
    { name: '黑底霓虹', main: '#0F172A', secondary: '#1E293B', accent: '#F43F5E', text: '#F8FAFC' },
  ],
};

// Original resume fields config (for initial preview & suggestions edit)
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

// Optimized resume fields config (for final generated output & result edit)
const resumeFields = [
  { key: 'name', label: '姓名', icon: User, multiline: false, placeholder: '請輸入您的姓名' },
  { key: 'email', label: '電子郵件', icon: Mail, multiline: false, placeholder: '請輸入您的電子郵件' },
  { key: 'phone', label: '聯絡電話', icon: Phone, multiline: false, placeholder: '請輸入您的聯絡電話' },
  { key: 'linkedin', label: 'LinkedIn', icon: Linkedin, multiline: false, placeholder: '請輸入 LinkedIn 連結' },
  { key: 'github', label: 'GitHub', icon: Code, multiline: false, placeholder: '請輸入 GitHub 連結' },
  { key: 'professional_summary', label: '專業摘要', icon: Sparkles, multiline: true, placeholder: '精簡的專業總結，包含核心價值與職缺關鍵字' },
  { key: 'professional_experience', label: '工作經驗', icon: Briefcase, multiline: true, placeholder: '公司、職稱、期間，描述以 STAR 原則撰寫' },
  { key: 'core_skills', label: '技能專長', icon: Star, multiline: false, placeholder: '6 個與推薦職缺相關的技術或軟實力關鍵字，以逗號分隔' },
  { key: 'projects', label: '專案作品集', icon: FolderOpen, multiline: true, placeholder: '專案名稱、技術棧與量化成果' },
  { key: 'education', label: '學歷', icon: GraduationCap, multiline: true, placeholder: '學校、系所、學位、畢業時間' },
  { key: 'autobiography', label: '自傳', icon: FileText, multiline: true, placeholder: '保留原本敘事順序與用詞習慣的優化內容' },
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

const OPTIMIZE_RESULT_KEY = 'resume-optimize-state';

interface PersistedOptimizeState {
  phase: Phase;
  suggestions: Suggestion[];
  selectedTemplate: string;
  selectedThemeIndex: number;
  resumeData: ResumeData;
  originalData: OriginalResumeData;
}

const loadOptimizeState = (): PersistedOptimizeState | null => {
  try {
    const saved = localStorage.getItem(OPTIMIZE_RESULT_KEY);
    if (saved) return JSON.parse(saved);
  } catch {}
  return null;
};

const saveOptimizeState = (state: PersistedOptimizeState) => {
  localStorage.setItem(OPTIMIZE_RESULT_KEY, JSON.stringify(state));
};

const clearOptimizeState = () => {
  localStorage.removeItem(OPTIMIZE_RESULT_KEY);
};

const Optimize = () => {
  const navigate = useNavigate();
  const { isLoggedIn, isResumeUploaded, isPersonalityQuizDone } = useAppState();
  const { resumes, selectedResumeId, setSelectedResumeId } = useResumes();

  // Restore persisted state if available
  const persisted = useMemo(() => loadOptimizeState(), []);
  const canRestore = persisted && (persisted.phase === 'suggestions' || persisted.phase === 'templates' || persisted.phase === 'result');

  const [phase, setPhase] = useState<Phase>(canRestore ? persisted!.phase : 'initial');
  const [originalData, setOriginalData] = useState<OriginalResumeData>(canRestore ? persisted!.originalData : mockOriginalResumeData);
  const [editedOriginalData, setEditedOriginalData] = useState<OriginalResumeData>(canRestore ? persisted!.originalData : mockOriginalResumeData);
  const [resumeData, setResumeData] = useState<ResumeData>(canRestore ? persisted!.resumeData : mockResumeData);
  const [editedData, setEditedData] = useState<ResumeData>(canRestore ? persisted!.resumeData : mockResumeData);
  const [suggestions, setSuggestions] = useState<Suggestion[]>(canRestore ? persisted!.suggestions : []);
  const [selectedTemplate, setSelectedTemplate] = useState<string>(canRestore ? persisted!.selectedTemplate : '');
  const [selectedThemeIndex, setSelectedThemeIndex] = useState<number>(canRestore ? persisted!.selectedThemeIndex : 0);
  const [isEditing, setIsEditing] = useState(false);
  const [showSaveConfirm, setShowSaveConfirm] = useState(false);
  const [showAccessAlert, setShowAccessAlert] = useState(false);
  const [accessAlertMessage, setAccessAlertMessage] = useState('');
  const [isDownloading, setIsDownloading] = useState(false);
  const resumeRef = useRef<HTMLDivElement>(null);
  const [showSuggestionsDrawer, setShowSuggestionsDrawer] = useState(false);
  const [editPhase, setEditPhase] = useState<'view' | 'edit'>('view');

  // Check access conditions
  useEffect(() => {
    if (isLoggedIn) {
      if (!isResumeUploaded) {
        setAccessAlertMessage('請先上傳您的履歷資料');
        setShowAccessAlert(true);
      } else if (!isPersonalityQuizDone) {
        setAccessAlertMessage('請先完成性格測驗');
        setShowAccessAlert(true);
      }
    }
  }, [isLoggedIn, isResumeUploaded, isPersonalityQuizDone]);

  const handleAccessAlertClose = () => {
    setShowAccessAlert(false);
    navigate(-1);
  };

  const handleStartOptimize = async () => {
    setPhase('analyzing');
    // TODO: Replace with API call
    await new Promise(resolve => setTimeout(resolve, 3000));
    setSuggestions(mockSuggestions);
    setPhase('suggestions');
    saveOptimizeState({ phase: 'suggestions', suggestions: mockSuggestions, selectedTemplate: '', selectedThemeIndex: 0, resumeData, originalData });
  };

  const handleSelectTemplate = async (templateId: string) => {
    setSelectedTemplate(templateId);
    setSelectedThemeIndex(0);
    setPhase('generating');
    await new Promise(resolve => setTimeout(resolve, 2500));
    setPhase('result');
    saveOptimizeState({ phase: 'result', suggestions, selectedTemplate: templateId, selectedThemeIndex: 0, resumeData, originalData });
  };

  const handleDownloadSuggestions = () => {
    const content = suggestions.map(s =>
      `【${s.section}】\n原始：${s.original}\n優化：${s.optimized}\n`
    ).join('\n');
    downloadTextFile(content, '履歷優化建議.txt');
  };

  const handleDownloadResume = async () => {
    if (!resumeRef.current) return;

    setIsDownloading(true);

    try {
      const element = resumeRef.current;
      const themes = TEMPLATE_THEMES[selectedTemplate] || TEMPLATE_THEMES.corporate;
      const theme = themes[selectedThemeIndex] || themes[0];

      const sections = element.querySelectorAll('[data-pdf-section]');
      sections.forEach((section) => {
        (section as HTMLElement).style.pageBreakInside = 'avoid';
        (section as HTMLElement).style.breakInside = 'avoid';
      });

      const opt = {
        margin: [10, 10, 10, 10] as [number, number, number, number],
        filename: `優化履歷_${selectedTemplate}_${theme.name}.pdf`,
        image: { type: 'jpeg' as const, quality: 0.98 },
        html2canvas: {
          scale: 2,
          useCORS: true,
          letterRendering: true,
          logging: false,
        },
        jsPDF: {
          unit: 'mm' as const,
          format: 'a4' as const,
          orientation: 'portrait' as const,
        },
        pagebreak: {
          mode: ['avoid-all', 'css', 'legacy'],
          before: '.page-break-before',
          after: '.page-break-after',
          avoid: ['[data-pdf-section]', '.avoid-break'],
        },
      };

      await html2pdf().set(opt).from(element).save();
    } catch (error) {
      console.error('PDF generation failed:', error);
    } finally {
      setIsDownloading(false);
    }
  };

  const downloadTextFile = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleSaveEdit = () => {
    setShowSaveConfirm(true);
  };

  const confirmSave = () => {
    setOriginalData(editedOriginalData);
    setEditPhase('view');
    setShowSaveConfirm(false);
  };

  const handleEnterEditMode = () => {
    setEditedOriginalData(originalData);
    setEditPhase('edit');
  };

  const handleExitEditMode = () => {
    setEditPhase('view');
    setShowSuggestionsDrawer(false);
  };

  const handleSmartBack = () => {
    if (editPhase === 'edit') {
      handleExitEditMode();
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
    setEditedOriginalData(mockOriginalResumeData);
    setEditedData(mockResumeData);
    setEditPhase('view');
    setShowSuggestionsDrawer(false);
    clearOptimizeState();
  };

  const handleBackToTemplates = () => {
    setPhase('templates');
    setSelectedTemplate('');
  };

  const hasAccess = isResumeUploaded && isPersonalityQuizDone;

  const formatDate = (dateStr: string) => {
    return dateStr.replace(/-/g, '');
  };

  return (
    <LoginRequired>
      <div className="container py-12 animate-fade-in">
        {/* Access Alert */}
        <AlertModal
          open={showAccessAlert}
          onClose={handleAccessAlertClose}
          type="warning"
          title="需要完成前置步驟"
          message={accessAlertMessage}
          confirmLabel="返回"
        />

        {/* Save Confirmation */}
        <AlertModal
          open={showSaveConfirm}
          onClose={() => setShowSaveConfirm(false)}
          type="info"
          title="確認儲存變更"
          message="確定要儲存您編輯的履歷內容嗎？"
          confirmLabel="確認儲存"
          cancelLabel="取消"
          showCancel
          onConfirm={confirmSave}
        />

        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-6">
            <FileText className="h-8 w-8 text-primary" />
          </div>
          <h1 className="text-3xl font-bold mb-4">履歷優化</h1>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            AI 智能分析您的履歷，提供專業優化建議並生成精美履歷
          </p>
        </div>

        {!hasAccess && isLoggedIn ? (
          <Card className="max-w-lg mx-auto">
            <CardContent className="p-8 text-center">
              <div className="h-16 w-16 rounded-full bg-amber-100 dark:bg-amber-900/30 mx-auto flex items-center justify-center mb-4">
                <FileText className="h-8 w-8 text-amber-600 dark:text-amber-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">尚未完成前置步驟</h3>
              <p className="text-muted-foreground mb-6">
                請先上傳履歷並完成性格測驗，才能使用履歷優化功能
              </p>
              <Button className="gradient-primary" onClick={() => navigate('/member/upload-resume')}>
                前往上傳履歷
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="max-w-4xl mx-auto">
            <AnimatePresence mode="wait">
              {phase === 'initial' && (
                <InitialPhase
                  originalData={originalData}
                  onStartOptimize={handleStartOptimize}
                  resumes={resumes}
                  selectedResumeId={selectedResumeId}
                  onResumeChange={setSelectedResumeId}
                  formatDate={formatDate}
                />
              )}

              {phase === 'analyzing' && (
                <motion.div
                  key="analyzing"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <AILoadingSpinner message="正在分析履歷，生成優化建議..." />
                  <AnalysisSkeleton />
                </motion.div>
              )}

              {phase === 'suggestions' && (
                <>
                  {editPhase === 'view' ? (
                    <SuggestionsPhase
                      suggestions={suggestions}
                      onDownload={handleDownloadSuggestions}
                      onGenerate={() => setPhase('templates')}
                      onEdit={handleEnterEditMode}
                      onBack={handleSmartBack}
                    />
                  ) : (
                    <ResumeEditMode
                      originalData={editedOriginalData}
                      suggestions={suggestions}
                      onChange={setEditedOriginalData}
                      onSave={() => setShowSaveConfirm(true)}
                      onCancel={handleExitEditMode}
                      showSuggestionsDrawer={showSuggestionsDrawer}
                      setShowSuggestionsDrawer={setShowSuggestionsDrawer}
                      onBack={handleSmartBack}
                    />
                  )}
                </>
              )}

              {phase === 'templates' && (
                <TemplateSelectionPhase
                  onSelect={handleSelectTemplate}
                  onBack={() => setPhase('suggestions')}
                />
              )}

              {phase === 'generating' && (
                <motion.div
                  key="generating"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <AILoadingSpinner message="正在生成優化履歷中..." />
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
                  onEdit={() => {
                    setEditedData(resumeData);
                    setIsEditing(true);
                  }}
                  onSave={handleSaveEdit}
                  onCancelEdit={() => setIsEditing(false)}
                  onDataChange={setEditedData}
                  onDownload={handleDownloadResume}
                  onBackToTemplates={handleBackToTemplates}
                  onReset={handleReset}
                  onThemeChange={setSelectedThemeIndex}
                />
              )}
            </AnimatePresence>
          </div>
        )}
      </div>
    </LoginRequired>
  );
};

// Theme Swatch Selector for Result Phase
const ThemeSwatchSelector = ({
  themes,
  selectedIndex,
  onChange,
}: {
  themes: ThemeColors[];
  selectedIndex: number;
  onChange: (index: number) => void;
}) => (
  <div className="flex gap-2">
    {themes.map((theme, i) => (
      <button
        key={i}
        onClick={() => onChange(i)}
        className={`group relative h-7 w-7 rounded-full border-2 transition-all duration-200 ${
          selectedIndex === i
            ? 'border-foreground scale-110 shadow-md'
            : 'border-border/60 hover:scale-105'
        }`}
        style={{ backgroundColor: theme.main }}
        title={theme.name}
      >
        {selectedIndex === i && (
          <Check className="absolute inset-0 m-auto h-3.5 w-3.5 text-white drop-shadow-md" />
        )}
      </button>
    ))}
  </div>
);

// Initial Phase Component with Resume Selector - uses ORIGINAL fields
const InitialPhase = ({
  originalData,
  onStartOptimize,
  resumes,
  selectedResumeId,
  onResumeChange,
  formatDate,
}: {
  originalData: OriginalResumeData;
  onStartOptimize: () => void;
  resumes: { id: number; name: string; updatedAt: string; content: string }[];
  selectedResumeId: number | null;
  onResumeChange: (id: number | null) => void;
  formatDate: (d: string) => string;
}) => (
  <motion.div
    key="initial"
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    className="space-y-6"
  >
    {/* Resume Version Selector */}
    <Card className="border-primary/30 shadow-[0_0_12px_rgba(141,73,3,0.1)]">
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <FileText className="h-5 w-5 text-primary" />
          選擇履歷版本
        </CardTitle>
        <CardDescription className="text-xs">
          請選擇要優化的履歷版本，系統將根據該版本進行 AI 分析
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Select
          value={selectedResumeId?.toString() ?? ''}
          onValueChange={(val) => onResumeChange(parseInt(val, 10))}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="請選擇履歷" />
          </SelectTrigger>
          <SelectContent>
            {resumes.map((r) => (
              <SelectItem key={r.id} value={r.id.toString()}>
                <span className="flex items-center gap-2">
                  <FileText className="h-3.5 w-3.5 text-primary shrink-0" />
                  <span className="truncate">{r.name}</span>
                  <span className="text-muted-foreground text-xs shrink-0">_{formatDate(r.updatedAt)}</span>
                </span>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </CardContent>
    </Card>

    {/* Original Resume Data Display */}
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <User className="h-5 w-5 text-primary" />
          您的履歷資料
        </CardTitle>
        <CardDescription>以下是您目前的履歷內容，點擊開始優化進行 AI 分析</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Basic Info Header */}
        <div className="flex items-start gap-6">
          <div className="h-24 w-24 rounded-full bg-muted flex items-center justify-center shrink-0">
            <User className="h-12 w-12 text-muted-foreground" />
          </div>
          <div className="flex-1 space-y-2">
            <h3 className="text-2xl font-bold">{originalData.name}</h3>
            <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
              <span className="flex items-center gap-1"><Mail className="h-4 w-4" />{originalData.email}</span>
              <span className="flex items-center gap-1"><Phone className="h-4 w-4" />{originalData.phone}</span>
              {originalData.address && <span className="flex items-center gap-1"><MapPin className="h-4 w-4" />{originalData.address}</span>}
            </div>
          </div>
        </div>

        {/* Original Resume Fields */}
        <div className="grid gap-4">
          {originalResumeFields
            .filter((f) => f.key !== 'name' && f.key !== 'phone' && f.key !== 'email' && f.key !== 'address')
            .map((field) => {
              const val = originalData[field.key as keyof OriginalResumeData];
              if (field.optional && !val) return null;
              return <ResumeField key={field.key} icon={field.icon} label={field.label} value={val} optional={field.optional} />;
            })}
        </div>
      </CardContent>
    </Card>

    <div className="flex justify-center">
      <Button size="lg" className="gradient-primary gap-2" onClick={onStartOptimize} disabled={!selectedResumeId}>
        <Sparkles className="h-5 w-5" />
        開始優化
      </Button>
    </div>
  </motion.div>
);

// Resume Field Display Component
const ResumeField = ({
  icon: Icon,
  label,
  value,
  optional = false,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
  optional?: boolean;
}) => (
  <div className="p-4 bg-muted/30 rounded-lg">
    <div className="flex items-center gap-2 mb-2">
      <Icon className="h-4 w-4 text-primary" />
      <span className="font-medium text-sm">{label}</span>
      {optional && <span className="text-xs text-muted-foreground">(選填)</span>}
    </div>
    <p className="text-sm whitespace-pre-line">{value || <span className="text-muted-foreground italic">尚未填寫</span>}</p>
  </div>
);

// Suggestions Phase Component
const SuggestionsPhase = ({
  suggestions,
  onDownload,
  onGenerate,
  onEdit,
  onBack,
}: {
  suggestions: Suggestion[];
  onDownload: () => void;
  onGenerate: () => void;
  onEdit: () => void;
  onBack: () => void;
}) => (
  <motion.div
    key="suggestions"
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    className="space-y-6"
  >
    <Button variant="ghost" className="gap-2 -ml-2" onClick={onBack}>
      <ChevronLeft className="h-4 w-4" />
      返回上一步
    </Button>

    <Card>
      <CardHeader className="flex flex-row items-start justify-between">
        <div>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            履歷優化建議
          </CardTitle>
          <CardDescription>AI 已分析您的履歷，以下是專業優化建議</CardDescription>
        </div>
        <Button variant="outline" className="gap-2 shrink-0" onClick={onEdit}>
          <Edit3 className="h-4 w-4" />
          編輯履歷
        </Button>
      </CardHeader>
      <CardContent className="space-y-6">
        {suggestions.map((s, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className="space-y-3"
          >
            <h4 className="font-medium text-primary flex items-center gap-2">
              <ChevronRight className="h-4 w-4" />
              {s.section}
            </h4>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="p-4 bg-muted/30 rounded-lg border border-transparent">
                <p className="text-xs text-muted-foreground mb-2">原始內容</p>
                <p className="text-sm">{s.original}</p>
              </div>
              <div className="p-4 bg-primary/5 rounded-lg border border-primary/20">
                <p className="text-xs text-primary mb-2">優化建議</p>
                <p className="text-sm">{s.optimized}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </CardContent>
    </Card>

    <div className="flex gap-4">
      <Button variant="outline" className="flex-1 gap-2" onClick={onDownload}>
        <Download className="h-4 w-4" />
        下載建議報告
      </Button>
      <Button className="flex-1 gradient-primary gap-2" onClick={onGenerate}>
        <Palette className="h-4 w-4" />
        生成優化履歷
      </Button>
    </div>
  </motion.div>
);

// Resume Edit Mode Component - uses ORIGINAL fields
const ResumeEditMode = ({
  originalData,
  suggestions,
  onChange,
  onSave,
  onCancel,
  showSuggestionsDrawer,
  setShowSuggestionsDrawer,
  onBack,
}: {
  originalData: OriginalResumeData;
  suggestions: Suggestion[];
  onChange: (data: OriginalResumeData) => void;
  onSave: () => void;
  onCancel: () => void;
  showSuggestionsDrawer: boolean;
  setShowSuggestionsDrawer: (open: boolean) => void;
  onBack: () => void;
}) => {
  const handleFieldChange = (field: keyof OriginalResumeData, value: string) => {
    onChange({ ...originalData, [field]: value });
  };

  return (
    <motion.div
      key="edit-mode"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <Button variant="ghost" className="gap-2 -ml-2" onClick={onBack}>
          <ChevronLeft className="h-4 w-4" />
          返回優化建議
        </Button>
        <Button
          variant="outline"
          className="gap-2 border-primary text-primary hover:bg-primary/10"
          onClick={() => setShowSuggestionsDrawer(true)}
        >
          <BookOpen className="h-4 w-4" />
          查看優化建議
        </Button>
      </div>

      <Card className="ring-2 ring-primary/30 shadow-[0_0_20px_rgba(141,73,3,0.15)]">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Edit3 className="h-5 w-5 text-primary" />
            履歷編輯表單
          </CardTitle>
          <CardDescription>
            根據優化建議修改您的履歷內容，所有欄位皆可編輯
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {originalResumeFields.map((field) => {
            const Icon = field.icon;
            const value = originalData[field.key as keyof OriginalResumeData] || '';

            return (
              <div key={field.key} className="space-y-2">
                <label className="flex items-center gap-2 text-sm font-medium">
                  <Icon className="h-4 w-4 text-primary" />
                  {field.label}
                  {field.optional && <span className="text-xs text-muted-foreground font-normal">(選填)</span>}
                </label>
                {field.multiline ? (
                  <Textarea
                    value={value}
                    onChange={(e) => handleFieldChange(field.key as keyof OriginalResumeData, e.target.value)}
                    placeholder={`請輸入${field.label}`}
                    className="ring-1 ring-primary/20 focus:ring-primary/50 shadow-[0_0_8px_rgba(141,73,3,0.1)] focus:shadow-[0_0_12px_rgba(141,73,3,0.2)] transition-all"
                    rows={4}
                  />
                ) : (
                  <Input
                    value={value}
                    onChange={(e) => handleFieldChange(field.key as keyof OriginalResumeData, e.target.value)}
                    placeholder={`請輸入${field.label}`}
                    className="ring-1 ring-primary/20 focus:ring-primary/50 shadow-[0_0_8px_rgba(141,73,3,0.1)] focus:shadow-[0_0_12px_rgba(141,73,3,0.2)] transition-all"
                  />
                )}
              </div>
            );
          })}
        </CardContent>
      </Card>

      <div className="sticky bottom-4 bg-background/95 backdrop-blur-sm border rounded-lg p-4 shadow-lg flex gap-4">
        <Button variant="outline" className="flex-1" onClick={onCancel}>
          取消編輯
        </Button>
        <Button className="flex-1 gradient-primary gap-2" onClick={onSave}>
          <Save className="h-4 w-4" />
          儲存變更
        </Button>
      </div>

      <RightDrawer
        open={showSuggestionsDrawer}
        onClose={() => setShowSuggestionsDrawer(false)}
        title="優化建議參考"
        subtitle="對照修改您的履歷內容"
      >
        <ScrollArea className="h-full pr-4">
          <div className="space-y-6">
            {suggestions.map((s, i) => (
              <div key={i} className="space-y-3 pb-4 border-b border-border last:border-0">
                <h4 className="font-medium text-primary flex items-center gap-2">
                  <ChevronRight className="h-4 w-4" />
                  {s.section}
                </h4>
                <div className="space-y-3">
                  <div className="p-3 bg-muted/50 rounded-lg">
                    <p className="text-xs text-muted-foreground mb-1">原始內容</p>
                    <p className="text-sm">{s.original}</p>
                  </div>
                  <div className="p-3 bg-primary/5 rounded-lg border border-primary/20">
                    <p className="text-xs text-primary mb-1">優化建議</p>
                    <p className="text-sm">{s.optimized}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </RightDrawer>
    </motion.div>
  );
};

// Static color swatches per template (main colors from each scheme)
const templateSwatches: Record<string, string[]> = {
  corporate: ['#1F3A5F', '#2E2E2E', '#6A1B2E', '#1B4332'],
  modern: ['#2563EB', '#374151', '#111111', '#334155'],
  creative: ['#E07A5F', '#6D28D9', '#F97316', '#0F172A'],
};

// Template Selection Phase Component with Thumbnail & Static Swatches
const TemplateSelectionPhase = ({
  onSelect,
  onBack,
}: {
  onSelect: (id: string) => void;
  onBack: () => void;
}) => {
  return (
    <motion.div
      key="templates"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold mb-2">選擇履歷樣板</h2>
        <p className="text-muted-foreground">根據您的職業目標選擇最適合的履歷風格與配色</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {templates.map((template, i) => {
          const swatches = templateSwatches[template.id] || [];

          return (
            <motion.div
              key={template.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              <Card className="overflow-hidden group border-border/60 hover:border-primary/40 hover:shadow-warm transition-all duration-300">
                {/* Template Thumbnail - SVG Wireframe */}
                <div className="w-full aspect-[4/3] bg-[#f5efe8] rounded-t-lg overflow-hidden border-b border-border/40 flex items-center justify-center p-4">
                  <div className="w-[70%] shadow-[inset_0_1px_3px_rgba(0,0,0,0.08),0_2px_8px_rgba(0,0,0,0.06)] border border-gray-200/60 rounded-sm overflow-hidden bg-white group-hover:scale-105 transition-transform duration-300">
                    {(() => {
                      const ThumbnailComponent = templateThumbnailComponents[template.id];
                      return ThumbnailComponent ? <ThumbnailComponent /> : null;
                    })()}
                  </div>
                </div>

                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">{template.name}</CardTitle>
                  <CardDescription className="text-xs">{template.subtitle}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground">{template.description}</p>
                  <ul className="space-y-1">
                    {template.features.map((feature, j) => (
                      <li key={j} className="text-xs flex items-center gap-2 text-muted-foreground">
                        <Check className="h-3 w-3 text-primary" />
                        {feature}
                      </li>
                    ))}
                  </ul>

                  {/* Static Color Swatches (read-only) */}
                  <div className="pt-2 border-t border-border/40">
                    <p className="text-xs text-muted-foreground mb-2">配色方案</p>
                    <div className="flex gap-2.5">
                      {swatches.map((color, j) => (
                        <div
                          key={j}
                          className="h-7 w-7 rounded-full border border-border/60 shadow-sm"
                          style={{ backgroundColor: color }}
                          title={color}
                        />
                      ))}
                    </div>
                  </div>

                  <Button
                    className="w-full gap-2 gradient-primary text-primary-foreground"
                    onClick={() => onSelect(template.id)}
                  >
                    選擇此樣板
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      <div className="flex justify-center pt-4">
        <Button variant="ghost" className="gap-2" onClick={onBack}>
          <ChevronLeft className="h-4 w-4" />
          返回上一步
        </Button>
      </div>
    </motion.div>
  );
};

// Result Phase Component
const ResultPhase = ({
  resumeData,
  selectedTemplate,
  selectedThemeIndex,
  isEditing,
  isDownloading,
  resumeRef,
  onEdit,
  onSave,
  onCancelEdit,
  onDataChange,
  onDownload,
  onBackToTemplates,
  onReset,
  onThemeChange,
}: {
  resumeData: ResumeData;
  selectedTemplate: string;
  selectedThemeIndex: number;
  isEditing: boolean;
  isDownloading: boolean;
  resumeRef: React.RefObject<HTMLDivElement>;
  onEdit: () => void;
  onSave: () => void;
  onCancelEdit: () => void;
  onDataChange: (data: ResumeData) => void;
  onDownload: () => void;
  onBackToTemplates: () => void;
  onReset: () => void;
  onThemeChange: (index: number) => void;
}) => {
  const template = templates.find(t => t.id === selectedTemplate);
  const themes = TEMPLATE_THEMES[selectedTemplate] || TEMPLATE_THEMES.corporate;
  const theme = themes[selectedThemeIndex] || themes[0];

  const handleFieldChange = (field: keyof ResumeData, value: string) => {
    onDataChange({ ...resumeData, [field]: value });
  };

  return (
    <motion.div
      key="result"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <div
            className="h-10 w-10 rounded-lg flex items-center justify-center"
            style={{ backgroundColor: theme.main }}
          >
            {template && <template.icon className="h-5 w-5 text-white" />}
          </div>
          <div>
            <p className="font-medium">{template?.name}</p>
            <p className="text-xs text-muted-foreground">{template?.subtitle}</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">配色：</span>
            <ThemeSwatchSelector
              themes={themes}
              selectedIndex={selectedThemeIndex}
              onChange={onThemeChange}
            />
          </div>

          {!isEditing && (
            <Button variant="outline" size="sm" className="gap-2" onClick={onEdit}>
              <Edit3 className="h-4 w-4" />
              編輯
            </Button>
          )}
        </div>
      </div>

      <Card className={isEditing ? 'ring-2 ring-primary/50 shadow-[0_0_20px_rgba(141,73,3,0.15)]' : ''}>
        <CardContent className="p-6">
          <div ref={resumeRef} className="pdf-container bg-white text-foreground">
            {selectedTemplate === 'corporate' && (
              <CorporateTemplate
                data={resumeData}
                isEditing={isEditing}
                onChange={handleFieldChange}
                theme={theme}
              />
            )}
            {selectedTemplate === 'modern' && (
              <ModernTemplate
                data={resumeData}
                isEditing={isEditing}
                onChange={handleFieldChange}
                theme={theme}
              />
            )}
            {selectedTemplate === 'creative' && (
              <CreativeTemplate
                data={resumeData}
                isEditing={isEditing}
                onChange={handleFieldChange}
                theme={theme}
              />
            )}
          </div>
        </CardContent>
      </Card>

      {isEditing ? (
        <div className="flex gap-4">
          <Button variant="outline" className="flex-1" onClick={onCancelEdit}>取消</Button>
          <Button className="flex-1 gradient-primary gap-2" onClick={onSave}>
            <Save className="h-4 w-4" />儲存
          </Button>
        </div>
      ) : (
        <div className="flex flex-wrap gap-4">
          <Button variant="outline" className="gap-2" onClick={onBackToTemplates}>
            <Palette className="h-4 w-4" />重新選擇樣板
          </Button>
          <Button variant="outline" className="gap-2" onClick={onReset}>
            <RotateCcw className="h-4 w-4" />重新填寫
          </Button>
          <Button
            className="flex-1 gap-2 text-white"
            style={{ backgroundColor: theme.main }}
            onClick={onDownload}
            disabled={isDownloading}
          >
            <Download className="h-4 w-4" />
            {isDownloading ? '生成中...' : '下載履歷'}
          </Button>
        </div>
      )}
    </motion.div>
  );
};

// Editable Field Component
const EditableField = ({
  value,
  onChange,
  isEditing,
  multiline = false,
  className = '',
}: {
  value: string;
  onChange: (value: string) => void;
  isEditing: boolean;
  multiline?: boolean;
  className?: string;
}) => {
  if (!isEditing) {
    return <span className={`whitespace-pre-line ${className}`}>{value}</span>;
  }

  const editClass = 'ring-1 ring-primary/30 shadow-[0_0_8px_rgba(141,73,3,0.2)] transition-shadow';

  if (multiline) {
    return (
      <Textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`${editClass} ${className}`}
        rows={4}
      />
    );
  }

  return (
    <Input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={`${editClass} ${className}`}
    />
  );
};

// Corporate Template with Dynamic Colors - Updated Schema
const CorporateTemplate = ({
  data,
  isEditing,
  onChange,
  theme,
}: {
  data: ResumeData;
  isEditing: boolean;
  onChange: (field: keyof ResumeData, value: string) => void;
  theme: ThemeColors;
}) => (
  <div className="font-serif space-y-6" style={{ color: theme.text }}>
    {/* Header */}
    <div
      className="text-center pb-4 avoid-break"
      data-pdf-section
      style={{ borderBottom: `2px solid ${theme.main}` }}
    >
      <h1 className="text-3xl font-bold tracking-wide" style={{ color: theme.main }}>
        <EditableField value={data.name} onChange={(v) => onChange('name', v)} isEditing={isEditing} />
      </h1>
      <div className="flex justify-center flex-wrap gap-4 mt-2 text-sm" style={{ color: theme.secondary }}>
        <EditableField value={data.email} onChange={(v) => onChange('email', v)} isEditing={isEditing} />
        <span>|</span>
        <EditableField value={data.phone} onChange={(v) => onChange('phone', v)} isEditing={isEditing} />
        {data.linkedin && <><span>|</span><EditableField value={data.linkedin} onChange={(v) => onChange('linkedin', v)} isEditing={isEditing} /></>}
        {data.github && <><span>|</span><EditableField value={data.github} onChange={(v) => onChange('github', v)} isEditing={isEditing} /></>}
      </div>
    </div>

    {data.professional_summary && (
      <div data-pdf-section className="avoid-break">
        <TemplateSectionWithColor title="專業摘要" theme={theme}>
          <EditableField value={data.professional_summary} onChange={(v) => onChange('professional_summary', v)} isEditing={isEditing} multiline />
        </TemplateSectionWithColor>
      </div>
    )}

    <div data-pdf-section className="avoid-break">
      <TemplateSectionWithColor title="學歷" theme={theme}>
        <EditableField value={data.education} onChange={(v) => onChange('education', v)} isEditing={isEditing} multiline />
      </TemplateSectionWithColor>
    </div>

    <div data-pdf-section className="avoid-break">
      <TemplateSectionWithColor title="工作經驗" theme={theme}>
        <EditableField value={data.professional_experience} onChange={(v) => onChange('professional_experience', v)} isEditing={isEditing} multiline />
      </TemplateSectionWithColor>
    </div>

    <div data-pdf-section className="avoid-break">
      <TemplateSectionWithColor title="技能專長" theme={theme}>
        <EditableField value={data.core_skills} onChange={(v) => onChange('core_skills', v)} isEditing={isEditing} />
      </TemplateSectionWithColor>
    </div>

    {data.projects && (
      <div data-pdf-section className="avoid-break">
        <TemplateSectionWithColor title="專案作品集" theme={theme}>
          <EditableField value={data.projects} onChange={(v) => onChange('projects', v)} isEditing={isEditing} multiline />
        </TemplateSectionWithColor>
      </div>
    )}

    {data.autobiography && (
      <div data-pdf-section className="avoid-break">
        <TemplateSectionWithColor title="自傳" theme={theme}>
          <EditableField value={data.autobiography} onChange={(v) => onChange('autobiography', v)} isEditing={isEditing} multiline />
        </TemplateSectionWithColor>
      </div>
    )}
  </div>
);

// Modern Template with Dynamic Colors - Updated Schema
const ModernTemplate = ({
  data,
  isEditing,
  onChange,
  theme,
}: {
  data: ResumeData;
  isEditing: boolean;
  onChange: (field: keyof ResumeData, value: string) => void;
  theme: ThemeColors;
}) => {
  const skills = data.core_skills.split(',').map(s => s.trim());

  return (
    <div className="grid md:grid-cols-[1fr_2.5fr] gap-6">
      {/* Left Sidebar */}
      <div
        className="space-y-6 p-4 rounded-lg avoid-break"
        data-pdf-section
        style={{ backgroundColor: `${theme.main}10` }}
      >
        <div
          className="h-32 w-32 mx-auto rounded-full flex items-center justify-center"
          style={{ backgroundColor: theme.main }}
        >
          <span className="text-4xl font-bold text-white">{data.name.charAt(0)}</span>
        </div>

        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2">
            <Mail className="h-4 w-4" style={{ color: theme.main }} />
            <EditableField value={data.email} onChange={(v) => onChange('email', v)} isEditing={isEditing} className="text-xs" />
          </div>
          <div className="flex items-center gap-2">
            <Phone className="h-4 w-4" style={{ color: theme.main }} />
            <EditableField value={data.phone} onChange={(v) => onChange('phone', v)} isEditing={isEditing} className="text-xs" />
          </div>
          {data.linkedin && (
            <div className="flex items-center gap-2">
              <Linkedin className="h-4 w-4" style={{ color: theme.main }} />
              <EditableField value={data.linkedin} onChange={(v) => onChange('linkedin', v)} isEditing={isEditing} className="text-xs" />
            </div>
          )}
          {data.github && (
            <div className="flex items-center gap-2">
              <Code className="h-4 w-4" style={{ color: theme.main }} />
              <EditableField value={data.github} onChange={(v) => onChange('github', v)} isEditing={isEditing} className="text-xs" />
            </div>
          )}
        </div>

        {/* Skills with Progress Bars */}
        <div className="space-y-3">
          <h3
            className="font-semibold text-sm pb-1"
            style={{ borderBottom: `1px solid ${theme.main}30` }}
          >
            技能專長
          </h3>
          {isEditing ? (
            <EditableField value={data.core_skills} onChange={(v) => onChange('core_skills', v)} isEditing={isEditing} multiline />
          ) : (
            <div className="space-y-2">
              {skills.slice(0, 6).map((skill, i) => (
                <div key={i}>
                  <div className="flex justify-between text-xs mb-1">
                    <span>{skill}</span>
                    <span>{95 - i * 8}%</span>
                  </div>
                  <div className="h-2 rounded-full overflow-hidden" style={{ backgroundColor: `${theme.secondary}30` }}>
                    <div
                      className="h-full rounded-full transition-all"
                      style={{
                        width: `${95 - i * 8}%`,
                        backgroundColor: theme.main,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Right Content */}
      <div className="space-y-6">
        <div data-pdf-section className="avoid-break">
          <h1 className="text-3xl font-bold" style={{ color: theme.main }}>
            <EditableField value={data.name} onChange={(v) => onChange('name', v)} isEditing={isEditing} />
          </h1>
          {data.professional_summary && (
            <p className="mt-1" style={{ color: theme.text }}>
              <EditableField value={data.professional_summary} onChange={(v) => onChange('professional_summary', v)} isEditing={isEditing} multiline />
            </p>
          )}
        </div>

        <div className="space-y-4" data-pdf-section>
          <h3
            className="font-semibold text-lg pb-1 flex items-center gap-2 avoid-break"
            style={{ borderBottom: `1px solid ${theme.main}30` }}
          >
            <Briefcase className="h-4 w-4" style={{ color: theme.main }} />
            工作經驗
          </h3>
          <EditableField value={data.professional_experience} onChange={(v) => onChange('professional_experience', v)} isEditing={isEditing} multiline className="text-sm" />
        </div>

        <div className="space-y-4" data-pdf-section>
          <h3
            className="font-semibold text-lg pb-1 flex items-center gap-2 avoid-break"
            style={{ borderBottom: `1px solid ${theme.main}30` }}
          >
            <GraduationCap className="h-4 w-4" style={{ color: theme.main }} />
            學歷
          </h3>
          <EditableField value={data.education} onChange={(v) => onChange('education', v)} isEditing={isEditing} multiline className="text-sm" />
        </div>

        {data.projects && (
          <div className="space-y-4" data-pdf-section>
            <h3
              className="font-semibold text-lg pb-1 flex items-center gap-2 avoid-break"
              style={{ borderBottom: `1px solid ${theme.main}30` }}
            >
              <FolderOpen className="h-4 w-4" style={{ color: theme.main }} />
              專案作品集
            </h3>
            <EditableField value={data.projects} onChange={(v) => onChange('projects', v)} isEditing={isEditing} multiline className="text-sm" />
          </div>
        )}

        {data.autobiography && (
          <div className="space-y-4" data-pdf-section>
            <h3
              className="font-semibold text-lg pb-1 flex items-center gap-2 avoid-break"
              style={{ borderBottom: `1px solid ${theme.main}30` }}
            >
              <FileText className="h-4 w-4" style={{ color: theme.main }} />
              自傳
            </h3>
            <EditableField value={data.autobiography} onChange={(v) => onChange('autobiography', v)} isEditing={isEditing} multiline className="text-sm" />
          </div>
        )}
      </div>
    </div>
  );
};

// Creative Template with Dynamic Colors - Updated Schema
const CreativeTemplate = ({
  data,
  isEditing,
  onChange,
  theme,
}: {
  data: ResumeData;
  isEditing: boolean;
  onChange: (field: keyof ResumeData, value: string) => void;
  theme: ThemeColors;
}) => (
  <div className="relative">
    <div
      className="absolute inset-0 rounded-lg opacity-10"
      style={{ backgroundColor: theme.main }}
    />

    <div className="relative p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-center gap-6 avoid-break" data-pdf-section>
        <div className="relative">
          <div
            className="h-36 w-36 rounded-full p-1"
            style={{ backgroundColor: theme.main }}
          >
            <div className="h-full w-full rounded-full bg-white flex items-center justify-center">
              <span
                className="text-5xl font-bold"
                style={{ color: theme.main }}
              >
                {data.name.charAt(0)}
              </span>
            </div>
          </div>
          <div
            className="absolute -bottom-2 -right-2 h-8 w-8 rounded-full flex items-center justify-center"
            style={{ backgroundColor: theme.accent }}
          >
            <Sparkles className="h-4 w-4 text-white" />
          </div>
        </div>

        <div className="text-center md:text-left flex-1">
          <h1
            className="text-4xl font-bold"
            style={{ color: theme.main }}
          >
            <EditableField value={data.name} onChange={(v) => onChange('name', v)} isEditing={isEditing} />
          </h1>
          {data.professional_summary && (
            <p className="mt-2" style={{ color: theme.text }}>
              <EditableField value={data.professional_summary} onChange={(v) => onChange('professional_summary', v)} isEditing={isEditing} multiline />
            </p>
          )}
          <div className="flex flex-wrap justify-center md:justify-start gap-4 mt-3 text-sm">
            <span className="flex items-center gap-1" style={{ color: theme.main }}>
              <Mail className="h-4 w-4" />
              <EditableField value={data.email} onChange={(v) => onChange('email', v)} isEditing={isEditing} />
            </span>
            <span className="flex items-center gap-1" style={{ color: theme.secondary }}>
              <Phone className="h-4 w-4" />
              <EditableField value={data.phone} onChange={(v) => onChange('phone', v)} isEditing={isEditing} />
            </span>
            {data.linkedin && (
              <span className="flex items-center gap-1" style={{ color: theme.main }}>
                <Linkedin className="h-4 w-4" />
                <EditableField value={data.linkedin} onChange={(v) => onChange('linkedin', v)} isEditing={isEditing} />
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Content Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        <div data-pdf-section className="avoid-break">
          <CreativeSectionWithColor title="工作經驗" theme={theme}>
            <EditableField value={data.professional_experience} onChange={(v) => onChange('professional_experience', v)} isEditing={isEditing} multiline />
          </CreativeSectionWithColor>
        </div>

        <div data-pdf-section className="avoid-break">
          <CreativeSectionWithColor title="學歷" theme={theme} useSecondary>
            <EditableField value={data.education} onChange={(v) => onChange('education', v)} isEditing={isEditing} multiline />
          </CreativeSectionWithColor>
        </div>
      </div>

      {/* Skills as Pills */}
      <div data-pdf-section className="avoid-break">
        <CreativeSectionWithColor title="技能專長" theme={theme} fullWidth>
          {isEditing ? (
            <EditableField value={data.core_skills} onChange={(v) => onChange('core_skills', v)} isEditing={isEditing} />
          ) : (
            <div className="flex flex-wrap gap-2">
              {data.core_skills.split(',').map((skill, i) => (
                <span
                  key={i}
                  className="px-3 py-1 rounded-full text-sm"
                  style={{
                    backgroundColor: `${theme.accent}20`,
                    color: theme.main,
                  }}
                >
                  {skill.trim()}
                </span>
              ))}
            </div>
          )}
        </CreativeSectionWithColor>
      </div>

      {/* Projects */}
      {data.projects && (
        <div data-pdf-section className="avoid-break">
          <CreativeSectionWithColor title="專案作品集" theme={theme} fullWidth useSecondary>
            <EditableField value={data.projects} onChange={(v) => onChange('projects', v)} isEditing={isEditing} multiline />
          </CreativeSectionWithColor>
        </div>
      )}

      {/* Autobiography */}
      {data.autobiography && (
        <div data-pdf-section className="avoid-break">
          <CreativeSectionWithColor title="自傳" theme={theme} fullWidth>
            <EditableField value={data.autobiography} onChange={(v) => onChange('autobiography', v)} isEditing={isEditing} multiline />
          </CreativeSectionWithColor>
        </div>
      )}
    </div>
  </div>
);

// Template Section Helper with Color
const TemplateSectionWithColor = ({
  title,
  children,
  theme,
}: {
  title: string;
  children: React.ReactNode;
  theme: ThemeColors;
}) => (
  <div>
    <h2
      className="text-lg font-bold pb-1 mb-3"
      style={{
        color: theme.main,
        borderBottom: `1px solid ${theme.main}40`,
      }}
    >
      {title}
    </h2>
    <div className="text-sm">{children}</div>
  </div>
);

// Creative Section Helper with Color
const CreativeSectionWithColor = ({
  title,
  children,
  theme,
  useSecondary = false,
  fullWidth = false,
}: {
  title: string;
  children: React.ReactNode;
  theme: ThemeColors;
  useSecondary?: boolean;
  fullWidth?: boolean;
}) => (
  <div
    className={`p-4 rounded-lg bg-white/50 dark:bg-white/5 ${fullWidth ? 'col-span-full' : ''}`}
    style={{ borderLeft: `4px solid ${useSecondary ? theme.secondary : theme.main}` }}
  >
    <h3
      className="font-semibold mb-3"
      style={{ color: useSecondary ? theme.secondary : theme.main }}
    >
      {title}
    </h3>
    <div className="text-sm">{children}</div>
  </div>
);

export default Optimize;

import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Download, Save, Palette, Briefcase, GraduationCap, Mail, Phone, User, Star, Sparkles, ChevronLeft, Target, Check, CheckCircle, AlertTriangle, ListChecks } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AILoadingSpinner, AnalysisSkeleton } from '@/components/loading/LoadingStates';
import { useAppState } from '@/contexts/AppContext';
import LoginRequired from '@/components/gatekeeper/LoginRequired';
import AlertModal from '@/components/modals/AlertModal';
import { motion, AnimatePresence } from 'framer-motion';
import logoCat from '@/assets/logocat.png';
import { mockResumeData } from '@/mocks/resumes';

type Phase = 'initial' | 'analyzing' | 'suggestions' | 'templates' | 'generating' | 'result';

const TEMPLATE_THEMES: Record<string, any[]> = {
  corporate: [{ name: '深海藍經典', main: '#1F3A5F', secondary: '#4A6FA5' }],
  modern: [{ name: '科技藍', main: '#2563EB', secondary: '#1E3A8A' }],
  creative: [{ name: '莫蘭迪粉橘', main: '#E07A5F', secondary: '#C9604A' }],
};

// ==========================================
// 🌟 核心新增：動態診斷生成器 (Dynamic Diagnosis Generator)
// 它會讀取你上傳的真實履歷，把你的經歷、學歷、技能截取出來，組成專屬的診斷報告！
// ==========================================
const generateDynamicDiagnosis = (data: any) => {
  // 安全地擷取真實履歷的一小段內容來當作「原文內容」
  const expSnippet = data.experience && data.experience.length > 10
    ? data.experience.slice(0, 60) + "..."
    : "缺乏具體的工作經歷描述";

  const skillsSnippet = data.skills && data.skills.length > 5
    ? data.skills.slice(0, 40) + "..."
    : "尚未填寫完整的技能清單";

  const eduSnippet = data.education ? data.education.split('\n')[0] : "相關學歷背景";

  return {
    candidate_positioning: `以「${data.name}」目前的背景來看，具備 ${eduSnippet} 的基礎，並擁有相關的實務經歷。若目標是往資深職位發展，在「技術影響力」與「專案量化成效」上還有凸顯的空間。`,
    target_role_gap_summary: `目前的履歷雖然列出了基本經歷與技能，但在「量化成果（如：提升多少效率）」的展現上稍顯薄弱。建議強化 STAR 敘事法，將會大幅提升 ATS 系統與 HR 的篩選通過率。`,
    overall_strengths: [
      `具備清晰的教育背景 (${eduSnippet.slice(0, 20)}...)`,
      `已羅列出專業技能 (${skillsSnippet.slice(0, 15)}...)，具備發展潛力`,
      `經歷描述具備基礎框架，段落分明`
    ],
    overall_weaknesses: [
      "工作經歷描述過於偏向「職責條列」，缺乏 STAR 結構化敘事",
      "技能列表僅為名詞堆疊，缺乏「熟練度分級」與「實際應用場景」",
      "缺少個人價值主張（Summary），難以在第一時間抓住面試官眼球"
    ],
    critical_issues: [
      {
        section: "工作經歷",
        severity: "嚴重扣分",
        original_text: expSnippet,
        issue_reason: "使用了過於平鋪直敘的語氣，未描述專案規模、面臨的挑戰與最終數據成果。面試官無法據此評估您的實際戰力。",
        improvement_direction: "改用「強動詞開頭 + 量化指標」，例如：「主導/參與 XXX 專案，運用 XXX 技術重構架構，使效能提升 40%」"
      },
      {
        section: "技能專長",
        severity: "明顯扣分",
        original_text: skillsSnippet,
        issue_reason: "技能以單字平鋪列出，無法區分「核心專長」與「輔助技能」。雖然能命中 ATS 關鍵字，但無法展現技術深度。",
        improvement_direction: "建議分類呈現，例如：「核心技能：XXX (3年)、XXX (2年)」、「熟悉工具：XXX、XXX」"
      }
    ],
    recommended_next_actions: [
      "使用 STAR 法則重新撰寫每一段工作經歷，確保每項都有「量化成果」",
      "將技能專長依據重要性進行分類，並標註熟練度或年資",
      "在履歷最上方增加一段 50 字的「個人專業摘要 (Summary)」",
      "針對心儀職缺的 JD 關鍵字，在履歷中增加對應描述以提升契合度"
    ]
  };
};

const Optimize = () => {
  const navigate = useNavigate();
  const { user, avatarUrl } = useAppState();

  const realUserId = user?.user_id || user?.id;

  const [phase, setPhase] = useState<Phase>('initial');
  const [realLatestResume, setRealLatestResume] = useState<any>(null);
  const [originalData, setOriginalData] = useState<any>({ name: '資料讀取中...' });
  const [resumeData, setResumeData] = useState<any>({});
  const [diagnosticResult, setDiagnosticResult] = useState<any>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('modern');
  const [selectedThemeIndex] = useState<number>(0);

  const [showAccessAlert, setShowAccessAlert] = useState(false);
  const [accessAlertMessage, setAccessAlertMessage] = useState('');
  const [isLoadingDB, setIsLoadingDB] = useState(true);
  const resumeRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchRealDatabaseResume = async () => {
      if (!realUserId) {
        setAccessAlertMessage('找不到使用者 ID，請重新登入');
        setShowAccessAlert(true);
        return;
      }

      try {
        const response = await fetch(`/api/resume_process/list/${realUserId}`);
        const result = await response.json();

        if (result.status === 'success' && result.data && result.data.length > 0) {
          const latest = result.data.sort((a: any, b: any) =>
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          )[0];

          console.log("✅ [真實連線] 從 Supabase 撈到的最新履歷:", latest);
          setRealLatestResume(latest);

          let raw = latest.resume_data || latest.structured_data || {};
          if (typeof raw === 'string') { try { raw = JSON.parse(raw); } catch { raw = {}; } }

          let flat: any = { ...raw };
          if (raw.data) Object.assign(flat, raw.data);
          if (raw.resume_data) Object.assign(flat, raw.resume_data);

          const safeStr = (v: any) => {
            if (!v) return '';
            if (typeof v === 'string') return v;
            if (Array.isArray(v)) return v.map(i => typeof i === 'string' ? i : Object.values(i).join(' - ')).join('\n\n');
            return String(v);
          };

          const mappedData = {
            name: flat.name || flat.full_name || '未辨識',
            email: flat.email || '',
            phone: flat.phone || '',
            education: safeStr(flat.education),
            experience: safeStr(flat.experience || flat.work_experience),
            skills: Array.isArray(flat.skills) ? flat.skills.join(', ') : safeStr(flat.skills),
            autobiography: flat.autobiography || flat.summary || flat.bio || '',
          };

          setOriginalData(mappedData);
          setResumeData({
            ...mockResumeData,
            ...mappedData,
            professional_experience: mappedData.experience,
            core_skills: mappedData.skills,
          });
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
  }, [realUserId]);

  const handleSaveOptimization = async () => {
    try {
      const payload = {
        user_id: realUserId,
        original_resume_id: realLatestResume?.resume_id || realLatestResume?.id,
        template_id: selectedTemplate,
        optimized_data: resumeData,
      };

      console.log("🚀 準備存入 resume_optimization 的資料:", payload);

      const response = await fetch('/api/resume_process/optimize/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      if (response.ok) {
        alert("🎉 優化版履歷已成功儲存至資料庫！");
      } else {
        alert("儲存失敗：" + (result.message || result.error));
      }
    } catch (error) {
      console.error("儲存優化履歷失敗:", error);
      alert("網路連線錯誤，儲存失敗！");
    }
  };

  const handleStartOptimize = async () => {
    setPhase('analyzing');
    // 模擬 AI 分析時間
    await new Promise(r => setTimeout(r, 2000));

    // 🌟 關鍵修改：呼叫動態生成器，將真實資料 (originalData) 餵給它！
    const dynamicReport = generateDynamicDiagnosis(originalData);
    setDiagnosticResult(dynamicReport);

    setPhase('suggestions');
  };

  if (isLoadingDB) {
    return <div className="flex h-screen items-center justify-center"><AILoadingSpinner message="正在與 Supabase 連線撈取資料..." /></div>;
  }

  return (
    <LoginRequired>
      <div className="container py-12 animate-fade-in">
        <AlertModal
          open={showAccessAlert}
          onClose={() => { setShowAccessAlert(false); navigate(-1); }}
          type="warning"
          title="系統提示"
          message={accessAlertMessage}
          confirmLabel="返回上傳"
        />

        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-6">
            <FileText className="h-8 w-8 text-primary" />
          </div>
          <h1 className="text-3xl font-bold mb-4">履歷優化</h1>
          <p className="text-muted-foreground">AI 智能分析您的履歷，生成精美履歷並儲存</p>
        </div>

        <div className="max-w-4xl mx-auto">
          <AnimatePresence mode="wait">

            {/* 階段 1：顯示真實資料 */}
            {phase === 'initial' && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-6">
                <div className="flex items-center gap-3 p-4 rounded-lg border border-green-500/30 bg-green-500/5">
                  <Check className="h-5 w-5 text-green-600 shrink-0" />
                  <p className="text-sm">成功從資料庫讀取您的真實履歷：<span className="font-semibold text-foreground">「{realLatestResume?.resume_name || '未命名'}」</span></p>
                </div>
                <Card>
                  <CardHeader><CardTitle className="flex items-center gap-2"><User className="h-5 w-5 text-primary" /> 您的履歷資料</CardTitle></CardHeader>
                  <CardContent className="space-y-6">
                    <div className="flex items-center gap-6">
                      <div className="h-20 w-20 rounded-full bg-muted flex items-center justify-center shrink-0 border-2 border-primary/10"><User className="h-10 w-10 text-muted-foreground" /></div>
                      <div className="flex-1">
                        <h3 className="text-2xl font-bold text-foreground">{originalData.name}</h3>
                        <p className="text-sm text-muted-foreground">{originalData.email} | {originalData.phone}</p>
                      </div>
                    </div>
                    <div className="grid gap-4 mt-6">
                      <div className="p-4 bg-muted/30 rounded-lg border"><p className="font-bold text-primary text-xs uppercase mb-2">教育背景</p><p className="text-sm whitespace-pre-line">{originalData.education}</p></div>
                      <div className="p-4 bg-muted/30 rounded-lg border"><p className="font-bold text-primary text-xs uppercase mb-2">工作經歷</p><p className="text-sm whitespace-pre-line">{originalData.experience}</p></div>
                    </div>
                  </CardContent>
                </Card>
                <div className="flex justify-center"><Button size="lg" className="gradient-primary h-14 px-8 text-lg" onClick={handleStartOptimize}><Sparkles className="mr-2 h-5 w-5" /> 開始 AI 分析優化</Button></div>
              </motion.div>
            )}

            {/* 階段 2：分析中動畫 */}
            {phase === 'analyzing' && (
              <motion.div key="analyzing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="text-center py-10">
                <AILoadingSpinner message="AI 正在深度診斷您的履歷中..." /><AnalysisSkeleton />
              </motion.div>
            )}

            {/* 🌟 階段 3：滿血版優化建議 UI (資料已動態替換) */}
            {phase === 'suggestions' && diagnosticResult && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                <div className="flex items-center justify-between">
                  <Button variant="ghost" className="gap-2 -ml-2" onClick={() => setPhase('initial')}>
                    <ChevronLeft className="h-4 w-4" />
                    返回上一步
                  </Button>
                </div>

                <Card className="border-primary/20 shadow-md">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2"><Target className="h-5 w-5 text-primary" /> 核心定位分析</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="p-4 rounded-lg bg-primary/5 border border-primary/15">
                      <h4 className="text-sm font-semibold text-primary mb-2">候選人定位</h4>
                      <p className="text-sm leading-relaxed">{diagnosticResult.candidate_positioning}</p>
                    </div>
                    <div className="p-4 rounded-lg bg-muted/40 border border-border">
                      <h4 className="text-sm font-semibold text-foreground mb-2">目標職位落差摘要</h4>
                      <p className="text-sm text-muted-foreground leading-relaxed">{diagnosticResult.target_role_gap_summary}</p>
                    </div>
                  </CardContent>
                </Card>

                <div className="grid md:grid-cols-2 gap-4">
                  <Card className="border-green-200/60">
                    <CardHeader className="pb-3"><CardTitle className="text-base flex items-center gap-2 text-green-700"><CheckCircle className="h-5 w-5" /> 整體優勢</CardTitle></CardHeader>
                    <CardContent className="space-y-3">
                      {diagnosticResult.overall_strengths?.map((s: any, i: any) => (
                        <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-green-50/60">
                          <CheckCircle className="h-4 w-4 text-green-600 shrink-0 mt-0.5" />
                          <p className="text-sm leading-relaxed">{s}</p>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                  <Card className="border-primary/20">
                    <CardHeader className="pb-3"><CardTitle className="text-base flex items-center gap-2 text-primary"><AlertTriangle className="h-5 w-5" /> 待改善項目</CardTitle></CardHeader>
                    <CardContent className="space-y-3">
                      {diagnosticResult.overall_weaknesses?.map((w: any, i: any) => (
                        <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-primary/5">
                          <AlertTriangle className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                          <p className="text-sm leading-relaxed">{w}</p>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                </div>

                {diagnosticResult.critical_issues && diagnosticResult.critical_issues.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2"><Sparkles className="h-5 w-5 text-primary" /> 關鍵問題診斷</CardTitle>
                      <CardDescription>針對履歷各區塊的深度分析與改善方向</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-5">
                      {diagnosticResult.critical_issues.map((issue: any, i: any) => {
                        const severityColors: Record<string, string> = {
                          '嚴重扣分': 'bg-red-100 text-red-800 border-red-200', '明顯扣分': 'bg-amber-100 text-amber-800 border-amber-200', '中度扣分': 'bg-orange-100 text-orange-800 border-orange-200', '輕微扣分': 'bg-yellow-100 text-yellow-800 border-yellow-200',
                        };
                        return (
                          <div key={i} className="rounded-lg border border-border overflow-hidden">
                            <div className="flex items-center gap-3 px-4 py-3 bg-muted/30 border-b border-border">
                              <span className="font-medium text-sm">{issue.section}</span>
                              <span className={`text-xs px-2 py-0.5 rounded border ${severityColors[issue.severity] || 'bg-muted'}`}>{issue.severity}</span>
                            </div>
                            <div className="p-4 space-y-4">
                              <div className="p-3 rounded-md bg-muted/40 border"><p className="text-xs text-muted-foreground mb-1">原文內容</p><p className="text-sm">{issue.original_text}</p></div>
                              <div><p className="text-xs text-muted-foreground mb-1">診斷分析</p><p className="text-sm">{issue.issue_reason}</p></div>
                              <div className="p-3 rounded-md bg-primary/5 border border-primary/15"><p className="text-xs text-primary mb-1 font-semibold">優化方向</p><p className="text-sm font-medium text-primary">{issue.improvement_direction}</p></div>
                            </div>
                          </div>
                        );
                      })}
                    </CardContent>
                  </Card>
                )}

                {diagnosticResult.recommended_next_actions && diagnosticResult.recommended_next_actions.length > 0 && (
                  <Card className="bg-[#fbf1e8]/40 border-primary/15">
                    <CardHeader><CardTitle className="flex items-center gap-2"><ListChecks className="h-5 w-5 text-primary" /> 後續行動計畫</CardTitle></CardHeader>
                    <CardContent className="space-y-3">
                      {diagnosticResult.recommended_next_actions.map((action: any, i: any) => (
                        <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-background/80 border border-border/50">
                          <div className="h-6 w-6 rounded-full bg-primary/10 text-primary flex items-center justify-center shrink-0 text-xs font-bold mt-0.5">{i + 1}</div>
                          <p className="text-sm leading-relaxed">{action}</p>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}

                <div className="flex gap-4 pt-4">
                  <Button variant="outline" className="flex-1 h-12"><Download className="mr-2 h-4 w-4" /> 下載建議報告</Button>
                  <Button className="flex-[2] h-12 gradient-primary text-lg" onClick={() => setPhase('templates')}><Palette className="mr-2 h-5 w-5" /> 選擇樣板並生成優化履歷</Button>
                </div>
              </motion.div>
            )}

            {/* 階段 4：選擇樣板 */}
            {phase === 'templates' && (
              <div className="grid md:grid-cols-3 gap-6">
                {['corporate', 'modern', 'creative'].map(id => (
                  <Card key={id} className="p-6 cursor-pointer hover:border-primary hover:shadow-warm transition-all" onClick={() => { setSelectedTemplate(id); setPhase('generating'); setTimeout(() => setPhase('result'), 1500); }}>
                    <div className="h-40 bg-muted mb-4 rounded-lg flex items-center justify-center uppercase font-black text-muted-foreground/30">{id}</div>
                    <Button variant="outline" className="w-full">使用此樣板</Button>
                  </Card>
                ))}
              </div>
            )}

            {/* 階段 5：優化結果與儲存 */}
            {phase === 'result' && (
              <div className="space-y-6">
                <Card className="shadow-2xl overflow-hidden"><CardContent className="p-8 bg-white"><div ref={resumeRef} className="text-black max-w-[800px] mx-auto min-h-[600px]">
                  <h1 className="text-4xl font-black border-b-4 pb-4 mb-8" style={{ color: TEMPLATE_THEMES[selectedTemplate][0].main, borderColor: TEMPLATE_THEMES[selectedTemplate][0].main }}>{resumeData.name}</h1>
                  <div className="grid md:grid-cols-[200px_1fr] gap-10">
                    <div className="space-y-6">
                      <div className="h-44 w-44 rounded-full overflow-hidden border-4 shadow-lg" style={{ borderColor: TEMPLATE_THEMES[selectedTemplate][0].main }}><img src={avatarUrl || logoCat} className="w-full h-full object-cover" /></div>
                      <div className="space-y-2 text-sm text-gray-600">
                        <p className="flex items-center gap-2"><Mail className="h-4 w-4" /> {resumeData.email}</p>
                        <p className="flex items-center gap-2"><Phone className="h-4 w-4" /> {resumeData.phone}</p>
                      </div>
                    </div>
                    <div className="space-y-8">
                      <section><h3 className="text-lg font-bold border-b-2 mb-4" style={{ color: TEMPLATE_THEMES[selectedTemplate][0].main, borderColor: `${TEMPLATE_THEMES[selectedTemplate][0].main}30` }}>工作經歷</h3><p className="text-sm whitespace-pre-line leading-relaxed text-gray-700">{resumeData.professional_experience}</p></section>
                      <section><h3 className="text-lg font-bold border-b-2 mb-4" style={{ color: TEMPLATE_THEMES[selectedTemplate][0].main, borderColor: `${TEMPLATE_THEMES[selectedTemplate][0].main}30` }}>教育背景</h3><p className="text-sm whitespace-pre-line leading-relaxed text-gray-700">{resumeData.education}</p></section>
                    </div>
                  </div>
                </div></CardContent></Card>
                <div className="flex gap-4">
                  <Button variant="outline" className="flex-1 h-12" onClick={() => setPhase('templates')}><Palette className="mr-2" />更換樣板</Button>
                  <Button onClick={handleSaveOptimization} className="flex-[2] h-12 bg-green-600 hover:bg-green-700 text-white text-lg font-bold"><Save className="mr-2" /> 儲存至優化資料庫</Button>
                  <Button className="flex-[2] h-12 gradient-primary text-lg font-bold"><Download className="mr-2" /> 下載 PDF</Button>
                </div>
              </div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </LoginRequired>
  );
};

export default Optimize;
import { useState, useCallback, useMemo } from "react";
import { Radar, FileText, BookOpen, TrendingUp, RefreshCw, Target, Shield, AlertTriangle, Zap, ShieldAlert, Clock, CalendarDays, CalendarRange, ScanSearch } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { motion, AnimatePresence } from "framer-motion";
import logoImage from "@/assets/logo.png";
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Radar as RechartsRadar } from "recharts";
import { useResumes } from "@/contexts/ResumeContext";
import { getMyUserId } from "@/services/memberService";
import { generateAnalysis } from "@/services/analysisService";
import type { AnalysisResult } from "@/types/analysis";
import { parseSWOT } from "@/types/analysis";

const ANALYSIS_DONE_KEY = "skills-analysis-done";
const ANALYSIS_RESULT_KEY = "skills-analysis-result";

const Skills = () => {
  const { resumes } = useResumes();
  const [phase, setPhase] = useState<"idle" | "loading" | "done">(() =>
    localStorage.getItem(ANALYSIS_DONE_KEY) === "true" ? "done" : "idle"
  );
  const [loadingMsg, setLoadingMsg] = useState("正在生成個人化建議...");

  const [analysisResult, setAnalysisResult] = useState<any>(() => {
    try {
      const saved = localStorage.getItem(ANALYSIS_RESULT_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch { return null; }
  });

  // 🌟 核心修復：根據你的 Console Log 對齊資料路徑
  const radarData = analysisResult?.radar_chart?.dimensions || [];
  const coreInsight = analysisResult?.preliminary_summary?.core_insight || "分析完成";
  const targetPos = analysisResult?.gap_analysis?.target_position || {};

  // 🌟 修正點：action_plan 直接從頂層拿，不再從 gap_analysis 拿
  const plans = analysisResult?.action_plan || {};

  const swot = useMemo(() => parseSWOT(targetPos?.gap_description || ""), [targetPos?.gap_description]);

  const latestResumeId = useMemo(() => {
    if (resumes.length === 0) return null;
    return [...resumes].sort((a, b) => b.updatedAt.localeCompare(a.updatedAt))[0].id;
  }, [resumes]);

  const startAnalysis = useCallback(async () => {
    setPhase("loading");
    try {
      const userId = await getMyUserId();
      const resumeId = latestResumeId;

      const animation = (async () => {
        const msgs = ["正在解析履歷...", "正在計算落差...", "正在生成建議..."];
        for (const m of msgs) {
          setLoadingMsg(m);
          await new Promise(r => setTimeout(r, 1500));
        }
      })();

      const apiReq = generateAnalysis({ user_id: String(userId), resume_id: Number(resumeId ?? 0) });
      const [, result] = await Promise.all([animation, apiReq]);

      if (result) {
        setAnalysisResult(result);
        localStorage.setItem(ANALYSIS_RESULT_KEY, JSON.stringify(result));
        localStorage.setItem(ANALYSIS_DONE_KEY, "true");
        setPhase("done");
      }
    } catch (error: any) {
      alert(`分析失敗：${error.message}`);
      setPhase("idle");
    }
  }, [latestResumeId]);

  const handleReAnalyse = () => {
    localStorage.removeItem(ANALYSIS_DONE_KEY);
    startAnalysis();
  };

  if (phase === "idle") return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="max-w-md w-full p-8 text-center space-y-6 shadow-xl">
        <div className="h-20 w-20 mx-auto rounded-full bg-orange-50 flex items-center justify-center"><ScanSearch className="h-10 w-10 text-orange-700" /></div>
        <h2 className="text-2xl font-bold text-gray-800">開始職能深度診斷</h2>
        <p className="text-gray-500">我們將串接 CrewAI 根據您的真實履歷產出後端分析報告。</p>
        <Button onClick={startAnalysis} className="w-full bg-gradient-to-r from-orange-700 to-orange-500 hover:opacity-90 py-6 text-lg"><Radar className="mr-2" /> 啟動 AI 導航</Button>
      </Card>
    </div>
  );

  if (phase === "loading") return (
    <div className="min-h-screen flex flex-col items-center justify-center space-y-8">
      <motion.img src={logoImage} className="h-24" animate={{ scale: [1, 1.1, 1] }} transition={{ repeat: Infinity, duration: 2 }} />
      <p className="text-xl font-medium text-orange-800 animate-pulse">{loadingMsg}</p>
      <div className="w-64 h-2 bg-gray-100 rounded-full overflow-hidden"><motion.div className="h-full bg-orange-600" initial={{ width: 0 }} animate={{ width: "100%" }} transition={{ duration: 8 }} /></div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50/50 container py-12 space-y-10">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold flex items-center gap-3 text-gray-800"><Radar className="text-orange-700" /> 職能圖譜分析完成</h1>
        <Button variant="outline" onClick={handleReAnalyse} className="border-orange-200 text-orange-800 hover:bg-orange-50"><RefreshCw size={16} className="mr-2" /> 重新生成</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-2 shadow-sm">
          <CardHeader><CardTitle className="text-lg flex items-center gap-2 text-orange-800"><TrendingUp size={20} /> 核心洞察</CardTitle></CardHeader>
          <CardContent className="bg-orange-50/50 m-4 rounded-xl p-6 border border-orange-100">
            <p className="leading-relaxed text-gray-700 font-medium whitespace-pre-wrap">{coreInsight}</p>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader><CardTitle className="text-lg flex items-center gap-2 text-orange-800"><Target size={20} /> 目標匹配</CardTitle></CardHeader>
          <CardContent className="text-center space-y-6 pt-4">
            <div className="text-6xl font-black text-orange-700">{targetPos?.match_score || 0}%</div>
            <div>
              <p className="text-gray-500 text-sm mb-1">目標職位</p>
              <p className="font-bold text-xl text-gray-800">{targetPos?.role || "未指定"}</p>
            </div>
            <Progress value={parseInt(String(targetPos?.match_score || 0))} className="h-3" />
          </CardContent>
        </Card>
      </div>

      <Card className="shadow-sm overflow-hidden">
        <CardHeader className="border-b bg-white"><CardTitle className="text-gray-800">六維職能分佈</CardTitle></CardHeader>
        <CardContent className="h-[450px] pt-10">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData}>
              <PolarGrid stroke="#e5e7eb" />
              <PolarAngleAxis dataKey="axis" tick={{ fill: '#4b5563', fontSize: 14, fontWeight: 500 }} />
              <PolarRadiusAxis domain={[0, 5]} tick={false} axisLine={false} />
              <RechartsRadar name="您的實力" dataKey="score" stroke="#c2410c" fill="#ea580c" fillOpacity={0.5} strokeWidth={3} />
            </RadarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { l: "技術優勢", i: Shield, t: swot.strengths, c: "text-emerald-700", bg: "bg-emerald-50" },
          { l: "待補足點", i: AlertTriangle, t: swot.weaknesses, c: "text-amber-700", bg: "bg-amber-50" },
          { l: "發展機會", i: Zap, t: swot.opportunities, c: "text-blue-700", bg: "bg-blue-50" },
          { l: "潛在威脅", i: ShieldAlert, t: swot.threats, c: "text-rose-700", bg: "bg-rose-50" },
        ].map(item => (
          <Card key={item.l} className={`${item.bg} border-none shadow-sm`}>
            <CardContent className="pt-6 space-y-3">
              <div className={`p-2 w-fit rounded-lg bg-white shadow-sm ${item.c}`}><item.i size={20} /></div>
              <div className={`font-bold text-lg ${item.c}`}>{item.l}</div>
              <p className="text-sm text-gray-600 leading-relaxed">{item.t || "尚無分析"}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="shadow-sm">
        <CardHeader><CardTitle className="flex items-center gap-2 text-orange-800"><BookOpen size={20} /> 職涯行動計畫</CardTitle></CardHeader>
        <CardContent className="p-6 space-y-6">
          {[
            { l: "短期計畫 (1-3個月)", t: plans.short_term, i: Clock, color: "text-orange-600" },
            { l: "中期計畫 (3-6個月)", t: plans.mid_term, i: CalendarDays, color: "text-orange-700" },
            { l: "長期計畫 (6個月以上)", t: plans.long_term, i: CalendarRange, color: "text-orange-800" },
          ].map(p => (
            <div key={p.l} className="flex gap-4 p-4 rounded-xl border border-gray-100 hover:border-orange-200 transition-colors">
              <div className={`shrink-0 ${p.color}`}><p.i size={24} /></div>
              <div className="space-y-1">
                <div className="font-bold text-gray-800">{p.l}</div>
                <p className="text-gray-600 text-sm leading-relaxed">{p.t || "計畫生成中..."}</p>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
};

export default Skills;
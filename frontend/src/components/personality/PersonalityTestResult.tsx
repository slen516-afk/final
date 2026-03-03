import { BarChart3, RefreshCw, Zap, Battery, Target } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
} from 'recharts';
import type { PersonalityResult } from '@/data/personalityScoring';
import { DIMENSIONS, DIMENSION_LABELS } from '@/data/personalityScoring';
import { getArchetypeDetail } from '@/data/archetypeDetails';

interface Props {
  result: PersonalityResult;
  onReset: () => void;
}


const DIMENSION_FULL_LABELS: Record<string, string> = {
  structure: '架構能力',
  ambiguity: '模糊耐受度',
  decision: '決策傾向',
  learning: '錯誤修正與學習',
  transfer: '敘事遷移能力',
};

const PersonalityTestResult = ({ result, onReset }: Props) => {
  const navigate = useNavigate();
  const { scaledScores, archetypes } = result;
  const primaryArchetype = archetypes[0];
  const secondaryArchetypes = archetypes.slice(1);
  const detail = getArchetypeDetail(primaryArchetype.id);
  const { bgColor, accentColor, accentColorLight, cardShadow } = detail;

  const radarData = DIMENSIONS.map((dim) => ({
    dimension: DIMENSION_LABELS[dim],
    score: scaledScores[dim],
    fullMark: 100,
  }));

  const cardClass = "rounded-2xl border-0 bg-white transition-shadow duration-500";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6 transition-colors duration-500"
      style={{ backgroundColor: bgColor, borderRadius: '1rem', padding: '1.5rem' }}
    >



      {/* Hero Section */}
      <div className="text-center mb-2">
        <h1 className="text-2xl md:text-3xl font-bold mb-1" style={{ color: '#000000' }}>
          個人天賦結構分析報告
        </h1>
        <p className="text-sm text-muted-foreground">探索你的低耗能高產出模式</p>
      </div>

      {/* Primary Archetype Card */}
      <Card className={cardClass} style={{ boxShadow: cardShadow }}>
        <CardContent className="p-6 md:p-8 text-center">
          <motion.img
            key={detail.image}
            src={detail.image}
            alt={detail.name}
            className="w-28 h-28 md:w-36 md:h-36 object-contain mb-4 mx-auto block"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          />
          <p className="text-xs text-muted-foreground mb-1 tracking-widest uppercase">主要天賦原型</p>
          <h2 className="text-xl md:text-2xl font-bold mb-1">{primaryArchetype.name}</h2>
          <p className="text-xs text-muted-foreground mb-3">{detail.englishName}</p>

          {secondaryArchetypes.length > 0 && (
            <div className="pt-3 border-t border-border/40">
              <p className="text-xs text-muted-foreground mb-2">次要天賦原型</p>
              <div className="flex flex-wrap justify-center gap-2">
                {secondaryArchetypes.map((a) => {
                  const secDetail = getArchetypeDetail(a.id);
                  return (
                    <span
                      key={a.id}
                      className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium transition-colors duration-500"
                      style={{ backgroundColor: secDetail.accentColorLight, color: secDetail.accentColor }}
                    >
                      {a.name}
                    </span>
                  );
                })}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Radar Chart */}
      <Card className={cardClass} style={{ boxShadow: cardShadow }}>
        <CardContent className="p-6 md:p-8">
          <h3 className="text-base font-semibold text-center mb-1">五大認知指標</h3>
          <p className="text-xs text-muted-foreground text-center mb-4">各維度標準化分數（0-100）</p>
          <div className="w-full h-[260px] md:h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                <PolarGrid stroke="#dabea8" />
                <PolarAngleAxis
                  dataKey="dimension"
                  tick={{ fill: 'hsl(23, 21%, 33%)', fontSize: 11, fontWeight: 500 }}
                />
                <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar
                  name="分數"
                  dataKey="score"
                  stroke={accentColor}
                  fill={accentColor}
                  fillOpacity={0.2}
                  strokeWidth={2}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-muted-foreground text-center mt-3 italic">
            「分數高低不代表能力優劣，而代表你在該類情境下的<strong>心理耗能與穩定度差異</strong>。」
          </p>
        </CardContent>
      </Card>

      {/* Score Bars */}
      <Card className={cardClass} style={{ boxShadow: cardShadow }}>
        <CardContent className="p-6 md:p-8 space-y-4">
          <h3 className="text-base font-semibold text-center mb-2">各維度標準化分數</h3>
          {DIMENSIONS.map((dim) => (
            <div key={dim} className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground font-medium">{DIMENSION_FULL_LABELS[dim]}</span>
                <span className="font-semibold">{scaledScores[dim]}</span>
              </div>
              <div className="h-2.5 rounded-full bg-muted overflow-hidden">
                <motion.div
                  className="h-full rounded-full transition-colors duration-500"
                  style={{ backgroundColor: accentColor }}
                  initial={{ width: 0 }}
                  animate={{ width: `${scaledScores[dim]}%` }}
                  transition={{ duration: 0.8, delay: 0.1 }}
                />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Archetype Cat Card */}
      <Card className={`${cardClass} overflow-hidden`} style={{ boxShadow: cardShadow }}>
        <CardContent className="p-0">
          <div className="p-6 md:p-8 text-center border-b border-border/30">
            <h3 className="text-base font-semibold mb-1">主要工作適配模式</h3>
            <p className="text-xs text-muted-foreground">
              以下說明你在不同工作情境中的自然反應模式，並非行為規範。
            </p>
          </div>

          <div className="flex flex-col items-center p-6 md:p-8">
            <div className="w-full space-y-4 text-left">
              {/* Strength */}
              <div
                className="flex items-start gap-3 p-4 rounded-xl transition-colors duration-500"
                style={{ backgroundColor: accentColorLight }}
              >
                <Zap className="h-5 w-5 mt-0.5 shrink-0 transition-colors duration-500" style={{ color: accentColor }} />
                <div>
                  <p className="text-sm font-semibold mb-1">核心優勢</p>
                  <p className="text-sm text-muted-foreground leading-relaxed">{detail.strength}</p>
                </div>
              </div>

              {/* Energy Cost */}
              <div
                className="flex items-start gap-3 p-4 rounded-xl transition-colors duration-500"
                style={{ backgroundColor: accentColorLight }}
              >
                <Battery className="h-5 w-5 mt-0.5 shrink-0 transition-colors duration-500" style={{ color: accentColor }} />
                <div>
                  <p className="text-sm font-semibold mb-1">耗能特徵</p>
                  <p className="text-sm text-muted-foreground leading-relaxed">{detail.energyCost}</p>
                </div>
              </div>

              {/* Scenarios */}
              <div
                className="flex items-start gap-3 p-4 rounded-xl transition-colors duration-500"
                style={{ backgroundColor: accentColorLight }}
              >
                <Target className="h-5 w-5 mt-0.5 shrink-0 transition-colors duration-500" style={{ color: accentColor }} />
                <div>
                  <p className="text-sm font-semibold mb-1">適配情境</p>
                  <ul className="space-y-1">
                    {detail.scenarios.map((s, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex items-center gap-2">
                        <span
                          className="w-1.5 h-1.5 rounded-full shrink-0 transition-colors duration-500"
                          style={{ backgroundColor: accentColor }}
                        />
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <Button
          onClick={() => navigate('/analysis/skills')}
          className="h-12 text-white transition-colors duration-500"
          style={{ backgroundColor: accentColor }}
        >
          <BarChart3 className="h-4 w-4 mr-2" />
          查看職能圖譜
        </Button>
        <Button
          variant="outline"
          onClick={onReset}
          className="h-12 transition-colors duration-500"
          style={{ borderColor: `${accentColor}66`, color: accentColor }}
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          重新填寫問卷
        </Button>
      </div>
    </motion.div>
  );
};

export default PersonalityTestResult;

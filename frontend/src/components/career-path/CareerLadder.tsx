import { useState, useMemo } from 'react';
import { Star } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import { useIsMobile } from '@/hooks/use-mobile';
import { careerTemplates, mockResumeExperiences, mockTargetCareer } from '@/data/careerLadderTemplates';

interface StepData {
  id: number;
  title: string;
  duties: string[];
  source: 'real' | 'ai';
  subtitle?: string;
}

/* ── Chevron Arrow (title only) ── */
const ChevronArrow = ({
  step,
  isCurrentStep,
  isReal,
  isMobile,
}: {
  step: StepData;
  isCurrentStep: boolean;
  isReal: boolean;
  isMobile: boolean;
}) => {
  const w = isMobile ? 140 : 180;
  const h = isMobile ? 48 : 56;
  const point = 16;

  const pathD = `M0,0 L${w - point},0 L${w},${h / 2} L${w - point},${h} L0,${h} L${point},${h / 2} Z`;

  const fillColor = isCurrentStep
    ? 'hsl(27 95% 28%)'
    : isReal
      ? 'hsl(30 40% 85%)'
      : 'hsl(30 15% 92%)';

  const strokeColor = isCurrentStep
    ? 'hsl(27 90% 22%)'
    : isReal
      ? 'hsl(30 35% 72%)'
      : 'hsl(30 10% 82%)';

  const textColor = isCurrentStep
    ? 'text-white font-bold'
    : isReal
      ? 'text-foreground font-semibold'
      : 'text-muted-foreground font-medium';

  return (
    <div className="relative flex-shrink-0" style={{ width: w, height: h }}>
      <svg className="absolute inset-0" width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
        {isCurrentStep && (
          <defs>
            <filter id="chevron-glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
        )}
        <path
          d={pathD}
          fill={fillColor}
          stroke={strokeColor}
          strokeWidth="1.5"
          filter={isCurrentStep ? 'url(#chevron-glow)' : undefined}
        />
      </svg>

      <div
        className={cn('absolute inset-0 flex items-center justify-center text-center', textColor)}
        style={{ paddingLeft: point + 6, paddingRight: point + 6 }}
      >
        {/* Step label */}
        <div className="flex flex-col items-center gap-0.5">
          <span className={cn(
            'text-[9px] uppercase tracking-wider opacity-70',
            isCurrentStep ? 'text-white' : ''
          )}>
            {isCurrentStep ? '📍 當前' : isReal ? `步驟 ${step.id}` : `步驟 ${step.id}`}
          </span>
          <span className={cn(
            'leading-tight',
            step.title.length > 8 ? (isMobile ? 'text-[10px]' : 'text-xs') : (isMobile ? 'text-xs' : 'text-sm'),
          )}>
            {step.title}
          </span>
        </div>
      </div>
    </div>
  );
};

/* ── Content Block (duties below chevron) ── */
const ContentBlock = ({
  step,
  isCurrentStep,
  isReal,
  isMobile,
}: {
  step: StepData;
  isCurrentStep: boolean;
  isReal: boolean;
  isMobile: boolean;
}) => {
  const w = isMobile ? 140 : 180;

  return (
    <div
      className={cn(
        'rounded-lg border p-3 flex-shrink-0',
        isCurrentStep
          ? 'border-primary/50 bg-primary/5'
          : isReal
            ? 'border-primary/20 bg-primary/[0.03]'
            : 'border-border bg-muted/30',
      )}
      style={{ width: w, minHeight: isMobile ? 90 : 110 }}
    >
      {/* Subtitle */}
      {step.subtitle && (
        <p className={cn(
          'text-[10px] mb-2 font-medium',
          isCurrentStep ? 'text-primary' : 'text-muted-foreground'
        )}>
          {step.subtitle}
        </p>
      )}

      {/* Duties */}
      <ul className="space-y-1">
        {step.duties.slice(0, 4).map((duty, idx) => (
          <li key={idx} className={cn(
            'text-[11px] leading-snug flex items-start gap-1.5',
            isReal ? 'text-foreground/80' : 'text-muted-foreground'
          )}>
            <span className={cn(
              'h-1 w-1 rounded-full mt-[5px] shrink-0',
              isCurrentStep ? 'bg-primary' : isReal ? 'bg-primary/40' : 'bg-muted-foreground/40'
            )} />
            {duty}
          </li>
        ))}
      </ul>
    </div>
  );
};

/* ── Transition Marker ── */
const TransitionMarker = ({ isMobile }: { isMobile: boolean }) => (
  <div className={cn('flex flex-col items-center justify-center flex-shrink-0 self-stretch', isMobile ? 'mx-1' : 'mx-2')}>
    <div className="flex-1 w-px border-l-2 border-dashed border-primary/50" />
    <div className="relative my-1.5">
      <div className="absolute inset-0 bg-primary/20 rounded-full blur-md" />
      <span className="relative text-[10px] font-semibold text-primary bg-primary/10 border border-primary/30 px-2.5 py-1 rounded-full whitespace-nowrap">
        建議路徑
      </span>
    </div>
    <div className="flex-1 w-px border-l-2 border-dashed border-primary/50" />
  </div>
);

/* ── Template Switcher ── */
const templateKeys = Object.keys(careerTemplates) as Array<keyof typeof careerTemplates>;
const templateLabels: Record<string, string> = {
  frontend: '前端',
  backend: '後端',
  fullstack: '全端',
  data: '資料科學',
  ai: 'AI',
  devops: 'DevOps',
};

/* ── Main Component ── */
const CareerLadder = ({ isLoading }: { isLoading: boolean }) => {
  const isMobile = useIsMobile();
  const [activeTemplate, setActiveTemplate] = useState<string>(mockTargetCareer);
  const template = careerTemplates[activeTemplate];

  const steps = useMemo<StepData[]>(() => {
    const realSteps: StepData[] = mockResumeExperiences.map((exp, i) => ({
      id: i + 1,
      title: exp.title,
      duties: exp.duties,
      source: 'real' as const,
      subtitle: `${exp.company} · ${exp.period}`,
    }));

    const futureSteps: StepData[] = template.levels.map((lvl, i) => ({
      id: realSteps.length + i + 1,
      title: lvl.title,
      duties: lvl.duties,
      source: 'ai' as const,
      subtitle: `Level ${lvl.level}`,
    }));

    return [...realSteps, ...futureSteps];
  }, [template]);

  const lastRealIndex = mockResumeExperiences.length - 1;

  if (isLoading) {
    return (
      <Card>
        <CardHeader className="pb-2 md:pb-4">
          <Skeleton className="w-40 h-5" />
          <Skeleton className="w-64 h-4 mt-2" />
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 overflow-x-auto pb-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} className={cn('rounded-lg flex-shrink-0', isMobile ? 'w-[140px] h-[160px]' : 'w-[180px] h-[190px]')} />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-2 md:pb-4 overflow-hidden">
        {/* Template switcher */}
        <div className="flex flex-wrap gap-1.5 mb-3">
          {templateKeys.map((key) => (
            <Button
              key={key}
              size="sm"
              variant={activeTemplate === key ? 'default' : 'outline'}
              className="text-xs h-7 px-2.5"
              onClick={() => setActiveTemplate(key)}
            >
              {templateLabels[key]}
            </Button>
          ))}
        </div>

        <div className="flex items-start justify-between gap-4">
          <div>
            <CardTitle className="flex items-center gap-2 text-base md:text-lg">
              <Star className="h-4 w-4 md:h-5 md:w-5 text-primary" />
              職涯階梯圖
            </CardTitle>
            <CardDescription className="text-xs md:text-sm mt-1">
              您的職涯發展路徑，當前位置以發光效果標示
            </CardDescription>
          </div>

          {/* Large stable mascot */}
          <div className="relative flex-shrink-0 overflow-hidden">
            <div className="absolute inset-0 bg-primary/15 rounded-full blur-2xl scale-75" />
            <img
              src={template.mascot}
              alt={`${template.name} 吉祥物`}
              className="relative object-contain drop-shadow-lg max-w-full"
              style={{ width: isMobile ? 140 : 220, height: isMobile ? 140 : 220 }}
            />
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-2 md:p-6">
        {/* Outer lock: strict width, local scroll only */}
        <div className="w-full max-w-full overflow-x-auto overflow-y-hidden pb-3 career-ladder-scroll" style={{ maxWidth: '100%' }}>
          {/* Inner content: flex row, naturally wider than parent */}
          <div className="flex items-start gap-0 flex-nowrap" style={{ width: 'max-content' }}>
            {steps.map((step, index) => {
              const isCurrentStep = index === lastRealIndex;
              const isReal = step.source === 'real';
              const showTransition = index === lastRealIndex + 1;

              return (
                <div key={step.id} className="flex items-start flex-shrink-0">
                  {showTransition && <TransitionMarker isMobile={isMobile} />}
                  <div className={cn('flex flex-col gap-2', isMobile ? 'mr-1' : 'mr-1.5')}>
                    <ChevronArrow
                      step={step}
                      isCurrentStep={isCurrentStep}
                      isReal={isReal}
                      isMobile={isMobile}
                    />
                    <ContentBlock
                      step={step}
                      isCurrentStep={isCurrentStep}
                      isReal={isReal}
                      isMobile={isMobile}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 mt-3 text-[10px] md:text-xs text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-sm" style={{ background: 'hsl(30 40% 85%)' }} />
            真實經歷
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-sm bg-muted border border-border" />
            建議路徑
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-sm bg-primary" style={{ boxShadow: '0 0 6px hsl(27 95% 28% / 0.5)' }} />
            當前位置
          </span>
        </div>
      </CardContent>
    </Card>
  );
};

export default CareerLadder;

import type { RankQuestion as RankQuestionType } from '@/data/surveyQuestions';

interface Props {
  question: RankQuestionType;
  value: string[]; // ordered array of selected values
  onChange: (val: string[]) => void;
}

const RankQuestion = ({ question, value, onChange }: Props) => {
  const maxSelection = question.validation.max_selection;

  const handleClick = (optValue: string) => {
    const idx = value.indexOf(optValue);
    if (idx >= 0) {
      // Remove and re-compact
      onChange(value.filter((v) => v !== optValue));
    } else if (value.length < maxSelection) {
      onChange([...value, optValue]);
    }
  };

  return (
    <div className="space-y-3">
      <p className="font-medium text-sm md:text-base">
        {question.required && <span className="text-destructive mr-1">*</span>}
        {question.question}
      </p>
      <p className="text-xs text-muted-foreground">點擊選擇前 {maxSelection} 名，點擊順序即為排名</p>
      <div className="space-y-2">
        {question.options.map((option) => {
          const rank = value.indexOf(option.value);
          const selected = rank >= 0;
          return (
            <div
              key={option.value}
              onClick={() => handleClick(option.value)}
              className={`flex items-center gap-3 p-3 rounded-lg border transition-all cursor-pointer hover:bg-muted/50 ${
                selected
                  ? 'border-primary/60 bg-primary/5 shadow-[0_0_8px_hsl(var(--primary)/0.15)]'
                  : 'border-border'
              }`}
            >
              <div
                className={`flex-shrink-0 h-7 w-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors ${
                  selected ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
                }`}
              >
                {selected ? rank + 1 : '-'}
              </div>
              <span className="text-sm md:text-base">{option.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default RankQuestion;

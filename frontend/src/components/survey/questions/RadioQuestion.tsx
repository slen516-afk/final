import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import type { RadioQuestion as RadioQuestionType } from '@/data/surveyQuestions';

interface Props {
  question: RadioQuestionType;
  value: string | number | undefined;
  onChange: (val: string | number) => void;
}

const RadioQuestion = ({ question, value, onChange }: Props) => {
  return (
    <div className="space-y-3">
      <p className="font-medium text-sm md:text-base">
        {question.required && <span className="text-destructive mr-1">*</span>}
        {question.question}
        <span className="text-xs text-muted-foreground ml-1.5">(單選)</span>
      </p>
      <RadioGroup
        value={value !== undefined ? String(value) : ''}
        onValueChange={(v) => {
          const opt = question.options.find((o) => String(o.value) === v);
          onChange(opt ? opt.value : v);
        }}
      >
        {question.options.map((option) => (
          <div
            key={String(option.value)}
            className={`flex items-start space-x-3 p-3 rounded-lg border transition-all cursor-pointer hover:bg-muted/50 ${
              String(value) === String(option.value)
                ? 'border-primary/60 bg-primary/5 shadow-[0_0_8px_hsl(var(--primary)/0.15)]'
                : 'border-border'
            }`}
          >
            <RadioGroupItem value={String(option.value)} id={`${question.id}-${option.value}`} className="mt-0.5" />
            <Label htmlFor={`${question.id}-${option.value}`} className="flex-1 cursor-pointer text-sm md:text-base leading-relaxed">
              {option.label}
            </Label>
          </div>
        ))}
      </RadioGroup>
    </div>
  );
};

export default RadioQuestion;

import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import type { CheckboxQuestion as CheckboxQuestionType } from '@/data/surveyQuestions';

interface Props {
  question: CheckboxQuestionType;
  value: string[];
  onChange: (val: string[]) => void;
}

const CheckboxQuestion = ({ question, value, onChange }: Props) => {
  const toggle = (optValue: string) => {
    if (value.includes(optValue)) {
      onChange(value.filter((v) => v !== optValue));
    } else {
      onChange([...value, optValue]);
    }
  };

  return (
    <div className="space-y-3">
      <p className="font-medium text-sm md:text-base">
        {question.required && <span className="text-destructive mr-1">*</span>}
        {question.question}
      </p>
      <div className="space-y-2">
        {question.options.map((option) => {
          const checked = value.includes(option.value);
          return (
            <div
              key={option.value}
              className={`flex items-start space-x-3 p-3 rounded-lg border transition-all cursor-pointer hover:bg-muted/50 ${
                checked
                  ? 'border-primary/60 bg-primary/5 shadow-[0_0_8px_hsl(var(--primary)/0.15)]'
                  : 'border-border'
              }`}
              onClick={() => toggle(option.value)}
            >
              <Checkbox
                checked={checked}
                onCheckedChange={() => toggle(option.value)}
                id={`${question.id}-${option.value}`}
                className="mt-0.5"
              />
              <Label htmlFor={`${question.id}-${option.value}`} className="flex-1 cursor-pointer text-sm md:text-base leading-relaxed">
                {option.label}
              </Label>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default CheckboxQuestion;

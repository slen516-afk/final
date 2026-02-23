import { Textarea } from '@/components/ui/textarea';
import type { TextQuestion as TextQuestionType } from '@/data/surveyQuestions';

interface Props {
  question: TextQuestionType;
  value: string;
  onChange: (val: string) => void;
}

const TextQuestion = ({ question, value, onChange }: Props) => {
  return (
    <div className="space-y-3">
      <p className="font-medium text-sm md:text-base">
        {question.required && <span className="text-destructive mr-1">*</span>}
        {question.question}
        {!question.required && <span className="text-xs text-muted-foreground ml-1">(選填)</span>}
      </p>
      <Textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={question.placeholder}
        className="focus-visible:ring-primary/40 transition-shadow min-h-[80px]"
        maxLength={200}
      />
    </div>
  );
};

export default TextQuestion;

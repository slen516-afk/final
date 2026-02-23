import { useState } from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';
import type { CategorizedSkillQuestion } from '@/data/surveyQuestions';

export interface SkillEntry {
  skill: string;
  rating: number;
}

interface Props {
  question: CategorizedSkillQuestion;
  value: SkillEntry[];
  onChange: (val: SkillEntry[]) => void;
}

const CategorizedSkillSelector = ({ question, value, onChange }: Props) => {
  const [pendingSkill, setPendingSkill] = useState('');
  const [pendingRating, setPendingRating] = useState('');
  const maxSelection = question.validation.max_selection;

  const addSkill = () => {
    if (!pendingSkill || !pendingRating) return;
    if (value.length >= maxSelection) return;
    if (value.some((v) => v.skill === pendingSkill)) return;
    onChange([...value, { skill: pendingSkill, rating: Number(pendingRating) }]);
    setPendingSkill('');
    setPendingRating('');
  };

  const removeSkill = (skill: string) => {
    onChange(value.filter((v) => v.skill !== skill));
  };

  return (
    <div className="space-y-3">
      <p className="font-medium text-sm md:text-base">
        {question.required && <span className="text-destructive mr-1">*</span>}
        {question.question}
      </p>
      <p className="text-xs text-muted-foreground">{question.meta.scale_desc}</p>

      {/* Selected skills */}
      {value.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {value.map((entry) => (
            <div
              key={entry.skill}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/30 text-sm"
            >
              <span className="font-medium">{entry.skill}</span>
              <span className="text-xs text-primary">Lv.{entry.rating}</span>
              <button onClick={() => removeSkill(entry.skill)} className="ml-1 hover:text-destructive">
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Add skill form */}
      {value.length < maxSelection && (
        <div className="flex flex-col sm:flex-row gap-2">
          <Select value={pendingSkill} onValueChange={setPendingSkill}>
            <SelectTrigger className="flex-1 focus:ring-primary/40">
              <SelectValue placeholder="選擇語言" />
            </SelectTrigger>
            <SelectContent>
              {question.options.map((cat) => (
                <div key={cat.category}>
                  <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground">{cat.category}</div>
                  {cat.options.map((opt) => (
                    <SelectItem
                      key={opt}
                      value={opt}
                      disabled={value.some((v) => v.skill === opt)}
                    >
                      {opt}
                    </SelectItem>
                  ))}
                </div>
              ))}
            </SelectContent>
          </Select>

          <Select value={pendingRating} onValueChange={setPendingRating}>
            <SelectTrigger className="w-full sm:w-28 focus:ring-primary/40">
              <SelectValue placeholder="熟練度" />
            </SelectTrigger>
            <SelectContent>
              {[1, 2, 3, 4, 5].map((n) => (
                <SelectItem key={n} value={String(n)}>Lv.{n}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Button type="button" size="sm" onClick={addSkill} disabled={!pendingSkill || !pendingRating} className="gradient-primary">
            新增
          </Button>
        </div>
      )}

      <p className="text-xs text-muted-foreground">
        已選擇 {value.length} / {maxSelection} 種語言
      </p>
    </div>
  );
};

export default CategorizedSkillSelector;

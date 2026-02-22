import { useId } from 'react';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface SyncRadioProps {
  value: 'sync' | 'manual';
  onChange: (value: 'sync' | 'manual') => void;
  syncDisabled: boolean;
  disabledTooltip?: string;
}

const SyncRadio = ({
  value,
  onChange,
  syncDisabled,
  disabledTooltip = '基本資料尚未填寫，無法同步',
}: SyncRadioProps) => {
  const id = useId();

  return (
    <RadioGroup
      value={value}
      onValueChange={(v) => onChange(v as 'sync' | 'manual')}
      className="flex items-center gap-4 mt-1.5"
    >
      <TooltipProvider delayDuration={200}>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="flex items-center gap-1.5">
              <RadioGroupItem
                value="sync"
                id={`${id}-sync`}
                disabled={syncDisabled}
              />
              <Label
                htmlFor={`${id}-sync`}
                className={`text-xs cursor-pointer select-none ${
                  syncDisabled
                    ? 'text-[#d1d5db] cursor-not-allowed'
                    : 'text-[#8d4903]'
                }`}
              >
                同步基本資料
              </Label>
            </div>
          </TooltipTrigger>
          {syncDisabled && (
            <TooltipContent side="top" className="text-xs">
              {disabledTooltip}
            </TooltipContent>
          )}
        </Tooltip>
      </TooltipProvider>

      <div className="flex items-center gap-1.5">
        <RadioGroupItem value="manual" id={`${id}-manual`} />
        <Label htmlFor={`${id}-manual`} className="text-xs cursor-pointer select-none text-[#8d4903]">
          手動填寫
        </Label>
      </div>
    </RadioGroup>
  );
};

export default SyncRadio;

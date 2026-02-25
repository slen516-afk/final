import { Lightbulb, FileText } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useResumes } from '@/contexts/ResumeContext';
import { motion } from 'framer-motion';

const ResumeSelector = () => {
  const { resumes, selectedResumeId, setSelectedResumeId } = useResumes();

  const formatDate = (dateStr: string) => {
    const [y, m, d] = dateStr.split('-');
    return `${y}/${m}/${d}`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <Card className={`transition-all duration-300 ${
        selectedResumeId
          ? 'border-primary/40 shadow-[0_0_12px_rgba(141,73,3,0.15)]'
          : 'border-border'
      }`}>
        <CardHeader className="pb-2 md:pb-4">
          <CardTitle className="text-base md:text-lg flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            選擇履歷
            <span className="inline-flex items-center gap-1 ml-2 text-xs font-normal text-primary bg-primary/10 px-2 py-0.5 rounded-full">
              <Lightbulb className="h-3 w-3" />
              智慧提示
            </span>
          </CardTitle>
          <CardDescription className="text-xs md:text-sm flex items-start gap-1.5">
            <span>選擇最適合的履歷，能幫助提供出更精準的職缺推薦</span>
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Select
            value={selectedResumeId?.toString() ?? ''}
            onValueChange={(val) => setSelectedResumeId(parseInt(val, 10))}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="請選擇履歷" />
            </SelectTrigger>
            <SelectContent>
              {resumes.map((r) => (
                <SelectItem key={r.id} value={r.id.toString()}>
                  <span className="flex items-center gap-2">
                    <FileText className="h-3.5 w-3.5 text-primary shrink-0" />
                    <span className="truncate">{r.name}</span>
                    <span className="text-muted-foreground text-xs shrink-0">- {formatDate(r.updatedAt)}</span>
                  </span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default ResumeSelector;

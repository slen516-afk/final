import { Lightbulb, FileText } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useResumes } from '@/contexts/ResumeContext';
import { motion } from 'framer-motion';

const ResumeSelector = () => {
  // 🌟 1. 從 Context 拿出所有需要的東西：包含 resumes 陣列和魔法棒
  const { resumes, selectedResumeId, setSelectedResumeId } = useResumes();

  // 簡單的日期格式化函數 (避免找不到 formatDate 報錯)
  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`;
  };

  return (
    // ❌ 這裡千萬不能包 HTML 的 <select>
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <Card className={`transition-all duration-300 ${selectedResumeId
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

          {/* 🌟 2. 這裡才是真正的下拉選單！利用 onValueChange 觸發魔法棒 */}
          <Select
            value={selectedResumeId?.toString() ?? ''}
            onValueChange={(val) => {
              console.log("✅ 使用者切換了履歷，新的 ID 是:", val);
              // 注意：如果你的 selectedResumeId 是數字，這裡要用 parseInt(val, 10)
              // 如果是字串，直接傳 val 即可。我們統一先當字串傳
              setSelectedResumeId(val);
            }}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="請選擇履歷" />
            </SelectTrigger>
            <SelectContent>
              {/* 確保 resumes 存在才進行 map */}
              {resumes && resumes.map((r) => (
                <SelectItem key={r.id} value={r.id.toString()}>
                  <span className="flex items-center gap-2">
                    <FileText className="h-3.5 w-3.5 text-primary shrink-0" />
                    <span className="truncate">{r.name || "未命名履歷"}</span>
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
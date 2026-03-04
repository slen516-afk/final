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
    </motion.div>
  );
};

export default ResumeSelector;
import { useState, useEffect } from 'react';
import { MapPin, Wallet, FileText, Loader2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { motion } from 'framer-motion';
import AlertModal from '@/components/modals/AlertModal';
import apiClient from '@/services/api';

// 引入必要工具：換成真實 API 與全域狀態
import { useAppState } from '@/contexts/AppContext';

const taiwanCities = [
  '台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市',
  '基隆市', '新竹市', '新竹縣', '苗栗縣', '彰化縣', '南投縣',
  '雲林縣', '嘉義市', '嘉義縣', '屏東縣', '宜蘭縣', '花蓮縣',
  '台東縣', '澎湖縣', '金門縣', '連江縣'
];

interface EmbeddedPreferenceSurveyProps {
  onComplete: (surveyData: any) => void;
}

const EmbeddedPreferenceSurvey = ({ onComplete }: EmbeddedPreferenceSurveyProps) => {
  const { user, isLoggedIn } = useAppState();
  const realUserId = user?.user_id;

  const [resumeOptions, setResumeOptions] = useState<any[]>([]);
  const [selectedResume, setSelectedResume] = useState<string>('');
  const [isLoadingResumes, setIsLoadingResumes] = useState(false);

  const [regionType, setRegionType] = useState('');
  const [selectedCity, setSelectedCity] = useState('');
  const [salaryRange, setSalaryRange] = useState<number[]>([40000, 80000]);
  const [showIncompleteAlert, setShowIncompleteAlert] = useState(false);

  useEffect(() => {
    const fetchMyResumes = async () => {
      if (isLoggedIn && realUserId) {
        setIsLoadingResumes(true);
        try {
          console.log("🚀 [偏好設定] 開始向後端請求 ID:", realUserId);
          // 💡 直接用 apiClient 呼叫，繞過舊的死板檢查
          const response: any = await apiClient.get(`/resume_process/list/${realUserId}`);

          let finalData: any[] = [];
          const rawData: any = response.data;

          if (Array.isArray(rawData)) {
            finalData = rawData;
          } else if (rawData?.data && Array.isArray(rawData.data)) {
            finalData = rawData.data;
          } else if (rawData?.resumes && Array.isArray(rawData.resumes)) {
            finalData = rawData.resumes;
          }

          // 💡 轉換格式給下拉選單使用 (加入 isOptimized 標記)
          // 💡 轉換格式給下拉選單使用 (加入 isOptimized 標記)
          const formatted = finalData.map((r: any) => ({
            id: r.resume_id || r.id,
            // 確保一定抓得到名字，否則顯示未命名
            title: r.resume_name || r.name || r.title || '未命名履歷',
            sourceType: r.type || r.resume_type || 'RESUME',
            isOptimized: r.is_optimized || false // 🌟 接住後端傳來的標記
          }));

          setResumeOptions(formatted);
        } catch (error) {
          console.error("❌ 載入履歷失敗", error);
        } finally {
          setIsLoadingResumes(false);
        }
      }
    };

    fetchMyResumes();
  }, [isLoggedIn, realUserId]);

  const formatSalary = (value: number) => {
    return value >= 100000
      ? `${(value / 10000).toFixed(0)}萬+`
      : `${(value / 1000).toFixed(0)}K`;
  };

  const handleRegionChange = (value: string) => {
    setRegionType(value);
    if (value !== 'taiwan') setSelectedCity('');
  };

  const handleSubmit = () => {
    const isTaiwanWithoutCity = regionType === 'taiwan' && !selectedCity;

    if (!regionType || isTaiwanWithoutCity || !selectedResume) {
      setShowIncompleteAlert(true);
      return;
    }

    const [sourceType, docId] = selectedResume.split('-');

    const realSurveyData = {
      region: regionType,
      city: selectedCity,
      minSalary: salaryRange[0],
      maxSalary: salaryRange[1],
      user_id: realUserId,
      document_id: docId, // 將 ID 傳給後端
      source_type: sourceType,
      filters: {
        city: [selectedCity],
        salary_min: salaryRange[0],
        salary_max: salaryRange[1]
      }
    };

    onComplete(realSurveyData);
  };

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-4 md:space-y-6"
      >
        <Card>
          <CardHeader className="pb-2 md:pb-4">
            <CardTitle className="text-base md:text-lg flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              配對履歷
            </CardTitle>
            <CardDescription className="text-xs md:text-sm">
              請選擇您要用來進行職缺配對的履歷 (目前 ID: {realUserId || '載入中'})
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Select value={selectedResume} onValueChange={setSelectedResume} disabled={isLoadingResumes}>
              <SelectTrigger className="w-full">
                {isLoadingResumes ? (
                  <div className="flex items-center gap-2"><Loader2 className="h-4 w-4 animate-spin" /> 載入中...</div>
                ) : (
                  <SelectValue placeholder="請選擇一份履歷..." />
                )}
              </SelectTrigger>
              <SelectContent>
                {resumeOptions.length > 0 ? (
                  resumeOptions.map((opt) => (
                    <SelectItem key={`${opt.sourceType}-${opt.id}`} value={`${opt.sourceType}-${opt.id}`}>
                      {/* 🌟 乾淨俐落的判斷：如果是優化版就不加字，如果是原版才加 (原版) */}
                      {opt.isOptimized ? opt.title : `${opt.title} (原版)`}
                    </SelectItem>
                  ))
                ) : (
                  <SelectItem value="none" disabled>目前沒有可用履歷</SelectItem>
                )}
              </SelectContent>
            </Select>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2 md:pb-4">
            <CardTitle className="text-base md:text-lg flex items-center gap-2">
              <MapPin className="h-5 w-5 text-primary" />
              期望工作地點
            </CardTitle>
            <CardDescription className="text-xs md:text-sm">
              請選擇您偏好的工作地區
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label className="text-sm md:text-base">地區類型</Label>
              <Select value={regionType} onValueChange={handleRegionChange}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="請選擇地區類型" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="taiwan">台灣地區</SelectItem>
                  <SelectItem value="other">其他地區</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {regionType === 'taiwan' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="space-y-2"
              >
                <Label className="text-sm md:text-base">縣市</Label>
                <Select value={selectedCity} onValueChange={setSelectedCity}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="請選擇縣市" />
                  </SelectTrigger>
                  <SelectContent>
                    {taiwanCities.map((city) => (
                      <SelectItem key={city} value={city}>{city}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </motion.div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2 md:pb-4">
            <CardTitle className="text-base md:text-lg flex items-center gap-2">
              <Wallet className="h-5 w-5 text-primary" />
              期望月薪範圍
            </CardTitle>
            <CardDescription className="text-xs md:text-sm">
              拖曳調整您的期望薪資區間
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="text-center">
              <span className="text-2xl md:text-3xl font-bold text-primary">
                NT$ {salaryRange[0].toLocaleString()} - {salaryRange[1].toLocaleString()}
              </span>
            </div>
            <div className="px-2">
              <Slider
                value={salaryRange}
                onValueChange={setSalaryRange}
                min={30000}
                max={200000}
                step={5000}
                className="w-full"
              />
            </div>
            <div className="flex justify-between text-xs md:text-sm text-muted-foreground">
              <span>{formatSalary(30000)}</span>
              <span>{formatSalary(100000)}</span>
              <span>{formatSalary(200000)}</span>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end">
          <Button onClick={handleSubmit} className="gradient-primary w-full sm:w-auto text-sm md:text-base">
            提交偏好，開始匹配職缺
          </Button>
        </div>
      </motion.div>

      <AlertModal
        open={showIncompleteAlert}
        onClose={() => setShowIncompleteAlert(false)}
        type="warning"
        title="請完成所有必填項目"
        message="請確保您已經【選擇履歷】、【選擇地區】並【設定薪資範圍】喔！"
        confirmLabel="了解"
      />
    </>
  );
};

export default EmbeddedPreferenceSurvey;
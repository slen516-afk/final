import { useState, useEffect } from 'react';
import { MapPin, Wallet, Building2, FileText } from 'lucide-react'; // 🌟 加入 FileText icon
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { motion } from 'framer-motion';
import AlertModal from '@/components/modals/AlertModal';
import { getResumes } from '@/mocks/resumes';

// ⚠️ 注意：請確認你的 supabase client 實際的路徑！
// 如果路徑不同，請把 '@/lib/supabaseClient' 改成你專案中正確的路徑
import { supabase } from '@/lib/supabaseClient';

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
  // 🌟 新增：履歷相關的 State
  const [resumeOptions, setResumeOptions] = useState<any[]>([]);
  const [selectedResume, setSelectedResume] = useState<string>(''); // 存 "RESUME-1" 或 "OPTIMIZATION-8"

  const [regionType, setRegionType] = useState('');
  const [selectedCity, setSelectedCity] = useState('');
  const [salaryRange, setSalaryRange] = useState<number[]>([40000, 80000]);
  const [showIncompleteAlert, setShowIncompleteAlert] = useState(false);

  // 🌟 修改：透過後端 API 撈取履歷清單
  // 🌟 修改：聰明版 API 呼叫 (帶有自動假資料備援)
  useEffect(() => {
    const fetchResumesForDropdown = async () => {
      try {
        // 2. 直接呼叫前端的 Supabase 完美版 API
        const data = await getResumes();

        // 3. 轉換成下拉選單要的格式
        const combinedOptions = data.map((r: any) => ({
          id: r.id,          // 這裡就會是正確的 3, 4, 5 了！
          title: r.name,
          sourceType: r.sourceType
        }));

        setResumeOptions(combinedOptions);
      } catch (error) {
        console.error("載入履歷失敗", error);
      }
    };

    fetchResumesForDropdown();
  }, []);

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

    // 🌟 防呆：如果沒選履歷、沒選地區，就跳出警告
    if (!regionType || isTaiwanWithoutCity || !selectedResume) {
      setShowIncompleteAlert(true);
      return;
    }

    // 🌟 拆解選中的履歷 (例如把 "RESUME-1" 拆成 "RESUME" 和 1)
    const [sourceType, docId] = selectedResume.split('-');

    // 🌟 完美打包成你 API (截圖二) 要的 JSON 格式
    const realSurveyData = {
      // 保留原本的欄位給可能需要的其他邏輯
      region: regionType,
      city: selectedCity,
      minSalary: salaryRange[0],
      maxSalary: salaryRange[1],

      // 給 V2 推薦引擎的精準參數
      user_id: 1, // 這裡可視需求改為動態取得
      document_id: parseInt(docId),
      source_type: sourceType,
      filters: {
        city: [selectedCity], // 後端 API 需要的是陣列
        salary_min: salaryRange[0],
        salary_max: salaryRange[1]
      }
    };

    // 將資料往上傳給父元件去發送 API
    onComplete(realSurveyData);
  };

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-4 md:space-y-6"
      >
        {/* 🌟 新增：選擇履歷的區塊 */}
        <Card>
          <CardHeader className="pb-2 md:pb-4">
            <CardTitle className="text-base md:text-lg flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              配對履歷
            </CardTitle>
            <CardDescription className="text-xs md:text-sm">
              請選擇您要用來進行職缺配對的履歷
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Select value={selectedResume} onValueChange={setSelectedResume}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="請選擇一份履歷..." />
              </SelectTrigger>
              <SelectContent>
                {resumeOptions.map((opt) => (
                  <SelectItem
                    key={`${opt.sourceType}-${opt.id}`}
                    value={`${opt.sourceType}-${opt.id}`}
                  >
                    {opt.title} ({opt.sourceType === 'RESUME' ? '原版' : '優化版'})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CardContent>
        </Card>

        {/* Location Selection */}
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

        {/* Salary Range */}
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
import { useState } from 'react';
import { MapPin, Wallet, Building2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { motion } from 'framer-motion';
import AlertModal from '@/components/modals/AlertModal';

const taiwanCities = [
  '台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市',
  '基隆市', '新竹市', '新竹縣', '苗栗縣', '彰化縣', '南投縣',
  '雲林縣', '嘉義市', '嘉義縣', '屏東縣', '宜蘭縣', '花蓮縣',
  '台東縣', '澎湖縣', '金門縣', '連江縣'
];

const workModes = [
  { id: 'onsite', label: '實體辦公' },
  { id: 'remote', label: '完全遠端' },
  { id: 'hybrid', label: '混合模式' },
];

interface EmbeddedPreferenceSurveyProps {
  onComplete: () => void;
}

const EmbeddedPreferenceSurvey = ({ onComplete }: EmbeddedPreferenceSurveyProps) => {
  const [regionType, setRegionType] = useState('');
  const [selectedCity, setSelectedCity] = useState('');
  const [salaryRange, setSalaryRange] = useState<number[]>([40000, 80000]);
  const [workMode, setWorkMode] = useState('');
  const [showIncompleteAlert, setShowIncompleteAlert] = useState(false);

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
    if (!regionType || isTaiwanWithoutCity || !workMode) {
      setShowIncompleteAlert(true);
      return;
    }
    onComplete();
  };

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-4 md:space-y-6"
      >
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

        {/* Work Mode */}
        <Card>
          <CardHeader className="pb-2 md:pb-4">
            <CardTitle className="text-base md:text-lg flex items-center gap-2">
              <Building2 className="h-5 w-5 text-primary" />
              辦公模式
            </CardTitle>
            <CardDescription className="text-xs md:text-sm">
              請選擇您偏好的工作方式
            </CardDescription>
          </CardHeader>
          <CardContent>
            <RadioGroup value={workMode} onValueChange={setWorkMode} className="space-y-3">
              {workModes.map((mode) => (
                <div
                  key={mode.id}
                  className={`flex items-center space-x-3 p-3 md:p-4 rounded-lg transition-colors cursor-pointer border ${
                    workMode === mode.id
                      ? 'bg-primary/10 border-primary/30'
                      : 'border-transparent hover:bg-muted'
                  }`}
                  onClick={() => setWorkMode(mode.id)}
                >
                  <RadioGroupItem value={mode.id} id={`pref-${mode.id}`} />
                  <Label htmlFor={`pref-${mode.id}`} className="flex-1 cursor-pointer text-sm md:text-base">
                    {mode.label}
                  </Label>
                </div>
              ))}
            </RadioGroup>
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
        message="請至少選擇一項工作偏好，並選擇期望薪資範圍"
        confirmLabel="了解"
      />
    </>
  );
};

export default EmbeddedPreferenceSurvey;

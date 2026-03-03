import { useState, useRef } from "react";
import {
  User,
  FileText,
  Map,
  Edit,
  Lock,
  ArrowRight,
  Sparkles,
  MapPin,
  Briefcase,
  GraduationCap,
  Github,
  Camera,
  Mail,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Link } from "react-router-dom";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { useAppState } from "@/contexts/AppContext";
import EditProfileModal from "@/components/member/EditProfileModal";
import PasswordModal from "@/components/member/PasswordModal";
import LoginRequired from "@/components/gatekeeper/LoginRequired";
import { mockUserId, mockProfile } from "@/mocks/member";
import logoCat from "@/assets/logocat.png";

const displayName = (name: string, userId: string) => (name?.trim() ? name : `用戶_${userId}`);

const fallback = (value: string | undefined) => (value?.trim() ? value : "無");

const MemberCenter = () => {
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [passwordModalOpen, setPasswordModalOpen] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) return;
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      setAvatarUrl(dataUrl);
    };
    reader.readAsDataURL(file);
    e.target.value = "";
  };
  const { isResumeUploaded, isPersonalityQuizDone, isPersonalityTestDone, avatarUrl, setAvatarUrl } = useAppState();

  const name = displayName(mockProfile.fullName, mockUserId);
  const titleText = fallback(mockProfile.title);
  const locationText = fallback(mockProfile.location);
  const experienceText = fallback(mockProfile.experience);
  const educationText = fallback(mockProfile.education);
  const githubText = fallback(mockProfile.github);
  const isEmpty = (v: string) => v === "無";

  return (
    <LoginRequired>
      <div className="container py-8 md:py-12 animate-fade-in">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8 md:mb-12">
            <div className="inline-flex items-center justify-center h-14 w-14 md:h-16 md:w-16 rounded-full bg-primary/10 mb-4 md:mb-6">
              <User className="h-7 w-7 md:h-8 md:w-8 text-primary" />
            </div>
            <h1 className="text-2xl md:text-3xl font-bold mb-3 md:mb-4">會員中心</h1>
            <p className="text-muted-foreground text-sm md:text-base max-w-2xl mx-auto">管理您的帳戶與職涯資訊</p>
          </div>

          {/* ── Profile Name Card ── */}
          <Card className="mb-6 md:mb-8 shadow-warm">
            <CardContent className="pt-5 md:pt-6">
              {/* Top section: Avatar + Primary Info */}
              <div className="flex flex-col sm:flex-row gap-5 items-center sm:items-start">
                {/* Avatar with upload hint */}
                <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleFileChange} />
                <button
                  type="button"
                  className="group relative shrink-0"
                  onClick={handleAvatarClick}
                  aria-label="上傳大頭貼"
                >
                  <Avatar className="h-20 w-20 md:h-24 md:w-24 border-2 border-border">
                    <AvatarImage src={avatarUrl || mockProfile.avatarUrl || logoCat} alt={name} />
                    <AvatarFallback className="bg-secondary text-muted-foreground text-2xl md:text-3xl font-semibold">
                      {name.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  <span className="absolute inset-0 flex items-center justify-center rounded-full bg-foreground/40 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Camera className="h-5 w-5 text-card" />
                  </span>
                </button>

                {/* Primary info */}
                <div className="flex-1 text-center sm:text-left">
                  <h2 className="text-xl md:text-2xl font-bold">{name}</h2>
                  <p
                    className={`text-sm mt-0.5 ${isEmpty(titleText) ? "text-muted-foreground/60" : "text-muted-foreground"}`}
                  >
                    {titleText === "無" ? "尚未填寫職位" : titleText}
                  </p>
                  <div className="flex items-center gap-1.5 mt-2 justify-center sm:justify-start">
                    <Mail className="h-3.5 w-3.5 text-primary" />
                    <span className="text-sm text-muted-foreground">{mockProfile.email}</span>
                  </div>
                </div>

                {/* Action buttons – right side on desktop */}
                <div className="flex gap-2 shrink-0">
                  <Button variant="outline" size="sm" onClick={() => setEditModalOpen(true)}>
                    <Edit className="h-4 w-4 mr-1.5" />
                    修改資料
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPasswordModalOpen(true)}
                    className="border-primary text-foreground hover:bg-primary hover:text-primary-foreground hover:shadow-[0_0_10px_hsl(var(--primary)/0.35)] hover:-translate-y-0.5 transition-all"
                  >
                    <Lock className="h-4 w-4 mr-1.5" />
                    變更密碼
                  </Button>
                </div>
              </div>

              {/* Divider */}
              <div className="border-t border-border my-4 md:my-5" />

              {/* Secondary info grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-3 text-sm">
                <div className="flex items-center gap-2.5">
                  <MapPin className="h-4 w-4 text-primary shrink-0" />
                  <span className="text-muted-foreground min-w-[4rem]">所在地</span>
                  <span className={`font-medium ${isEmpty(locationText) ? "text-muted-foreground/60" : ""}`}>
                    {locationText}
                  </span>
                </div>
                <div className="flex items-center gap-2.5">
                  <Briefcase className="h-4 w-4 text-primary shrink-0" />
                  <span className="text-muted-foreground min-w-[4rem]">工作年資</span>
                  <span className={`font-medium ${isEmpty(experienceText) ? "text-muted-foreground/60" : ""}`}>
                    {experienceText}
                  </span>
                </div>
                <div className="flex items-center gap-2.5">
                  <GraduationCap className="h-4 w-4 text-primary shrink-0" />
                  <span className="text-muted-foreground min-w-[4rem]">教育背景</span>
                  <span className={`font-medium ${isEmpty(educationText) ? "text-muted-foreground/60" : ""}`}>
                    {educationText}
                  </span>
                </div>
                <div className="flex items-center gap-2.5">
                  <Github className="h-4 w-4 text-primary shrink-0" />
                  <span className="text-muted-foreground min-w-[4rem]">GitHub</span>
                  <span className={`font-medium ${isEmpty(githubText) ? "text-muted-foreground/60" : ""}`}>
                    {githubText}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Status Cards - kept as-is */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 md:gap-4 mb-6 md:mb-8">
            <Link to="/member/upload-resume" className="group block">
              <Card className="h-full transition-all duration-300 hover:-translate-y-1 hover:shadow-medium cursor-pointer">
                <CardContent className="pt-4 md:pt-6">
                  <div className="flex items-center justify-between">
                    <span className="text-xs md:text-sm font-medium">履歷上傳</span>
                    <Badge variant={isResumeUploaded ? "default" : "secondary"} className="text-xs">
                      {isResumeUploaded ? "已完成" : "未完成"}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1.5">
                    {isResumeUploaded ? "查看已上傳的履歷" : "立即上傳"}
                  </p>
                </CardContent>
              </Card>
            </Link>
            <Link to="/member/survey/personality-test" className="group block">
              <Card className="h-full transition-all duration-300 hover:-translate-y-1 hover:shadow-medium cursor-pointer">
                <CardContent className="pt-4 md:pt-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs md:text-sm font-medium">人格特質問卷</span>
                    </div>
                    <Badge variant={isPersonalityTestDone ? "default" : "secondary"} className="text-xs">
                      {isPersonalityTestDone ? "已完成" : "未完成"}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1.5">
                    {isPersonalityTestDone ? "查看測驗結果" : "開始測驗"}
                  </p>
                </CardContent>
              </Card>
            </Link>
            <Link to="/member/survey/personality" className="group block">
              <Card className="h-full transition-all duration-300 hover:-translate-y-1 hover:shadow-medium cursor-pointer">
                <CardContent className="pt-4 md:pt-6">
                  <div className="flex items-center justify-between">
                    <span className="text-xs md:text-sm font-medium">職涯問卷</span>
                    <Badge variant={isPersonalityQuizDone ? "default" : "secondary"} className="text-xs">
                      {isPersonalityQuizDone ? "已完成" : "未完成"}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1.5">
                    {isPersonalityQuizDone ? "查看問卷結果" : "開始測驗"}
                  </p>
                </CardContent>
              </Card>
            </Link>
          </div>

          {/* Hero Portal Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-6">
            {/* 我的履歷 Card */}
            <Link to="/member/my-resumes" className="group block">
              <div className="relative rounded-2xl border bg-card p-6 md:p-8 flex flex-col items-center text-center h-full overflow-hidden transition-all duration-300 hover:-translate-y-1.5 hover:shadow-[0_0_20px_hsl(var(--primary)/0.15)] hover:border-primary/30">
                {/* Subtle tech grid overlay */}
                <div
                  className="absolute inset-0 opacity-[0.04] pointer-events-none"
                  style={{
                    backgroundImage: `
                      linear-gradient(hsl(var(--foreground)) 1px, transparent 1px),
                      linear-gradient(90deg, hsl(var(--foreground)) 1px, transparent 1px)
                    `,
                    backgroundSize: "24px 24px",
                  }}
                />
                <div className="relative z-10 flex flex-col items-center gap-4">
                  <div className="h-14 w-14 md:h-16 md:w-16 rounded-2xl bg-primary/10 flex items-center justify-center">
                    <FileText className="h-7 w-7 md:h-8 md:w-8 text-primary" />
                  </div>
                  <div>
                    <h2 className="text-lg md:text-xl font-bold mb-1.5">我的履歷</h2>
                    <p className="text-sm text-muted-foreground">查看並編輯您優化後的專業履歷</p>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    className="mt-2 group-hover:bg-primary group-hover:text-primary-foreground transition-colors"
                  >
                    進入查看
                    <ArrowRight className="h-4 w-4 ml-1" />
                  </Button>
                </div>
              </div>
            </Link>

            {/* 職涯地圖 Card */}
            <Link to="/member/career-path" className="group block">
              <div
                className="relative rounded-2xl p-6 md:p-8 flex flex-col items-center text-center h-full overflow-hidden transition-all duration-300 hover:-translate-y-1.5 hover:shadow-[0_0_20px_hsl(var(--primary)/0.3)]"
                style={{
                  background: "linear-gradient(135deg, hsl(30 96% 28%), hsl(30 80% 22%))",
                }}
              >
                <div className="relative z-10 flex flex-col items-center gap-4">
                  <div className="h-14 w-14 md:h-16 md:w-16 rounded-2xl bg-white/15 flex items-center justify-center">
                    <Map className="h-7 w-7 md:h-8 md:w-8 text-white" />
                  </div>
                  <div>
                    <h2 className="text-lg md:text-xl font-bold mb-1.5 text-white">職涯地圖</h2>
                    <p className="text-sm text-white/75">掌握您的職能發展路徑與階梯圖</p>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    className="mt-2 border-white/40 text-white hover:bg-white/20 hover:text-white bg-transparent"
                  >
                    進入地圖
                    <ArrowRight className="h-4 w-4 ml-1" />
                  </Button>
                </div>
              </div>
            </Link>
          </div>
        </div>

        <EditProfileModal open={editModalOpen} onOpenChange={setEditModalOpen} />
        <PasswordModal open={passwordModalOpen} onOpenChange={setPasswordModalOpen} />
      </div>
    </LoginRequired>
  );
};

export default MemberCenter;

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { useAppState } from '@/contexts/AppContext';
import { Mail, Lock, Loader2 } from 'lucide-react';
// 補上這一行，我們要用它來查資料庫

import { login } from '@/services/authService';

interface AuthModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const AuthModal = ({ open, onOpenChange }: AuthModalProps) => {
  // 🌟 1. 關鍵修改：把 setUser 呼叫出來！
  const { setIsLoggedIn, setUser } = useAppState();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // 1. 呼叫我們剛剛更新過的 login 服務
      const response = await login(email.trim(), password);

      setIsLoggedIn(true);

      // 🌟 2. 關鍵修改：從 response.user 裡直接拿資料
      // 這裡使用了可選鏈語法，並加上 11 作為最後的開發防呆
      if (response && response.user) {
        setUser({
          user_id: response.user.user_id || 11, // 優先拿後端回傳的整數 ID
          email: response.user.email || email.trim(),
          ...response.user
        });
      }

      onOpenChange(false);
      setEmail('');
      setPassword('');
    } catch (error: any) {
      console.error('Login failed:', error);
      alert(error.message || '登入失敗，請檢查帳號密碼');
    } finally {
      setIsLoading(false);
    }
  };


  const handleGoogleLogin = async () => {
    setIsLoading(true);

    // Simulate Google login
    await new Promise(resolve => setTimeout(resolve, 1000));

    setIsLoggedIn(true);

    // 🌟 4. Google 模擬登入也要存 user！
    setUser({
      user_id: 11, // 模擬登入一律先給 11 號測試
      email: "google_test@gmail.com"
    });

    setIsLoading(false);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-2xl text-center">歡迎回來</DialogTitle>
          <DialogDescription className="text-center">
            登入您的帳號以繼續使用所有功能
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleEmailLogin} className="space-y-4 mt-4">
          <div className="space-y-2">
            <Label htmlFor="email">電子信箱</Label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                id="email"
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="pl-10"
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">密碼</Label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="pl-10"
                required
              />
            </div>
          </div>

          <Button type="submit" className="w-full gradient-primary" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                登入中...
              </>
            ) : (
              '登入'
            )}
          </Button>
        </form>

        <div className="relative my-4">
          <Separator />
          <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-background px-2 text-xs text-muted-foreground">
            或
          </span>
        </div>

        <Button
          variant="outline"
          className="w-full gap-2"
          onClick={handleGoogleLogin}
          disabled={isLoading}
        >
          <svg className="h-4 w-4" viewBox="0 0 24 24">
            <path
              fill="currentColor"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="currentColor"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="currentColor"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="currentColor"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          使用 Google 登入
        </Button>

        <div className="text-center text-sm text-muted-foreground mt-4">
          還沒有帳號？{' '}
          <Link
            to="/auth/register-form"
            className="text-primary hover:underline font-medium"
            onClick={() => onOpenChange(false)}
          >
            立即註冊
          </Link>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default AuthModal;
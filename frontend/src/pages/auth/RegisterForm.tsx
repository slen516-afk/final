import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { UserPlus, Loader2 } from 'lucide-react';
import AuthModal from '@/components/auth/AuthModal';
import { register } from '@/services/authService';
import { useNavigate } from 'react-router-dom';

const RegisterForm = () => {
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      alert('密碼與確認密碼不符');
      return;
    }

    setIsLoading(true);
    try {
      await register(formData.email.trim(), formData.password, formData.name);
      alert('註冊成功！請登入。');
      setAuthModalOpen(true);
    } catch (error: any) {
      console.error('Registration failed:', error);
      alert(error.message || '註冊失敗，請稍後再試');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [e.target.id]: e.target.value }));
  };

  return (
    <>
      <div className="container py-12 animate-fade-in">
        <div className="max-w-md mx-auto">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-6">
              <UserPlus className="h-8 w-8 text-primary" />
            </div>
            <h1 className="text-3xl font-bold mb-2">註冊帳號</h1>
            <p className="text-muted-foreground">開始您的職涯智慧之旅</p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>建立帳號</CardTitle>
              <CardDescription>填寫以下資料完成註冊</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleRegister} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">姓名</Label>
                  <Input id="name" placeholder="請輸入姓名" value={formData.name} onChange={handleChange} required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">電子郵件</Label>
                  <Input id="email" type="email" placeholder="請輸入電子郵件" value={formData.email} onChange={handleChange} required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">密碼</Label>
                  <Input id="password" type="password" placeholder="請輸入密碼" value={formData.password} onChange={handleChange} required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">確認密碼</Label>
                  <Input id="confirmPassword" type="password" placeholder="請再次輸入密碼" value={formData.confirmPassword} onChange={handleChange} required />
                </div>
                <Button className="w-full gradient-primary" disabled={isLoading}>
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      註冊中...
                    </>
                  ) : (
                    '註冊'
                  )}
                </Button>
              </form>
              <p className="text-center text-sm text-muted-foreground mt-4">
                已有帳號？{' '}
                <button
                  type="button"
                  onClick={() => setAuthModalOpen(true)}
                  className="text-primary hover:underline font-medium"
                >
                  登入
                </button>
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
      <AuthModal open={authModalOpen} onOpenChange={setAuthModalOpen} />
    </>
  );
};


export default RegisterForm;

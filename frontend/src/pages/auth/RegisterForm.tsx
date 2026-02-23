import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { UserPlus } from 'lucide-react';

const RegisterForm = () => {
  return (
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
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">姓名</Label>
              <Input id="name" placeholder="請輸入姓名" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">電子郵件</Label>
              <Input id="email" type="email" placeholder="請輸入電子郵件" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">密碼</Label>
              <Input id="password" type="password" placeholder="請輸入密碼" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">確認密碼</Label>
              <Input id="confirmPassword" type="password" placeholder="請再次輸入密碼" />
            </div>
            <Button className="w-full gradient-primary">註冊</Button>
            <p className="text-center text-sm text-muted-foreground">
              已有帳號？{' '}
              <Link to="/" className="text-primary hover:underline">
                登入
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default RegisterForm;

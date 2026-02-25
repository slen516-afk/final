import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useAppState } from '@/contexts/AppContext';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { NavigationMenu, NavigationMenuContent, NavigationMenuItem, NavigationMenuLink, NavigationMenuList, NavigationMenuTrigger } from '@/components/ui/navigation-menu';
import { FileText, BarChart3, User, Menu, LogOut, FileUp, Search, Target, ChevronDown, Map, ClipboardList, Lock, Sparkles, HelpCircle } from 'lucide-react';
import logoImage from '@/assets/logo.png';
import logoCat from '@/assets/logocat.png';
import { Separator } from '@/components/ui/separator';
import { useState } from 'react';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import AuthModal from '@/components/auth/AuthModal';
import PasswordModal from '@/components/member/PasswordModal';

const Navbar = () => {
  const { isLoggedIn, setIsLoggedIn, avatarUrl } = useAppState();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [passwordModalOpen, setPasswordModalOpen] = useState(false);

  const productLinks = [
  { to: '/jobs/skill-search', label: '職類核心技能查詢', icon: Search, description: '根據技能搜尋最適合的職缺' },
  { to: '/resume/optimize', label: '履歷優化', icon: FileText, description: '專業分析並優化您的履歷' },
  { to: '/analysis/skills', label: '職能圖譜', icon: BarChart3, description: '深度分析技能優勢與發展方向' },
  { to: '/jobs/recommendations', label: '推薦職缺', icon: Target, description: '根據您的條件推薦最佳職缺' }];


  const navLinks = [
  { to: '/', label: '首頁' },
  { to: '/team', label: '關於我們' }];


  const handleLogout = () => {
    setIsLoggedIn(false);
    navigate('/');
  };

  return (
    <>
      {/* Warm brown header #966949 */}
      <nav className="sticky top-0 z-50 w-full header-bg border-b border-white/10">
        <div className="container flex h-16 items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5">
            <img src={logoImage} alt="職星領航員 Logo" className="h-9 w-9 object-contain" />
            <div className="flex flex-col leading-none">
              <span className="text-lg font-bold text-white">職星領航員</span>
              <span className="text-xs text-white/60">Career Pilot</span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) =>
            <Link key={link.to} to={link.to}>
                <Button variant="ghost" className="text-white/80 hover:text-white hover:bg-white/10">
                  {link.label}
                </Button>
              </Link>
            )}

            {/* Product Dropdown - 服務項目 */}
            <NavigationMenu>
              <NavigationMenuList>
                <NavigationMenuItem>
                  <NavigationMenuTrigger className="bg-transparent text-white/80 hover:text-white hover:bg-white/10 data-[state=open]:bg-white/10">
                    服務項目
                  </NavigationMenuTrigger>
                  <NavigationMenuContent>
                    <ul className="grid w-[400px] gap-1 p-4 md:w-[500px] md:grid-cols-1">
                      {productLinks.map((link) =>
                      <li key={link.to}>
                          <NavigationMenuLink asChild>
                            <Link to={link.to} className="flex items-center gap-3 select-none rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent/10 focus:bg-accent/10">
                              <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                                <link.icon className="h-5 w-5 text-primary" />
                              </div>
                              <div>
                                <div className="text-sm font-medium leading-none mb-1">{link.label}</div>
                                <p className="text-xs text-muted-foreground">{link.description}</p>
                              </div>
                            </Link>
                          </NavigationMenuLink>
                        </li>
                      )}
                    </ul>
                  </NavigationMenuContent>
                </NavigationMenuItem>
              </NavigationMenuList>
            </NavigationMenu>

            <Link to="/faq">
              <Button variant="ghost" className="text-white/80 hover:text-white hover:bg-white/10">常見問答</Button>
            </Link>
          </div>

          {/* Auth Section */}
          <div className="hidden md:flex items-center gap-3">
            {isLoggedIn ?
            <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="gap-2 pl-2 text-white/80 hover:text-white hover:bg-white/10">
                    <Avatar className="h-8 w-8 border border-white/20 bg-white/80">
                      <AvatarImage src={avatarUrl || logoCat} className="object-cover" />
                      <AvatarFallback className="bg-white/10 text-white text-sm">U</AvatarFallback>
                    </Avatar>
                    <span>會員中心</span>
                    <ChevronDown className="h-4 w-4 opacity-50" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <DropdownMenuItem asChild>
                    <Link to="/member/center" className="flex items-center gap-2"><User className="h-4 w-4" />會員中心</Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/member/my-resumes" className="flex items-center gap-2"><FileText className="h-4 w-4" />我的履歷</Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/member/career-path" className="flex items-center gap-2"><Map className="h-4 w-4" />職涯地圖</Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link to="/member/upload-resume" className="flex items-center gap-2"><FileUp className="h-4 w-4" />履歷上傳</Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/member/survey/personality-test" className="flex items-center gap-2"><Sparkles className="h-4 w-4" />人格特質問卷</Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/member/survey/personality" className="flex items-center gap-2"><ClipboardList className="h-4 w-4" />職涯問卷</Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => setPasswordModalOpen(true)} className="flex items-center gap-2 cursor-pointer">
                    <Lock className="h-4 w-4" />密碼設定
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={handleLogout} className="flex items-center gap-2 text-destructive">
                    <LogOut className="h-4 w-4" />登出
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu> :

            <>
                <Link to="/auth/register-form">
                  <Button variant="ghost" className="text-white/80 hover:text-white hover:bg-white/10">註冊</Button>
                </Link>
                <Button onClick={() => setAuthModalOpen(true)} className="gradient-primary text-primary-foreground">
                  登入
                </Button>
              </>
            }
          </div>

          {/* Mobile Menu */}
          <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
            <SheetTrigger asChild className="md:hidden">
              <Button variant="ghost" size="icon" className="text-white hover:bg-white/10">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-72 bg-white p-0">
              <div className="flex items-center gap-2.5 px-5 pt-5 pb-4 mb-2 bg-[#fbf1e8]">
                <img src={logoImage} alt="職星領航員 Logo" className="h-9 w-9 object-contain" />
                <div className="flex flex-col leading-none">
                  <span className="text-lg font-bold">職星領航員</span>
                  <span className="text-xs text-muted-foreground">Career Pilot</span>
                </div>
              </div>
              <div className="flex flex-col gap-1 px-3">
                {navLinks.map((link) =>
                <Link key={link.to} to={link.to} onClick={() => setMobileOpen(false)} className="flex items-center gap-3 p-3 rounded-lg hover:bg-[#fbf1e8] active:bg-[#fbf1e8] transition-colors">
                    <span className="font-medium">{link.label}</span>
                  </Link>
                )}
                <Link to="/faq" onClick={() => setMobileOpen(false)} className="flex items-center gap-3 p-3 rounded-lg hover:bg-[#fbf1e8] active:bg-[#fbf1e8] transition-colors">
                    <HelpCircle className="h-5 w-5 text-primary" />
                    <span className="font-medium">常見問答</span>
                </Link>
                <div className="border-t border-border my-2 pt-2">
                  <p className="text-xs text-muted-foreground px-3 mb-2">服務項目</p>
                  {productLinks.map((link) =>
                  <Link key={link.to} to={link.to} onClick={() => setMobileOpen(false)} className="flex items-center gap-3 p-3 rounded-lg hover:bg-[#fbf1e8] active:bg-[#fbf1e8] transition-colors">
                      <link.icon className="h-5 w-5 text-primary" />
                      <span className="font-medium">{link.label}</span>
                    </Link>
                  )}
                </div>
                <div className="border-t border-border my-2" />
                {isLoggedIn ?
                <>
                    <Link to="/member/center" onClick={() => setMobileOpen(false)} className="flex items-center gap-3 p-3 rounded-lg hover:bg-[#fbf1e8] active:bg-[#fbf1e8] transition-colors">
                      <User className="h-5 w-5 text-primary" />
                      <span className="font-medium">會員中心</span>
                    </Link>
                    <button onClick={() => {handleLogout();setMobileOpen(false);}} className="flex items-center gap-3 p-3 rounded-lg hover:bg-[#fbf1e8] active:bg-[#fbf1e8] transition-colors text-destructive">
                      <LogOut className="h-5 w-5" />
                      <span className="font-medium">登出</span>
                    </button>
                  </> :

                <div className="flex flex-col gap-2">
                    <Link to="/auth/register-form" onClick={() => setMobileOpen(false)}>
                      <Button variant="outline" className="w-full">註冊</Button>
                    </Link>
                    <Button onClick={() => {setAuthModalOpen(true);setMobileOpen(false);}} className="w-full gradient-primary">
                      登入
                    </Button>
                  </div>
                }
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </nav>

      <AuthModal open={authModalOpen} onOpenChange={setAuthModalOpen} />
      <PasswordModal open={passwordModalOpen} onOpenChange={setPasswordModalOpen} />
    </>);

};

export default Navbar;
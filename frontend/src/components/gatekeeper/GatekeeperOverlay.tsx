import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useAppState } from '@/contexts/AppContext';
import { Check, Circle, LogIn, FileUp, ClipboardCheck, ArrowRight } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

interface GatekeeperOverlayProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onLoginClick: () => void;
}

const GatekeeperOverlay = ({ open, onOpenChange, onLoginClick }: GatekeeperOverlayProps) => {
  const navigate = useNavigate();
  const { isLoggedIn, isResumeUploaded, isPersonalityQuizDone } = useAppState();

  const tasks = [
    {
      label: '登入帳號',
      completed: isLoggedIn,
      icon: LogIn,
      action: () => {
        onOpenChange(false);
        onLoginClick();
      },
      actionLabel: '前往登入',
    },
    {
      label: '上傳履歷',
      completed: isResumeUploaded,
      icon: FileUp,
      to: '/member/upload-resume',
      actionLabel: '上傳履歷',
    },
    {
      label: '完成個性測驗',
      completed: isPersonalityQuizDone,
      icon: ClipboardCheck,
      to: '/member/survey/personality',
      actionLabel: '開始測驗',
    },
  ];

  const completedCount = tasks.filter(t => t.completed).length;
  const progress = (completedCount / tasks.length) * 100;

  const handleOpenChange = (isOpen: boolean) => {
    if (!isOpen) {
      // Navigate back to previous page when closing
      navigate(-1);
    }
    onOpenChange(isOpen);
  };

  return (
    <>
      {/* Backdrop Blur Overlay */}
      {open && (
        <div className="fixed inset-0 z-40 bg-background/60 backdrop-blur-sm" />
      )}
      
      <Dialog open={open} onOpenChange={handleOpenChange}>
        <DialogContent className="sm:max-w-lg z-50">
          <DialogHeader>
            <DialogTitle className="text-xl flex items-center gap-2">
              <span className="text-2xl">🔒</span>
              解鎖此功能
            </DialogTitle>
            <DialogDescription>
              完成以下任務即可使用完整功能
            </DialogDescription>
          </DialogHeader>

          {/* Progress Bar */}
          <div className="mb-4">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-muted-foreground">完成進度</span>
              <span className="font-medium">{completedCount}/{tasks.length}</span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div 
                className="h-full bg-primary transition-all duration-500 rounded-full"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          {/* Task Checklist */}
          <div className="space-y-3">
            {tasks.map((task, index) => (
              <div
                key={index}
                className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
                  task.completed 
                    ? 'bg-primary/5 border-primary/20' 
                    : 'bg-muted/30 border-border'
                }`}
              >
                <div className="flex items-center gap-3">
                  {task.completed ? (
                    <div className="h-6 w-6 rounded-full bg-primary flex items-center justify-center">
                      <Check className="h-4 w-4 text-primary-foreground" />
                    </div>
                  ) : (
                    <div className="h-6 w-6 rounded-full border-2 border-muted-foreground/30 flex items-center justify-center">
                      <Circle className="h-3 w-3 text-muted-foreground/30" />
                    </div>
                  )}
                  <span className={task.completed ? 'text-muted-foreground line-through' : 'font-medium'}>
                    {task.label}
                  </span>
                </div>
                
                {!task.completed && (
                  task.to ? (
                    <Link to={task.to} onClick={() => onOpenChange(false)}>
                      <Button size="sm" variant="outline" className="gap-1">
                        {task.actionLabel}
                        <ArrowRight className="h-3 w-3" />
                      </Button>
                    </Link>
                  ) : (
                    <Button size="sm" variant="outline" className="gap-1" onClick={task.action}>
                      {task.actionLabel}
                      <ArrowRight className="h-3 w-3" />
                    </Button>
                  )
                )}
              </div>
            ))}
          </div>

          <div className="mt-4 p-3 bg-amber-50 dark:bg-amber-950/20 rounded-lg border border-amber-200 dark:border-amber-800">
            <p className="text-sm text-amber-800 dark:text-amber-200">
              💡 <strong>提示：</strong>登入帳號是使用所有功能的第一步，請先完成登入！
            </p>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default GatekeeperOverlay;

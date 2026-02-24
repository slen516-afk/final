import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useAppState } from '@/contexts/AppContext';
import { Check, Circle, LogIn, FileUp, ClipboardCheck, Brain, Heart, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { GateFlag } from './ProtectedRoute';

interface GatekeeperOverlayProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onLoginClick: () => void;
  requiredFlags?: GateFlag[];
}

const GatekeeperOverlay = ({ open, onOpenChange, onLoginClick, requiredFlags }: GatekeeperOverlayProps) => {
  const state = useAppState();

  // All possible tasks
  const allTasks: Record<GateFlag, {
    label: string;
    completed: boolean;
    icon: typeof LogIn;
    action?: () => void;
    to?: string;
    actionLabel: string;
  }> = {
    isLoggedIn: {
      label: '登入帳號',
      completed: state.isLoggedIn,
      icon: LogIn,
      action: () => {
        onOpenChange(false);
        onLoginClick();
      },
      actionLabel: '前往登入',
    },
    isResumeUploaded: {
      label: '上傳履歷',
      completed: state.isResumeUploaded,
      icon: FileUp,
      to: '/member/upload-resume',
      actionLabel: '上傳履歷',
    },
    isPersonalityQuizDone: {
      label: '完成職涯問卷',
      completed: state.isPersonalityQuizDone,
      icon: ClipboardCheck,
      to: '/member/survey/personality',
      actionLabel: '開始測驗',
    },
    isPersonalityTestDone: {
      label: '完成人格問卷',
      completed: state.isPersonalityTestDone,
      icon: Brain,
      to: '/member/survey/personality-test',
      actionLabel: '開始測驗',
    },
    isJobPreferenceQuizDone: {
      label: '完成工作偏好問卷',
      completed: state.isJobPreferenceQuizDone,
      icon: Heart,
      to: '/jobs/recommendations',
      actionLabel: '開始填寫',
    },
  };

  // Filter to only required flags
  const flags = requiredFlags || ['isLoggedIn', 'isResumeUploaded', 'isPersonalityQuizDone'];
  const tasks = flags.map((f) => allTasks[f]);

  const completedCount = tasks.filter(t => t.completed).length;
  const progress = (completedCount / tasks.length) * 100;

  const handleOpenChange = (isOpen: boolean) => {
    onOpenChange(isOpen);
  };

  return (
    <>
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
                    <Link to={task.to}>
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
              💡 <strong>提示：</strong>請依序完成上方任務以解鎖此功能！
            </p>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default GatekeeperOverlay;

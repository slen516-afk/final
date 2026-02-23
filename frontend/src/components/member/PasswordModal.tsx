import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Lock, X, Eye, EyeOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import AlertModal from '@/components/modals/AlertModal';

interface PasswordModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const PasswordModal = ({ open, onOpenChange }: PasswordModalProps) => {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [confirmAlertOpen, setConfirmAlertOpen] = useState(false);
  const [resultAlert, setResultAlert] = useState<{ open: boolean; type: 'success' | 'error'; title: string; message: string }>({
    open: false, type: 'success', title: '', message: ''
  });

  const resetForm = () => {
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
    setShowCurrent(false);
    setShowNew(false);
    setShowConfirm(false);
    setErrors({});
  };

  const handleClose = () => {
    resetForm();
    onOpenChange(false);
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!currentPassword.trim()) {
      newErrors.currentPassword = '請輸入目前密碼';
    }
    if (!newPassword.trim()) {
      newErrors.newPassword = '請輸入新密碼';
    } else if (newPassword.length < 8) {
      newErrors.newPassword = '新密碼長度至少需要 8 個字元';
    }
    if (!confirmPassword.trim()) {
      newErrors.confirmPassword = '請再次輸入新密碼';
    } else if (newPassword !== confirmPassword) {
      newErrors.confirmPassword = '兩次輸入的新密碼不一致，請重新確認';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmitClick = () => {
    if (!validate()) return;
    setConfirmAlertOpen(true);
  };

  const handleConfirm = () => {
    // Simulate API call — in real app, call backend here
    const isCurrentPasswordCorrect = currentPassword === 'password123'; // placeholder check

    if (!isCurrentPasswordCorrect) {
      setResultAlert({
        open: true,
        type: 'error',
        title: '密碼更新失敗',
        message: '目前密碼不正確，請重新輸入。',
      });
      setErrors({ currentPassword: '目前密碼不正確，請重新輸入' });
      return;
    }

    setResultAlert({
      open: true,
      type: 'success',
      title: '密碼已更新',
      message: '您的密碼已成功變更。',
    });
    resetForm();
  };

  const handleResultClose = () => {
    setResultAlert(prev => ({ ...prev, open: false }));
    if (resultAlert.type === 'success') {
      onOpenChange(false);
    }
  };

  const mismatch = confirmPassword.length > 0 && newPassword !== confirmPassword;

  return (
    <>
      <AnimatePresence>
        {open && (
          <>
            <motion.div
              className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={handleClose}
            />
            <motion.div
              className="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 px-4"
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            >
              <div className="ui-white rounded-2xl border overflow-hidden">
                {/* Header */}
                <div className="relative p-5 pb-3 border-b">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <Lock className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold">變更密碼</h3>
                      <p className="text-xs text-muted-foreground">請輸入您的目前密碼與新密碼</p>
                    </div>
                  </div>
                  <button
                    onClick={handleClose}
                    className="absolute right-4 top-4 h-8 w-8 rounded-full hover:bg-muted flex items-center justify-center transition-colors"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>

                {/* Form */}
                <div className="p-5 space-y-4">
                  {/* Current Password */}
                  <div className="space-y-1.5">
                    <Label htmlFor="modal-currentPassword" className="text-sm">目前密碼</Label>
                    <div className="relative">
                      <Input
                        id="modal-currentPassword"
                        type={showCurrent ? 'text' : 'password'}
                        placeholder="請輸入目前密碼"
                        value={currentPassword}
                        onChange={(e) => { setCurrentPassword(e.target.value); setErrors(prev => ({ ...prev, currentPassword: '' })); }}
                        className={`pr-10 text-sm transition-shadow ${errors.currentPassword ? 'border-destructive focus-visible:ring-destructive' : 'focus-visible:ring-primary/40 focus-visible:border-primary focus-visible:shadow-[0_0_0_3px_hsl(var(--primary)/0.12)]'}`}
                      />
                      <button type="button" onClick={() => setShowCurrent(!showCurrent)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors">
                        {showCurrent ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                    {errors.currentPassword && <p className="text-xs text-destructive">{errors.currentPassword}</p>}
                  </div>

                  {/* New Password */}
                  <div className="space-y-1.5">
                    <Label htmlFor="modal-newPassword" className="text-sm">新密碼</Label>
                    <div className="relative">
                      <Input
                        id="modal-newPassword"
                        type={showNew ? 'text' : 'password'}
                        placeholder="請輸入新密碼（至少 8 個字元）"
                        value={newPassword}
                        onChange={(e) => { setNewPassword(e.target.value); setErrors(prev => ({ ...prev, newPassword: '' })); }}
                        className={`pr-10 text-sm transition-shadow ${errors.newPassword ? 'border-destructive focus-visible:ring-destructive' : 'focus-visible:ring-primary/40 focus-visible:border-primary focus-visible:shadow-[0_0_0_3px_hsl(var(--primary)/0.12)]'}`}
                      />
                      <button type="button" onClick={() => setShowNew(!showNew)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors">
                        {showNew ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                    {errors.newPassword && <p className="text-xs text-destructive">{errors.newPassword}</p>}
                  </div>

                  {/* Confirm Password */}
                  <div className="space-y-1.5">
                    <Label htmlFor="modal-confirmPassword" className="text-sm">確認新密碼</Label>
                    <div className="relative">
                      <Input
                        id="modal-confirmPassword"
                        type={showConfirm ? 'text' : 'password'}
                        placeholder="請再次輸入新密碼"
                        value={confirmPassword}
                        onChange={(e) => { setConfirmPassword(e.target.value); setErrors(prev => ({ ...prev, confirmPassword: '' })); }}
                        className={`pr-10 text-sm transition-shadow ${errors.confirmPassword || mismatch ? 'border-destructive focus-visible:ring-destructive' : 'focus-visible:ring-primary/40 focus-visible:border-primary focus-visible:shadow-[0_0_0_3px_hsl(var(--primary)/0.12)]'}`}
                      />
                      <button type="button" onClick={() => setShowConfirm(!showConfirm)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors">
                        {showConfirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                    {errors.confirmPassword && <p className="text-xs text-destructive">{errors.confirmPassword}</p>}
                    {mismatch && !errors.confirmPassword && <p className="text-xs text-destructive">兩次輸入的新密碼不一致</p>}
                  </div>
                </div>

                {/* Actions */}
                <div className="p-4 bg-muted/30 border-t flex gap-3">
                  <Button variant="outline" className="flex-1" onClick={handleClose}>
                    取消
                  </Button>
                  <Button className="flex-1 gradient-primary" onClick={handleSubmitClick}>
                    確認修改
                  </Button>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Confirm Alert */}
      <AlertModal
        open={confirmAlertOpen}
        onClose={() => setConfirmAlertOpen(false)}
        type="warning"
        title="確認變更密碼"
        message="您確定要更新密碼嗎？"
        showCancel
        confirmLabel="確定更新"
        cancelLabel="取消"
        onConfirm={handleConfirm}
      />

      {/* Result Alert */}
      <AlertModal
        open={resultAlert.open}
        onClose={handleResultClose}
        type={resultAlert.type}
        title={resultAlert.title}
        message={resultAlert.message}
      />
    </>
  );
};

export default PasswordModal;

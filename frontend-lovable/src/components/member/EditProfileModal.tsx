import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface EditProfileModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const EditProfileModal = ({ open, onOpenChange }: EditProfileModalProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>修改基本資料</DialogTitle>
          <DialogDescription>
            更新您的個人資訊，完成後點擊儲存。所有欄位皆為選填。
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4 max-h-[60vh] overflow-y-auto">
          <div className="space-y-2">
            <Label htmlFor="name">姓名</Label>
            <Input id="name" placeholder="請輸入姓名（選填）" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="title">目前職位</Label>
            <Input id="title" placeholder="例如：前端工程師" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="location">所在地（縣市）</Label>
            <Input id="location" placeholder="例如：桃園市" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="experience">工作年資</Label>
            <Input id="experience" placeholder="例如：3 年" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="education">教育背景</Label>
            <Input id="education" placeholder="例如：國立臺灣大學 資訊工程學系" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="github">GitHub 連結</Label>
            <Input id="github" placeholder="例如：https://github.com/username" />
          </div>
        </div>
        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            取消
          </Button>
          <Button onClick={() => onOpenChange(false)} className="gradient-primary">
            儲存變更
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default EditProfileModal;

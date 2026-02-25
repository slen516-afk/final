import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { X, Download, Loader2 } from 'lucide-react';

interface RightDrawerProps {
  open: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  showDownload?: boolean;
  onDownload?: () => void;
  isDownloading?: boolean;
}

const RightDrawer = ({
  open,
  onClose,
  title,
  subtitle,
  children,
  showDownload = false,
  onDownload,
  isDownloading = false,
}: RightDrawerProps) => {
  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 z-50 bg-black/50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Drawer */}
          <motion.div
            className="fixed right-0 top-0 z-50 h-full w-full max-w-md bg-background shadow-large border-l"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b">
              <div>
                <h2 className="text-lg font-semibold">{title}</h2>
                {subtitle && (
                  <p className="text-sm text-muted-foreground">{subtitle}</p>
                )}
              </div>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-5 w-5" />
              </Button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6 h-[calc(100%-140px)]">
              {children}
            </div>

            {/* Footer */}
            {showDownload && (
              <div className="absolute bottom-0 left-0 right-0 p-4 border-t bg-background">
                <Button
                  className="w-full gradient-primary gap-2"
                  onClick={onDownload}
                  disabled={isDownloading}
                >
                  {isDownloading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      下載中...
                    </>
                  ) : (
                    <>
                      <Download className="h-4 w-4" />
                      下載文件
                    </>
                  )}
                </Button>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default RightDrawer;

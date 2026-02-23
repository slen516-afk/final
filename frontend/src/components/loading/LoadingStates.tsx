import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import logoImage from '@/assets/logo.png';
import { Skeleton } from '@/components/ui/skeleton';

interface AILoadingSpinnerProps {
  message?: string;
}

export const AILoadingSpinner = ({ message = '正在為您處理，請稍候...' }: AILoadingSpinnerProps) => {
  return (
    <motion.div
      className="flex flex-col items-center justify-center py-12"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="relative">
        <img src={logoImage} alt="載入中" className="h-16 w-16 object-contain animate-pulse" />
        <Loader2 className="absolute -top-1 -right-1 h-6 w-6 text-primary animate-spin" />
      </div>
      <p className="mt-4 text-muted-foreground animate-pulse">{message}</p>
    </motion.div>
  );
};

export const CardSkeleton = () => {
  return (
    <div className="rounded-lg border bg-card p-6 space-y-4">
      <div className="flex items-center space-x-4">
        <Skeleton className="h-12 w-12 rounded-full" />
        <div className="space-y-2 flex-1">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
        </div>
      </div>
      <Skeleton className="h-20 w-full" />
      <div className="flex gap-2">
        <Skeleton className="h-6 w-16 rounded-full" />
        <Skeleton className="h-6 w-20 rounded-full" />
        <Skeleton className="h-6 w-14 rounded-full" />
      </div>
    </div>
  );
};

export const ResultsSkeleton = () => {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
};

export const AnalysisSkeleton = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-10 w-32" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="rounded-lg border bg-card p-4 space-y-3">
            <Skeleton className="h-6 w-24" />
            <Skeleton className="h-24 w-full" />
          </div>
        ))}
      </div>
      <div className="rounded-lg border bg-card p-6 space-y-4">
        <Skeleton className="h-6 w-32" />
        <div className="space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
          <Skeleton className="h-4 w-4/5" />
        </div>
      </div>
    </div>
  );
};

interface ContentTransitionProps {
  isLoading: boolean;
  skeleton: React.ReactNode;
  children: React.ReactNode;
}

export const ContentTransition = ({ isLoading, skeleton, children }: ContentTransitionProps) => {
  return (
    <motion.div
      initial={false}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {isLoading ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          {skeleton}
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
        >
          {children}
        </motion.div>
      )}
    </motion.div>
  );
};

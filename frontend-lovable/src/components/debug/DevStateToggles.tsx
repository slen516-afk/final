import { useState, forwardRef } from 'react';
import { useAppState } from '@/contexts/AppContext';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Settings, X, ChevronUp, ChevronDown, Unlock } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const DevStateToggles = forwardRef<HTMLDivElement>((_, ref) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const {
    isLoggedIn,
    isResumeUploaded,
    isPersonalityQuizDone,
    isJobPreferenceQuizDone,
    isPersonalityTestDone,
    setIsLoggedIn,
    setIsResumeUploaded,
    setIsPersonalityQuizDone,
    setIsJobPreferenceQuizDone,
    setIsPersonalityTestDone,
  } = useAppState();

  const unlockAll = () => {
    setIsLoggedIn(true);
    setIsResumeUploaded(true);
    setIsPersonalityQuizDone(true);
    setIsJobPreferenceQuizDone(true);
    setIsPersonalityTestDone(true);
  };

  const resetAll = () => {
    setIsLoggedIn(false);
    setIsResumeUploaded(false);
    setIsPersonalityQuizDone(false);
    setIsJobPreferenceQuizDone(false);
    setIsPersonalityTestDone(false);
  };

  const toggles = [
    { label: 'isLoggedIn', value: isLoggedIn, setter: setIsLoggedIn },
    { label: 'isResumeUploaded', value: isResumeUploaded, setter: setIsResumeUploaded },
    { label: 'isPersonalityQuizDone', value: isPersonalityQuizDone, setter: setIsPersonalityQuizDone },
    { label: 'isJobPreferenceQuizDone', value: isJobPreferenceQuizDone, setter: setIsJobPreferenceQuizDone },
    { label: 'isPersonalityTestDone', value: isPersonalityTestDone, setter: setIsPersonalityTestDone },
  ];

  if (!isOpen) {
    return (
      <motion.button
        className="fixed bottom-6 left-6 z-50 h-12 w-12 rounded-full bg-foreground/90 text-background shadow-lg flex items-center justify-center hover:scale-110 transition-transform"
        onClick={() => setIsOpen(true)}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        title="開發者調試面板"
      >
        <Settings className="h-5 w-5" />
      </motion.button>
    );
  }

  return (
    <AnimatePresence>
      <motion.div
        className="fixed bottom-6 left-6 z-50 w-72 bg-card border border-border rounded-xl shadow-large overflow-hidden"
        initial={{ opacity: 0, y: 20, scale: 0.9 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 20, scale: 0.9 }}
      >
        {/* Header */}
        <div className="bg-foreground/5 px-4 py-3 flex items-center justify-between border-b border-border">
          <div className="flex items-center gap-2">
            <Settings className="h-4 w-4 text-primary" />
            <span className="text-sm font-semibold">Dev State Toggles</span>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="h-7 w-7 rounded-md hover:bg-muted flex items-center justify-center transition-colors"
            >
              {isMinimized ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </button>
            <button
              onClick={() => setIsOpen(false)}
              className="h-7 w-7 rounded-md hover:bg-muted flex items-center justify-center transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Content */}
        {!isMinimized && (
          <div className="p-4 space-y-4">
            {/* Toggles */}
            <div className="space-y-3">
              {toggles.map((toggle) => (
                <div key={toggle.label} className="flex items-center justify-between">
                  <Label htmlFor={toggle.label} className="text-xs font-mono">
                    {toggle.label}
                  </Label>
                  <Switch
                    id={toggle.label}
                    checked={toggle.value}
                    onCheckedChange={toggle.setter}
                  />
                </div>
              ))}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2 pt-2 border-t border-border">
              <Button
                size="sm"
                className="flex-1 gradient-primary gap-1"
                onClick={unlockAll}
              >
                <Unlock className="h-3 w-3" />
                一鍵解鎖
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="flex-1"
                onClick={resetAll}
              >
                重置全部
              </Button>
            </div>

            {/* Status Summary */}
            <div className="pt-2 border-t border-border">
              <p className="text-xs text-muted-foreground text-center">
                已解鎖: {toggles.filter(t => t.value).length} / {toggles.length}
              </p>
            </div>
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  );
});

DevStateToggles.displayName = 'DevStateToggles';

export default DevStateToggles;

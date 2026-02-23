import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AppState {
  isLoggedIn: boolean;
  isResumeUploaded: boolean;
  isPersonalityQuizDone: boolean;
  isJobPreferenceQuizDone: boolean;
  isPersonalityTestDone: boolean;
  avatarUrl: string | null;
  setIsLoggedIn: (value: boolean) => void;
  setIsResumeUploaded: (value: boolean) => void;
  setIsPersonalityQuizDone: (value: boolean) => void;
  setIsJobPreferenceQuizDone: (value: boolean) => void;
  setIsPersonalityTestDone: (value: boolean) => void;
  setAvatarUrl: (value: string | null) => void;
}

const APP_STATE_KEY = 'app-global-state';

interface PersistedFlags {
  isLoggedIn: boolean;
  isResumeUploaded: boolean;
  isPersonalityQuizDone: boolean;
  isJobPreferenceQuizDone: boolean;
  isPersonalityTestDone: boolean;
  avatarUrl: string | null;
}

const loadFlags = (): PersistedFlags => {
  try {
    const saved = localStorage.getItem(APP_STATE_KEY);
    if (saved) return JSON.parse(saved);
  } catch {}
  return {
    isLoggedIn: false,
    isResumeUploaded: false,
    isPersonalityQuizDone: false,
    isJobPreferenceQuizDone: false,
    isPersonalityTestDone: false,
    avatarUrl: null,
  };
};

const AppContext = createContext<AppState | undefined>(undefined);

export const AppProvider = ({ children }: { children: ReactNode }) => {
  const initial = loadFlags();
  const [isLoggedIn, setIsLoggedIn] = useState(initial.isLoggedIn);
  const [isResumeUploaded, setIsResumeUploaded] = useState(initial.isResumeUploaded);
  const [isPersonalityQuizDone, setIsPersonalityQuizDone] = useState(initial.isPersonalityQuizDone);
  const [isJobPreferenceQuizDone, setIsJobPreferenceQuizDone] = useState(initial.isJobPreferenceQuizDone);
  const [isPersonalityTestDone, setIsPersonalityTestDone] = useState(initial.isPersonalityTestDone);
  const [avatarUrl, setAvatarUrl] = useState(initial.avatarUrl);

  // Persist flags whenever they change
  useEffect(() => {
    const flags: PersistedFlags = {
      isLoggedIn,
      isResumeUploaded,
      isPersonalityQuizDone,
      isJobPreferenceQuizDone,
      isPersonalityTestDone,
      avatarUrl,
    };
    localStorage.setItem(APP_STATE_KEY, JSON.stringify(flags));
  }, [isLoggedIn, isResumeUploaded, isPersonalityQuizDone, isJobPreferenceQuizDone, isPersonalityTestDone, avatarUrl]);

  return (
    <AppContext.Provider
      value={{
        isLoggedIn,
        isResumeUploaded,
        isPersonalityQuizDone,
        isJobPreferenceQuizDone,
        isPersonalityTestDone,
        avatarUrl,
        setIsLoggedIn,
        setIsResumeUploaded,
        setIsPersonalityQuizDone,
        setIsJobPreferenceQuizDone,
        setIsPersonalityTestDone,
        setAvatarUrl,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useAppState = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppState must be used within an AppProvider');
  }
  return context;
};

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// 🌟 1. 定義使用者的資料結構 (對應你 Supabase 裡的 users 資料表)
export interface UserData {
  user_id: number;
  email: string;
  // 未來如果需要，隨時可以在這裡擴充其他欄位 (例如 optimization_quota_per_month)
  [key: string]: any;
}

interface AppState {
  isLoggedIn: boolean;
  user: UserData | null; // 👈 新增：用來存放當前登入使用者的完整資訊
  isResumeUploaded: boolean;
  isPersonalityQuizDone: boolean;
  isJobPreferenceQuizDone: boolean;
  isPersonalityTestDone: boolean;
  avatarUrl: string | null;
  setIsLoggedIn: (value: boolean) => void;
  setUser: (user: UserData | null) => void; // 👈 新增：用來更新使用者資訊的函式
  setIsResumeUploaded: (value: boolean) => void;
  setIsPersonalityQuizDone: (value: boolean) => void;
  setIsJobPreferenceQuizDone: (value: boolean) => void;
  setIsPersonalityTestDone: (value: boolean) => void;
  setAvatarUrl: (value: string | null) => void;
}

const APP_STATE_KEY = 'app-global-state';

interface PersistedFlags {
  isLoggedIn: boolean;
  user: UserData | null; // 👈 新增
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
  } catch { }
  return {
    isLoggedIn: false,
    user: null, // 👈 新增：預設為未登入(null)
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
  const [user, setUser] = useState<UserData | null>(initial.user); // 👈 新增
  const [isResumeUploaded, setIsResumeUploaded] = useState(initial.isResumeUploaded);
  const [isPersonalityQuizDone, setIsPersonalityQuizDone] = useState(initial.isPersonalityQuizDone);
  const [isJobPreferenceQuizDone, setIsJobPreferenceQuizDone] = useState(initial.isJobPreferenceQuizDone);
  const [isPersonalityTestDone, setIsPersonalityTestDone] = useState(initial.isPersonalityTestDone);
  const [avatarUrl, setAvatarUrl] = useState(initial.avatarUrl);

  // Persist flags whenever they change
  useEffect(() => {
    const flags: PersistedFlags = {
      isLoggedIn,
      user, // 👈 新增：把使用者資訊也存進 localStorage，這樣重新整理網頁才不會被登出
      isResumeUploaded,
      isPersonalityQuizDone,
      isJobPreferenceQuizDone,
      isPersonalityTestDone,
      avatarUrl,
    };
    localStorage.setItem(APP_STATE_KEY, JSON.stringify(flags));
  }, [isLoggedIn, user, isResumeUploaded, isPersonalityQuizDone, isJobPreferenceQuizDone, isPersonalityTestDone, avatarUrl]); // 記得依賴陣列也要加上 user

  return (
    <AppContext.Provider
      value={{
        isLoggedIn,
        user, // 👈 新增
        isResumeUploaded,
        isPersonalityQuizDone,
        isJobPreferenceQuizDone,
        isPersonalityTestDone,
        avatarUrl,
        setIsLoggedIn,
        setUser, // 👈 新增
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
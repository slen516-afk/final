import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { ResumeItem } from '@/types/resume';
import { MOCK_RESUMES } from '@/mocks/resumes';

// Re-export for backward compatibility
export type { ResumeItem };

interface ResumeState {
  resumes: ResumeItem[];
  selectedResumeId: number | null;
  setSelectedResumeId: (id: number | null) => void;
}

const STORAGE_KEY = 'selectedResumeId';

export const ResumeProvider = ({ children }: { children: ReactNode }) => {
  // TODO: Replace with API call
  const resumes = MOCK_RESUMES;

  // Smart default: pick most recent resume by updatedAt, or use localStorage
  const getDefaultId = (): number | null => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const id = parseInt(stored, 10);
      if (resumes.some((r) => r.id === id)) return id;
    }
    if (resumes.length === 0) return null;
    const sorted = [...resumes].sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
    return sorted[0].id;
  };

  const [selectedResumeId, setSelectedResumeIdState] = useState<number | null>(getDefaultId);

  const setSelectedResumeId = (id: number | null) => {
    setSelectedResumeIdState(id);
    if (id !== null) {
      localStorage.setItem(STORAGE_KEY, id.toString());
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  };

  return (
    <ResumeContext.Provider value={{ resumes, selectedResumeId, setSelectedResumeId }}>
      {children}
    </ResumeContext.Provider>
  );
};

const ResumeContext = createContext<ResumeState | undefined>(undefined);

export const useResumes = () => {
  const context = useContext(ResumeContext);
  if (!context) {
    throw new Error('useResumes must be used within a ResumeProvider');
  }
  return context;
};

"use client";

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { MockQueryResult, PipelineStage, HistoryItem, mockHistory } from '@/services/mockData';

export type Persona = 'manufacturer' | 'importer' | 'consumer';
export type Language = 'en' | 'hi' | 'mr' | 'ta' | 'te';

export interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info';
}

export interface ClassificationResult {
  scheme: string;
  reasons: string[];
}

interface AppState {
  // Persona
  persona: Persona;
  setPersona: (p: Persona) => void;

  // Language
  language: Language;
  setLanguage: (l: Language) => void;

  // Query
  activeQuery: string;
  setActiveQuery: (q: string) => void;

  // Pipeline
  pipelineStages: PipelineStage[];
  setPipelineStages: (s: PipelineStage[]) => void;
  isPipelineRunning: boolean;
  setIsPipelineRunning: (r: boolean) => void;

  // Result
  activeResult: MockQueryResult | null;
  setActiveResult: (r: MockQueryResult | null) => void;

  classificationResult: ClassificationResult | null;
  setClassificationResult: (r: ClassificationResult | null) => void;

  // History
  queryHistory: HistoryItem[];
  addToHistory: (item: HistoryItem) => void;

  // Toasts
  toasts: Toast[];
  addToast: (t: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;

  // Modals
  isLabFinderOpen: boolean;
  setLabFinderOpen: (open: boolean) => void;
  isLoggedIn: boolean;
  setLoggedIn: (logged: boolean) => void;

  // Active tab
  activeTab: 'roadmap' | 'impact' | 'verify';
  setActiveTab: (tab: 'roadmap' | 'impact' | 'verify') => void;

  // New query / reset
  setNewQuery: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      persona: 'manufacturer',
      setPersona: (p) => set({ persona: p }),

      language: 'en',
      setLanguage: (l) => set({ language: l }),

      activeQuery: '',
      setActiveQuery: (q) => set({ activeQuery: q }),

      pipelineStages: [],
      setPipelineStages: (s) => set({ pipelineStages: s }),
      isPipelineRunning: false,
      setIsPipelineRunning: (r) => set({ isPipelineRunning: r }),

      activeResult: null,
      setActiveResult: (r) => set({ activeResult: r }),

      classificationResult: null,
      setClassificationResult: (r) => set({ classificationResult: r }),

      queryHistory: mockHistory,
      addToHistory: (item) => set((state) => ({ queryHistory: [item, ...state.queryHistory] })),

      toasts: [],
      addToast: (t) => set((state) => ({
        toasts: [...state.toasts, { ...t, id: `toast-${Date.now()}-${Math.random()}` }]
      })),
      removeToast: (id) => set((state) => ({
        toasts: state.toasts.filter(t => t.id !== id)
      })),

      isLabFinderOpen: false,
      setLabFinderOpen: (open) => set({ isLabFinderOpen: open }),
      isLoggedIn: false,
      setLoggedIn: (logged) => set({ isLoggedIn: logged }),

      activeTab: 'roadmap',
      setActiveTab: (tab) => set({ activeTab: tab }),

      setNewQuery: () => set({
        activeQuery: '',
        pipelineStages: [],
        isPipelineRunning: false,
        activeResult: null,
        activeTab: 'roadmap',
      }),
    }),
    {
      name: 'navic-app-store',
      // We only want to persist language and persona, not active state
      partialize: (state) => ({
        language: state.language,
        persona: state.persona,
      }),
    }
  )
);

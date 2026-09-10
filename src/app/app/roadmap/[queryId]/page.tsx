"use client";

import { useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useAppStore } from '@/store/useAppStore';
import { mockQueries } from '@/services/mockData';
import ChatPanel from '@/components/chat/ChatPanel';
import RoadmapOutput from '@/components/roadmap/RoadmapOutput';

export default function RoadmapPage() {
  const params = useParams();
  const { setActiveResult, setActiveTab, activeResult } = useAppStore();
  const queryId = params.queryId as string;

  useEffect(() => {
    // Find result by ID
    const result = Object.values(mockQueries).find(q => q.id === queryId);
    if (result && !activeResult) {
      setActiveResult(result);
      setActiveTab('roadmap');
    }
  }, [queryId, setActiveResult, setActiveTab, activeResult]);

  return (
    <div className="flex-1 max-w-[1440px] w-full mx-auto px-4 py-6">
      <div className="flex flex-col lg:flex-row gap-6 h-full">
        <div className="w-full lg:w-[35%] lg:max-h-[calc(100vh-10rem)] lg:overflow-y-auto lg:sticky lg:top-20 bg-card rounded-2xl border border-border p-5 shadow-sm">
          <ChatPanel />
        </div>
        <div className="w-full lg:w-[65%] min-h-[60vh]">
          <RoadmapOutput />
        </div>
      </div>
    </div>
  );
}

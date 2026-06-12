import React from 'react';
import { Sidebar } from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Layout: React.FC<LayoutProps> = ({ children, activeTab, setActiveTab }) => {
  return (
    <div className="h-full flex overflow-hidden">
      {/* Sidebar Frame */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      {/* Scrollable Content Area */}
      <main className="flex-1 overflow-y-auto bg-slate-50 dark:bg-slate-900 transition-colors p-8">
        <div className="max-w-6xl mx-auto h-full">
          {children}
        </div>
      </main>
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import DashboardOverview from './components/DashboardOverview';
import AIProvidersManager from './components/AIProvidersManager';
import ImageProvidersManager from './components/ImageProvidersManager';
import FacebookSettings from './components/FacebookSettings';
import SchedulerManager from './components/SchedulerManager';
import CaptionTemplateManager from './components/CaptionTemplateManager';
import ContentManager from './components/ContentManager';
import QuickGenerateModal from './components/QuickGenerateModal';
import { api } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState(null);
  const [isQuickGenerateOpen, setIsQuickGenerateOpen] = useState(false);
  const [automationEnabled, setAutomationEnabled] = useState(true);

  const fetchDashboardData = async () => {
    try {
      const data = await api.getDashboard();
      setDashboardData(data);
      if (data?.stats?.automation_enabled !== undefined) {
        setAutomationEnabled(data.stats.automation_enabled);
      }
    } catch (err) {
      console.error('Error fetching dashboard summary:', err);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 20000); // 20s refresh
    return () => clearInterval(interval);
  }, []);

  const handleToggleAutomation = async () => {
    try {
      const nextState = !automationEnabled;
      setAutomationEnabled(nextState);
      await api.toggleAutomation(nextState);
      fetchDashboardData();
    } catch (err) {
      alert(`Error toggling automation: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-100 flex flex-col font-sans">
      
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        automationEnabled={automationEnabled}
        onToggleAutomation={handleToggleAutomation}
        onOpenQuickGenerate={() => setIsQuickGenerateOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {activeTab === 'dashboard' && (
          <DashboardOverview
            dashboardData={dashboardData}
            onRefresh={fetchDashboardData}
            onNavigateTab={(tab) => setActiveTab(tab)}
            onOpenQuickGenerate={() => setIsQuickGenerateOpen(true)}
          />
        )}

        {activeTab === 'providers' && <AIProvidersManager />}

        {activeTab === 'images' && <ImageProvidersManager />}

        {activeTab === 'facebook' && <FacebookSettings />}

        {activeTab === 'scheduler' && <SchedulerManager />}

        {activeTab === 'templates' && <CaptionTemplateManager />}

        {activeTab === 'content' && (
          <ContentManager onOpenQuickGenerate={() => setIsQuickGenerateOpen(true)} />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p>© 2026 Universal AI Social Publisher · Fully Automated Fixed-Time Social Architecture</p>
          <div className="flex items-center gap-4 text-slate-400">
            <span>Official Meta Graph API v21.0</span>
            <span>•</span>
            <span>Documentary AI Engine</span>
          </div>
        </div>
      </footer>

      {/* Quick Generate Modal */}
      <QuickGenerateModal
        isOpen={isQuickGenerateOpen}
        onClose={() => setIsQuickGenerateOpen(false)}
        onSuccess={() => {
          fetchDashboardData();
        }}
      />

    </div>
  );
}

import React from 'react';

export default function Navbar({ activeTab, setActiveTab, automationEnabled, onToggleAutomation, onOpenQuickGenerate }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'providers', label: 'AI Providers', icon: '🧠' },
    { id: 'images', label: 'Image Engine', icon: '🎨' },
    { id: 'facebook', label: 'Facebook Page', icon: '🌐' },
    { id: 'scheduler', label: 'Fixed Scheduler', icon: '⏰' },
    { id: 'templates', label: 'Caption Styles', icon: '✍️' },
    { id: 'content', label: 'Content Library', icon: '📚' },
  ];

  return (
    <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          
          {/* Brand Logo & Name */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center shadow-lg shadow-indigo-500/25">
              <span className="text-xl">⚡</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-base tracking-tight text-white">UNIVERSAL AI</span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">PRO</span>
              </div>
              <p className="text-xs text-slate-400 font-medium">Social Publisher</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden lg:flex items-center gap-1">
            {navItems.map((item) => {
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
                    isActive
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Action Area: Automation Toggle & Generate Post */}
          <div className="flex items-center gap-3">
            {/* Automation Master Switch */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800">
              <div className="text-right hidden sm:block">
                <p className="text-[11px] font-semibold text-slate-300">Auto Publishing</p>
                <p className={`text-[10px] font-bold ${automationEnabled ? 'text-emerald-400' : 'text-slate-500'}`}>
                  {automationEnabled ? '● 5 Posts Active' : '○ Paused'}
                </p>
              </div>
              <button
                type="button"
                onClick={onToggleAutomation}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                  automationEnabled ? 'bg-emerald-500' : 'bg-slate-700'
                }`}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    automationEnabled ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>

            {/* Quick Generate Button */}
            <button
              onClick={onOpenQuickGenerate}
              className="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white shadow-lg shadow-indigo-500/20 active:scale-95 transition-all flex items-center gap-1.5"
            >
              <span>✨</span>
              <span className="hidden sm:inline">Create Post</span>
            </button>
          </div>

        </div>

        {/* Mobile Navigation bar */}
        <div className="lg:hidden flex items-center overflow-x-auto py-2 border-t border-slate-900 gap-1.5 scrollbar-none">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`px-2.5 py-1 rounded-md text-xs font-medium whitespace-nowrap shrink-0 transition-all ${
                  isActive
                    ? 'bg-indigo-600 text-white'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                {item.icon} {item.label}
              </button>
            );
          })}
        </div>

      </div>
    </header>
  );
}

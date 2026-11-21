import React from 'react';

export default function DashboardOverview({ dashboardData, onRefresh, onNavigateTab, onOpenQuickGenerate }) {
  if (!dashboardData) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs text-slate-400">Loading publisher dashboard...</p>
        </div>
      </div>
    );
  }

  const { stats, services, recent_posts } = dashboardData;

  const statCards = [
    {
      title: 'Total Published',
      value: stats.total_published || 0,
      subtext: 'Documentary posts live',
      icon: '🚀',
      gradient: 'from-blue-600/20 to-indigo-600/10',
      border: 'border-blue-500/20',
      textColor: 'text-blue-400',
    },
    {
      title: "Today's Published",
      value: `${stats.today_published || 0} / 5`,
      subtext: 'Daily target progress',
      icon: '🎯',
      gradient: 'from-emerald-600/20 to-teal-600/10',
      border: 'border-emerald-500/20',
      textColor: 'text-emerald-400',
    },
    {
      title: 'Scheduled Queue',
      value: stats.scheduled_count || 0,
      subtext: 'Ready for auto-posting',
      icon: '⏳',
      gradient: 'from-purple-600/20 to-pink-600/10',
      border: 'border-purple-500/20',
      textColor: 'text-purple-400',
    },
    {
      title: 'Failed Posts',
      value: stats.failed_count || 0,
      subtext: stats.failed_count > 0 ? 'Action required' : 'All systems normal',
      icon: '⚠️',
      gradient: 'from-rose-600/20 to-red-600/10',
      border: 'border-rose-500/20',
      textColor: stats.failed_count > 0 ? 'text-rose-400' : 'text-slate-400',
    },
  ];

  return (
    <div className="space-y-6">
      
      {/* Hero Welcome & Operational Banner */}
      <div className="relative overflow-hidden rounded-2xl glass-panel p-6 sm:p-8 bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-indigo-500/20">
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold mb-3">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Universal AI Social Publisher Engine
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              100% Automated Facebook Publishing
            </h1>
            <p className="text-slate-400 text-xs sm:text-sm mt-1 max-w-2xl leading-relaxed">
              Generates high-impact documentary stories, photorealistic AI imagery, verified research, and publishes to your Facebook Page automatically at 5 fixed daily times.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
            <button
              onClick={onRefresh}
              className="px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700/80 transition-all flex items-center gap-2"
            >
              <span>🔄</span> Refresh Status
            </button>
            <button
              onClick={onOpenQuickGenerate}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white text-xs font-bold shadow-lg shadow-indigo-500/25 transition-all flex items-center gap-2"
            >
              <span>✨</span> Create New Post
            </button>
          </div>
        </div>
      </div>

      {/* 4 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, i) => (
          <div
            key={i}
            className={`rounded-xl p-5 bg-gradient-to-br ${card.gradient} glass-panel border ${card.border} transition-all`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300">{card.title}</span>
              <span className="text-xl p-2 rounded-lg bg-slate-800/60">{card.icon}</span>
            </div>
            <div className="mt-4">
              <div className={`text-2xl sm:text-3xl font-extrabold tracking-tight ${card.textColor}`}>
                {card.value}
              </div>
              <p className="text-[11px] text-slate-400 mt-1 font-medium">{card.subtext}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Integration Status Triad */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        
        {/* Facebook Page Status */}
        <div
          onClick={() => onNavigateTab('facebook')}
          className="rounded-xl p-5 glass-panel glass-panel-hover border cursor-pointer transition-all"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-300 flex items-center gap-2">
              <span>🌐</span> Meta Facebook Page
            </span>
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
              services.facebook.is_connected ? 'badge-connected' : 'badge-failed'
            }`}>
              {services.facebook.is_connected ? 'CONNECTED' : 'DISCONNECTED'}
            </span>
          </div>
          <p className="text-sm font-bold text-white truncate">
            {services.facebook.page_name || 'No Page Connected'}
          </p>
          <p className="text-[11px] font-mono text-slate-400 mt-0.5 truncate">
            ID: {services.facebook.page_id || 'Configure in Facebook tab'}
          </p>
          <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-indigo-400 font-semibold">
            <span>Manage Meta Graph API</span>
            <span>→</span>
          </div>
        </div>

        {/* AI Provider Status */}
        <div
          onClick={() => onNavigateTab('providers')}
          className="rounded-xl p-5 glass-panel glass-panel-hover border cursor-pointer transition-all"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-300 flex items-center gap-2">
              <span>🧠</span> AI Text Engine
            </span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full badge-connected">
              {services.ai.active_count} ACTIVE
            </span>
          </div>
          <p className="text-sm font-bold text-white truncate">
            {services.ai.default_provider || 'Google Gemini'}
          </p>
          <p className="text-[11px] text-slate-400 mt-0.5 truncate">
            Status: <span className="capitalize text-slate-300">{services.ai.status || 'Ready'}</span>
          </p>
          <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-indigo-400 font-semibold">
            <span>Configure AI Providers</span>
            <span>→</span>
          </div>
        </div>

        {/* Image Engine Status */}
        <div
          onClick={() => onNavigateTab('images')}
          className="rounded-xl p-5 glass-panel glass-panel-hover border cursor-pointer transition-all"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-300 flex items-center gap-2">
              <span>🎨</span> Photorealistic Images
            </span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full badge-connected">
              {services.image.active_count} ACTIVE
            </span>
          </div>
          <p className="text-sm font-bold text-white truncate">
            {services.image.default_provider || 'Gemini Imagen 3'}
          </p>
          <p className="text-[11px] text-slate-400 mt-0.5 truncate">
            Style: Photorealistic Documentary 8K
          </p>
          <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-indigo-400 font-semibold">
            <span>Configure Image Models</span>
            <span>→</span>
          </div>
        </div>

      </div>

      {/* Next Schedule & Fixed Times Banner */}
      <div className="rounded-xl glass-panel p-5 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 text-lg">
            ⏰
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-300">Next Automated Slot</p>
            <p className="text-sm font-bold text-white">
              {stats.next_publishing ? (
                <>Slot #{stats.next_publishing.slot_number} at <span className="text-indigo-400 font-mono">{stats.next_publishing.post_time}</span> ({stats.next_publishing.category_preference})</>
              ) : (
                'All 5 slots active (06:00, 10:00, 14:00, 18:00, 21:00)'
              )}
            </p>
          </div>
        </div>
        <button
          onClick={() => onNavigateTab('scheduler')}
          className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-all"
        >
          Adjust Schedule Times
        </button>
      </div>

      {/* Recent Activity Table */}
      <div className="rounded-xl glass-panel border border-slate-800/80 overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-white">Recent Publishing Activity</h3>
            <p className="text-xs text-slate-400">Latest automated & manual Facebook posts</p>
          </div>
          <button
            onClick={() => onNavigateTab('content')}
            className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold"
          >
            View Full Library →
          </button>
        </div>

        <div className="overflow-x-auto">
          {recent_posts && recent_posts.length > 0 ? (
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                <tr>
                  <th className="px-5 py-3">Headline</th>
                  <th className="px-5 py-3">Category</th>
                  <th className="px-5 py-3">AI Engine</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {recent_posts.map((post) => (
                  <tr key={post.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-5 py-3.5 font-medium text-white max-w-xs truncate">
                      {post.headline}
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-slate-700/60 text-[11px]">
                        {post.category}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-slate-400">
                      {post.ai_provider_used || 'Gemini'}
                    </td>
                    <td className="px-5 py-3.5">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        post.status === 'published' ? 'badge-connected' :
                        post.status === 'failed' ? 'badge-failed' : 'badge-pending'
                      }`}>
                        {post.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-slate-400 font-mono text-[11px]">
                      {post.published_at ? new Date(post.published_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Pending'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="py-12 text-center text-slate-500 text-xs">
              No posts generated yet. Tap "Create New Post" or let the 5 daily fixed schedules run automatically.
            </div>
          )}
        </div>
      </div>

    </div>
  );
}

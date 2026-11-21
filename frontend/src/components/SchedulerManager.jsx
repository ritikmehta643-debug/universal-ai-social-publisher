import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function SchedulerManager() {
  const [schedules, setSchedules] = useState([]);
  const [settings, setSettings] = useState({});
  const [templates, setTemplates] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [schedRes, tmplRes, catRes] = await Promise.all([
        api.getSchedules(),
        api.getTemplates(),
        api.getCategories(),
      ]);
      setSchedules(schedRes.slots || []);
      setSettings(schedRes.settings || {});
      setTemplates(tmplRes || []);
      setCategories(['Any', ...(catRes || [])]);
    } catch (err) {
      alert(`Error loading schedules: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSlotChange = (index, field, value) => {
    const updated = [...schedules];
    updated[index][field] = value;
    setSchedules(updated);
  };

  const handleSaveSchedules = async () => {
    try {
      setSaving(true);
      await api.updateSchedules(schedules);
      await api.updateSettings(settings);
      alert('Schedules & settings saved successfully!');
      loadData();
    } catch (err) {
      alert(`Error saving schedules: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 glass-panel rounded-2xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xl">⏰</span>
            <h2 className="text-lg font-bold text-white">Fixed-Time Automated Posting Engine</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Configure up to 5 daily fixed publishing times. The persistent background scheduler generates and publishes documentary posts independently without keeping the app open.
          </p>
        </div>
        <button
          onClick={handleSaveSchedules}
          disabled={saving}
          className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-md shadow-indigo-600/30 transition-all disabled:opacity-50 self-start sm:self-auto"
        >
          {saving ? 'Saving...' : '💾 Save Schedule Changes'}
        </button>
      </div>

      {/* Global Automation Controls */}
      <div className="p-6 glass-panel rounded-2xl border border-slate-800 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">Timezone</label>
          <select
            value={settings.timezone || 'Asia/Kolkata'}
            onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white font-mono"
          >
            <option value="Asia/Kolkata">Asia/Kolkata (IST - UTC+05:30)</option>
            <option value="UTC">UTC (Universal Coordinated Time)</option>
            <option value="America/New_York">America/New_York (EST)</option>
            <option value="Europe/London">Europe/London (GMT)</option>
            <option value="Asia/Dubai">Asia/Dubai (GST)</option>
            <option value="Asia/Singapore">Asia/Singapore (SGT)</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">Daily Post Target</label>
          <input
            type="number"
            min="1"
            max="10"
            value={settings.daily_post_target || 5}
            onChange={(e) => setSettings({ ...settings, daily_post_target: e.target.value })}
            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">Duplicate Topic Guard (Days)</label>
          <input
            type="number"
            min="7"
            max="180"
            value={settings.duplicate_window_days || 30}
            onChange={(e) => setSettings({ ...settings, duplicate_window_days: e.target.value })}
            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
          />
        </div>
      </div>

      {/* 5 Daily Slots */}
      {loading ? (
        <div className="text-center py-16 text-slate-400 text-xs">Loading schedules...</div>
      ) : (
        <div className="space-y-3">
          <h3 className="text-sm font-bold text-slate-200">5 Daily Fixed Posting Slots</h3>
          {schedules.map((slot, index) => (
            <div
              key={slot.id || index}
              className={`p-4 rounded-xl glass-panel border transition-all flex flex-col md:flex-row md:items-center justify-between gap-4 ${
                slot.is_enabled ? 'border-slate-800' : 'border-slate-800/40 opacity-60 bg-slate-950/40'
              }`}
            >
              {/* Slot Number & Toggle */}
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => handleSlotChange(index, 'is_enabled', !slot.is_enabled)}
                  className={`relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out ${
                    slot.is_enabled ? 'bg-indigo-600' : 'bg-slate-700'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition duration-200 ease-in-out ${
                      slot.is_enabled ? 'translate-x-4' : 'translate-x-0'
                    }`}
                  />
                </button>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-extrabold text-white">Slot #{slot.slot_number}</span>
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                      slot.is_enabled ? 'bg-indigo-500/20 text-indigo-300' : 'bg-slate-800 text-slate-500'
                    }`}>
                      {slot.is_enabled ? 'ACTIVE' : 'DISABLED'}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    {slot.slot_number === 1 ? 'Morning Kickoff (06:00 AM default)' :
                     slot.slot_number === 2 ? 'Mid-Morning Feature (10:00 AM default)' :
                     slot.slot_number === 3 ? 'Afternoon Deep Dive (02:00 PM default)' :
                     slot.slot_number === 4 ? 'Evening Prime (06:00 PM default)' :
                     'Night Documentary (09:00 PM default)'}
                  </p>
                </div>
              </div>

              {/* Time & Category & Template Selectors */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 flex-1 md:max-w-2xl">
                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 mb-1">Time (24h)</label>
                  <input
                    type="time"
                    value={slot.post_time}
                    onChange={(e) => handleSlotChange(index, 'post_time', e.target.value)}
                    className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white font-mono"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 mb-1">Category Preference</label>
                  <select
                    value={slot.category_preference || 'Any'}
                    onChange={(e) => handleSlotChange(index, 'category_preference', e.target.value)}
                    className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white"
                  >
                    {categories.map((cat) => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 mb-1">Caption Template</label>
                  <select
                    value={slot.caption_template_id || ''}
                    onChange={(e) => handleSlotChange(index, 'caption_template_id', e.target.value ? parseInt(e.target.value) : null)}
                    className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white"
                  >
                    <option value="">Default Template</option>
                    {templates.map((t) => (
                      <option key={t.id} value={t.id}>{t.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Last Run Info */}
              <div className="text-right text-[11px] text-slate-400 hidden lg:block min-w-[120px]">
                <span className="block text-slate-500">Last Run:</span>
                <span className="font-mono text-slate-300">
                  {slot.last_run_at ? new Date(slot.last_run_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Never'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}

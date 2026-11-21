import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function ImageProvidersManager() {
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingProvider, setEditingProvider] = useState(null);
  const [testingId, setTestingId] = useState(null);
  const [testResult, setTestResult] = useState({});

  const loadProviders = async () => {
    try {
      setLoading(true);
      const data = await api.getImageProviders();
      setProviders(data);
    } catch (err) {
      alert(`Error loading image providers: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProviders();
  }, []);

  const handleTest = async (id) => {
    try {
      setTestingId(id);
      setTestResult((prev) => ({ ...prev, [id]: { testing: true } }));
      const res = await api.testImageProvider(id);
      setTestResult((prev) => ({ ...prev, [id]: { success: res.success, message: res.message } }));
      loadProviders();
    } catch (err) {
      setTestResult((prev) => ({ ...prev, [id]: { success: false, message: err.message } }));
    } finally {
      setTestingId(null);
    }
  };

  const handleSetDefault = async (id) => {
    try {
      await api.setDefaultImageProvider(id);
      loadProviders();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const handleSaveEdit = async () => {
    if (!editingProvider) return;
    try {
      await api.updateImageProvider(editingProvider.id, editingProvider);
      setEditingProvider(null);
      loadProviders();
    } catch (err) {
      alert(`Error updating image provider: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      
      <div className="p-6 glass-panel rounded-2xl border border-slate-800">
        <div className="flex items-center gap-2">
          <span className="text-xl">🎨</span>
          <h2 className="text-lg font-bold text-white">Universal Image Generation Engine</h2>
        </div>
        <p className="text-xs text-slate-400 mt-1 max-w-2xl">
          Automate photorealistic documentary-grade visuals. Configure Gemini Imagen 3, DALL-E 3, Hugging Face FLUX.1, or custom endpoints with aspect ratios, negative prompts, and archival photography aesthetics.
        </p>
      </div>

      {loading ? (
        <div className="text-center py-16 text-slate-400 text-xs">Loading image providers...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {providers.map((p) => {
            const res = testResult[p.id];
            return (
              <div
                key={p.id}
                className={`rounded-xl glass-panel p-5 border transition-all ${
                  p.is_default ? 'border-purple-500/50 bg-purple-950/10' : 'border-slate-800'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-bold text-white">{p.name}</h3>
                      {p.is_default && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-purple-500 text-white">
                          DEFAULT
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 font-mono mt-0.5">{p.model}</p>
                  </div>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                    p.is_enabled ? 'badge-connected' : 'badge-untested'
                  }`}>
                    {p.is_enabled ? 'ACTIVE' : 'INACTIVE'}
                  </span>
                </div>

                <div className="mt-4 p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs space-y-1.5">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-slate-400">Aspect Ratio:</span>
                    <span className="font-semibold text-slate-200">{p.aspect_ratio} ({p.resolution})</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-slate-400">Style:</span>
                    <span className="text-slate-300 capitalize">{p.style}</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-slate-400">API Key:</span>
                    <span className="font-mono text-slate-200">
                      {p.has_key ? p.masked_key : <span className="text-amber-400 font-sans">Using shared AI key</span>}
                    </span>
                  </div>
                </div>

                {res && (
                  <div className={`mt-3 p-2.5 rounded-lg text-xs ${
                    res.testing ? 'bg-purple-950/40 text-purple-300' : res.success ? 'bg-emerald-950/40 text-emerald-300' : 'bg-rose-950/40 text-rose-300'
                  }`}>
                    {res.testing ? 'Validating...' : res.message}
                  </div>
                )}

                <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center gap-2">
                  <button
                    onClick={() => handleTest(p.id)}
                    disabled={testingId === p.id}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all"
                  >
                    ⚡ Test
                  </button>
                  <button
                    onClick={() => setEditingProvider({ ...p, api_key: '' })}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all"
                  >
                    ⚙️ Configure
                  </button>
                  {!p.is_default && (
                    <button
                      onClick={() => handleSetDefault(p.id)}
                      className="px-2.5 py-1.5 rounded-lg text-purple-400 hover:bg-purple-500/10 text-xs font-semibold transition-all"
                    >
                      Set Default
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Edit Image Modal */}
      {editingProvider && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="w-full max-w-lg glass-panel rounded-2xl p-6 border border-slate-700 space-y-4">
            <h3 className="text-base font-bold text-white">Configure {editingProvider.name}</h3>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Aspect Ratio</label>
                <select
                  value={editingProvider.aspect_ratio}
                  onChange={(e) => setEditingProvider({ ...editingProvider, aspect_ratio: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
                >
                  <option value="1:1">1:1 Square (Instagram/FB)</option>
                  <option value="4:5">4:5 Vertical Portrait</option>
                  <option value="16:9">16:9 Cinematic Landscape</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Resolution</label>
                <select
                  value={editingProvider.resolution}
                  onChange={(e) => setEditingProvider({ ...editingProvider, resolution: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
                >
                  <option value="1024x1024">1024x1024 (HD Standard)</option>
                  <option value="1024x1280">1024x1280 (High Vertical)</option>
                  <option value="1792x1024">1792x1024 (Ultra Landscape)</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Photographic Style</label>
              <select
                value={editingProvider.style}
                onChange={(e) => setEditingProvider({ ...editingProvider, style: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
              >
                <option value="photorealistic documentary">Photorealistic Documentary 8K</option>
                <option value="cinematic historical">Cinematic Historical Archival</option>
                <option value="national geographic style">National Geographic Realism</option>
                <option value="dramatic atmospheric photograph">Dramatic Atmospheric Lighting</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Negative Prompt (Avoid)</label>
              <input
                type="text"
                value={editingProvider.negative_prompt}
                onChange={(e) => setEditingProvider({ ...editingProvider, negative_prompt: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">API Key</label>
              <input
                type="password"
                placeholder={editingProvider.has_key ? '••••••••••••••••' : 'Enter dedicated API key (or uses AI key)'}
                value={editingProvider.api_key}
                onChange={(e) => setEditingProvider({ ...editingProvider, api_key: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white font-mono"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
              <button
                onClick={() => setEditingProvider(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-xs text-slate-300 hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveEdit}
                className="px-4 py-2 rounded-xl bg-purple-600 text-xs text-white font-bold hover:bg-purple-500"
              >
                Save Configuration
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

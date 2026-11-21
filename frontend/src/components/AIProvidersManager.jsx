import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function AIProvidersManager() {
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [testingId, setTestingId] = useState(null);
  const [testResult, setTestResult] = useState({});
  const [editingProvider, setEditingProvider] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newProvider, setNewProvider] = useState({
    name: '',
    provider_type: 'custom',
    api_endpoint: 'http://localhost:11434/v1',
    api_key: '',
    model: 'llama3',
    image_model: '',
  });

  const loadProviders = async () => {
    try {
      setLoading(true);
      const data = await api.getAIProviders();
      setProviders(data);
    } catch (err) {
      alert(`Failed to load AI providers: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProviders();
  }, []);

  const handleTestConnection = async (id) => {
    try {
      setTestingId(id);
      setTestResult((prev) => ({ ...prev, [id]: { testing: true } }));
      const res = await api.testAIProvider(id);
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
      await api.setDefaultAIProvider(id);
      loadProviders();
    } catch (err) {
      alert(`Error setting default: ${err.message}`);
    }
  };

  const handleSetFallback = async (id) => {
    try {
      await api.setFallbackAIProvider(id);
      loadProviders();
    } catch (err) {
      alert(`Error setting fallback: ${err.message}`);
    }
  };

  const handleToggleEnable = async (provider) => {
    try {
      await api.updateAIProvider(provider.id, { is_enabled: !provider.is_enabled });
      loadProviders();
    } catch (err) {
      alert(`Error toggling provider: ${err.message}`);
    }
  };

  const handleSaveEdit = async () => {
    if (!editingProvider) return;
    try {
      await api.updateAIProvider(editingProvider.id, editingProvider);
      setEditingProvider(null);
      loadProviders();
    } catch (err) {
      alert(`Error updating provider: ${err.message}`);
    }
  };

  const handleCreateCustom = async () => {
    if (!newProvider.name || !newProvider.model) {
      alert('Name and model are required.');
      return;
    }
    try {
      await api.createAIProvider(newProvider);
      setShowAddModal(false);
      setNewProvider({
        name: '',
        provider_type: 'custom',
        api_endpoint: 'http://localhost:11434/v1',
        api_key: '',
        model: 'llama3',
        image_model: '',
      });
      loadProviders();
    } catch (err) {
      alert(`Error adding provider: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 glass-panel rounded-2xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xl">🧠</span>
            <h2 className="text-lg font-bold text-white">Universal AI Provider Management</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Integrate Google Gemini, OpenAI, Anthropic Claude, Groq, OpenRouter, Hugging Face, or any OpenAI-compatible endpoint. Setup primary and automatic fallback engines.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-md shadow-indigo-600/30 transition-all flex items-center gap-1.5 self-start sm:self-auto"
        >
          <span>➕</span> Add Custom Provider
        </button>
      </div>

      {/* Providers Grid */}
      {loading ? (
        <div className="text-center py-16 text-slate-400 text-xs">Loading AI providers...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {providers.map((p) => {
            const result = testResult[p.id];
            return (
              <div
                key={p.id}
                className={`rounded-xl glass-panel p-5 border transition-all ${
                  p.is_default
                    ? 'border-indigo-500/50 bg-indigo-950/10'
                    : p.is_fallback
                    ? 'border-amber-500/40 bg-amber-950/10'
                    : 'border-slate-800'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-bold text-white">{p.name}</h3>
                      {p.is_default && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-indigo-500 text-white">
                          DEFAULT
                        </span>
                      )}
                      {p.is_fallback && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-500 text-black">
                          FALLBACK
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 font-mono mt-0.5">{p.model}</p>
                  </div>

                  {/* Enable Switch */}
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] text-slate-400 font-medium">
                      {p.is_enabled ? 'Active' : 'Disabled'}
                    </span>
                    <button
                      onClick={() => handleToggleEnable(p)}
                      className={`relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out ${
                        p.is_enabled ? 'bg-indigo-600' : 'bg-slate-700'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition duration-200 ease-in-out ${
                          p.is_enabled ? 'translate-x-4' : 'translate-x-0'
                        }`}
                      />
                    </button>
                  </div>
                </div>

                {/* API Key Status & Endpoint */}
                <div className="mt-4 p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs space-y-1.5">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-slate-400">API Key:</span>
                    <span className="font-mono text-slate-200">
                      {p.has_key ? p.masked_key : <span className="text-rose-400 font-sans">Key not set</span>}
                    </span>
                  </div>
                  {p.api_endpoint && (
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="text-slate-400">Endpoint:</span>
                      <span className="font-mono text-slate-300 truncate max-w-[200px]">{p.api_endpoint}</span>
                    </div>
                  )}
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-slate-400">Health:</span>
                    <span className={`capitalize font-semibold ${
                      p.status === 'connected' ? 'text-emerald-400' :
                      p.status === 'failed' ? 'text-rose-400' : 'text-slate-400'
                    }`}>
                      {p.status}
                    </span>
                  </div>
                </div>

                {/* Test Feedback */}
                {result && (
                  <div className={`mt-3 p-2.5 rounded-lg text-xs ${
                    result.testing
                      ? 'bg-indigo-950/40 text-indigo-300 border border-indigo-800/40'
                      : result.success
                      ? 'bg-emerald-950/40 text-emerald-300 border border-emerald-800/40'
                      : 'bg-rose-950/40 text-rose-300 border border-rose-800/40'
                  }`}>
                    {result.testing ? 'Testing connection...' : result.message}
                  </div>
                )}

                {/* Card Action Buttons */}
                <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-wrap items-center gap-2">
                  <button
                    onClick={() => handleTestConnection(p.id)}
                    disabled={testingId === p.id}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all disabled:opacity-50"
                  >
                    {testingId === p.id ? 'Testing...' : '⚡ Test Connection'}
                  </button>

                  <button
                    onClick={() => setEditingProvider({ ...p, api_key: '' })}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all"
                  >
                    ⚙️ Edit / Key
                  </button>

                  {!p.is_default && (
                    <button
                      onClick={() => handleSetDefault(p.id)}
                      className="px-2.5 py-1.5 rounded-lg text-indigo-400 hover:bg-indigo-500/10 text-xs font-semibold transition-all"
                    >
                      Set Default
                    </button>
                  )}

                  {!p.is_fallback && !p.is_default && (
                    <button
                      onClick={() => handleSetFallback(p.id)}
                      className="px-2.5 py-1.5 rounded-lg text-amber-400 hover:bg-amber-500/10 text-xs font-semibold transition-all"
                    >
                      Set Fallback
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Edit Provider Modal */}
      {editingProvider && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="w-full max-w-lg glass-panel rounded-2xl p-6 border border-slate-700 space-y-4">
            <h3 className="text-base font-bold text-white">Configure {editingProvider.name}</h3>
            
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Provider Name</label>
              <input
                type="text"
                value={editingProvider.name}
                onChange={(e) => setEditingProvider({ ...editingProvider, name: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                API Key {editingProvider.has_key && <span className="text-slate-500 font-normal">(Leave blank to keep existing)</span>}
              </label>
              <input
                type="password"
                placeholder={editingProvider.has_key ? '••••••••••••••••••••' : 'Enter API Key'}
                value={editingProvider.api_key}
                onChange={(e) => setEditingProvider({ ...editingProvider, api_key: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Model Name</label>
              <input
                type="text"
                value={editingProvider.model}
                onChange={(e) => setEditingProvider({ ...editingProvider, model: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">API Endpoint URL</label>
              <input
                type="text"
                value={editingProvider.api_endpoint}
                onChange={(e) => setEditingProvider({ ...editingProvider, api_endpoint: e.target.value })}
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
                className="px-4 py-2 rounded-xl bg-indigo-600 text-xs text-white font-bold hover:bg-indigo-500"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Custom Provider Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="w-full max-w-lg glass-panel rounded-2xl p-6 border border-slate-700 space-y-4">
            <h3 className="text-base font-bold text-white">Add Custom AI Provider</h3>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Provider Name</label>
              <input
                type="text"
                placeholder="e.g. Local Ollama, Together AI, DeepSeek"
                value={newProvider.name}
                onChange={(e) => setNewProvider({ ...newProvider, name: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">API Endpoint (OpenAI Compatible)</label>
              <input
                type="text"
                placeholder="http://localhost:11434/v1"
                value={newProvider.api_endpoint}
                onChange={(e) => setNewProvider({ ...newProvider, api_endpoint: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Model Name</label>
              <input
                type="text"
                placeholder="e.g. llama3.3, deepseek-chat"
                value={newProvider.model}
                onChange={(e) => setNewProvider({ ...newProvider, model: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">API Key (Optional for local models)</label>
              <input
                type="password"
                placeholder="sk-..."
                value={newProvider.api_key}
                onChange={(e) => setNewProvider({ ...newProvider, api_key: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white font-mono"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-xs text-slate-300 hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateCustom}
                className="px-4 py-2 rounded-xl bg-indigo-600 text-xs text-white font-bold hover:bg-indigo-500"
              >
                Create Provider
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

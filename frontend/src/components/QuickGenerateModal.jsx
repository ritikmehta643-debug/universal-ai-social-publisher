import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function QuickGenerateModal({ isOpen, onClose, onSuccess }) {
  const [categories, setCategories] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [category, setCategory] = useState('');
  const [customTopic, setCustomTopic] = useState('');
  const [language, setLanguage] = useState('en');
  const [templateId, setTemplateId] = useState('');
  const [publishNow, setPublishNow] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (isOpen) {
      api.getCategories().then((c) => {
        setCategories(c || []);
        if (c && c.length > 0) setCategory(c[0]);
      }).catch(() => {});

      api.getTemplates().then((t) => {
        setTemplates(t || []);
        const def = t?.find((item) => item.is_default);
        if (def) setTemplateId(def.id);
      }).catch(() => {});
      
      setResult(null);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleGenerate = async (e) => {
    e.preventDefault();
    try {
      setGenerating(true);
      setResult(null);
      const res = await api.generatePost({
        category,
        topic: customTopic || undefined,
        language,
        template_id: templateId ? parseInt(templateId) : undefined,
        publish_now: publishNow,
      });
      setResult(res);
      if (onSuccess) onSuccess();
    } catch (err) {
      alert(`Generation failed: ${err.message}`);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm overflow-y-auto">
      <div className="w-full max-w-2xl glass-panel rounded-2xl p-6 border border-slate-700 space-y-4 my-8">
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">✨</span>
            <h3 className="text-base font-bold text-white">Create On-Demand Post</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-lg">✕</button>
        </div>

        {!result ? (
          <form onSubmit={handleGenerate} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
                >
                  {categories.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Language</label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
                >
                  <option value="en">English (Global)</option>
                  <option value="hi">Hindi (हिंदी देवनागरी)</option>
                  <option value="hinglish">Hinglish</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Custom Topic (Optional)
              </label>
              <input
                type="text"
                placeholder="Leave blank to auto-discover an untold topic from library"
                value={customTopic}
                onChange={(e) => setCustomTopic(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Caption Template</label>
              <select
                value={templateId}
                onChange={(e) => setTemplateId(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
              >
                {templates.map((t) => (
                  <option key={t.id} value={t.id}>{t.name} ({t.caption_length})</option>
                ))}
              </select>
            </div>

            {/* Instant Publish Checkbox */}
            <div className="flex items-center gap-2.5 p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <input
                type="checkbox"
                id="publishNowCheck"
                checked={publishNow}
                onChange={(e) => setPublishNow(e.target.checked)}
                className="rounded border-slate-700 text-indigo-600 focus:ring-0"
              />
              <label htmlFor="publishNowCheck" className="text-xs text-slate-200 cursor-pointer">
                Publish immediately to Facebook Page upon generation
              </label>
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 rounded-xl bg-slate-800 text-xs text-slate-300 hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={generating}
                className="px-5 py-2 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white text-xs font-bold shadow-lg shadow-indigo-500/25 transition-all disabled:opacity-50 flex items-center gap-2"
              >
                {generating ? (
                  <>
                    <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                    <span>AI Researching & Crafting...</span>
                  </>
                ) : (
                  <span>🚀 Generate Content</span>
                )}
              </button>
            </div>
          </form>
        ) : (
          /* Result View */
          <div className="space-y-4">
            <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-800/40 text-emerald-300 text-xs flex items-center justify-between">
              <span>✅ Post generated successfully! Status: <strong className="uppercase">{result.status}</strong></span>
              {result.fb_post_id && <span>Post ID: {result.fb_post_id}</span>}
            </div>

            <h4 className="text-sm font-bold text-white">{result.data.headline}</h4>

            {result.data.image_url && (
              <div className="rounded-xl overflow-hidden max-h-60 bg-slate-900">
                <img
                  src={result.data.image_url.startsWith('http') ? result.data.image_url : `/media/${result.data.image_url.split('/').pop()}`}
                  alt=""
                  className="w-full h-full object-cover"
                />
              </div>
            )}

            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-200 whitespace-pre-line leading-relaxed max-h-60 overflow-y-auto">
              {result.data.caption}
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
              <button
                onClick={onClose}
                className="px-4 py-2 rounded-xl bg-indigo-600 text-xs text-white font-bold hover:bg-indigo-500"
              >
                Done
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

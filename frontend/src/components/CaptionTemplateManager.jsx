import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function CaptionTemplateManager() {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [newTemplate, setNewTemplate] = useState({
    name: '',
    hook_style: 'shocking_fact',
    caption_length: 'documentary',
    storytelling_format: 'deep_dive',
    language: 'en',
    emoji_usage: 'moderate',
    hashtag_quantity: 10,
    cta_style: 'follow_page',
    brand_voice: 'dramatic',
    ending_line: '👉 Follow our page for unforgettable stories and untold history.',
  });

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const data = await api.getTemplates();
      setTemplates(data);
    } catch (err) {
      alert(`Error loading templates: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTemplates();
  }, []);

  const handleSetDefault = async (id) => {
    try {
      await api.setDefaultTemplate(id);
      loadTemplates();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleSaveEdit = async () => {
    if (!editingTemplate) return;
    try {
      await api.updateTemplate(editingTemplate.id, editingTemplate);
      setEditingTemplate(null);
      loadTemplates();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleCreate = async () => {
    if (!newTemplate.name) {
      alert('Template name is required.');
      return;
    }
    try {
      await api.createTemplate(newTemplate);
      setShowCreate(false);
      setNewTemplate({
        name: '',
        hook_style: 'shocking_fact',
        caption_length: 'documentary',
        storytelling_format: 'deep_dive',
        language: 'en',
        emoji_usage: 'moderate',
        hashtag_quantity: 10,
        cta_style: 'follow_page',
        brand_voice: 'dramatic',
        ending_line: '👉 Follow our page for unforgettable stories and untold history.',
      });
      loadTemplates();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this template?')) return;
    try {
      await api.deleteTemplate(id);
      loadTemplates();
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div className="space-y-6">
      
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 glass-panel rounded-2xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xl">✍️</span>
            <h2 className="text-lg font-bold text-white">Caption Template & Storytelling Engine</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Control the narrative hook, caption depth, Hindi or English language style, emoji density, brand voice, and Call-to-Action for every published post.
          </p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-md shadow-indigo-600/30 flex items-center gap-1.5 self-start sm:self-auto"
        >
          <span>➕</span> New Template
        </button>
      </div>

      {loading ? (
        <div className="text-center py-16 text-slate-400 text-xs">Loading caption templates...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {templates.map((t) => (
            <div
              key={t.id}
              className={`rounded-xl glass-panel p-5 border transition-all ${
                t.is_default ? 'border-indigo-500/50 bg-indigo-950/10' : 'border-slate-800'
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-bold text-white">{t.name}</h3>
                    {t.is_default && (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-indigo-500 text-white">
                        DEFAULT
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 capitalize mt-0.5">
                    {t.language === 'en' ? 'English' : t.language === 'hi' ? 'Hindi (हिंदी)' : 'Hinglish'} · {t.caption_length} · {t.storytelling_format}
                  </p>
                </div>
              </div>

              {/* Badges / Specs */}
              <div className="mt-4 grid grid-cols-2 gap-2 text-[11px] text-slate-300">
                <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Hook Style</span>
                  <span className="font-semibold capitalize">{t.hook_style?.replace('_', ' ')}</span>
                </div>
                <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Brand Voice</span>
                  <span className="font-semibold capitalize">{t.brand_voice}</span>
                </div>
                <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Hashtags Count</span>
                  <span className="font-semibold">{t.hashtag_quantity} targeted tags</span>
                </div>
                <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">CTA Style</span>
                  <span className="font-semibold capitalize">{t.cta_style?.replace('_', ' ')}</span>
                </div>
              </div>

              {t.ending_line && (
                <div className="mt-3 p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80 text-[11px] text-slate-300 italic">
                  "{t.ending_line}"
                </div>
              )}

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center gap-2">
                <button
                  onClick={() => setEditingTemplate(t)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all"
                >
                  ✏️ Edit
                </button>
                {!t.is_default && (
                  <button
                    onClick={() => handleSetDefault(t.id)}
                    className="px-2.5 py-1.5 rounded-lg text-indigo-400 hover:bg-indigo-500/10 text-xs font-semibold transition-all"
                  >
                    Set as Default
                  </button>
                )}
                {!t.is_default && (
                  <button
                    onClick={() => handleDelete(t.id)}
                    className="px-2.5 py-1.5 rounded-lg text-rose-400 hover:bg-rose-500/10 text-xs font-semibold ml-auto transition-all"
                  >
                    Delete
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Edit / Create Modal */}
      {(editingTemplate || showCreate) && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm overflow-y-auto">
          <div className="w-full max-w-xl glass-panel rounded-2xl p-6 border border-slate-700 space-y-4 my-8">
            <h3 className="text-base font-bold text-white">
              {editingTemplate ? `Edit Template: ${editingTemplate.name}` : 'Create New Caption Template'}
            </h3>

            {/* Form Fields */}
            {(() => {
              const item = editingTemplate || newTemplate;
              const setItem = editingTemplate ? setEditingTemplate : setNewTemplate;

              return (
                <div className="space-y-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Template Name</label>
                    <input
                      type="text"
                      value={item.name}
                      onChange={(e) => setItem({ ...item, name: e.target.value })}
                      placeholder="e.g. Historical Mystery (Hindi)"
                      className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">Language</label>
                      <select
                        value={item.language}
                        onChange={(e) => setItem({ ...item, language: e.target.value })}
                        className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
                      >
                        <option value="en">English</option>
                        <option value="hi">Hindi (हिंदी देवनागरी)</option>
                        <option value="hinglish">Hinglish</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">Hook Style</label>
                      <select
                        value={item.hook_style}
                        onChange={(e) => setItem({ ...item, hook_style: e.target.value })}
                        className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
                      >
                        <option value="shocking_fact">Shocking Historical Fact</option>
                        <option value="intriguing_question">Intriguing Question</option>
                        <option value="dramatic_statement">Dramatic Narrative Statement</option>
                        <option value="historical_flashback">Historical Flashback</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">Story Format</label>
                      <select
                        value={item.storytelling_format}
                        onChange={(e) => setItem({ ...item, storytelling_format: e.target.value })}
                        className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
                      >
                        <option value="deep_dive">Documentary Deep Dive</option>
                        <option value="chronological">Chronological Timeline</option>
                        <option value="mystery_reveal">Mystery & Revelation</option>
                        <option value="emotional_biography">Emotional Biography</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">Caption Length</label>
                      <select
                        value={item.caption_length}
                        onChange={(e) => setItem({ ...item, caption_length: e.target.value })}
                        className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
                      >
                        <option value="documentary">Full Documentary (3-5 rich paragraphs)</option>
                        <option value="long">Long Story (2-3 paragraphs)</option>
                        <option value="medium">Medium Feature (1-2 paragraphs)</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">Emoji Style</label>
                      <select
                        value={item.emoji_usage}
                        onChange={(e) => setItem({ ...item, emoji_usage: e.target.value })}
                        className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
                      >
                        <option value="minimal">Minimal</option>
                        <option value="moderate">Moderate</option>
                        <option value="expressive">Expressive</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">Hashtags Count</label>
                      <input
                        type="number"
                        min="3"
                        max="25"
                        value={item.hashtag_quantity}
                        onChange={(e) => setItem({ ...item, hashtag_quantity: e.target.value })}
                        className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">Brand Voice</label>
                      <select
                        value={item.brand_voice}
                        onChange={(e) => setItem({ ...item, brand_voice: e.target.value })}
                        className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
                      >
                        <option value="dramatic">Dramatic</option>
                        <option value="authoritative">Authoritative</option>
                        <option value="inspiring">Inspiring</option>
                        <option value="educational">Educational</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Ending Line / Call To Action</label>
                    <textarea
                      rows={2}
                      value={item.ending_line}
                      onChange={(e) => setItem({ ...item, ending_line: e.target.value })}
                      placeholder="e.g. 👉 Follow our page for unforgettable stories and untold history."
                      className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
                    />
                  </div>

                  <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                    <button
                      onClick={() => {
                        setEditingTemplate(null);
                        setShowCreate(false);
                      }}
                      className="px-4 py-2 rounded-xl bg-slate-800 text-xs text-slate-300 hover:bg-slate-700"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={editingTemplate ? handleSaveEdit : handleCreate}
                      className="px-4 py-2 rounded-xl bg-indigo-600 text-xs text-white font-bold hover:bg-indigo-500"
                    >
                      {editingTemplate ? 'Save Template' : 'Create Template'}
                    </button>
                  </div>
                </div>
              );
            })()}
          </div>
        </div>
      )}

    </div>
  );
}

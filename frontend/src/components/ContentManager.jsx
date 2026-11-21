import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function ContentManager({ onOpenQuickGenerate }) {
  const [subTab, setSubTab] = useState('posts'); // 'posts' or 'topics'
  const [posts, setPosts] = useState([]);
  const [topics, setTopics] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [postStatusFilter, setPostStatusFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [viewingPost, setViewingPost] = useState(null);
  const [editingPost, setEditingPost] = useState(null);
  const [publishingId, setPublishingId] = useState(null);

  // New Topic Form
  const [newTopic, setNewTopic] = useState({ category: 'History', title: '', prompt_seed: '' });
  const [showAddTopic, setShowAddTopic] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [cats, pList, tList] = await Promise.all([
        api.getCategories(),
        api.getPosts(postStatusFilter),
        api.getTopics(selectedCategory),
      ]);
      setCategories(cats || []);
      setPosts(pList || []);
      setTopics(tList || []);
    } catch (err) {
      alert(`Error loading content: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [postStatusFilter, selectedCategory]);

  const handlePublishNow = async (id) => {
    try {
      setPublishingId(id);
      const res = await api.publishPost(id);
      alert(`Published! Facebook Post ID: ${res.fb_post_id}`);
      loadData();
    } catch (err) {
      alert(`Failed: ${err.message}`);
    } finally {
      setPublishingId(null);
    }
  };

  const handleDeletePost = async (id) => {
    if (!confirm('Delete this post?')) return;
    try {
      await api.deletePost(id);
      loadData();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleSavePostEdit = async () => {
    if (!editingPost) return;
    try {
      await api.updatePost(editingPost.id, editingPost);
      setEditingPost(null);
      loadData();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleAddTopic = async () => {
    if (!newTopic.title) {
      alert('Topic title is required.');
      return;
    }
    try {
      await api.createTopic(newTopic);
      setShowAddTopic(false);
      setNewTopic({ category: 'History', title: '', prompt_seed: '' });
      loadData();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDeleteTopic = async (id) => {
    if (!confirm('Delete this topic?')) return;
    try {
      await api.deleteTopic(id);
      loadData();
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Navigation Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 glass-panel rounded-2xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xl">📚</span>
            <h2 className="text-lg font-bold text-white">Content & Library Management</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Review queued, published and failed posts. Manage the topics repository and verify documentary accuracy before publishing.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="p-1 rounded-xl bg-slate-900 border border-slate-800 flex items-center">
            <button
              onClick={() => setSubTab('posts')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                subTab === 'posts' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Posts Queue ({posts.length})
            </button>
            <button
              onClick={() => setSubTab('topics')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                subTab === 'topics' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Topics Library ({topics.length})
            </button>
          </div>

          {subTab === 'topics' ? (
            <button
              onClick={() => setShowAddTopic(true)}
              className="px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-md shadow-indigo-600/30 flex items-center gap-1"
            >
              <span>➕</span> Add Topic
            </button>
          ) : (
            <button
              onClick={onOpenQuickGenerate}
              className="px-3.5 py-2 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white text-xs font-bold shadow-md shadow-indigo-500/20 flex items-center gap-1"
            >
              <span>✨</span> Create Post
            </button>
          )}
        </div>
      </div>

      {/* Subtab: POSTS */}
      {subTab === 'posts' && (
        <div className="space-y-4">
          
          {/* Filter Pills */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2">
            {['all', 'ready', 'pending', 'published', 'failed'].map((st) => (
              <button
                key={st}
                onClick={() => setPostStatusFilter(st)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all whitespace-nowrap ${
                  postStatusFilter === st
                    ? 'bg-slate-700 text-white border border-slate-600'
                    : 'bg-slate-900 text-slate-400 border border-slate-800 hover:bg-slate-800'
                }`}
              >
                {st}
              </button>
            ))}
          </div>

          {loading ? (
            <div className="text-center py-16 text-slate-400 text-xs">Loading posts...</div>
          ) : posts.length === 0 ? (
            <div className="p-12 text-center glass-panel rounded-2xl border border-slate-800 text-slate-400 text-xs">
              No posts found with status "{postStatusFilter}".
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {posts.map((post) => (
                <div
                  key={post.id}
                  className="rounded-xl glass-panel p-5 border border-slate-800 flex flex-col justify-between gap-4"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <span className="px-2 py-0.5 rounded-md bg-slate-800 text-indigo-300 text-[11px] font-bold border border-slate-700/80">
                        {post.category}
                      </span>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        post.status === 'published' ? 'badge-connected' :
                        post.status === 'failed' ? 'badge-failed' : 'badge-pending'
                      }`}>
                        {post.status.toUpperCase()}
                      </span>
                    </div>

                    <h3 className="text-sm font-bold text-white line-clamp-2 leading-snug">
                      {post.headline}
                    </h3>

                    {/* Image Preview if available */}
                    {post.image_url && (
                      <div className="relative rounded-lg overflow-hidden h-36 bg-slate-900 border border-slate-800">
                        <img
                          src={post.image_url.startsWith('http') ? post.image_url : `/media/${post.image_url.split('/').pop()}`}
                          alt={post.headline}
                          className="w-full h-full object-cover"
                          onError={(e) => { e.target.style.display = 'none'; }}
                        />
                      </div>
                    )}

                    <p className="text-xs text-slate-300 line-clamp-3 leading-relaxed whitespace-pre-line font-normal">
                      {post.caption}
                    </p>

                    {post.hashtags && (
                      <p className="text-[11px] text-indigo-400 font-medium truncate">
                        {post.hashtags}
                      </p>
                    )}

                    {post.error_message && (
                      <div className="p-2.5 rounded-lg bg-rose-950/40 border border-rose-800/40 text-rose-300 text-xs">
                        ⚠️ Error: {post.error_message}
                      </div>
                    )}

                    {post.fb_post_id && (
                      <p className="text-[10px] font-mono text-slate-500">
                        Facebook Post ID: {post.fb_post_id}
                      </p>
                    )}
                  </div>

                  {/* Action Bar */}
                  <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
                    <button
                      onClick={() => setViewingPost(post)}
                      className="text-indigo-400 hover:text-indigo-300 font-semibold"
                    >
                      View Full →
                    </button>

                    <div className="flex items-center gap-2">
                      {post.status !== 'published' && (
                        <>
                          <button
                            onClick={() => setEditingPost(post)}
                            className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handlePublishNow(post.id)}
                            disabled={publishingId === post.id}
                            className="px-3 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-bold"
                          >
                            {publishingId === post.id ? 'Publishing...' : 'Publish Now'}
                          </button>
                        </>
                      )}

                      <button
                        onClick={() => handleDeletePost(post.id)}
                        className="px-2 py-1 rounded text-rose-400 hover:bg-rose-500/10"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Subtab: TOPICS */}
      {subTab === 'topics' && (
        <div className="space-y-4">
          
          {/* Category Filter */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2">
            <button
              onClick={() => setSelectedCategory('All')}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                selectedCategory === 'All' ? 'bg-indigo-600 text-white' : 'bg-slate-900 text-slate-400 border border-slate-800'
              }`}
            >
              All Categories
            </button>
            {categories.map((c) => (
              <button
                key={c}
                onClick={() => setSelectedCategory(c)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                  selectedCategory === c ? 'bg-indigo-600 text-white' : 'bg-slate-900 text-slate-400 border border-slate-800'
                }`}
              >
                {c}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {topics.map((top) => (
              <div
                key={top.id}
                className="p-4 rounded-xl glass-panel border border-slate-800 flex flex-col justify-between gap-3"
              >
                <div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                    {top.category}
                  </span>
                  <h4 className="text-xs font-bold text-white mt-2 leading-snug">
                    {top.title}
                  </h4>
                  {top.prompt_seed && (
                    <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                      {top.prompt_seed}
                    </p>
                  )}
                </div>

                <div className="flex items-center justify-between text-[10px] text-slate-500 pt-2 border-t border-slate-800/80">
                  <span>Used: {top.times_used} times</span>
                  <button
                    onClick={() => handleDeleteTopic(top.id)}
                    className="text-rose-400 hover:text-rose-300 font-semibold"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Add Topic Modal */}
      {showAddTopic && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="w-full max-w-lg glass-panel rounded-2xl p-6 border border-slate-700 space-y-4">
            <h3 className="text-base font-bold text-white">Add Topic to Library</h3>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Category</label>
              <select
                value={newTopic.category}
                onChange={(e) => setNewTopic({ ...newTopic, category: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
              >
                {categories.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Topic Title</label>
              <input
                type="text"
                placeholder="e.g. The Mystery of Roanoke Colony"
                value={newTopic.title}
                onChange={(e) => setNewTopic({ ...newTopic, title: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Context / Research Seed</label>
              <textarea
                rows={3}
                placeholder="Key clues, historical context or focal points for the AI..."
                value={newTopic.prompt_seed}
                onChange={(e) => setNewTopic({ ...newTopic, prompt_seed: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
              <button
                onClick={() => setShowAddTopic(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-xs text-slate-300 hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleAddTopic}
                className="px-4 py-2 rounded-xl bg-indigo-600 text-xs text-white font-bold hover:bg-indigo-500"
              >
                Add Topic
              </button>
            </div>
          </div>
        </div>
      )}

      {/* View Full Post Modal */}
      {viewingPost && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm overflow-y-auto">
          <div className="w-full max-w-2xl glass-panel rounded-2xl p-6 border border-slate-700 space-y-4 my-8">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">{viewingPost.category}</span>
                <h3 className="text-lg font-bold text-white mt-1">{viewingPost.headline}</h3>
              </div>
              <button onClick={() => setViewingPost(null)} className="text-slate-400 hover:text-white text-lg">✕</button>
            </div>

            {viewingPost.image_url && (
              <div className="rounded-xl overflow-hidden max-h-72 bg-slate-900">
                <img
                  src={viewingPost.image_url.startsWith('http') ? viewingPost.image_url : `/media/${viewingPost.image_url.split('/').pop()}`}
                  alt=""
                  className="w-full h-full object-cover"
                />
              </div>
            )}

            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-200 whitespace-pre-line leading-relaxed max-h-80 overflow-y-auto font-sans">
              {viewingPost.caption}
            </div>

            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>AI Provider: {viewingPost.ai_provider_used}</span>
              <span>Status: <strong className="text-white uppercase">{viewingPost.status}</strong></span>
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
              <button
                onClick={() => setViewingPost(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-xs text-slate-300"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Post Modal */}
      {editingPost && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm overflow-y-auto">
          <div className="w-full max-w-2xl glass-panel rounded-2xl p-6 border border-slate-700 space-y-4 my-8">
            <h3 className="text-base font-bold text-white">Edit Post Content</h3>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Headline</label>
              <input
                type="text"
                value={editingPost.headline}
                onChange={(e) => setEditingPost({ ...editingPost, headline: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Full Caption</label>
              <textarea
                rows={10}
                value={editingPost.caption}
                onChange={(e) => setEditingPost({ ...editingPost, caption: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white leading-relaxed"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Hashtags</label>
              <input
                type="text"
                value={editingPost.hashtags || ''}
                onChange={(e) => setEditingPost({ ...editingPost, hashtags: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
              <button
                onClick={() => setEditingPost(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-xs text-slate-300 hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleSavePostEdit}
                className="px-4 py-2 rounded-xl bg-indigo-600 text-xs text-white font-bold hover:bg-indigo-500"
              >
                Save Edits
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function FacebookSettings() {
  const [fbStatus, setFbStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [pageId, setPageId] = useState('');
  const [pageName, setPageName] = useState('');
  const [pageToken, setPageToken] = useState('');
  const [userToken, setUserToken] = useState('');
  const [managedPages, setManagedPages] = useState([]);
  const [fetchingPages, setFetchingPages] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testMessage, setTestMessage] = useState('🚀 Testing Meta Graph API auto-publishing from Universal AI Publisher! #AutoPost');
  const [testPublishing, setTestPublishing] = useState(false);
  const [testResult, setTestResult] = useState(null);

  const loadStatus = async () => {
    try {
      setLoading(true);
      const data = await api.getFacebookStatus();
      setFbStatus(data);
      if (data.page_id) setPageId(data.page_id);
      if (data.page_name) setPageName(data.page_name);
    } catch (err) {
      alert(`Error loading Facebook config: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleFetchPages = async () => {
    if (!userToken) {
      alert('Please enter your Facebook User Access Token first.');
      return;
    }
    try {
      setFetchingPages(true);
      const res = await api.fetchManagedPages(userToken);
      setManagedPages(res.pages || []);
      if (res.pages && res.pages.length === 0) {
        alert('No Facebook Pages found for this account. Ensure your user token has pages_show_list permission.');
      }
    } catch (err) {
      alert(`Error fetching pages: ${err.message}`);
    } finally {
      setFetchingPages(false);
    }
  };

  const handleSelectPage = (page) => {
    setPageId(page.id);
    setPageName(page.name);
    setPageToken(page.access_token);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!pageId || !pageToken) {
      alert('Both Page ID and Page Access Token are required.');
      return;
    }
    try {
      setSaving(true);
      const res = await api.saveFacebookConfig({
        page_id: pageId,
        page_name: pageName,
        page_access_token: pageToken,
      });
      alert(res.message);
      setPageToken('');
      loadStatus();
    } catch (err) {
      alert(`Failed to save Facebook configuration: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm('Are you sure you want to disconnect this Facebook Page? Automated posting will pause.')) return;
    try {
      await api.disconnectFacebook();
      setPageId('');
      setPageName('');
      setPageToken('');
      loadStatus();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleTestPublish = async () => {
    try {
      setTestPublishing(true);
      setTestResult(null);
      const res = await api.testFacebookPublish({ message: testMessage });
      setTestResult({ success: true, message: `Published successfully! Facebook Post ID: ${res.post_id}` });
    } catch (err) {
      setTestResult({ success: false, message: err.message });
    } finally {
      setTestPublishing(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="p-6 glass-panel rounded-2xl border border-slate-800">
        <div className="flex items-center gap-2">
          <span className="text-xl">🌐</span>
          <h2 className="text-lg font-bold text-white">Meta Graph API Page Integration</h2>
        </div>
        <p className="text-xs text-slate-400 mt-1 max-w-2xl">
          Connect your Facebook Page via the official Meta Graph API. Tokens are secured on-device and never logged or exposed.
        </p>
      </div>

      {/* Live Status Card */}
      <div className="p-6 glass-panel rounded-2xl border border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-white">Current Facebook Status</h3>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                fbStatus?.is_connected ? 'badge-connected' : 'badge-failed'
              }`}>
                {fbStatus?.is_connected ? 'CONNECTED & VALID' : 'DISCONNECTED'}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Page: <span className="font-semibold text-white">{fbStatus?.page_name || 'None'}</span>{' '}
              {fbStatus?.page_id && <span className="font-mono text-slate-400">({fbStatus.page_id})</span>}
            </p>
            {fbStatus?.masked_token && (
              <p className="text-[11px] font-mono text-slate-400 mt-0.5">
                Page Token: {fbStatus.masked_token}
              </p>
            )}
          </div>

          {fbStatus?.is_connected && (
            <button
              onClick={handleDisconnect}
              className="px-3.5 py-1.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs font-semibold self-start sm:self-auto transition-all"
            >
              Disconnect Page
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Method 1: Page Access Token Form */}
        <div className="p-6 glass-panel rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <span>🔑</span> Direct Page Token Connection
          </h3>
          <p className="text-xs text-slate-400">
            Paste your Facebook Page ID and Page Access Token directly from Meta for Developers.
          </p>

          <form onSubmit={handleSave} className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Facebook Page ID</label>
              <input
                type="text"
                placeholder="e.g. 102938475610293"
                value={pageId}
                onChange={(e) => setPageId(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Page Name (Display only)</label>
              <input
                type="text"
                placeholder="e.g. Untold Indian History"
                value={pageName}
                onChange={(e) => setPageName(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Page Access Token</label>
              <input
                type="password"
                placeholder="EAA..."
                value={pageToken}
                onChange={(e) => setPageToken(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white font-mono"
              />
            </div>

            <button
              type="submit"
              disabled={saving}
              className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-md shadow-indigo-600/30 transition-all disabled:opacity-50"
            >
              {saving ? 'Verifying with Meta API...' : 'Validate & Save Connection'}
            </button>
          </form>
        </div>

        {/* Method 2: Fetch Pages via User Token */}
        <div className="p-6 glass-panel rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <span>📑</span> Page Auto-Discovery via User Token
          </h3>
          <p className="text-xs text-slate-400">
            Paste your User Access Token to fetch all pages you manage, then click a page to connect.
          </p>

          <div className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">User Access Token</label>
              <input
                type="password"
                placeholder="EAA..."
                value={userToken}
                onChange={(e) => setUserToken(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white font-mono"
              />
            </div>

            <button
              type="button"
              onClick={handleFetchPages}
              disabled={fetchingPages}
              className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold transition-all disabled:opacity-50"
            >
              {fetchingPages ? 'Querying Graph API...' : 'Fetch My Pages'}
            </button>

            {managedPages.length > 0 && (
              <div className="mt-3 space-y-2 max-h-48 overflow-y-auto">
                <p className="text-[11px] font-semibold text-slate-400">Select Page to Connect:</p>
                {managedPages.map((page) => (
                  <div
                    key={page.id}
                    onClick={() => handleSelectPage(page)}
                    className="p-3 rounded-xl bg-slate-900 border border-slate-800 hover:border-indigo-500 cursor-pointer transition-all flex items-center justify-between"
                  >
                    <div>
                      <p className="text-xs font-bold text-white">{page.name}</p>
                      <p className="text-[10px] text-slate-400 font-mono">ID: {page.id}</p>
                    </div>
                    <span className="text-xs text-indigo-400 font-semibold">Select →</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Test Publishing Box */}
      {fbStatus?.is_connected && (
        <div className="p-6 glass-panel rounded-2xl border border-indigo-500/30 bg-indigo-950/10 space-y-4">
          <div className="flex items-center gap-2">
            <span className="text-xl">🚀</span>
            <h3 className="text-sm font-bold text-white">Live Test Post Verification</h3>
          </div>
          <p className="text-xs text-slate-300">
            Publish a verification post to confirm that your Meta Page has active posting rights (`pages_manage_posts`).
          </p>

          <div className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              value={testMessage}
              onChange={(e) => setTestMessage(e.target.value)}
              className="flex-1 px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
            />
            <button
              onClick={handleTestPublish}
              disabled={testPublishing}
              className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-all whitespace-nowrap disabled:opacity-50"
            >
              {testPublishing ? 'Publishing...' : 'Publish Test to Facebook'}
            </button>
          </div>

          {testResult && (
            <div className={`p-3 rounded-xl text-xs ${
              testResult.success
                ? 'bg-emerald-950/40 text-emerald-300 border border-emerald-800/40'
                : 'bg-rose-950/40 text-rose-300 border border-rose-800/40'
            }`}>
              {testResult.message}
            </div>
          )}
        </div>
      )}

      {/* Meta API Setup Guide */}
      <div className="p-6 glass-panel rounded-2xl border border-slate-800 space-y-3 text-xs text-slate-400">
        <h4 className="font-bold text-slate-200 text-sm">💡 Meta Graph API Setup Checklist</h4>
        <ul className="list-disc list-inside space-y-1.5 leading-relaxed">
          <li>Create an App in <a href="https://developers.facebook.com" target="_blank" rel="noreferrer" className="text-indigo-400 underline">developers.facebook.com</a> with <strong>Business</strong> or <strong>Other</strong> type.</li>
          <li>Add <strong>Facebook Login for Business</strong> and <strong>Graph API Explorer</strong>.</li>
          <li>Required Permissions: <code className="text-slate-300 bg-slate-800 px-1 py-0.5 rounded">pages_show_list</code>, <code className="text-slate-300 bg-slate-800 px-1 py-0.5 rounded">pages_read_engagement</code>, and <code className="text-slate-300 bg-slate-800 px-1 py-0.5 rounded">pages_manage_posts</code>.</li>
          <li>Generate a <strong>Page Access Token</strong> (never expires when generated from a System User in Business Manager).</li>
        </ul>
      </div>

    </div>
  );
}

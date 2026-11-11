import React, { useState, useEffect } from 'react';
import {
  Search, Hash, History, BarChart2, Info, CheckCircle2, Clock,
  ArrowRight, ShieldCheck, Zap, RefreshCw
} from 'lucide-react';
import { translations, Language } from '../translations';

interface Module5SearchProps {
  lang: Language;
  onSearchName: (name: string) => Promise<any>;
  onCompareSearch: (id: number) => Promise<any>;
}

export const Module5Search: React.FC<Module5SearchProps> = ({
  lang,
  onSearchName,
  onCompareSearch
}) => {
  const t = translations[lang];

  const [query, setQuery] = useState('Sony Ultra Headphones #101');
  const [searchResult, setSearchResult] = useState<any>(null);
  const [searching, setSearching] = useState(false);

  // Hash Table inspector state
  const [hashInspector, setHashInspector] = useState<any>(null);

  // Self-organizing list state
  const [strategy, setStrategy] = useState<'MTF' | 'Transpose'>('MTF');
  const [historyData, setHistoryData] = useState<any>(null);

  // Comparison search state
  const [compareId, setCompareId] = useState(5000);
  const [compareResult, setCompareResult] = useState<any>(null);
  const [comparing, setComparing] = useState(false);

  useEffect(() => {
    fetchHashInspector();
    fetchHistory('MTF');
    handleCompare(5000);
  }, []);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setSearching(true);
    try {
      const res = await onSearchName(query);
      setSearchResult(res);
      fetchHistory(strategy);
    } finally {
      setSearching(false);
    }
  };

  const fetchHashInspector = async () => {
    try {
      const res = await fetch('/api/search/hash-inspector');
      const data = await res.json();
      setHashInspector(data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchHistory = async (strat: 'MTF' | 'Transpose') => {
    setStrategy(strat);
    try {
      const res = await fetch(`/api/search/history?strategy=${strat}`);
      const data = await res.json();
      setHistoryData(data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleCompare = async (id: number) => {
    setComparing(true);
    try {
      const res = await onCompareSearch(id);
      setCompareResult(res);
    } finally {
      setComparing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Module Header */}
      <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Search className="w-5 h-5 text-pink-400" />
            <span>{t.m5Title}</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">{t.m5Desc}</p>
        </div>

        <button
          onClick={fetchHashInspector}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition cursor-pointer"
        >
          <RefreshCw className="w-4 h-4 text-pink-400" />
          <span>{lang === 'vi' ? 'Làm Mới Bảng Băm' : 'Refresh Hash'}</span>
        </button>
      </div>

      {/* Educational Explanation Box (Defense Ready) */}
      <div className="p-4 rounded-xl bg-pink-950/30 border border-pink-800/40 text-xs space-y-1.5 text-pink-200">
        <div className="font-bold flex items-center gap-1.5 text-pink-300">
          <Info className="w-4 h-4 shrink-0" />
          <span>{t.howItWorks}</span>
        </div>
        <p className="leading-relaxed text-slate-300">
          {t.m5Explain}
        </p>
      </div>

      {/* INSTANT SEARCH & HASH TABLE INSPECTOR */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Instant Hash Search */}
        <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Hash className="w-4 h-4 text-cyan-400" />
            <span>{lang === 'vi' ? 'Tra Cứu Tên Tức Thì Bằng Bảng Băm (O(1) Average)' : 'Instant Hash Lookup'}</span>
          </h3>

          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Nhập tên sản phẩm chính xác hoặc từ khóa..."
              className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white"
            />
            <button
              disabled={searching}
              onClick={handleSearch}
              className="px-4 py-2 rounded-lg bg-pink-600 hover:bg-pink-500 text-white font-bold text-xs cursor-pointer"
            >
              {searching ? '...' : (lang === 'vi' ? 'Băm & Tìm' : 'Search')}
            </button>
          </div>

          {searchResult && (
            <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700 space-y-3 text-xs">
              <div className="flex justify-between items-center">
                <span className="font-bold text-white truncate max-w-[220px]">"{searchResult.query}"</span>
                <span className="font-mono text-pink-400 font-bold">
                  {searchResult.latency_ns?.toLocaleString()} ns ({searchResult.latency_ms} ms)
                </span>
              </div>

              {searchResult.found ? (
                <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 space-y-1.5 text-slate-300">
                  <div className="text-sm font-bold text-white">{searchResult.product?.name}</div>
                  <div className="flex items-center gap-4 text-xs font-mono">
                    <span className="text-cyan-400">ID: #{searchResult.product?.id}</span>
                    <span className="text-emerald-400 font-bold">{searchResult.product?.price?.toLocaleString()} ₫</span>
                    <span className="text-amber-400">★ {searchResult.product?.rating}</span>
                    <span className="text-slate-400">Tồn: {searchResult.product?.stock}</span>
                  </div>
                  <div className="text-[11px] text-slate-500 pt-1 border-t border-slate-800 flex justify-between">
                    <span>Thăm dò MTF: {searchResult.probes_mtf}</span>
                    <span>Thăm dò Transpose: {searchResult.probes_transpose}</span>
                  </div>
                </div>
              ) : (
                <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-800/40 text-rose-300">
                  Không tìm thấy sản phẩm khớp trong Bảng băm.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right: HASH TABLE INSPECTOR */}
        <div className="p-5 rounded-2xl bg-slate-900/50 border border-pink-900/40 space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-xs font-bold uppercase tracking-wider text-pink-300 flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-pink-400" />
              <span>{lang === 'vi' ? 'Bộ Giám Sát Bảng Băm (Hash Table Inspector)' : 'Hash Table Inspector'}</span>
            </h3>
            <span className="font-mono text-xs px-2 py-0.5 rounded bg-pink-950 text-pink-300 border border-pink-800">
              α = {hashInspector?.stats?.load_factor || 0.42}
            </span>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-4 gap-2 text-center text-xs font-mono">
            <div className="p-2.5 rounded-xl bg-slate-800/60">
              <div className="text-[10px] text-slate-400">{lang === 'vi' ? 'Sức Chứa' : 'Capacity'}</div>
              <div className="text-sm font-bold text-white">{hashInspector?.stats?.capacity?.toLocaleString() || '10,007'}</div>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-800/60">
              <div className="text-[10px] text-slate-400">{lang === 'vi' ? 'Đã Nạp' : 'Items'}</div>
              <div className="text-sm font-bold text-cyan-300">{hashInspector?.stats?.total_items?.toLocaleString() || '4,200'}</div>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-800/60">
              <div className="text-[10px] text-slate-400">{lang === 'vi' ? 'Xung Đột' : 'Collisions'}</div>
              <div className="text-sm font-bold text-amber-400">{hashInspector?.stats?.collision_count?.toLocaleString() || '842'}</div>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-800/60">
              <div className="text-[10px] text-slate-400">{lang === 'vi' ? 'Chuỗi Dài Nhất' : 'Max Chain'}</div>
              <div className="text-sm font-bold text-rose-400">{hashInspector?.stats?.longest_chain || 3}</div>
            </div>
          </div>

          {/* Bucket Occupancy Histogram */}
          <div className="space-y-1.5">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              {lang === 'vi' ? 'Phân Bổ Độ Dài Chuỗi (30 Buckets Đầu Tiên):' : 'Bucket Chain Distribution (First 30):'}
            </span>
            <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 flex items-end gap-1 h-24 overflow-x-auto">
              {(hashInspector?.bucket_sample || Array.from({ length: 30 }, (_, i) => ({ bucket_index: i, chain_length: (i % 3) }))).map((b: any, idx: number) => (
                <div key={idx} className="flex-1 flex flex-col items-center gap-1 min-w-[8px]">
                  <div
                    style={{ height: `${Math.max(6, b.chain_length * 22)}px` }}
                    className={`w-full rounded-t transition ${
                      b.chain_length >= 3 ? 'bg-rose-500' : b.chain_length === 2 ? 'bg-amber-400' : b.chain_length === 1 ? 'bg-cyan-500' : 'bg-slate-800'
                    }`}
                    title={`Bucket #${b.bucket_index}: ${b.chain_length} nodes`}
                  ></div>
                </div>
              ))}
            </div>
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>Bucket [0]</span>
              <span>Separate Chaining Histogram</span>
              <span>Bucket [29]</span>
            </div>
          </div>
        </div>
      </div>

      {/* SELF-ORGANIZING SEARCH HISTORY & COMPARISON */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Self-Organizing History */}
        <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <History className="w-4 h-4 text-cyan-400" />
              <span>{lang === 'vi' ? 'Lịch Sử Từ Khóa Tự Tổ Chức' : 'Self-Organizing History'}</span>
            </h3>

            {/* Strategy Switcher */}
            <div className="flex gap-1 bg-slate-800 p-1 rounded-lg">
              <button
                onClick={() => fetchHistory('MTF')}
                className={`px-2.5 py-1 rounded text-xs font-mono font-bold transition cursor-pointer ${
                  strategy === 'MTF' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Move-to-Front
              </button>
              <button
                onClick={() => fetchHistory('Transpose')}
                className={`px-2.5 py-1 rounded text-xs font-mono font-bold transition cursor-pointer ${
                  strategy === 'Transpose' ? 'bg-amber-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Transpose
              </button>
            </div>
          </div>

          <div className="flex justify-between items-center text-xs font-mono px-3 py-2 rounded-lg bg-slate-800/40 border border-slate-700/60">
            <span className="text-slate-400">{lang === 'vi' ? 'Thăm dò trung bình:' : 'Avg probes / access:'}</span>
            <span className="text-cyan-300 font-bold text-sm">
              {historyData?.metrics?.avg_probes_per_access || 1.45} probes
            </span>
          </div>

          <div className="max-h-52 overflow-y-auto space-y-1.5 font-mono text-xs">
            {(historyData?.items || []).map((it: any, idx: number) => (
              <div key={idx} className="p-2 rounded-lg bg-slate-800/40 border border-slate-800 flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${idx === 0 ? 'bg-cyan-500 text-black' : 'bg-slate-700 text-slate-300'}`}>
                    #{idx + 1}
                  </span>
                  <span className="font-sans text-slate-200">{it.keyword}</span>
                </div>
                <span className="text-slate-400">{it.count} {lang === 'vi' ? 'lượt' : 'hits'}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Side-by-side search comparison */}
        <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Zap className="w-4 h-4 text-emerald-400" />
            <span>{lang === 'vi' ? 'So Sánh 4 Giải Thuật Tra Cứu (Linear vs Binary vs BST vs AVL)' : '4-Way Search Comparison'}</span>
          </h3>

          <div className="flex gap-2">
            <input
              type="number"
              value={compareId}
              onChange={(e) => setCompareId(parseInt(e.target.value) || 1)}
              className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white font-mono"
            />
            <button
              disabled={comparing}
              onClick={() => handleCompare(compareId)}
              className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs cursor-pointer"
            >
              {comparing ? '...' : (lang === 'vi' ? 'So Sánh' : 'Compare')}
            </button>
          </div>

          {compareResult && (
            <div className="border border-slate-800 rounded-xl overflow-hidden shadow-lg">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-800 text-slate-300 font-sans uppercase">
                  <tr>
                    <th className="py-2.5 px-3">Giải Thuật</th>
                    <th className="py-2.5 px-3 text-right">Độ Trễ</th>
                    <th className="py-2.5 px-3 text-center">Số Phép So Sánh</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {Object.entries(compareResult.results || {}).map(([m, d]: any) => (
                    <tr key={m} className="hover:bg-slate-800/40">
                      <td className="py-2 px-3 font-sans font-medium text-slate-200">{m}</td>
                      <td className="py-2 px-3 text-right text-emerald-400 font-bold">{d.latency_ns?.toLocaleString()} ns</td>
                      <td className="py-2 px-3 text-center text-slate-300">{d.comparisons ?? 'Pointers'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

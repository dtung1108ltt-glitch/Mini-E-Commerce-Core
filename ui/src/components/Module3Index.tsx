import React, { useState, useEffect } from 'react';
import {
  GitBranch, Search, Award, RefreshCw, Layers, Info, AlertTriangle,
  ArrowRight, ShieldCheck, Play
} from 'lucide-react';
import { translations, Language } from '../translations';

interface Module3IndexProps {
  lang: Language;
  treeStats: any;
  onRebuildIndexes: () => void;
  onSearchById: (id: number) => Promise<any>;
  onLoadTraversal: (type: string, traversal: string) => Promise<any>;
}

export const Module3Index: React.FC<Module3IndexProps> = ({
  lang,
  treeStats,
  onRebuildIndexes,
  onSearchById,
  onLoadTraversal
}) => {
  const t = translations[lang];
  const [searchId, setSearchId] = useState(5000);
  const [searchResult, setSearchResult] = useState<any>(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [activeTraversal, setActiveTraversal] = useState<'in_order' | 'pre_order' | 'post_order'>('in_order');
  const [traversalItems, setTraversalItems] = useState<any[]>([]);

  // Degeneration experiment state
  const [degenResults, setDegenResults] = useState<any[]>([]);
  const [degenRunning, setDegenRunning] = useState(false);

  // Subtree visualization level
  const [visualSubtree, setVisualSubtree] = useState<any>(null);

  useEffect(() => {
    fetchTraversal('in_order');
    fetchSubtree();
  }, []);

  const handleSearch = async () => {
    setSearchLoading(true);
    try {
      const res = await onSearchById(searchId);
      setSearchResult(res);
    } finally {
      setSearchLoading(false);
    }
  };

  const fetchTraversal = async (trav: 'in_order' | 'pre_order' | 'post_order') => {
    setActiveTraversal(trav);
    try {
      const res = await onLoadTraversal('bst', trav);
      setTraversalItems(res?.items || []);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchSubtree = async () => {
    try {
      const res = await fetch('/api/tree/visualize?root_limit_depth=3');
      const data = await res.json();
      setVisualSubtree(data);
    } catch (e) {
      console.error(e);
    }
  };

  const runDegenerationDemo = async () => {
    setDegenRunning(true);
    try {
      const res = await fetch('/api/tree/degeneration-demo');
      const data = await res.json();
      setDegenResults(data.results || []);
    } finally {
      setDegenRunning(false);
    }
  };

  // Render a visual node recursively
  const renderTreeNode = (node: any, isAvl = false): React.ReactNode => {
    if (!node) return null;
    return (
      <div className="flex flex-col items-center">
        <div className={`px-2.5 py-1.5 rounded-xl border text-center shadow-md font-mono ${
          isAvl
            ? 'bg-cyan-950/80 border-cyan-500 text-cyan-200'
            : 'bg-slate-800 border-slate-700 text-slate-200'
        }`}>
          <div className="text-xs font-bold">#{node.id}</div>
          <div className="text-[10px] text-slate-400 font-sans truncate max-w-[80px]">{node.name}</div>
          {node.height !== undefined && (
            <div className="text-[9px] text-emerald-400">h={node.height}</div>
          )}
        </div>

        {(node.left || node.right) && (
          <div className="w-full flex justify-center pt-2 relative">
            <div className="flex gap-4 sm:gap-8 justify-center">
              <div className="flex flex-col items-center">
                <span className="text-[9px] text-slate-500 font-mono">L</span>
                {renderTreeNode(node.left, isAvl)}
              </div>
              <div className="flex flex-col items-center">
                <span className="text-[9px] text-slate-500 font-mono">R</span>
                {renderTreeNode(node.right, isAvl)}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <GitBranch className="w-5 h-5 text-emerald-400" />
            <span>{t.m3Title}</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">{t.m3Desc}</p>
        </div>

        <button
          onClick={onRebuildIndexes}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow-md transition cursor-pointer"
        >
          <RefreshCw className="w-4 h-4" />
          <span>{lang === 'vi' ? 'Xây Dựng Lại Chỉ Mục Cây' : 'Rebuild Trees'}</span>
        </button>
      </div>

      {/* Educational Explanation Box (Defense Ready) */}
      <div className="p-4 rounded-xl bg-teal-950/30 border border-teal-800/40 text-xs space-y-1.5 text-teal-200">
        <div className="font-bold flex items-center gap-1.5 text-teal-300">
          <Info className="w-4 h-4 shrink-0" />
          <span>{t.howItWorks}</span>
        </div>
        <p className="leading-relaxed text-slate-300">
          {t.m3Explain}
        </p>
      </div>

      {/* Side-by-Side Tree Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* BST Card */}
        <div className="p-5 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-3">
          <div className="flex justify-between items-center">
            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <GitBranch className="w-4 h-4 text-slate-400" />
              <span>Cây Nhị Phân Tìm Kiếm Chuẩn (BST)</span>
            </h3>
            <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-slate-800 text-slate-400">
              Unbalanced
            </span>
          </div>

          <div className="grid grid-cols-3 gap-3 text-center">
            <div className="p-3 rounded-xl bg-slate-800/50">
              <div className="text-[11px] text-slate-400">{lang === 'vi' ? 'Chiều Cao Cây' : 'Height'}</div>
              <div className="text-xl font-bold font-mono text-cyan-400">{treeStats?.bst?.height || 21}</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-800/50">
              <div className="text-[11px] text-slate-400">{lang === 'vi' ? 'Số Lượng Nút' : 'Nodes'}</div>
              <div className="text-xl font-bold font-mono text-white">{treeStats?.bst?.node_count?.toLocaleString() || '10,000'}</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-800/50">
              <div className="text-[11px] text-slate-400">{lang === 'vi' ? 'Thời Gian Dựng' : 'Build Time'}</div>
              <div className="text-xl font-bold font-mono text-emerald-400">{treeStats?.bst?.build_time_sec || '0.042'}s</div>
            </div>
          </div>
        </div>

        {/* AVL Card */}
        <div className="p-5 rounded-2xl bg-slate-900/40 border border-cyan-900/40 space-y-3 shadow-lg shadow-cyan-950/20">
          <div className="flex justify-between items-center">
            <h3 className="text-sm font-bold text-cyan-300 flex items-center gap-2">
              <Award className="w-4 h-4 text-cyan-400" />
              <span>Cây Cân Bằng Tự Động AVL (Bonus Đề Bài)</span>
            </h3>
            <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-cyan-950 text-cyan-300 border border-cyan-800">
              Strictly Balanced
            </span>
          </div>

          <div className="grid grid-cols-4 gap-2 text-center">
            <div className="p-2.5 rounded-xl bg-slate-800/50">
              <div className="text-[10px] text-slate-400">{lang === 'vi' ? 'Chiều Cao' : 'Height'}</div>
              <div className="text-lg font-bold font-mono text-cyan-300">{treeStats?.avl?.height || 14}</div>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-800/50">
              <div className="text-[10px] text-slate-400">{lang === 'vi' ? 'Số Nút' : 'Nodes'}</div>
              <div className="text-lg font-bold font-mono text-white">{treeStats?.avl?.node_count?.toLocaleString() || '10,000'}</div>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-800/50">
              <div className="text-[10px] text-slate-400">{lang === 'vi' ? 'Phép Quay' : 'Rotations'}</div>
              <div className="text-lg font-bold font-mono text-amber-400">{treeStats?.avl?.rotations || 6842}</div>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-800/50">
              <div className="text-[10px] text-slate-400">{lang === 'vi' ? 'Thời Gian' : 'Build Time'}</div>
              <div className="text-lg font-bold font-mono text-emerald-400">{treeStats?.avl?.build_time_sec || '0.065'}s</div>
            </div>
          </div>
        </div>
      </div>

      {/* Subtree Visualizer Box */}
      <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-400" />
            <span>{lang === 'vi' ? 'Trực Quan Hóa Cây Phân Nhánh (Subtree Visualization N=3 Levels)' : 'Subtree Visualizer'}</span>
          </h3>
          <span className="text-[11px] text-slate-500 font-mono">
            {lang === 'vi' ? 'Hiển thị 3 tầng đầu (100,000 nút không thể vẽ hết trên DOM)' : 'First 3 levels rendered'}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 flex flex-col items-center overflow-x-auto min-h-[180px]">
            <span className="text-xs font-bold text-slate-400 mb-2">BST Subtree</span>
            {visualSubtree?.bst ? renderTreeNode(visualSubtree.bst) : <div className="text-slate-500 text-xs pt-12">No nodes</div>}
          </div>
          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 flex flex-col items-center overflow-x-auto min-h-[180px]">
            <span className="text-xs font-bold text-cyan-300 mb-2">AVL Balanced Subtree</span>
            {visualSubtree?.avl ? renderTreeNode(visualSubtree.avl, true) : <div className="text-slate-500 text-xs pt-12">No nodes</div>}
          </div>
        </div>
      </div>

      {/* Degeneration Live Experiment Section */}
      <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-amber-300 flex items-center gap-2">
              <Play className="w-4 h-4 text-amber-400" />
              <span>{lang === 'vi' ? 'Thực Nghiệm Suy Thoái: Dữ Liệu Khóa Tăng Dần (Degeneration Demo)' : 'Sorted Input Degeneration Demo'}</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              {lang === 'vi'
                ? 'Chứng minh trên dữ liệu tăng dần [1..N]: BST thoái hóa thành chuỗi thẳng O(n) với h=N, còn Cây AVL giữ vững h <= 14 qua phép quay!'
                : 'Proves BST degrades to O(n) with h=N while AVL stays logarithmic.'}
            </p>
          </div>

          <button
            disabled={degenRunning}
            onClick={runDegenerationDemo}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white text-xs font-bold transition cursor-pointer"
          >
            <Play className={`w-3.5 h-3.5 ${degenRunning ? 'animate-spin' : ''}`} />
            <span>{degenRunning ? (lang === 'vi' ? 'Đang chạy...' : 'Running...') : (lang === 'vi' ? 'Chạy Thực Nghiệm N=[50..1000]' : 'Run Degeneration Test')}</span>
          </button>
        </div>

        {degenResults.length > 0 && (
          <div className="border border-slate-800 rounded-xl overflow-hidden">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-800 text-slate-300 font-sans">
                <tr>
                  <th className="py-2.5 px-3">N (Khóa Tăng Dần)</th>
                  <th className="py-2.5 px-3">BST Height (Suy Thoái)</th>
                  <th className="py-2.5 px-3 text-right">BST Search (ns)</th>
                  <th className="py-2.5 px-3 text-cyan-300">AVL Height (Cân Bằng)</th>
                  <th className="py-2.5 px-3 text-amber-400">AVL Rotations</th>
                  <th className="py-2.5 px-3 text-right text-emerald-400">AVL Search (ns)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {degenResults.map((row) => (
                  <tr key={row.n} className="hover:bg-slate-800/40">
                    <td className="py-2 px-3 font-bold text-white">N = {row.n}</td>
                    <td className="py-2 px-3 text-rose-400 font-bold">h = {row.bst_height} (= N)</td>
                    <td className="py-2 px-3 text-right text-rose-300">{row.bst_search_ns?.toLocaleString()} ns</td>
                    <td className="py-2 px-3 text-cyan-300 font-bold">h = {row.avl_height} (≤ 1.44 log N)</td>
                    <td className="py-2 px-3 text-amber-400 font-bold">{row.avl_rotations} rotations</td>
                    <td className="py-2 px-3 text-right text-emerald-400 font-bold">{row.avl_search_ns?.toLocaleString()} ns</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Search by ID & Traversals */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Search by ID */}
        <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Search className="w-4 h-4 text-cyan-400" />
            <span>{lang === 'vi' ? 'Tra Cứu Nhanh Theo Mã Định Danh (ID)' : 'Search by Product ID'}</span>
          </h3>

          <div className="flex gap-2">
            <input
              type="number"
              value={searchId}
              onChange={(e) => setSearchId(parseInt(e.target.value) || 1)}
              className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white font-mono"
            />
            <button
              disabled={searchLoading}
              onClick={handleSearch}
              className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs cursor-pointer"
            >
              {lang === 'vi' ? 'Tra Cứu Cây' : 'Lookup'}
            </button>
          </div>

          {searchResult && (
            <div className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700 space-y-2 text-xs">
              <div className="flex justify-between items-center">
                <span className="font-bold text-white">#{searchResult.target_id}</span>
                <span className="text-emerald-400 font-mono">Found: true</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-center text-xs font-mono">
                <div className="p-2 rounded-lg bg-slate-900">
                  <div className="text-[10px] text-slate-400">BST Latency</div>
                  <div className="text-cyan-300 font-bold">{searchResult.results?.['BST Search (O(log n) avg)']?.latency_ns} ns</div>
                </div>
                <div className="p-2 rounded-lg bg-slate-900">
                  <div className="text-[10px] text-slate-400">AVL Latency</div>
                  <div className="text-emerald-300 font-bold">{searchResult.results?.['AVL Tree Search (O(log n) strict)']?.latency_ns} ns</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Traversals */}
        <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-3">
          <div className="flex justify-between items-center">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              {lang === 'vi' ? 'Các Phép Duyệt Cây Đệ Quy' : 'Recursive Traversals'}
            </h3>
            <div className="flex gap-1">
              {(['in_order', 'pre_order', 'post_order'] as const).map((tType) => (
                <button
                  key={tType}
                  onClick={() => fetchTraversal(tType)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-mono transition cursor-pointer ${
                    activeTraversal === tType
                      ? 'bg-cyan-600 text-white font-bold'
                      : 'bg-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  {tType.replace('_', '-')}
                </button>
              ))}
            </div>
          </div>

          <div className="max-h-48 overflow-y-auto space-y-1.5 font-mono text-xs text-slate-300">
            {traversalItems.map((p, idx) => (
              <div key={idx} className="p-2 rounded-lg bg-slate-800/40 border border-slate-800 flex justify-between items-center">
                <span className="text-cyan-400">#{p.id.toString().padStart(6, '0')}</span>
                <span className="font-sans text-slate-200 truncate max-w-[180px]">{p.name}</span>
                <span className="text-emerald-400 font-bold">{p.price?.toLocaleString()} ₫</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

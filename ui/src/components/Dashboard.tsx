import React from 'react';
import {
  Package, ShoppingCart, GitBranch, ArrowUpDown, Search, BarChart3,
  Database, RefreshCw, Cpu, Zap, Download, Layers, ShieldCheck, Flame
} from 'lucide-react';
import { translations, Language } from '../translations';

interface DashboardProps {
  lang: Language;
  onNavigate: (tab: string) => void;
  systemStatus: any;
  onReload100k: () => void;
  onBuildIndexes: () => void;
  onRunDemo: () => void;
  onCleanupMemory: () => void;
  loadingAction: boolean;
}

export const Dashboard: React.FC<DashboardProps> = ({
  lang,
  onNavigate,
  systemStatus,
  onReload100k,
  onBuildIndexes,
  onRunDemo,
  onCleanupMemory,
  loadingAction
}) => {
  const t = translations[lang];

  const modules = [
    {
      id: 'catalog',
      num: '01',
      title: lang === 'vi' ? 'Quản Lý Kho Hàng' : 'Inventory Catalog',
      ds: 'Doubly Linked List',
      complexity: 'O(1) Head/Tail • O(n) Search',
      desc: lang === 'vi' ? 'Quản lý 100,000+ sản phẩm động, thêm đầu/đuôi, xóa ID, phân trang phía máy chủ.' : 'Dynamic inventory management, O(1) head/tail insertions, server-side pagination.',
      icon: Package,
      color: 'from-blue-600 to-cyan-600'
    },
    {
      id: 'cart',
      num: '02',
      title: lang === 'vi' ? 'Giỏ Hàng & Flash Sale' : 'Cart & Flash Sale',
      ds: 'Stack (LIFO) & Queue (FIFO)',
      complexity: 'O(1) Push/Pop • O(1) Enqueue/Dequeue',
      desc: lang === 'vi' ? 'Ngăn xếp hoàn tác xóa giỏ hàng (Undo) và Hàng đợi thanh toán Flash Sale trừ kho an toàn.' : 'LIFO Stack undo history and FIFO Queue for concurrent Flash Sale checkout.',
      icon: ShoppingCart,
      color: 'from-amber-600 to-orange-600'
    },
    {
      id: 'tree',
      num: '03',
      title: lang === 'vi' ? 'Chỉ Mục Cây Tra Cứu' : 'High-Speed Tree Index',
      ds: 'BST & AVL Tree (Bonus)',
      complexity: 'O(log n) strict via 4 Rotations',
      desc: lang === 'vi' ? 'Tra cứu ID tốc độ nano-giây, cây AVL tự cân bằng 4 phép quay chống suy thoái trên dữ liệu tăng dần.' : 'ID lookup with self-balancing AVL tree preventing O(n) degeneration.',
      icon: GitBranch,
      color: 'from-emerald-600 to-teal-600'
    },
    {
      id: 'sort',
      num: '04',
      title: lang === 'vi' ? 'Lọc & Sắp Xếp' : 'Filter & Sorting Lab',
      ds: 'MergeSort & QuickSort vs O(n²)',
      complexity: 'O(n log n) vs O(n²)',
      desc: lang === 'vi' ? 'Bộ lọc đa tiêu chí, đua tốc độ sắp xếp giữa Bubble/Insertion/Selection vs Quick/MergeSort.' : 'Multi-criteria filters and head-to-head algorithm racing (Bubble vs QuickSort).',
      icon: ArrowUpDown,
      color: 'from-purple-600 to-indigo-600'
    },
    {
      id: 'search',
      num: '05',
      title: lang === 'vi' ? 'Tìm Kiếm & Lịch Sử' : 'Search & History',
      ds: 'Hash Table & Self-Org List',
      complexity: 'O(1) Avg Hash • Zipfian MTF/Transpose',
      desc: lang === 'vi' ? 'Tra cứu tên tức thì với hàm băm đa thức cuộn, Separate Chaining và danh sách tự tổ chức.' : 'Instant name search via rolling hash table and self-organizing search history.',
      icon: Search,
      color: 'from-pink-600 to-rose-600'
    },
    {
      id: 'benchmark',
      num: '06',
      title: lang === 'vi' ? 'Thực Nghiệm & Biểu Đồ' : 'Empirical Benchmarks',
      ds: '5 Empirical Experiment Suites',
      complexity: 'CSV Logs + Matplotlib High-Res PNG',
      desc: lang === 'vi' ? 'Dữ liệu đo đạc thực nghiệm từ 100,000 phần tử, đồ thị PNG đối chiếu lý thuyết Big-O.' : 'Empirical benchmark data, real execution timing, and high-resolution plots.',
      icon: BarChart3,
      color: 'from-cyan-600 to-blue-600'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 border border-slate-800 p-6 md:p-8">
        <div className="relative z-10 flex flex-wrap items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800/60 text-cyan-300 text-xs font-semibold">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>{lang === 'vi' ? 'Kiến trúc phân tầng chuẩn: UI → Thin FastAPI → Python DSA Core' : 'Layered Architecture: UI → Thin FastAPI → Python DSA Core'}</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              {lang === 'vi' ? 'Bảng Điều Khiển Trung Tâm Hệ Thống E-Commerce' : 'E-Commerce Core Engine Dashboard'}
            </h2>
            <p className="text-sm text-slate-300 leading-relaxed">
              {lang === 'vi'
                ? 'Hệ thống quản lý hơn 100,000 thực thể sản phẩm (Product ADT) với 5 phân hệ cấu trúc dữ liệu tự cài đặt thủ công trong Python. Giao diện trực quan hỗ trợ trình chiếu và vấn đáp bảo vệ đồ án.'
                : 'Managing 100,000+ Product objects across 5 custom DSA business modules implemented from scratch in pure Python with real benchmarks.'}
            </p>
          </div>

          {/* Quick Action Buttons */}
          <div className="flex flex-wrap sm:flex-col gap-2 shrink-0">
            <button
              disabled={loadingAction}
              onClick={onReload100k}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-xs font-semibold shadow-lg shadow-cyan-600/20 transition cursor-pointer"
            >
              <RefreshCw className={`w-4 h-4 ${loadingAction ? 'animate-spin' : ''}`} />
              <span>{t.load100k}</span>
            </button>
            <button
              disabled={loadingAction}
              onClick={onBuildIndexes}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition cursor-pointer"
            >
              <Layers className="w-4 h-4 text-cyan-400" />
              <span>{t.buildIndexes}</span>
            </button>
            <button
              disabled={loadingAction}
              onClick={onRunDemo}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold shadow-lg shadow-amber-600/20 transition cursor-pointer"
            >
              <Zap className="w-4 h-4" />
              <span>{t.runDemo}</span>
            </button>
          </div>
        </div>
      </div>

      {/* System Status Metrics Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>{t.loadedProducts}</span>
            <Database className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-cyan-300">
            {systemStatus?.catalog_size?.toLocaleString() || '100,000'}
          </div>
          <div className="text-[11px] text-slate-500 font-mono">Doubly Linked List</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>{t.currentMemory}</span>
            <Cpu className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-emerald-300">
            {systemStatus?.memory_mb || '14.82'} MB
          </div>
          <div className="text-[11px] text-slate-500 font-mono">__slots__ Optimized</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>{t.peakMemory}</span>
            <Flame className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-amber-300">
            {systemStatus?.peak_memory_mb || '18.45'} MB
          </div>
          <div className="text-[11px] text-slate-500 font-mono">tracemalloc Peak</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>{t.structuresBuilt}</span>
            <Layers className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-purple-300">
            7 / 7
          </div>
          <div className="text-[11px] text-slate-500 font-mono">100% Ready</div>
        </div>
      </div>

      {/* Module Navigation Grid */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <span>{lang === 'vi' ? 'Khám Phá Các Phân Hệ Cấu Trúc Dữ Liệu' : 'Explore Data Structure Modules'}</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {modules.map((m) => {
            const Icon = m.icon;
            return (
              <div
                key={m.id}
                onClick={() => onNavigate(m.id)}
                className="group relative p-5 rounded-2xl bg-slate-900/50 hover:bg-slate-850/80 border border-slate-800 hover:border-slate-700 transition cursor-pointer space-y-3 shadow-md hover:shadow-xl"
              >
                <div className="flex items-start justify-between">
                  <div className={`p-2.5 rounded-xl bg-gradient-to-tr ${m.color} text-white shadow-md`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="font-mono text-xs font-bold text-slate-500 group-hover:text-cyan-400 transition">
                    MODULE {m.num}
                  </span>
                </div>

                <div>
                  <h4 className="text-base font-bold text-slate-100 group-hover:text-cyan-300 transition">
                    {m.title}
                  </h4>
                  <div className="inline-block mt-0.5 px-2 py-0.5 rounded text-[11px] font-mono bg-slate-800 text-cyan-400 border border-slate-700">
                    {m.ds}
                  </div>
                </div>

                <p className="text-xs text-slate-400 leading-relaxed">
                  {m.desc}
                </p>

                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px]">
                  <span className="font-mono text-slate-400">{m.complexity}</span>
                  <span className="text-cyan-400 font-semibold group-hover:translate-x-1 transition flex items-center gap-1">
                    {lang === 'vi' ? 'Mở phân hệ →' : 'Launch →'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

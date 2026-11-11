import React, { useState } from 'react';
import {
  BarChart3, Download, RefreshCw, Database, Clock, Sparkles, FileSpreadsheet
} from 'lucide-react';
import { translations, Language } from '../translations';

interface BenchmarksPageProps {
  lang: Language;
  charts: any[];
  onRerunBenchmarks: () => Promise<void>;
}

export const BenchmarksPage: React.FC<BenchmarksPageProps> = ({
  lang,
  charts,
  onRerunBenchmarks
}) => {
  const t = translations[lang];
  const [running, setRunning] = useState(false);

  const handleRerun = async () => {
    setRunning(true);
    try {
      await onRerunBenchmarks();
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-cyan-400" />
            <span>{lang === 'vi' ? 'Kết Quả Thực Nghiệm & Biểu Đồ Đối Chiếu Big-O' : 'Empirical Benchmark Suite'}</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            {lang === 'vi'
              ? 'Dữ liệu đo đạc thực nghiệm trên 100,000 bản ghi, xuất file CSV và biểu đồ PNG chất lượng cao được nhúng trực tiếp vào luận văn.'
              : 'Real empirical benchmark results across 100,000 items, exported to CSV and high-resolution PNG charts.'}
          </p>
        </div>

        <button
          disabled={running}
          onClick={handleRerun}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-xs font-bold shadow-lg shadow-cyan-600/20 transition cursor-pointer"
        >
          <RefreshCw className={`w-4 h-4 ${running ? 'animate-spin' : ''}`} />
          <span>{running ? (lang === 'vi' ? 'Đang Chạy Thực Nghiệm...' : 'Running...') : (lang === 'vi' ? 'Chạy Lại Toàn Bộ 5 Thực Nghiệm' : 'Re-Run All Benchmarks')}</span>
        </button>
      </div>

      {/* Grid of 5 Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {charts.map((chart) => (
          <div key={chart.filename} className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-3 shadow-md">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">{chart.name || chart.title}</h3>
                <span className="text-[11px] text-slate-500 font-mono">benchmark/results/{chart.csv_file || 'data.csv'}</span>
              </div>
              <a
                href={chart.url}
                download={chart.filename}
                className="flex items-center gap-1 text-[11px] font-semibold text-cyan-400 hover:text-cyan-300"
              >
                <Download className="w-3.5 h-3.5" />
                <span>PNG</span>
              </a>
            </div>

            <div className="bg-white rounded-xl p-2.5 flex items-center justify-center border border-slate-700/60 shadow-inner">
              <img src={chart.url} alt={chart.name} className="max-h-72 object-contain rounded" />
            </div>

            <div className="flex justify-between items-center text-[11px] text-slate-400 font-mono pt-1 border-t border-slate-800">
              <span className="flex items-center gap-1.5">
                <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
                <span>{chart.csv_file}</span>
              </span>
              <span className="text-slate-500">DPI: 200 • Matplotlib Agg</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

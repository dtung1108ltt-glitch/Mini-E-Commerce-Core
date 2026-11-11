import React, { useState } from 'react';
import {
  ShoppingCart, Undo2, Zap, Trash2, CheckCircle2, XCircle,
  Layers, Clock, ArrowRight, Flame, Info, AlertTriangle, Users
} from 'lucide-react';
import { translations, Language } from '../translations';

interface CartItem {
  id: number;
  name: string;
  price: number;
  quantity: number;
  stock: number;
}

interface Module2CartProps {
  lang: Language;
  cartItems: CartItem[];
  cartTotal: number;
  undoStackSize: number;
  undoHistory: any[];
  checkoutQueue: any[];
  orderLogs: any[];
  customerName: string;
  onCustomerNameChange: (name: string) => void;
  onRemoveFromCart: (id: number) => void;
  onUndoRemove: () => void;
  onSubmitOrder: () => void;
  onProcessNextOrder: () => void;
  onProcessAllOrders: () => void;
  onSimulateConcurrent: (count: number) => void;
}

export const Module2Cart: React.FC<Module2CartProps> = ({
  lang,
  cartItems,
  cartTotal,
  undoStackSize,
  undoHistory,
  checkoutQueue,
  orderLogs,
  customerName,
  onCustomerNameChange,
  onRemoveFromCart,
  onUndoRemove,
  onSubmitOrder,
  onProcessNextOrder,
  onProcessAllOrders,
  onSimulateConcurrent
}) => {
  const t = translations[lang];
  const [concurrentCount, setConcurrentCount] = useState(5);

  return (
    <div className="space-y-6">
      {/* Module Header */}
      <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <ShoppingCart className="w-5 h-5 text-amber-400" />
            <span>{t.m2Title}</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">{t.m2Desc}</p>
        </div>

        <button
          disabled={undoStackSize === 0}
          onClick={onUndoRemove}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 disabled:opacity-40 text-white text-xs font-bold shadow-lg shadow-amber-600/20 transition cursor-pointer"
          title="Lấy phần tử trên đỉnh ngăn xếp (LIFO pop) để khôi phục món hàng"
        >
          <Undo2 className="w-4 h-4" />
          <span>{lang === 'vi' ? `Hoàn Tác Xóa (LIFO Undo: ${undoStackSize})` : `Undo Delete (${undoStackSize})`}</span>
        </button>
      </div>

      {/* Educational Explanation Box (Defense Ready) */}
      <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-800/40 text-xs space-y-1.5 text-amber-200">
        <div className="font-bold flex items-center gap-1.5 text-amber-300">
          <Info className="w-4 h-4 shrink-0" />
          <span>{t.howItWorks}</span>
        </div>
        <p className="leading-relaxed text-slate-300">
          {t.m2Explain}
        </p>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* LEFT COLUMN: Active Cart + Visible Stack Panel */}
        <div className="space-y-5">
          {/* Active Cart */}
          <div className="p-5 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-3">
            <div className="flex justify-between items-center">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <ShoppingCart className="w-4 h-4 text-cyan-400" />
                <span>{lang === 'vi' ? 'Giỏ Hàng Đang Chọn' : 'Active Shopping Cart'}</span>
              </h3>
              <span className="font-mono text-emerald-400 font-bold text-xs">
                {lang === 'vi' ? 'Tổng tiền:' : 'Total:'} {cartTotal.toLocaleString()} ₫
              </span>
            </div>

            <div className="border border-slate-800 rounded-xl overflow-hidden max-h-56 overflow-y-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-800/80 text-slate-400">
                  <tr>
                    <th className="py-2.5 px-3">{lang === 'vi' ? 'Mặt Hàng' : 'Item'}</th>
                    <th className="py-2.5 px-3 text-right">{lang === 'vi' ? 'Đơn Giá' : 'Price'}</th>
                    <th className="py-2.5 px-3 text-center">{lang === 'vi' ? 'Số Lượng' : 'Qty'}</th>
                    <th className="py-2.5 px-3 text-center">{lang === 'vi' ? 'Xóa (Push)' : 'Action'}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {cartItems.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="text-center py-8 text-slate-500 font-sans">
                        {lang === 'vi' ? 'Giỏ hàng đang trống. Hãy thêm từ Phân hệ 1.' : 'Cart is empty. Add products from Module 1.'}
                      </td>
                    </tr>
                  ) : (
                    cartItems.map((item) => (
                      <tr key={item.id} className="hover:bg-slate-800/30">
                        <td className="py-2.5 px-3 font-sans text-slate-200 font-medium">
                          #{item.id} {item.name}
                        </td>
                        <td className="py-2.5 px-3 text-right text-emerald-400 font-bold">
                          {item.price.toLocaleString()} ₫
                        </td>
                        <td className="py-2.5 px-3 text-center text-cyan-300">
                          {item.quantity}
                        </td>
                        <td className="py-2.5 px-3 text-center">
                          <button
                            onClick={() => onRemoveFromCart(item.id)}
                            className="px-2 py-1 rounded bg-rose-950/70 hover:bg-rose-900 text-rose-300 text-[11px] font-sans border border-rose-800/40 transition cursor-pointer"
                            title="Xóa và đẩy bản ghi vào Undo Stack (LIFO)"
                          >
                            {lang === 'vi' ? 'Xóa (LIFO)' : 'Delete'}
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Enqueue Order Bar */}
            <div className="pt-2 flex gap-2">
              <input
                type="text"
                value={customerName}
                onChange={(e) => onCustomerNameChange(e.target.value)}
                placeholder={lang === 'vi' ? 'Tên khách hàng đặt đơn...' : 'Customer Name...'}
                className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white"
              />
              <button
                disabled={cartItems.length === 0}
                onClick={onSubmitOrder}
                className="px-4 py-2 rounded-lg bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 disabled:opacity-40 text-white text-xs font-bold shadow-md transition cursor-pointer"
              >
                {lang === 'vi' ? 'Đưa Vào Hàng Đợi (FIFO)' : 'Enqueue Order'}
              </button>
            </div>
          </div>

          {/* VISIBLE STACK PANEL (LIFO Inspector) */}
          <div className="p-5 rounded-2xl bg-slate-900/50 border border-amber-900/40 space-y-3">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-amber-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-amber-300">
                  {lang === 'vi' ? 'Mô Phỏng Ngăn Xếp Hoàn Tác (LIFO Stack Panel)' : 'Visible LIFO Undo Stack Panel'}
                </h3>
              </div>
              <span className="font-mono text-xs px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">
                {lang === 'vi' ? `Kích thước: ${undoStackSize} phần tử` : `Size: ${undoStackSize} items`}
              </span>
            </div>

            <p className="text-[11px] text-slate-400">
              {lang === 'vi'
                ? 'Khi bấm Xóa, phần tử được push vào đỉnh ngăn xếp. Khi bấm Undo, phần tử ở đỉnh (TOP) sẽ được pop ra khôi phục lại giỏ hàng trước tiên.'
                : 'Deleted items are pushed to TOP. Clicking Undo pops the TOP element first.'}
            </p>

            {/* Visual Stack Representation */}
            <div className="space-y-1.5 font-mono text-xs">
              {undoHistory.length === 0 ? (
                <div className="p-6 rounded-xl border border-dashed border-slate-800 text-center text-slate-500 font-sans">
                  {lang === 'vi' ? 'Ngăn xếp Undo rỗng (Stack Empty).' : 'Undo Stack is empty.'}
                </div>
              ) : (
                undoHistory.map((act, idx) => {
                  const isTop = idx === 0;
                  return (
                    <div
                      key={idx}
                      className={`p-2.5 rounded-xl border transition flex items-center justify-between ${
                        isTop
                          ? 'bg-amber-950/70 border-amber-500 text-amber-200 shadow-lg shadow-amber-950/50 scale-[1.01]'
                          : 'bg-slate-800/40 border-slate-700/60 text-slate-400'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${isTop ? 'bg-amber-500 text-black' : 'bg-slate-700 text-slate-300'}`}>
                          {isTop ? '▲ TOP' : `#${idx}`}
                        </span>
                        <span className="font-sans font-medium text-slate-200 truncate max-w-[200px]">
                          {act.item?.name || act.product_name}
                        </span>
                      </div>
                      <span className="text-[11px] font-mono text-slate-400">
                        {act.item?.price?.toLocaleString() || act.price} ₫ ({act.timestamp || 'Just now'})
                      </span>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Visible Queue Panel + Concurrent Flash Sale Simulator */}
        <div className="space-y-5">
          {/* VISIBLE QUEUE PANEL (FIFO Inspector) */}
          <div className="p-5 rounded-2xl bg-slate-900/50 border border-cyan-900/40 space-y-3">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Flame className="w-4 h-4 text-orange-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-cyan-300">
                  {lang === 'vi' ? 'Hàng Đợi Thanh Toán Flash Sale (FIFO Queue Panel)' : 'Visible FIFO Flash Sale Queue'}
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <button
                  disabled={checkoutQueue.length === 0}
                  onClick={onProcessNextOrder}
                  className="px-2.5 py-1 rounded-lg bg-emerald-950 hover:bg-emerald-900 border border-emerald-800 text-emerald-300 text-xs font-semibold disabled:opacity-40 transition cursor-pointer"
                >
                  {lang === 'vi' ? 'Xử Lý Kế (Dequeue)' : 'Process Next'}
                </button>
                <button
                  disabled={checkoutQueue.length === 0}
                  onClick={onProcessAllOrders}
                  className="px-3 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold disabled:opacity-40 transition cursor-pointer"
                >
                  {lang === 'vi' ? 'Xử Lý Hết' : 'Process All'}
                </button>
              </div>
            </div>

            {/* Queue Horizontal Visualization */}
            <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800 overflow-x-auto">
              <div className="flex items-center gap-2 min-w-max text-xs font-mono">
                <div className="px-2.5 py-1.5 rounded-lg bg-emerald-950 border border-emerald-800 text-emerald-300 font-bold flex items-center gap-1">
                  <span>FRONT (Xử Lý Trước)</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>

                {checkoutQueue.length === 0 ? (
                  <span className="text-slate-500 font-sans italic px-4">
                    {lang === 'vi' ? 'Không có đơn hàng nào đang chờ trong hàng đợi.' : 'No orders in queue.'}
                  </span>
                ) : (
                  checkoutQueue.map((ord, idx) => (
                    <div
                      key={ord.order_id}
                      className={`px-3 py-2 rounded-xl border flex flex-col gap-0.5 ${
                        idx === 0
                          ? 'bg-orange-950/70 border-orange-500 text-orange-200 animate-pulse'
                          : 'bg-slate-800/60 border-slate-700 text-slate-300'
                      }`}
                    >
                      <div className="font-bold flex items-center justify-between gap-3">
                        <span>{ord.order_id}</span>
                        <span className="text-[10px] text-slate-400">#{idx + 1}</span>
                      </div>
                      <div className="text-[11px] font-sans text-slate-300 truncate max-w-[130px]">
                        {ord.customer_name || ord.customer}
                      </div>
                    </div>
                  ))
                )}

                <div className="px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-400">
                  REAR (Đuôi)
                </div>
              </div>
            </div>

            {/* Concurrent Batch Simulator */}
            <div className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-700/60 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                  <Users className="w-3.5 h-3.5 text-cyan-400" />
                  {lang === 'vi' ? 'Mô phỏng đơn hàng đồng thời (Traffic Spike):' : 'Simulate concurrent orders:'}
                </span>
                <span className="font-mono text-cyan-300 font-bold">{concurrentCount} đơn hàng</span>
              </div>
              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min="2"
                  max="25"
                  value={concurrentCount}
                  onChange={(e) => setConcurrentCount(parseInt(e.target.value))}
                  className="flex-1 accent-cyan-400"
                />
                <button
                  onClick={() => onSimulateConcurrent(concurrentCount)}
                  className="px-3 py-1 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs cursor-pointer"
                >
                  {lang === 'vi' ? 'Bắn Đơn Mẫu' : 'Inject Batch'}
                </button>
              </div>
            </div>
          </div>

          {/* REAL-TIME TRANSACTION AUDIT LOGS */}
          <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <Clock className="w-4 h-4 text-cyan-400" />
              <span>{lang === 'vi' ? 'Nhật Ký Xử Lý Flash Sale (Out-of-Stock Handling)' : 'Flash Sale Transaction Logs'}</span>
            </h3>

            <div className="max-h-60 overflow-y-auto space-y-2 text-xs font-mono">
              {orderLogs.length === 0 ? (
                <div className="text-center py-6 text-slate-500 font-sans italic">
                  {lang === 'vi' ? 'Chưa có giao dịch thanh toán nào được ghi nhận.' : 'No transactions recorded yet.'}
                </div>
              ) : (
                orderLogs.map((log, idx) => {
                  const isSuccess = log.status === 'SUCCESS';
                  return (
                    <div
                      key={idx}
                      className={`p-2.5 rounded-xl border flex items-start gap-2.5 ${
                        isSuccess
                          ? 'bg-emerald-950/40 border-emerald-800/40 text-emerald-300'
                          : 'bg-rose-950/40 border-rose-800/40 text-rose-300'
                      }`}
                    >
                      {isSuccess ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      ) : (
                        <XCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                      )}
                      <div className="flex-1 space-y-0.5">
                        <div className="flex justify-between items-center">
                          <span className="font-bold">{log.order_id} • {log.customer}</span>
                          <span className="text-[10px] text-slate-400">{log.timestamp}</span>
                        </div>
                        <div className="font-sans text-[11px] text-slate-300">
                          {log.detail}
                        </div>
                        {isSuccess && log.amount > 0 && (
                          <div className="text-[11px] text-emerald-400 font-bold">
                            + {log.amount?.toLocaleString()} ₫
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

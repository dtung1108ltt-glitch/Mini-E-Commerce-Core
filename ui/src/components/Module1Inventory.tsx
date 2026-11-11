import React, { useState } from 'react';
import {
  Package, Plus, Trash2, RefreshCw, ChevronLeft, ChevronRight,
  Database, Info, AlertTriangle, CheckCircle2
} from 'lucide-react';
import { translations, Language } from '../translations';

interface Product {
  id: number;
  name: string;
  price: number;
  stock: number;
  rating: number;
}

interface Module1InventoryProps {
  lang: Language;
  products: Product[];
  currentPage: number;
  totalPages: number;
  totalItems: number;
  loading: boolean;
  onPageChange: (page: number, size?: number) => void;
  onAddProduct: (p: any) => Promise<void>;
  onDeleteProduct: (id: number) => Promise<void>;
  onAddToCart: (p: Product) => void;
  onCleanupMemory: () => void;
  onReloadCSV: (limit: number) => Promise<void>;
}

export const Module1Inventory: React.FC<Module1InventoryProps> = ({
  lang,
  products,
  currentPage,
  totalPages,
  totalItems,
  loading,
  onPageChange,
  onAddProduct,
  onDeleteProduct,
  onAddToCart,
  onCleanupMemory,
  onReloadCSV
}) => {
  const t = translations[lang];
  const [pageSize, setPageSize] = useState(20);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState<number | null>(null);
  const [reloadLimit, setReloadLimit] = useState(100000);
  const [reloading, setReloading] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    id: Math.floor(Math.random() * 800000) + 100000,
    name: '',
    price: 1500000,
    stock: 50,
    rating: 4.8,
    position: 'tail'
  });
  const [formError, setFormError] = useState('');

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');

    if (!formData.name.trim()) {
      setFormError(lang === 'vi' ? 'Vui lòng nhập tên sản phẩm.' : 'Please enter product name.');
      return;
    }
    if (formData.price <= 0) {
      setFormError(lang === 'vi' ? 'Giá sản phẩm phải lớn hơn 0.' : 'Price must be greater than 0.');
      return;
    }
    if (formData.stock < 0) {
      setFormError(lang === 'vi' ? 'Tồn kho không được âm.' : 'Stock cannot be negative.');
      return;
    }
    if (formData.rating < 1.0 || formData.rating > 5.0) {
      setFormError(lang === 'vi' ? 'Đánh giá phải từ 1.0 đến 5.0 sao.' : 'Rating must be between 1.0 and 5.0.');
      return;
    }

    try {
      await onAddProduct(formData);
      setShowAddModal(false);
      setFormData({
        id: Math.floor(Math.random() * 800000) + 100000,
        name: '',
        price: 1500000,
        stock: 50,
        rating: 4.8,
        position: 'tail'
      });
    } catch (err: any) {
      setFormError(err.message || 'Error adding product.');
    }
  };

  const confirmDelete = async () => {
    if (showDeleteModal !== null) {
      await onDeleteProduct(showDeleteModal);
      setShowDeleteModal(null);
    }
  };

  const handleReload = async () => {
    setReloading(true);
    try {
      await onReloadCSV(reloadLimit);
    } finally {
      setReloading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Package className="w-5 h-5 text-cyan-400" />
            <span>{t.m1Title}</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">{t.m1Desc}</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow-md transition cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>{lang === 'vi' ? 'Thêm Sản Phẩm (Đầu/Đuôi)' : 'Add Product (Head/Tail)'}</span>
          </button>

          <button
            onClick={onCleanupMemory}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-rose-950/70 hover:bg-rose-900/80 border border-rose-800/60 text-rose-300 text-xs font-semibold transition cursor-pointer"
            title="Duyệt ngắt con trỏ prev/next và kích hoạt gc.collect()"
          >
            <RefreshCw className="w-4 h-4" />
            <span>{t.releaseMemory}</span>
          </button>
        </div>
      </div>

      {/* Educational Explanation Box (Defense Ready) */}
      <div className="p-4 rounded-xl bg-blue-950/30 border border-blue-800/40 text-xs space-y-1.5 text-blue-200">
        <div className="font-bold flex items-center gap-1.5 text-blue-300">
          <Info className="w-4 h-4 text-cyan-400 shrink-0" />
          <span>{t.howItWorks}</span>
        </div>
        <p className="leading-relaxed text-slate-300">
          {t.m1Explain}
        </p>
      </div>

      {/* CSV Reload Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-xl bg-slate-900/40 border border-slate-800 text-xs">
        <div className="flex items-center gap-2">
          <Database className="w-4 h-4 text-cyan-400" />
          <span className="text-slate-300 font-medium">{lang === 'vi' ? 'Quy mô dữ liệu nạp vào DLL:' : 'Dataset load size:'}</span>
          <select
            value={reloadLimit}
            onChange={(e) => setReloadLimit(parseInt(e.target.value))}
            className="bg-slate-800 border border-slate-700 rounded px-2.5 py-1 text-slate-100 font-mono text-xs"
          >
            <option value="10000">10,000 items</option>
            <option value="50000">50,000 items</option>
            <option value="100000">100,000 items (Full Scale)</option>
          </select>
          <button
            disabled={reloading}
            onClick={handleReload}
            className="flex items-center gap-1 px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 font-medium transition cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${reloading ? 'animate-spin' : ''}`} />
            <span>{reloading ? (lang === 'vi' ? 'Đang nạp...' : 'Loading...') : (lang === 'vi' ? 'Nạp lại CSV' : 'Reload CSV')}</span>
          </button>
        </div>

        <div className="flex items-center gap-2 text-slate-400">
          <span>{lang === 'vi' ? 'Số dòng / trang:' : 'Rows / page:'}</span>
          <select
            value={pageSize}
            onChange={(e) => {
              const sz = parseInt(e.target.value);
              setPageSize(sz);
              onPageChange(1, sz);
            }}
            className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-slate-100 font-mono text-xs"
          >
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
        </div>
      </div>

      {/* Main Table */}
      <div className="border border-slate-800 rounded-2xl overflow-hidden bg-slate-900/40 shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-800/80 text-slate-300 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Product ID</th>
                <th className="py-3 px-4">{lang === 'vi' ? 'Tên Sản Phẩm' : 'Product Name'}</th>
                <th className="py-3 px-4 text-right">{lang === 'vi' ? 'Đơn Giá (VND)' : 'Price (VND)'}</th>
                <th className="py-3 px-4 text-center">{lang === 'vi' ? 'Tồn Kho' : 'Stock'}</th>
                <th className="py-3 px-4 text-center">{lang === 'vi' ? 'Đánh Giá' : 'Rating'}</th>
                <th className="py-3 px-4 text-center">{lang === 'vi' ? 'Thao Tác' : 'Actions'}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-slate-400">
                    <div className="flex items-center justify-center gap-2">
                      <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
                      <span>{lang === 'vi' ? 'Đang truy xuất trang từ Danh sách liên kết...' : 'Fetching page from Doubly Linked List...'}</span>
                    </div>
                  </td>
                </tr>
              ) : products.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-slate-500">
                    {t.emptyNotice}
                  </td>
                </tr>
              ) : (
                products.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-4 font-mono text-cyan-400 font-semibold">
                      #{p.id.toString().padStart(6, '0')}
                    </td>
                    <td className="py-3 px-4 font-medium text-slate-200 max-w-xs truncate">
                      {p.name}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-emerald-400 font-bold">
                      {p.price.toLocaleString()} ₫
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-medium font-mono ${
                        p.stock > 10 ? 'bg-emerald-950/70 text-emerald-400 border border-emerald-800/50' :
                        p.stock > 0 ? 'bg-amber-950/70 text-amber-400 border border-amber-800/50' :
                        'bg-rose-950/70 text-rose-400 border border-rose-800/50'
                      }`}>
                        {p.stock} {lang === 'vi' ? 'cái' : 'pcs'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center text-amber-400 font-semibold font-mono">
                      ★ {p.rating.toFixed(1)}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <button
                          onClick={() => onAddToCart(p)}
                          className="px-2.5 py-1 rounded bg-slate-800 hover:bg-cyan-950 hover:text-cyan-300 text-slate-300 text-[11px] font-medium border border-slate-700 transition cursor-pointer"
                        >
                          + {lang === 'vi' ? 'Giỏ Hàng' : 'Cart'}
                        </button>
                        <button
                          onClick={() => setShowDeleteModal(p.id)}
                          className="p-1.5 rounded bg-slate-800 hover:bg-rose-950 text-slate-400 hover:text-rose-400 border border-slate-700 transition cursor-pointer"
                          title="Xóa theo ID"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Server-Side Pagination Bar */}
        <div className="px-4 py-3 bg-slate-900/80 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-400">
          <div>
            <span>{lang === 'vi' ? 'Trang' : 'Page'} <strong className="text-white">{currentPage}</strong> / {totalPages} ({totalItems.toLocaleString()} nodes)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <button
              disabled={currentPage <= 1 || loading}
              onClick={() => onPageChange(1, pageSize)}
              className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300 font-mono transition cursor-pointer"
            >
              «
            </button>
            <button
              disabled={currentPage <= 1 || loading}
              onClick={() => onPageChange(currentPage - 1, pageSize)}
              className="p-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300 transition cursor-pointer"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-3 py-1 bg-slate-800/80 text-cyan-300 font-mono rounded border border-slate-700">
              {currentPage}
            </span>
            <button
              disabled={currentPage >= totalPages || loading}
              onClick={() => onPageChange(currentPage + 1, pageSize)}
              className="p-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300 transition cursor-pointer"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
            <button
              disabled={currentPage >= totalPages || loading}
              onClick={() => onPageChange(totalPages, pageSize)}
              className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300 font-mono transition cursor-pointer"
            >
              »
            </button>
          </div>
        </div>
      </div>

      {/* Add Product Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Plus className="w-4 h-4 text-cyan-400" />
                <span>{lang === 'vi' ? 'Thêm Sản Phẩm Mới Vào Kho (O(1))' : 'Insert Product to Doubly Linked List'}</span>
              </h3>
            </div>

            {formError && (
              <div className="p-2.5 rounded-lg bg-rose-950/80 border border-rose-800 text-rose-300 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{formError}</span>
              </div>
            )}

            <form onSubmit={handleFormSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Mã Định Danh (ID)</label>
                <input
                  type="number"
                  value={formData.id}
                  onChange={(e) => setFormData({ ...formData, id: parseInt(e.target.value) || 0 })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white font-mono"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">{lang === 'vi' ? 'Tên Sản Phẩm' : 'Product Name'}</label>
                <input
                  type="text"
                  placeholder="Sony WH-1000XM5 Wireless Headphones"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">{lang === 'vi' ? 'Đơn Giá (VND)' : 'Price'}</label>
                  <input
                    type="number"
                    value={formData.price}
                    onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white font-mono"
                    required
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">{lang === 'vi' ? 'Số Lượng Tồn' : 'Stock'}</label>
                  <input
                    type="number"
                    value={formData.stock}
                    onChange={(e) => setFormData({ ...formData, stock: parseInt(e.target.value) || 0 })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white font-mono"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">{lang === 'vi' ? 'Đánh Giá (1.0 - 5.0)' : 'Rating'}</label>
                  <input
                    type="number"
                    step="0.1"
                    min="1.0"
                    max="5.0"
                    value={formData.rating}
                    onChange={(e) => setFormData({ ...formData, rating: parseFloat(e.target.value) || 4.5 })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white font-mono"
                    required
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">{lang === 'vi' ? 'Vị Trí Chèn O(1)' : 'Insert Position'}</label>
                  <select
                    value={formData.position}
                    onChange={(e) => setFormData({ ...formData, position: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white"
                  >
                    <option value="head">HEAD (Đầu danh sách)</option>
                    <option value="tail">TAIL (Cuối danh sách)</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium cursor-pointer"
                >
                  {lang === 'vi' ? 'Hủy' : 'Cancel'}
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold cursor-pointer"
                >
                  {lang === 'vi' ? 'Xác Nhận Thêm' : 'Insert Product'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal !== null && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-sm w-full shadow-2xl space-y-4">
            <div className="flex items-center gap-3 text-rose-400">
              <AlertTriangle className="w-6 h-6 shrink-0" />
              <h3 className="text-base font-bold text-white">
                {lang === 'vi' ? 'Xác Nhận Xóa Sản Phẩm' : 'Confirm Deletion'}
              </h3>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              {lang === 'vi'
                ? `Bạn có chắc muốn xóa vĩnh viễn sản phẩm #${showDeleteModal} khỏi Danh sách liên kết đôi không? Thao tác này sẽ tách con trỏ prev và next khỏi chuỗi.`
                : `Are you sure you want to delete product #${showDeleteModal} from the Doubly Linked List?`}
            </p>
            <div className="flex justify-end gap-2 pt-2 border-t border-slate-800 text-xs">
              <button
                onClick={() => setShowDeleteModal(null)}
                className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium cursor-pointer"
              >
                {lang === 'vi' ? 'Hủy Bỏ' : 'Cancel'}
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-bold cursor-pointer"
              >
                {lang === 'vi' ? 'Xóa Nút (Unlink)' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

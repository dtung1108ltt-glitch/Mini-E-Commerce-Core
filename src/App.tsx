import React, { useState, useEffect } from 'react';
import {
  Package, ShoppingCart, GitBranch, ArrowUpDown, Search, BarChart3,
  Cpu, Database, RefreshCw, Globe, Home
} from 'lucide-react';
import { translations, Language } from '../ui/src/translations';
import { Dashboard } from '../ui/src/components/Dashboard';
import { Module1Inventory } from '../ui/src/components/Module1Inventory';
import { Module2Cart } from '../ui/src/components/Module2Cart';
import { Module3Index } from '../ui/src/components/Module3Index';
import { Module4SortFilter } from '../ui/src/components/Module4SortFilter';
import { Module5Search } from '../ui/src/components/Module5Search';
import { BenchmarksPage } from '../ui/src/components/BenchmarksPage';
import { MemoryPage } from '../ui/src/components/MemoryPage';

export default function App() {
  const [lang, setLang] = useState<Language>('vi'); // Vietnamese default per requirement
  const [activeTab, setActiveTab] = useState<string>('dashboard');

  // Global system status
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [loadingAction, setLoadingAction] = useState(false);

  // Module 1: Catalog
  const [products, setProducts] = useState<any[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(100000);
  const [loadingCatalog, setLoadingCatalog] = useState(false);

  // Module 2: Cart & Checkout
  const [cartItems, setCartItems] = useState<any[]>([]);
  const [cartTotal, setCartTotal] = useState(0);
  const [undoStackSize, setUndoStackSize] = useState(0);
  const [undoHistory, setUndoHistory] = useState<any[]>([]);
  const [checkoutQueue, setCheckoutQueue] = useState<any[]>([]);
  const [orderLogs, setOrderLogs] = useState<any[]>([]);
  const [customerName, setCustomerName] = useState('Nguyen Van A');

  // Module 3: Trees
  const [treeStats, setTreeStats] = useState<any>(null);

  // Benchmarks
  const [charts, setCharts] = useState<any[]>([]);

  const t = translations[lang];

  useEffect(() => {
    fetchSystemStatus();
    loadCatalog(1, 20);
    fetchCart();
    fetchCheckoutStatus();
    loadTreeStats();
    loadCharts();
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const res = await fetch('/api/system/status');
      const data = await res.json();
      setSystemStatus(data);
    } catch (e) {
      console.error(e);
    }
  };

  const loadCatalog = async (page: number, size = 20) => {
    setLoadingCatalog(true);
    try {
      const res = await fetch(`/api/catalog?page=${page}&pageSize=${size}`);
      const data = await res.json();
      if (data && data.items) {
        setProducts(data.items);
        setCurrentPage(data.page);
        setTotalPages(data.total_pages);
        setTotalItems(data.total_items);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingCatalog(false);
    }
  };

  const handleAddProduct = async (prod: any) => {
    const res = await fetch('/api/catalog/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(prod),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to add product');
    }
    loadCatalog(currentPage);
    fetchSystemStatus();
  };

  const handleDeleteProduct = async (id: number) => {
    const res = await fetch(`/api/catalog/${id}`, { method: 'DELETE' });
    if (!res.ok) {
      throw new Error('Failed to delete product');
    }
    loadCatalog(currentPage);
    fetchSystemStatus();
  };

  const handleCleanupMemory = async () => {
    const res = await fetch('/api/catalog/cleanup', { method: 'POST' });
    const data = await res.json();
    fetchSystemStatus();
    loadCatalog(1);
    return data;
  };

  const handleReloadCSV = async (limit: number) => {
    setLoadingAction(true);
    try {
      await fetch(`/api/catalog/reload?limit=${limit}`, { method: 'POST' });
      loadCatalog(1);
      fetchSystemStatus();
      loadTreeStats();
    } finally {
      setLoadingAction(false);
    }
  };

  // Cart & Checkout
  const fetchCart = async () => {
    try {
      const res = await fetch('/api/cart');
      const data = await res.json();
      setCartItems(data.items || []);
      setCartTotal(data.totalAmount || 0);
      setUndoStackSize(data.undoStackSize || 0);
      setUndoHistory(data.undoHistory || []);
    } catch (e) {
      console.error(e);
    }
  };

  const handleAddToCart = async (prod: any) => {
    await fetch('/api/cart/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: prod.id, name: prod.name, price: prod.price, stock: prod.stock, quantity: 1 }),
    });
    fetchCart();
    fetchSystemStatus();
  };

  const handleRemoveFromCart = async (id: number) => {
    await fetch('/api/cart/remove', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id }),
    });
    fetchCart();
    fetchSystemStatus();
  };

  const handleUndoRemove = async () => {
    const res = await fetch('/api/cart/undo', { method: 'POST' });
    if (!res.ok) {
      alert(lang === 'vi' ? 'Ngăn xếp hoàn tác rỗng!' : 'Undo stack is empty!');
      return;
    }
    fetchCart();
    fetchSystemStatus();
  };

  const fetchCheckoutStatus = async () => {
    try {
      const res = await fetch('/api/checkout/status');
      const data = await res.json();
      setCheckoutQueue(data.queue || []);
      setOrderLogs(data.logs || []);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSubmitOrder = async () => {
    if (cartItems.length === 0) {
      alert(lang === 'vi' ? 'Giỏ hàng đang rỗng!' : 'Cart is empty!');
      return;
    }
    await fetch('/api/checkout/submit-order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ customerName }),
    });
    fetchCart();
    fetchCheckoutStatus();
    fetchSystemStatus();
  };

  const handleProcessNextOrder = async () => {
    await fetch('/api/checkout/process-next', { method: 'POST' });
    fetchCheckoutStatus();
    fetchSystemStatus();
    loadCatalog(currentPage);
  };

  const handleProcessAllOrders = async () => {
    await fetch('/api/checkout/process-all', { method: 'POST' });
    fetchCheckoutStatus();
    fetchSystemStatus();
    loadCatalog(currentPage);
  };

  const handleSimulateConcurrent = async (count: number) => {
    for (let i = 1; i <= count; i++) {
      const sampleItem = products[i % products.length] || { id: i, name: `Sample Product #${i}`, price: 100000, stock: 10 };
      await fetch('/api/cart/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...sampleItem, quantity: 1 }),
      });
      await fetch('/api/checkout/submit-order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customerName: `Khách Hàng Flash Sale #${i}` }),
      });
    }
    fetchCart();
    fetchCheckoutStatus();
    fetchSystemStatus();
  };

  // Trees
  const loadTreeStats = async () => {
    try {
      const res = await fetch('/api/tree/stats?count=10000');
      const data = await res.json();
      setTreeStats(data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSearchById = async (id: number) => {
    const res = await fetch(`/api/search/compare?id=${id}`);
    return await res.json();
  };

  const handleLoadTraversal = async (type: string, trav: string) => {
    const res = await fetch(`/api/tree/traversal?type=${type}&traversal=${trav}&limit=15`);
    return await res.json();
  };

  // Sorting
  const handleRunSortBenchmark = async (size: number) => {
    const res = await fetch('/api/sort/benchmark', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sample: size, by: 'price', ascending: true }),
    });
    return await res.json();
  };

  // Search
  const handleSearchName = async (name: string) => {
    const res = await fetch(`/api/search/name?q=${encodeURIComponent(name)}`);
    return await res.json();
  };

  const handleCompareSearch = async (id: number) => {
    const res = await fetch(`/api/search/compare?id=${id}`);
    return await res.json();
  };

  // Benchmarks
  const loadCharts = async () => {
    try {
      const res = await fetch('/api/benchmark/plots');
      const data = await res.json();
      setCharts(data.charts || []);
    } catch (e) {
      console.error(e);
    }
  };

  const handleRerunBenchmarks = async () => {
    await fetch('/api/benchmark/run', { method: 'POST' });
    await loadCharts();
  };

  // Quick Action demos
  const handleQuickBuildIndexes = async () => {
    setLoadingAction(true);
    try {
      await loadTreeStats();
      await fetch('/api/search/name?q=Sony');
      alert(lang === 'vi' ? 'Đã xây dựng xong chỉ mục BST, AVL và Bảng băm!' : 'Built BST, AVL, and Hash Table indexes!');
    } finally {
      setLoadingAction(false);
    }
  };

  const handleQuickRunDemo = async () => {
    setLoadingAction(true);
    try {
      await handleSimulateConcurrent(5);
      alert(lang === 'vi' ? 'Đã mô phỏng nạp 5 đơn hàng Flash Sale vào Hàng đợi FIFO!' : 'Injected 5 Flash Sale orders to FIFO queue!');
      setActiveTab('cart');
    } finally {
      setLoadingAction(false);
    }
  };

  const navItems = [
    { id: 'dashboard', label: t.navDashboard, icon: Home },
    { id: 'catalog', label: t.navCatalog, icon: Package },
    { id: 'cart', label: t.navCart, icon: ShoppingCart },
    { id: 'tree', label: t.navTree, icon: GitBranch },
    { id: 'sort', label: t.navSort, icon: ArrowUpDown },
    { id: 'search', label: t.navSearch, icon: Search },
    { id: 'benchmark', label: t.navBenchmarks, icon: BarChart3 },
    { id: 'memory', label: t.navMemory, icon: Cpu },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-black">
      {/* Top Main Navigation Bar */}
      <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-40 px-6 py-3.5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-tr from-cyan-600 to-blue-600 rounded-xl shadow-lg shadow-cyan-500/20">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-base font-extrabold tracking-tight bg-gradient-to-r from-cyan-400 via-sky-300 to-blue-400 bg-clip-text text-transparent">
              {t.appTitle}
            </h1>
            <p className="text-xs text-slate-400 flex items-center gap-2">
              <span>{t.appSubtitle}</span>
            </p>
          </div>
        </div>

        {/* Global Controls & Language Switch */}
        <div className="flex items-center gap-3">
          {/* Language Switch Button (Bonus) */}
          <button
            onClick={() => setLang(lang === 'vi' ? 'en' : 'vi')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold text-slate-200 transition cursor-pointer"
            title="Switch Language (Vietnamese / English)"
          >
            <Globe className="w-3.5 h-3.5 text-cyan-400" />
            <span>{lang === 'vi' ? 'Tiếng Việt (VI)' : 'English (EN)'}</span>
          </button>
        </div>
      </header>

      {/* Module Horizontal Nav Tabs */}
      <nav className="border-b border-slate-800 bg-slate-900/50 px-6 overflow-x-auto flex gap-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center gap-2 py-3 px-3.5 text-xs font-medium border-b-2 transition whitespace-nowrap cursor-pointer ${
                isActive
                  ? 'border-cyan-400 text-cyan-300 bg-slate-800/40 font-bold'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/20'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Main View Area */}
      <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
        {activeTab === 'dashboard' && (
          <Dashboard
            lang={lang}
            onNavigate={(tab) => setActiveTab(tab)}
            systemStatus={systemStatus}
            onReload100k={() => handleReloadCSV(100000)}
            onBuildIndexes={handleQuickBuildIndexes}
            onRunDemo={handleQuickRunDemo}
            onCleanupMemory={handleCleanupMemory}
            loadingAction={loadingAction}
          />
        )}

        {activeTab === 'catalog' && (
          <Module1Inventory
            lang={lang}
            products={products}
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={totalItems}
            loading={loadingCatalog}
            onPageChange={(page, sz) => loadCatalog(page, sz)}
            onAddProduct={handleAddProduct}
            onDeleteProduct={handleDeleteProduct}
            onAddToCart={handleAddToCart}
            onCleanupMemory={handleCleanupMemory}
            onReloadCSV={handleReloadCSV}
          />
        )}

        {activeTab === 'cart' && (
          <Module2Cart
            lang={lang}
            cartItems={cartItems}
            cartTotal={cartTotal}
            undoStackSize={undoStackSize}
            undoHistory={undoHistory}
            checkoutQueue={checkoutQueue}
            orderLogs={orderLogs}
            customerName={customerName}
            onCustomerNameChange={(name) => setCustomerName(name)}
            onRemoveFromCart={handleRemoveFromCart}
            onUndoRemove={handleUndoRemove}
            onSubmitOrder={handleSubmitOrder}
            onProcessNextOrder={handleProcessNextOrder}
            onProcessAllOrders={handleProcessAllOrders}
            onSimulateConcurrent={handleSimulateConcurrent}
          />
        )}

        {activeTab === 'tree' && (
          <Module3Index
            lang={lang}
            treeStats={treeStats}
            onRebuildIndexes={loadTreeStats}
            onSearchById={handleSearchById}
            onLoadTraversal={handleLoadTraversal}
          />
        )}

        {activeTab === 'sort' && (
          <Module4SortFilter
            lang={lang}
            onRunSortBenchmark={handleRunSortBenchmark}
          />
        )}

        {activeTab === 'search' && (
          <Module5Search
            lang={lang}
            onSearchName={handleSearchName}
            onCompareSearch={handleCompareSearch}
          />
        )}

        {activeTab === 'benchmark' && (
          <BenchmarksPage
            lang={lang}
            charts={charts}
            onRerunBenchmarks={handleRerunBenchmarks}
          />
        )}

        {activeTab === 'memory' && (
          <MemoryPage
            lang={lang}
            onCleanupMemory={handleCleanupMemory}
          />
        )}
      </main>
    </div>
  );
}

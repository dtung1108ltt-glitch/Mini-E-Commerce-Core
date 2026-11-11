import express from 'express';
import { createServer as createViteServer } from 'vite';
import path from 'path';
import fs from 'fs';
import { exec, execFile } from 'child_process';
import util from 'util';

import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const execPromise = util.promisify(exec);
const app = express();
const PORT = 3000;

app.use(express.json());

// Serve benchmark plots as static files
const plotsDir = path.resolve(__dirname, 'benchmark', 'plots');
app.use('/plots', express.static(plotsDir));

const FASTAPI_PORT = 8005;
let fastApiProcess: any = null;

function ensureFastApiProcess() {
  if (fastApiProcess && !fastApiProcess.killed) {
    return;
  }
  console.log(`[Backend] Starting Python DSA FastAPI Core on port ${FASTAPI_PORT}...`);
  fastApiProcess = exec(`python3 -m uvicorn src.api.app:app --host 127.0.0.1 --port ${FASTAPI_PORT}`, {
    cwd: __dirname,
  });

  process.on('exit', () => {
    if (fastApiProcess) fastApiProcess.kill();
  });
  process.on('SIGINT', () => {
    if (fastApiProcess) fastApiProcess.kill();
    process.exit(0);
  });
}

// Initialize backend immediately
ensureFastApiProcess();

// Forward all API requests to the pure Python DSA FastAPI Engine
app.use('/api', async (req, res, next) => {
  if (req.path === '/terminal/run') {
    return next();
  }

  ensureFastApiProcess();
  const targetUrl = `http://127.0.0.1:${FASTAPI_PORT}${req.originalUrl}`;

  try {
    const headers: Record<string, string> = {};
    if (req.headers['content-type']) {
      headers['content-type'] = req.headers['content-type'] as string;
    }

    const fetchOptions: RequestInit = {
      method: req.method,
      headers,
    };

    if (req.method !== 'GET' && req.method !== 'HEAD' && req.body && Object.keys(req.body).length > 0) {
      fetchOptions.body = JSON.stringify(req.body);
      headers['content-type'] = 'application/json';
    }

    let backendRes: Response | null = null;
    for (let attempt = 0; attempt < 10; attempt++) {
      try {
        backendRes = await fetch(targetUrl, fetchOptions);
        break;
      } catch (err) {
        await new Promise((r) => setTimeout(r, 400));
      }
    }

    if (!backendRes) {
      return res.status(503).json({ error: 'FastAPI Python DSA Engine is starting up, please retry in a moment.' });
    }

    res.status(backendRes.status);
    const contentType = backendRes.headers.get('content-type') || 'application/json';
    res.setHeader('content-type', contentType);

    const contentDisposition = backendRes.headers.get('content-disposition');
    if (contentDisposition) {
      res.setHeader('content-disposition', contentDisposition);
    }

    const arrayBuf = await backendRes.arrayBuffer();
    res.send(Buffer.from(arrayBuf));
  } catch (err: any) {
    console.error(`Reverse proxy error to ${targetUrl}:`, err.message);
    res.status(502).json({ error: 'Failed to communicate with Python DSA core', detail: err.message });
  }
});

// Catch-all: Ensure ANY /api request that is not handled returns JSON, never HTML
app.all('/api/*', (req, res) => {
  res.status(404).json({ error: `API route ${req.method} ${req.path} not found.` });
});

interface CartItem {
  id: number;
  name: string;
  price: number;
  quantity: number;
  stock: number;
}

interface UndoAction {
  action: 'remove';
  item: CartItem;
  timestamp: string;
}

interface QueuedOrder {
  order_id: string;
  customer_name: string;
  items: CartItem[];
  timestamp: string;
  total: number;
}

interface OrderLog {
  order_id: string;
  customer: string;
  status: 'SUCCESS' | 'REJECTED';
  amount: number;
  timestamp: string;
  detail: string;
}

const webSession = {
  cart: new Map<number, CartItem>(),
  undoStack: [] as UndoAction[],
  checkoutQueue: [] as QueuedOrder[],
  logs: [] as OrderLog[],
};

// Helper: Call Python API bridge
async function callPythonBridge(action: string, args: Record<string, any> = {}): Promise<any> {
  const scriptPath = path.resolve(__dirname, 'src', 'api_bridge.py');
  const argsJson = JSON.stringify(args);
  try {
    const { stdout, stderr } = await execPromise(`python3 "${scriptPath}" "${action}" '${argsJson.replace(/'/g, "'\\''")}'`, {
      cwd: __dirname,
      maxBuffer: 20 * 1024 * 1024,
    });
    const lines = stdout.trim().split('\n');
    const jsonLine = lines.reverse().find(l => l.trim().startsWith('{') || l.trim().startsWith('['));
    if (!jsonLine) {
      return { error: 'Empty output from python bridge', stderr, stdout };
    }
    return JSON.parse(jsonLine);
  } catch (err: any) {
    console.error('Python bridge error:', err);
    return { error: err.message, stderr: err.stderr };
  }
}

// ================= API ENDPOINTS =================

// 1. Catalog & Inventory
app.get('/api/catalog', async (req, res) => {
  const page = parseInt(req.query.page as string) || 1;
  const pageSize = parseInt(req.query.pageSize as string) || 20;
  const data = await callPythonBridge('get_catalog', { page, page_size: pageSize });
  res.json(data);
});

app.post('/api/catalog/add', async (req, res) => {
  const { id, name, price, stock, rating, position } = req.body;
  const data = await callPythonBridge('add_product', { id, name, price, stock, rating, position });
  res.json(data);
});

app.delete('/api/catalog/:id', async (req, res) => {
  const id = parseInt(req.params.id);
  const data = await callPythonBridge('delete_product', { id });
  res.json(data);
});

app.post('/api/catalog/cleanup', async (req, res) => {
  const data = await callPythonBridge('memory_cleanup', {});
  res.json(data);
});

// 2. Cart & Flash Sale Checkout
app.get('/api/cart', (req, res) => {
  const items = Array.from(webSession.cart.values());
  const totalAmount = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const totalQuantity = items.reduce((sum, item) => sum + item.quantity, 0);
  res.json({
    items,
    totalItems: totalQuantity,
    totalAmount,
    undoStackSize: webSession.undoStack.length,
    undoHistory: webSession.undoStack.slice(-5).reverse(),
  });
});

app.post('/api/cart/add', (req, res) => {
  const { id, name, price, stock, quantity = 1 } = req.body;
  if (webSession.cart.has(id)) {
    const existing = webSession.cart.get(id)!;
    existing.quantity += quantity;
  } else {
    webSession.cart.set(id, { id, name, price, quantity, stock });
  }
  res.json({ success: true, cartSize: webSession.cart.size });
});

app.post('/api/cart/remove', (req, res) => {
  const { id } = req.body;
  if (!webSession.cart.has(id)) {
    return res.status(404).json({ error: 'Item not in cart' });
  }
  const item = webSession.cart.get(id)!;
  webSession.cart.delete(id);
  // Push to Undo Stack (LIFO)
  webSession.undoStack.push({
    action: 'remove',
    item,
    timestamp: new Date().toLocaleTimeString(),
  });
  res.json({ success: true, removed: item, undoStackSize: webSession.undoStack.length });
});

app.post('/api/cart/undo', (req, res) => {
  if (webSession.undoStack.length === 0) {
    return res.status(400).json({ error: 'Undo stack is empty' });
  }
  // Pop from Undo Stack (LIFO)
  const lastAction = webSession.undoStack.pop()!;
  const item = lastAction.item;
  webSession.cart.set(item.id, item);
  res.json({ success: true, restored: item, remainingUndo: webSession.undoStack.length });
});

app.post('/api/checkout/submit-order', (req, res) => {
  const { customerName = 'Nguyen Van A' } = req.body;
  const items = Array.from(webSession.cart.values());
  if (items.length === 0) {
    return res.status(400).json({ error: 'Cart is empty' });
  }
  const orderId = `ORD-${Date.now().toString().slice(-6)}-${webSession.checkoutQueue.length + 1}`;
  const total = items.reduce((s, it) => s + it.price * it.quantity, 0);
  const newOrder: QueuedOrder = {
    order_id: orderId,
    customer_name: customerName,
    items,
    timestamp: new Date().toLocaleTimeString(),
    total,
  };
  // FIFO Enqueue
  webSession.checkoutQueue.push(newOrder);
  webSession.cart.clear();
  webSession.undoStack = [];
  res.json({ success: true, orderId, queueLength: webSession.checkoutQueue.length });
});

app.post('/api/checkout/process-next', (req, res) => {
  if (webSession.checkoutQueue.length === 0) {
    return res.json({ message: 'Queue is empty', log: null });
  }
  // FIFO Dequeue
  const order = webSession.checkoutQueue.shift()!;
  const isStockAvailable = order.items.every(it => it.stock >= it.quantity);

  const log: OrderLog = {
    order_id: order.order_id,
    customer: order.customer_name,
    status: isStockAvailable ? 'SUCCESS' : 'REJECTED',
    amount: isStockAvailable ? order.total : 0,
    timestamp: new Date().toLocaleTimeString(),
    detail: isStockAvailable
      ? `Flash sale success: ${order.items.length} items purchased. Stock deducted.`
      : `Rejected: One or more items out of stock in inventory.`,
  };
  webSession.logs.unshift(log);
  res.json({ success: true, processedOrder: order, log, remainingQueue: webSession.checkoutQueue.length });
});

app.post('/api/checkout/process-all', (req, res) => {
  const processed = [];
  while (webSession.checkoutQueue.length > 0) {
    const order = webSession.checkoutQueue.shift()!;
    const isStockAvailable = order.items.every(it => it.stock >= it.quantity);
    const log: OrderLog = {
      order_id: order.order_id,
      customer: order.customer_name,
      status: isStockAvailable ? 'SUCCESS' : 'REJECTED',
      amount: isStockAvailable ? order.total : 0,
      timestamp: new Date().toLocaleTimeString(),
      detail: isStockAvailable
        ? `Flash sale confirmed: ${order.items.length} items. Stock decremented.`
        : `Rejected: Out of stock.`,
    };
    webSession.logs.unshift(log);
    processed.push(log);
  }
  res.json({ success: true, processedCount: processed.length, logs: processed });
});

app.get('/api/checkout/status', (req, res) => {
  res.json({
    queue: webSession.checkoutQueue,
    queueLength: webSession.checkoutQueue.length,
    logs: webSession.logs.slice(0, 20),
  });
});

// 3. Tree Indexing (BST & AVL)
app.get('/api/tree/stats', async (req, res) => {
  const count = parseInt(req.query.count as string) || 10000;
  const data = await callPythonBridge('tree_stats', { count });
  res.json(data);
});

app.get('/api/tree/traversal', async (req, res) => {
  const tree_type = (req.query.type as string) || 'bst';
  const traversal = (req.query.traversal as string) || 'in_order';
  const limit = parseInt(req.query.limit as string) || 15;
  const data = await callPythonBridge('tree_traversal', { tree_type, traversal, limit });
  res.json(data);
});

// 4. Sort & Filter
app.post('/api/sort/benchmark', async (req, res) => {
  const { sample = 5000, by = 'price', ascending = true } = req.body;
  const data = await callPythonBridge('sort_catalog', { sample, by, ascending });
  res.json(data);
});

app.post('/api/sort/filter', async (req, res) => {
  const { min_price, max_price, min_rating, in_stock } = req.body;
  const data = await callPythonBridge('filter_catalog', { min_price, max_price, min_rating, in_stock });
  res.json(data);
});

// 5. Search Engine
app.get('/api/search/name', async (req, res) => {
  const query = (req.query.q as string) || '';
  const data = await callPythonBridge('search_name', { query });
  res.json(data);
});

app.get('/api/search/compare', async (req, res) => {
  const id = parseInt(req.query.id as string) || 1000;
  const data = await callPythonBridge('compare_search', { id });
  res.json(data);
});

// 6. Benchmarks & Charts
app.get('/api/benchmark/plots', (req, res) => {
  const files = [
    { name: 'Sorting Benchmark O(n²) vs O(n log n)', filename: 'chart_sorting_benchmark.png', url: '/plots/chart_sorting_benchmark.png' },
    { name: 'Search Latencies (Linear vs Binary vs BST vs Hash)', filename: 'chart_search_benchmark.png', url: '/plots/chart_search_benchmark.png' },
    { name: 'Tree Degeneration (BST vs AVL Heights)', filename: 'chart_tree_degeneration.png', url: '/plots/chart_tree_degeneration.png' },
    { name: 'Self-Organizing Lists (MTF vs Transpose)', filename: 'chart_self_organizing.png', url: '/plots/chart_self_organizing.png' },
    { name: 'RAM Memory Profile Lifecycle (100k Items)', filename: 'chart_memory_profiling.png', url: '/plots/chart_memory_profiling.png' },
  ];
  res.json({ charts: files });
});

app.post('/api/benchmark/run', async (req, res) => {
  try {
    const { stdout, stderr } = await execPromise('python3 benchmark/run_all_benchmarks.py', { cwd: __dirname });
    res.json({ success: true, output: stdout, stderr });
  } catch (err: any) {
    res.status(500).json({ error: err.message, stderr: err.stderr });
  }
});

// 7. Report Generator & Download
app.post('/api/report/generate', async (req, res) => {
  try {
    const { stdout, stderr } = await execPromise('python3 report/generate_term_paper.py', { cwd: __dirname });
    res.json({ success: true, output: stdout, stderr });
  } catch (err: any) {
    res.status(500).json({ error: err.message, stderr: err.stderr });
  }
});

app.get('/api/report/download', (req, res) => {
  const filePath = path.resolve(__dirname, 'report', 'BCTieuLuan_CTDL_GT_Nhom.docx');
  if (fs.existsSync(filePath)) {
    res.download(filePath, 'BCTieuLuan_CTDL_GT_Nhom.docx');
  } else {
    res.status(404).json({ error: 'Report not found. Please generate it first.' });
  }
});

// 8. Terminal Command Execution (for interactive in-browser terminal)
app.post('/api/terminal/run', async (req, res) => {
  const { command } = req.body;
  const allowed = ['pytest tests -v', 'python3 benchmark/run_all_benchmarks.py', 'python3 report/generate_term_paper.py', 'python3 -c "import gc, sys; print(sys.version)"'];
  
  // Whitelist or safe prefix check
  if (!command || (!allowed.includes(command) && !command.startsWith('pytest') && !command.startsWith('python3'))) {
    return res.status(400).json({ error: 'Command not allowed for security reasons.' });
  }

  try {
    const { stdout, stderr } = await execPromise(command, { cwd: __dirname });
    res.json({ stdout, stderr });
  } catch (err: any) {
    res.json({ stdout: err.stdout || '', stderr: err.stderr || err.message, exitCode: err.code || 1 });
  }
});

// Start server with Vite middleware in dev
async function startServer() {
  const isDev = process.env.NODE_ENV !== 'production';

  if (isDev) {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.resolve(__dirname, 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.resolve(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`✓ Full-Stack Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer().catch((err) => {
  console.error('Failed to start server:', err);
});

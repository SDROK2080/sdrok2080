// GovData Analyzer Frontend Engine
let currentView = 'dashboard';
let currentDatasetId = null;
let currentDatasetData = null;
let currentScrapeResult = null;
let currentApiResult = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  loadDashboardData();
  loadSourcesDirectory();
  loadDatasetsList();
});

// Navigation Controller
function setupNavigation() {
  const links = document.querySelectorAll('[data-view]');
  links.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const viewName = link.getAttribute('data-view');
      navigateTo(viewName);
    });
  });
}

function navigateTo(viewName) {
  currentView = viewName;
  document.querySelectorAll('.view-section').forEach(sec => sec.classList.add('hidden'));
  const activeSec = document.getElementById(`view-${viewName}`);
  if (activeSec) {
    activeSec.classList.remove('hidden');
  }

  // Update nav link styles
  document.querySelectorAll('[data-view]').forEach(l => {
    if (l.getAttribute('data-view') === viewName) {
      l.classList.add('bg-blue-50', 'text-blue-700', 'font-semibold', 'dark:bg-blue-900/30', 'dark:text-blue-400');
      l.classList.remove('text-slate-600', 'hover:bg-slate-100');
    } else {
      l.classList.remove('bg-blue-50', 'text-blue-700', 'font-semibold', 'dark:bg-blue-900/30', 'dark:text-blue-400');
      l.classList.add('text-slate-600', 'hover:bg-slate-100');
    }
  });

  // Action hooks
  if (viewName === 'dashboard') loadDashboardData();
  if (viewName === 'sources') loadSourcesDirectory();
  if (viewName === 'datasets') loadDatasetsList();
  if (viewName === 'clean' && currentDatasetId) loadCleaningDataset();
  if (viewName === 'analyze' && currentDatasetId) runAnalysis();
  if (viewName === 'visualize' && currentDatasetId) setupVisualizationSelectors();
  if (viewName === 'reports' && currentDatasetId) generateReportPreview();
}

// Toast Notification
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  const bg = type === 'success' ? 'bg-emerald-600' : type === 'error' ? 'bg-rose-600' : 'bg-slate-800';
  toast.className = `fixed bottom-5 right-5 z-50 text-white px-5 py-3 rounded-lg shadow-xl text-sm font-medium flex items-center gap-2 transform transition-all duration-300 translate-y-5 opacity-0 ${bg}`;
  toast.innerHTML = `<span>${message}</span>`;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.classList.remove('translate-y-5', 'opacity-0');
  }, 10);
  setTimeout(() => {
    toast.classList.add('translate-y-5', 'opacity-0');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// 1. Dashboard
async function loadDashboardData() {
  try {
    const res = await fetch('/api/dashboard/summary');
    const data = await res.json();
    document.getElementById('metric-total-datasets').textContent = data.total_datasets || 0;
    document.getElementById('metric-total-records').textContent = (data.total_records || 0).toLocaleString();
    document.getElementById('metric-total-reports').textContent = data.total_reports || 0;

    // Render Recent Datasets
    const recentTable = document.getElementById('dashboard-recent-datasets');
    if (data.recent_imports && data.recent_imports.length > 0) {
      recentTable.innerHTML = data.recent_imports.map(d => `
        <tr class="hover:bg-slate-50 transition border-b border-slate-100">
          <td class="px-4 py-3 font-medium text-slate-800">${escapeHtml(d.name)}</td>
          <td class="px-4 py-3"><span class="px-2 py-0.5 rounded text-xs uppercase font-bold tracking-wider bg-slate-100 text-slate-700">${d.source_type}</span></td>
          <td class="px-4 py-3 text-slate-600">${(d.rows || 0).toLocaleString()}</td>
          <td class="px-4 py-3 text-slate-400 text-xs">${d.created_at}</td>
          <td class="px-4 py-3 text-right">
            <button onclick="selectDatasetAndNavigate(${d.id}, 'analyze')" class="text-blue-600 hover:text-blue-800 text-xs font-semibold">Explore &rarr;</button>
          </td>
        </tr>
      `).join('');
    } else {
      recentTable.innerHTML = `<tr><td colspan="5" class="p-6 text-center text-slate-400 text-sm">No datasets imported yet. Use Web Scraper, API, or File Import above.</td></tr>`;
    }

    // Render Recent Processing Activity
    const historyList = document.getElementById('dashboard-recent-history');
    if (data.recent_history && data.recent_history.length > 0) {
      historyList.innerHTML = data.recent_history.map(h => `
        <div class="flex items-start gap-3 py-2.5 border-b border-slate-100 last:border-0 text-sm">
          <div class="w-2 h-2 rounded-full bg-blue-500 mt-1.5 shrink-0"></div>
          <div class="flex-1">
            <div class="flex items-center justify-between">
              <span class="font-semibold text-slate-800">${escapeHtml(h.operation)}</span>
              <span class="text-xs text-slate-400">${h.created_at}</span>
            </div>
            <p class="text-xs text-slate-500 mt-0.5">${escapeHtml(h.details || '')}</p>
          </div>
        </div>
      `).join('');
    } else {
      historyList.innerHTML = `<p class="text-slate-400 text-xs text-center py-4">No audit logs available.</p>`;
    }
  } catch (err) {
    console.error("Dashboard error:", err);
  }
}

// 2. Sources Directory
async function loadSourcesDirectory() {
  try {
    const res = await fetch('/api/sources');
    const data = await res.json();
    const container = document.getElementById('sources-list-container');
    container.innerHTML = data.sources.map(src => `
      <div class="bg-white p-5 rounded-xl border border-slate-200 hover:shadow-md transition">
        <div class="flex items-start justify-between">
          <div>
            <h3 class="font-bold text-slate-800 text-base">${escapeHtml(src.name)}</h3>
            <span class="inline-block mt-1 px-2.5 py-0.5 text-xs font-medium rounded-full ${src.is_official ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-slate-100 text-slate-600'}">
              ${src.is_official ? '✓ Official Nepal Gov Portal' : 'Civil Data Portal'}
            </span>
          </div>
          <span class="text-xs font-medium text-slate-400">${src.country}</span>
        </div>
        <p class="text-slate-600 text-xs mt-3 leading-relaxed">${escapeHtml(src.description)}</p>
        <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
          <a href="${src.url}" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:underline flex items-center gap-1 font-medium">
            Visit Source <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
          </a>
          ${src.sample_dataset_file ? `
            <button onclick="loadSampleDataset('${src.sample_dataset_file.replace('.csv', '')}')" class="bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700 font-medium transition shadow-sm">
              Ingest Sample
            </button>
          ` : ''}
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error("Sources error:", err);
  }
}

async function loadSampleDataset(sampleName) {
  try {
    showToast("Ingesting verified Nepal public dataset...", "info");
    const res = await fetch(`/api/import/sample/${sampleName}`, { method: 'POST' });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to load sample");
    showToast("Dataset successfully added to workspace!", "success");
    currentDatasetId = data.dataset_id;
    navigateTo('datasets');
  } catch (err) {
    showToast(err.message, "error");
  }
}

// 3. Web Scraper
async function handleScrapeForm(e) {
  e.preventDefault();
  const url = document.getElementById('scrape-url-input').value.trim();
  const btn = document.getElementById('scrape-btn');
  const spinner = document.getElementById('scrape-spinner');
  const previewSec = document.getElementById('scrape-results-section');

  if (!url) {
    showToast("Please enter a valid URL.", "error");
    return;
  }

  try {
    btn.disabled = true;
    spinner.classList.remove('hidden');
    showToast("Analyzing website structure & respecting robots.txt...", "info");

    const res = await fetch('/api/scrape', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Scraping failed.");

    currentScrapeResult = data;
    renderScrapePreview(data);
    previewSec.classList.remove('hidden');
    showToast(`Found ${data.tables_found} tables and ${data.detected_data_links.length} public files!`, "success");
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    btn.disabled = false;
    spinner.classList.add('hidden');
  }
}

function renderScrapePreview(data) {
  document.getElementById('scrape-page-title').textContent = data.page_title || "Extracted Page";
  document.getElementById('scrape-page-url').textContent = data.url;
  document.getElementById('scrape-tables-count').textContent = data.tables_found;

  const container = document.getElementById('scrape-tables-container');
  if (data.tables && data.tables.length > 0) {
    container.innerHTML = data.tables.map((t, idx) => `
      <div class="border border-slate-200 rounded-lg p-4 bg-white shadow-sm mb-4">
        <div class="flex items-center justify-between mb-3">
          <h4 class="font-bold text-slate-800 text-sm">Table #${t.table_index + 1} (${t.total_rows} rows, ${t.headers.length} columns)</h4>
          <button onclick="saveScrapedTable(${idx})" class="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-xs font-semibold hover:bg-blue-700 shadow-sm">
            Save to Workspace
          </button>
        </div>
        <div class="overflow-x-auto max-h-60 border border-slate-100 rounded">
          <table class="min-w-full text-xs text-left text-slate-700 divide-y divide-slate-200">
            <thead class="bg-slate-50 sticky top-0">
              <tr>${t.headers.map(h => `<th class="px-3 py-2 font-semibold">${escapeHtml(h)}</th>`).join('')}</tr>
            </thead>
            <tbody class="divide-y divide-slate-100 bg-white">
              ${t.rows_sample.map(r => `
                <tr>${t.headers.map(h => `<td class="px-3 py-1.5 whitespace-nowrap">${escapeHtml(r[h] || '')}</td>`).join('')}</tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `).join('');
  } else {
    container.innerHTML = `<div class="p-6 text-center text-slate-400 text-sm">No tabular records found directly on page HTML. Check detected download links below.</div>`;
  }

  // Detected downloadable files
  const linksContainer = document.getElementById('scrape-detected-links');
  if (data.detected_data_links && data.detected_data_links.length > 0) {
    linksContainer.innerHTML = data.detected_data_links.map(l => `
      <div class="flex items-center justify-between py-2 border-b border-slate-100 text-xs">
        <span class="font-medium text-slate-700 truncate max-w-md">${escapeHtml(l.text)}</span>
        <button onclick="importFromScrapedUrl('${escapeHtml(l.url)}')" class="text-blue-600 hover:text-blue-800 font-bold ml-2 shrink-0">
          Download & Ingest &rarr;
        </button>
      </div>
    `).join('');
  } else {
    linksContainer.innerHTML = `<p class="text-xs text-slate-400">No public dataset links detected on this URL.</p>`;
  }
}

async function saveScrapedTable(tableIdx) {
  if (!currentScrapeResult || !currentScrapeResult.tables[tableIdx]) return;
  const tbl = currentScrapeResult.tables[tableIdx];
  const title = prompt("Enter a name for this dataset:", `${currentScrapeResult.page_title} - Table ${tbl.table_index + 1}`);
  if (!title) return;

  try {
    showToast("Saving dataset to workspace...", "info");
    const res = await fetch('/api/scrape/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: currentScrapeResult.url,
        table_index: tbl.table_index,
        dataset_name: title,
        headers: tbl.headers,
        rows: tbl.all_rows
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to save table.");
    showToast("Dataset successfully saved!", "success");
    currentDatasetId = data.dataset_id;
    navigateTo('datasets');
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function importFromScrapedUrl(url) {
  try {
    showToast("Downloading and parsing government file...", "info");
    const res = await fetch('/api/import/url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_url: url })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Download failed.");
    showToast("File ingested into workspace!", "success");
    currentDatasetId = data.dataset_id;
    navigateTo('datasets');
  } catch (err) {
    showToast(err.message, "error");
  }
}

// 4. API Extractor
async function handleApiForm(e) {
  e.preventDefault();
  const url = document.getElementById('api-url-input').value.trim();
  const method = document.getElementById('api-method-select').value;
  const paramsRaw = document.getElementById('api-params-input').value.trim();
  const token = document.getElementById('api-token-input').value.trim();
  const saveToWs = document.getElementById('api-save-checkbox').checked;
  const dsName = document.getElementById('api-dataset-name').value.trim();

  let params = null;
  if (paramsRaw) {
    try {
      params = JSON.parse(paramsRaw);
    } catch {
      showToast("Invalid JSON in Query Parameters field.", "error");
      return;
    }
  }

  try {
    showToast("Querying API endpoint...", "info");
    const res = await fetch('/api/extract/api', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        endpoint_url: url,
        method: method,
        params: params,
        auth_token: token || null,
        dataset_name: dsName || null,
        save_dataset: saveToWs
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "API extraction failed.");

    currentApiResult = data;
    renderApiPreview(data);
    showToast(`Retrieved ${data.total_records} records!`, "success");
    if (data.dataset_id) {
      currentDatasetId = data.dataset_id;
      showToast("Dataset automatically registered in workspace!", "success");
    }
  } catch (err) {
    showToast(err.message, "error");
  }
}

function renderApiPreview(data) {
  const container = document.getElementById('api-results-preview');
  container.classList.remove('hidden');
  document.getElementById('api-total-records').textContent = data.total_records;
  document.getElementById('api-columns-count').textContent = data.columns.length;

  const tableHead = document.getElementById('api-table-head');
  const tableBody = document.getElementById('api-table-body');

  tableHead.innerHTML = `<tr>${data.columns.map(c => `<th class="px-3 py-2 font-semibold text-slate-700">${escapeHtml(c)}</th>`).join('')}</tr>`;
  tableBody.innerHTML = data.preview.map(row => `
    <tr class="hover:bg-slate-50 border-b border-slate-100">
      ${data.columns.map(c => `<td class="px-3 py-1.5 whitespace-nowrap text-slate-600">${escapeHtml(String(row[c] || ''))}</td>`).join('')}
    </tr>
  `).join('');
}

// 5. File Import
async function handleFileUpload(e) {
  e.preventDefault();
  const fileInput = document.getElementById('file-upload-input');
  const dsName = document.getElementById('file-dataset-name').value.trim();

  if (!fileInput.files || fileInput.files.length === 0) {
    showToast("Please select a file to upload.", "error");
    return;
  }

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  if (dsName) formData.append('dataset_name', dsName);

  try {
    showToast("Processing dataset file (OCR/Parsing)...", "info");
    const res = await fetch('/api/import/upload', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Upload failed.");

    showToast("File uploaded and parsed successfully!", "success");
    currentDatasetId = data.dataset_id;
    navigateTo('datasets');
  } catch (err) {
    showToast(err.message, "error");
  }
}

// 6. Datasets Workspace & History
async function loadDatasetsList() {
  try {
    const res = await fetch('/api/datasets');
    const data = await res.json();
    const container = document.getElementById('datasets-list-container');
    const selector = document.getElementById('global-dataset-selector');

    if (!data.datasets || data.datasets.length === 0) {
      container.innerHTML = `<div class="p-12 text-center text-slate-400 bg-white rounded-xl border border-slate-200">No datasets found. Import or scrape data to begin.</div>`;
      if (selector) selector.innerHTML = `<option value="">No datasets available</option>`;
      return;
    }

    // Populate global topbar dataset selector
    if (selector) {
      selector.innerHTML = data.datasets.map(d => `
        <option value="${d.id}" ${currentDatasetId === d.id ? 'selected' : ''}>${escapeHtml(d.name)} (${(d.total_rows || 0).toLocaleString()} rows)</option>
      `).join('');
      if (!currentDatasetId && data.datasets.length > 0) {
        currentDatasetId = data.datasets[0].id;
      }
    }

    container.innerHTML = data.datasets.map(d => `
      <div class="bg-white rounded-xl border ${currentDatasetId === d.id ? 'border-blue-500 ring-2 ring-blue-100' : 'border-slate-200'} p-5 hover:shadow-md transition">
        <div class="flex items-start justify-between">
          <div>
            <h3 class="font-bold text-slate-800 text-base flex items-center gap-2">
              ${escapeHtml(d.name)}
              ${d.is_cleaned ? '<span class="px-2 py-0.5 text-xs font-semibold rounded bg-amber-50 text-amber-700 border border-amber-200">Cleaned</span>' : '<span class="px-2 py-0.5 text-xs font-semibold rounded bg-slate-100 text-slate-600">Raw</span>'}
            </h3>
            <p class="text-xs text-slate-500 mt-1">${escapeHtml(d.description || 'Public government dataset')}</p>
          </div>
          <div class="flex items-center gap-1.5">
            <button onclick="exportDataset(${d.id}, 'csv')" title="Export CSV" class="p-1.5 hover:bg-slate-100 text-slate-600 rounded text-xs font-medium border border-slate-200">CSV</button>
            <button onclick="exportDataset(${d.id}, 'excel')" title="Export Excel" class="p-1.5 hover:bg-slate-100 text-slate-600 rounded text-xs font-medium border border-slate-200">XLSX</button>
            <button onclick="deleteDataset(${d.id})" title="Delete" class="p-1.5 hover:bg-rose-50 text-rose-600 rounded text-xs border border-rose-200">✕</button>
          </div>
        </div>

        <div class="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-slate-100 text-xs">
          <div><span class="text-slate-400 block">Total Records</span><span class="font-bold text-slate-700">${(d.total_rows || 0).toLocaleString()}</span></div>
          <div><span class="text-slate-400 block">Total Columns</span><span class="font-bold text-slate-700">${d.total_columns || 0}</span></div>
          <div><span class="text-slate-400 block">Source</span><span class="font-bold text-slate-700 uppercase">${d.source_type}</span></div>
        </div>

        <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
          <button onclick="selectDatasetAndNavigate(${d.id}, 'clean')" class="text-amber-600 hover:text-amber-700 font-semibold flex items-center gap-1">
            Data Cleaning &rarr;
          </button>
          <button onclick="selectDatasetAndNavigate(${d.id}, 'analyze')" class="text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1">
            Statistical Analysis &rarr;
          </button>
          <button onclick="selectDatasetAndNavigate(${d.id}, 'visualize')" class="text-indigo-600 hover:text-indigo-700 font-semibold flex items-center gap-1">
            Visual Charts &rarr;
          </button>
          <button onclick="selectDatasetAndNavigate(${d.id}, 'reports')" class="text-emerald-600 hover:text-emerald-700 font-semibold flex items-center gap-1">
            Report &rarr;
          </button>
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error("Datasets list error:", err);
  }
}

function selectDatasetAndNavigate(id, view) {
  currentDatasetId = id;
  const selector = document.getElementById('global-dataset-selector');
  if (selector) selector.value = id;
  navigateTo(view);
}

function handleGlobalDatasetChange(id) {
  currentDatasetId = parseInt(id);
  if (currentView === 'clean') loadCleaningDataset();
  if (currentView === 'analyze') runAnalysis();
  if (currentView === 'visualize') setupVisualizationSelectors();
  if (currentView === 'reports') generateReportPreview();
}

async function exportDataset(id, format) {
  window.open(`/api/datasets/${id}/export?format=${format}`, '_blank');
}

async function deleteDataset(id) {
  if (!confirm("Are you sure you want to delete this dataset?")) return;
  try {
    const res = await fetch(`/api/datasets/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error("Delete failed.");
    showToast("Dataset removed.", "info");
    if (currentDatasetId === id) currentDatasetId = null;
    loadDatasetsList();
    loadDashboardData();
  } catch (err) {
    showToast(err.message, "error");
  }
}

// 7. Data Cleaning Interface
async function loadCleaningDataset() {
  if (!currentDatasetId) return;
  try {
    const res = await fetch(`/api/datasets/${currentDatasetId}?page=1&page_size=25`);
    const data = await res.json();
    currentDatasetData = data;

    document.getElementById('clean-dataset-title').textContent = data.name;
    document.getElementById('clean-dataset-rows').textContent = data.total_rows.toLocaleString();
    document.getElementById('clean-dataset-cols').textContent = data.total_columns;

    // Populate Column Dropdowns in Cleaning UI
    const colOptions = data.columns.map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join('');
    document.getElementById('clean-fill-col').innerHTML = `<option value="">All Columns</option>` + colOptions;
    document.getElementById('clean-drop-col').innerHTML = colOptions;
    document.getElementById('clean-filter-col').innerHTML = colOptions;

    // Render Table Preview
    renderCleaningPreviewTable(data);

    // Render Cleaning Audit Logs
    const logContainer = document.getElementById('clean-history-logs');
    if (data.history && data.history.length > 0) {
      logContainer.innerHTML = data.history.map(h => `
        <div class="text-xs py-1.5 border-b border-slate-100 flex items-center justify-between">
          <span class="font-medium text-slate-700">${escapeHtml(h.operation)}: ${escapeHtml(h.details)}</span>
          <span class="text-slate-400">${h.created_at}</span>
        </div>
      `).join('');
    } else {
      logContainer.innerHTML = `<p class="text-xs text-slate-400 py-2">No cleaning operations applied yet.</p>`;
    }
  } catch (err) {
    console.error("Clean load error:", err);
  }
}

function renderCleaningPreviewTable(data) {
  const tableHead = document.getElementById('clean-table-head');
  const tableBody = document.getElementById('clean-table-body');

  tableHead.innerHTML = `<tr>${data.columns.map(c => `<th class="px-3 py-2 font-semibold text-slate-700">${escapeHtml(c)}</th>`).join('')}</tr>`;
  tableBody.innerHTML = data.rows.map(row => `
    <tr class="hover:bg-slate-50 border-b border-slate-100">
      ${data.columns.map(c => `<td class="px-3 py-1.5 whitespace-nowrap text-slate-600">${escapeHtml(String(row[c] || ''))}</td>`).join('')}
    </tr>
  `).join('');
}

async function applyCleanOperation(op) {
  if (!currentDatasetId) return;
  try {
    showToast("Applying cleaning transformation...", "info");
    const res = await fetch(`/api/datasets/${currentDatasetId}/clean`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ operations: [op] })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Cleaning error.");
    showToast("Operation applied successfully!", "success");
    loadCleaningDataset();
    loadDashboardData();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function resetCleaning() {
  if (!currentDatasetId) return;
  if (!confirm("Revert this dataset back to its original raw state?")) return;
  try {
    const res = await fetch(`/api/datasets/${currentDatasetId}/reset-cleaning`, { method: 'POST' });
    if (!res.ok) throw new Error("Reset failed.");
    showToast("Reverted to raw data.", "info");
    loadCleaningDataset();
  } catch (err) {
    showToast(err.message, "error");
  }
}

// 8. Statistical Analysis Engine
async function runAnalysis() {
  if (!currentDatasetId) return;
  try {
    showToast("Calculating comprehensive descriptive statistics...", "info");
    const res = await fetch(`/api/datasets/${currentDatasetId}/analyze`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Analysis failed.");

    // Fill Summary Cards
    document.getElementById('stat-total-records').textContent = data.summary.total_records.toLocaleString();
    document.getElementById('stat-num-cols').textContent = data.summary.numeric_columns_count;
    document.getElementById('stat-cat-cols').textContent = data.summary.categorical_columns_count;

    // Fill Column Statistics Table
    const tableBody = document.getElementById('stat-columns-table');
    tableBody.innerHTML = Object.values(data.column_statistics).map(s => `
      <tr class="hover:bg-slate-50 border-b border-slate-100">
        <td class="px-4 py-3 font-semibold text-slate-800">${escapeHtml(s.name)}</td>
        <td class="px-4 py-3"><span class="px-2 py-0.5 rounded text-xs uppercase font-bold ${s.type === 'numeric' ? 'bg-blue-50 text-blue-700' : 'bg-slate-100 text-slate-600'}">${s.type}</span></td>
        <td class="px-4 py-3 text-slate-600">${s.type === 'numeric' ? (s.mean ?? '-') : 'N/A'}</td>
        <td class="px-4 py-3 text-slate-600">${s.type === 'numeric' ? (s.median ?? '-') : 'N/A'}</td>
        <td class="px-4 py-3 text-slate-600">${s.type === 'numeric' ? (s.std ?? '-') : 'N/A'}</td>
        <td class="px-4 py-3 text-slate-600">${s.type === 'numeric' ? `${s.min} - ${s.max}` : 'N/A'}</td>
        <td class="px-4 py-3 text-slate-600">${s.unique_count}</td>
        <td class="px-4 py-3 ${s.missing_count > 0 ? 'text-amber-600 font-semibold' : 'text-slate-400'}">${s.missing_count} (${s.missing_pct}%)</td>
      </tr>
    `).join('');

    // Setup Group Aggregation Selectors
    const groupColSel = document.getElementById('agg-group-by');
    const aggTargetSel = document.getElementById('agg-target-col');

    groupColSel.innerHTML = data.summary.columns.map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join('');
    aggTargetSel.innerHTML = (data.summary.numeric_columns.length > 0 ? data.summary.numeric_columns : data.summary.columns)
      .map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join('');

    // If administrative column exists, default select it
    if (data.summary.detected_geo_columns.length > 0) {
      groupColSel.value = data.summary.detected_geo_columns[0];
    }
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function runGroupAggregation() {
  if (!currentDatasetId) return;
  const groupBy = document.getElementById('agg-group-by').value;
  const target = document.getElementById('agg-target-col').value;
  const func = document.getElementById('agg-func-select').value;

  try {
    const res = await fetch(`/api/datasets/${currentDatasetId}/aggregate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ group_by: groupBy, target_column: target, func: func })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Aggregation failed.");

    const tableBody = document.getElementById('agg-result-table');
    tableBody.innerHTML = data.result.map(row => `
      <tr class="hover:bg-slate-50 border-b border-slate-100">
        <td class="px-4 py-2 font-medium text-slate-800">${escapeHtml(String(row[groupBy]))}</td>
        <td class="px-4 py-2 font-bold text-blue-600">${(row[target] || 0).toLocaleString()}</td>
      </tr>
    `).join('');
  } catch (err) {
    showToast(err.message, "error");
  }
}

// 9. Interactive Visualizations (Plotly.js)
async function setupVisualizationSelectors() {
  if (!currentDatasetId) return;
  try {
    const res = await fetch(`/api/datasets/${currentDatasetId}?page=1&page_size=1`);
    const data = await res.json();

    const xSel = document.getElementById('viz-x-col');
    const ySel = document.getElementById('viz-y-col');
    const grpSel = document.getElementById('viz-group-col');

    const options = data.columns.map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join('');
    xSel.innerHTML = options;
    ySel.innerHTML = `<option value="">(None - Count frequency)</option>` + options;
    grpSel.innerHTML = `<option value="">(None)</option>` + options;

    if (data.columns.length > 1) {
      xSel.selectedIndex = 0;
      ySel.selectedIndex = 1;
    }

    renderInteractiveChart();
  } catch (err) {
    console.error("Viz setup error:", err);
  }
}

async function renderInteractiveChart() {
  if (!currentDatasetId) return;
  const chartType = document.getElementById('viz-chart-type').value;
  const xCol = document.getElementById('viz-x-col').value;
  const yCol = document.getElementById('viz-y-col').value;
  const groupCol = document.getElementById('viz-group-col').value;

  if (!xCol) return;

  try {
    const res = await fetch(`/api/datasets/${currentDatasetId}/chart`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chart_type: chartType,
        x_col: xCol,
        y_col: yCol || null,
        group_col: groupCol || null
      })
    });
    const spec = await res.json();
    if (!res.ok) throw new Error(spec.detail || "Chart rendering failed.");

    Plotly.newPlot('plotly-chart-container', spec.data, spec.layout, { responsive: true, displayModeBar: true });
  } catch (err) {
    showToast(err.message, "error");
  }
}

// 10. Automated Reporting Engine
async function generateReportPreview() {
  if (!currentDatasetId) return;
  try {
    showToast("Compiling analytical report findings...", "info");
    const res = await fetch(`/api/datasets/${currentDatasetId}/report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    const rep = await res.json();
    if (!res.ok) throw new Error(rep.detail || "Report generation failed.");

    document.getElementById('report-title-display').textContent = rep.report_title;
    document.getElementById('report-timestamp-display').textContent = rep.generated_at;
    document.getElementById('report-source-display').textContent = rep.source_url;
    document.getElementById('report-summary-text').textContent = rep.executive_summary;

    // Quality metrics
    document.getElementById('report-records-count').textContent = rep.total_records.toLocaleString();
    document.getElementById('report-integrity-score').textContent = rep.data_quality.integrity_score;
    document.getElementById('report-duplicate-count').textContent = rep.data_quality.duplicate_records;

    // Key findings
    const findingsList = document.getElementById('report-findings-list');
    findingsList.innerHTML = rep.key_findings.map(f => `
      <li class="flex items-start gap-2.5">
        <span class="text-blue-600 font-bold">•</span>
        <span class="text-slate-700">${escapeHtml(f)}</span>
      </li>
    `).join('');

    // Methodological limitations
    const limitationsList = document.getElementById('report-limitations-list');
    limitationsList.innerHTML = rep.limitations.map(l => `
      <li class="flex items-start gap-2.5">
        <span class="text-amber-500 font-bold">⚠</span>
        <span class="text-slate-600">${escapeHtml(l)}</span>
      </li>
    `).join('');

    // Recommendations
    const recsList = document.getElementById('report-recommendations-list');
    recsList.innerHTML = rep.recommendations.map(r => `
      <li class="flex items-start gap-2.5">
        <span class="text-emerald-600 font-bold">✓</span>
        <span class="text-slate-700 font-medium">${escapeHtml(r)}</span>
      </li>
    `).join('');

    showToast("Report generated successfully!", "success");
  } catch (err) {
    showToast(err.message, "error");
  }
}

function printAnalyticalReport() {
  window.print();
}

// Utility: HTML Escaping
function escapeHtml(text) {
  if (text === null || text === undefined) return '';
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

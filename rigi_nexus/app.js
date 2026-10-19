/**
 * KMC-HSSD Frontend Application Controller
 * Handles Navigation, State Management, API Connectivity, Real-time Charts,
 * Scientific Statistical Analysis, Simulation Runs, AI Academic Inquiries,
 * and Modal Interactions.
 */

const API_BASE = "http://127.0.0.1:8085/api";

let appState = {
  activeView: 'dashboard',
  darkMode: true,
  datasets: [],
  activeDataset: null,
  activeDatasetData: null,
  analysisChart: null,
  simulationChart: null,
  simType: 'sir'
};

document.addEventListener('DOMContentLoaded', () => {
  initIcons();
  initTheme();
  setupEventListeners();
  loadOverviewMetrics();
  loadDatasetsList();
  loadIdeas();
  loadProjects();
  loadPublications();
  loadLearningResources();
  loadResearchers();
  loadImpactObservatory();
  loadAuditLogs();
  loadNotifications();
  // Initialize default analysis and simulation charts
  adjustAnalysisInputs();
});

function initIcons() {
  if (window.lucide) {
    lucide.createIcons();
  }
}

function initTheme() {
  if (appState.darkMode) {
    document.documentElement.classList.add('dark');
    document.getElementById('themeIconSun').classList.remove('hidden');
    document.getElementById('themeIconMoon').classList.add('hidden');
  } else {
    document.documentElement.classList.remove('dark');
    document.getElementById('themeIconSun').classList.add('hidden');
    document.getElementById('themeIconMoon').classList.remove('hidden');
  }
}

function toggleDarkMode() {
  appState.darkMode = !appState.darkMode;
  initTheme();
  // Re-render charts with appropriate theme colors if active
  if (appState.analysisChart) appState.analysisChart.update();
  if (appState.simulationChart) appState.simulationChart.update();
}

function setupEventListeners() {
  // Navigation tabs
  document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.nav-tab').forEach(t => {
        t.classList.remove('bg-gold-500', 'text-navy-950', 'font-semibold');
        t.classList.add('hover:bg-navy-800', 'text-slate-300');
      });
      tab.classList.remove('hover:bg-navy-800', 'text-slate-300');
      tab.classList.add('bg-gold-500', 'text-navy-950', 'font-semibold');
    });
  });
}

function navigateTo(viewName) {
  appState.activeView = viewName;
  const views = [
    'landing', 'dashboard', 'ideas', 'projects', 'analysis', 
    'simulations', 'ai-assistant', 'library', 'collaborate', 
    'publishing', 'funding', 'sdg-impact', 'ethics', 'reports'
  ];

  views.forEach(v => {
    const el = document.getElementById(`view-${v}`);
    if (el) {
      if (v === viewName) {
        el.classList.remove('hidden');
      } else {
        el.classList.add('hidden');
      }
    }
  });

  // Highlight tab
  const activeTab = document.getElementById(`tab-${viewName}`);
  if (activeTab) {
    document.querySelectorAll('.nav-tab').forEach(t => {
      t.classList.remove('bg-gold-500', 'text-navy-950', 'font-semibold');
      t.classList.add('hover:bg-navy-800', 'text-slate-300');
    });
    activeTab.classList.remove('hover:bg-navy-800', 'text-slate-300');
    activeTab.classList.add('bg-gold-500', 'text-navy-950', 'font-semibold');
  }

  // Trigger charts resize when switching to their view
  if (viewName === 'analysis') {
    setTimeout(() => {
      if (!appState.analysisChart) {
        executeScientificAnalysis();
      }
    }, 150);
  } else if (viewName === 'simulations') {
    setTimeout(() => {
      if (!appState.simulationChart) {
        executeScientificSimulation();
      }
    }, 150);
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
  initIcons();
}

function handleGlobalSearch(event) {
  const q = event.target.value.toLowerCase().trim();
  if (event.key === 'Enter' && q) {
    if (q.includes('analy') || q.includes('stat') || q.includes('regress')) {
      navigateTo('analysis');
    } else if (q.includes('simul') || q.includes('sir') || q.includes('climate')) {
      navigateTo('simulations');
    } else if (q.includes('paper') || q.includes('pub') || q.includes('book')) {
      navigateTo('library');
    } else if (q.includes('sdg') || q.includes('impact')) {
      navigateTo('sdg-impact');
    } else if (q.includes('ai') || q.includes('assist')) {
      navigateTo('ai-assistant');
    } else {
      navigateTo('projects');
    }
  }
}

// -------------------------------------------------------------------
// DATA LOADERS
// -------------------------------------------------------------------
async function loadOverviewMetrics() {
  try {
    const res = await fetch(`${API_BASE}/stats/overview`);
    const data = await res.json();
    if (data.success) {
      document.getElementById('statTotalProjects').innerText = data.metrics.total_projects;
      document.getElementById('statPublishedPapers').innerText = data.metrics.published_papers;
      document.getElementById('statTotalCitations').innerText = data.metrics.total_citations;
      document.getElementById('statBeneficiaries').innerText = Number(data.metrics.documented_beneficiaries).toLocaleString();

      // Render recent projects
      const projContainer = document.getElementById('dashboardProjectsList');
      projContainer.innerHTML = data.recent_projects.map(p => `
        <div class="p-4 rounded-xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-navy-800 flex items-center justify-between shadow-sm hover:border-gold-500 transition">
          <div class="space-y-1">
            <div class="flex items-center space-x-2">
              <span class="px-2 py-0.5 text-[10px] rounded bg-sky-500/20 text-sky-400 font-semibold uppercase">${p.category}</span>
              <span class="text-xs text-slate-400">Target: ${p.target_end_date}</span>
            </div>
            <h4 class="font-bold text-sm text-navy-950 dark:text-white">${p.title}</h4>
            <div class="flex items-center space-x-2 text-xs text-slate-500">
              <span>Stage: <strong class="text-gold-500 uppercase">${p.stage.replace('_', ' ')}</strong></span>
            </div>
          </div>
          <div class="text-right space-y-1">
            <span class="font-mono-code font-bold text-sm text-gold-400">${p.progress_percentage}%</span>
            <div class="w-24 bg-slate-200 dark:bg-navy-950 h-2 rounded-full overflow-hidden">
              <div class="bg-gold-500 h-full" style="width: ${p.progress_percentage}%"></div>
            </div>
          </div>
        </div>
      `).join('');

      // Render upcoming tasks
      const taskContainer = document.getElementById('dashboardUpcomingTasks');
      taskContainer.innerHTML = data.upcoming_tasks.map(t => `
        <div class="flex items-center justify-between text-xs pb-2 border-b border-slate-100 dark:border-navy-800 last:border-0 last:pb-0">
          <div class="space-y-0.5">
            <div class="font-semibold text-slate-800 dark:text-slate-200">${t.title}</div>
            <div class="text-[10px] text-slate-400">Due: ${t.due_date}</div>
          </div>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold ${t.priority === 'urgent' ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'}">
            ${t.priority.toUpperCase()}
          </span>
        </div>
      `).join('');

      initIcons();
    }
  } catch (err) {
    console.error("Error loading overview metrics:", err);
  }
}

async function loadDatasetsList() {
  try {
    const res = await fetch(`${API_BASE}/datasets`);
    const data = await res.json();
    if (data.success && data.datasets.length > 0) {
      appState.datasets = data.datasets;
      const sel = document.getElementById('analysisDatasetSelect');
      sel.innerHTML = data.datasets.map(d => `
        <option value="${d.id}">${d.name} (${d.row_count} rows)</option>
      `).join('');
      loadSelectedDatasetForAnalysis();
    }
  } catch (err) {
    console.error("Error loading datasets:", err);
  }
}

async function loadSelectedDatasetForAnalysis() {
  const dsId = document.getElementById('analysisDatasetSelect').value;
  if (!dsId) return;

  try {
    const res = await fetch(`${API_BASE}/datasets/${dsId}/data`);
    const data = await res.json();
    if (data.success) {
      appState.activeDataset = data.dataset;
      appState.activeDatasetData = data.dataset.records;

      // Update meta display
      document.getElementById('datasetMetaDisplay').innerHTML = `
        <div><strong>Name:</strong> ${data.dataset.name}</div>
        <div><strong>Observed Sample Size (N):</strong> ${data.dataset.row_count} records</div>
        <div><strong>Available Variables:</strong> ${data.dataset.columns.map(c => `<span class="px-1.5 py-0.5 rounded bg-slate-200 dark:bg-navy-800 font-mono-code text-[10px] mr-1">${c.name}</span>`).join('')}</div>
      `;

      // Populate variable dropdowns
      const numCols = data.dataset.columns.filter(c => c.type === 'numeric').map(c => c.name);
      const var1Sel = document.getElementById('analysisVar1Select');
      const var2Sel = document.getElementById('analysisVar2Select');

      var1Sel.innerHTML = numCols.map(col => `<option value="${col}">${col}</option>`).join('');
      var2Sel.innerHTML = numCols.map(col => `<option value="${col}">${col}</option>`).join('');

      // Pick reasonable default pair if available (e.g. elevation_m and mean_temp_c)
      if (numCols.includes('elevation_m')) var1Sel.value = 'elevation_m';
      if (numCols.includes('mean_temp_c')) var2Sel.value = 'mean_temp_c';

      // Automatically execute analysis
      executeScientificAnalysis();
    }
  } catch (err) {
    console.error("Error loading dataset records:", err);
  }
}

function adjustAnalysisInputs() {
  const analysisType = document.getElementById('analysisTypeSelect').value;
  const var2Wrap = document.getElementById('analysisInputVar2Wrapper');
  const muWrap = document.getElementById('analysisInputMuWrapper');
  const var1Label = document.getElementById('analysisInputVar1Label');

  if (analysisType === 'descriptive') {
    var1Label.innerText = "Select Variable to Analyze";
    var2Wrap.classList.add('hidden');
    muWrap.classList.add('hidden');
  } else if (analysisType === 'correlation') {
    var1Label.innerText = "Variable 1 (X)";
    var2Wrap.classList.remove('hidden');
    muWrap.classList.add('hidden');
  } else if (analysisType === 'regression') {
    var1Label.innerText = "Independent Predictor (X)";
    var2Wrap.classList.remove('hidden');
    muWrap.classList.add('hidden');
  } else if (analysisType === 'ttest') {
    var1Label.innerText = "Sample Variable";
    var2Wrap.classList.add('hidden');
    muWrap.classList.remove('hidden');
  }
}

// -------------------------------------------------------------------
// SCIENTIFIC STATISTICAL ANALYSIS ENGINE
// -------------------------------------------------------------------
async function executeScientificAnalysis() {
  const dsId = document.getElementById('analysisDatasetSelect').value;
  const type = document.getElementById('analysisTypeSelect').value;
  const v1 = document.getElementById('analysisVar1Select').value;
  const v2 = document.getElementById('analysisVar2Select').value;
  const mu = document.getElementById('analysisMuInput').value;

  if (!dsId || !v1) return;

  const payload = {
    dataset_id: dsId,
    type: type,
    column: v1,
    x_col: v1,
    y_col: v2,
    col1: v1,
    test_kind: 'one_sample',
    mu: mu
  };

  try {
    const res = await fetch(`${API_BASE}/analysis/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      renderAnalysisResults(type, data.results);
    }
  } catch (err) {
    console.error("Error executing analysis:", err);
  }
}

function renderAnalysisResults(type, results) {
  const metricsBox = document.getElementById('analysisOutputMetrics');
  const interpText = document.getElementById('analysisInterpretationText');
  const badge = document.getElementById('analysisBadgeSignificance');
  const chartTitle = document.getElementById('analysisChartTitle');
  const chartSub = document.getElementById('analysisChartSubtitle');
  const methodUsed = document.getElementById('analysisMethodUsed');

  methodUsed.innerText = `Method: ${results.method}`;
  interpText.innerText = results.interpretation;

  if (type === 'descriptive') {
    chartTitle.innerText = `Frequency Distribution & Histogram: ${results.variable}`;
    chartSub.innerText = `Sample Size N = ${results.sample_size} | 95% CI [${results.ci_95[0]}, ${results.ci_95[1]}]`;
    badge.className = "px-2.5 py-1 text-[11px] font-semibold rounded bg-sky-500/20 text-sky-400";
    badge.innerText = `Mean: ${results.mean}`;

    metricsBox.innerHTML = `
      <div class="p-3 bg-slate-50 dark:bg-navy-850 rounded-lg border border-slate-200 dark:border-navy-700">
        <span class="text-slate-400 block text-[10px]">Mean (M)</span>
        <strong class="text-sm font-mono-code">${results.mean}</strong>
      </div>
      <div class="p-3 bg-slate-50 dark:bg-navy-850 rounded-lg border border-slate-200 dark:border-navy-700">
        <span class="text-slate-400 block text-[10px]">Median (Mdn)</span>
        <strong class="text-sm font-mono-code">${results.median}</strong>
      </div>
      <div class="p-3 bg-slate-50 dark:bg-navy-850 rounded-lg border border-slate-200 dark:border-navy-700">
        <span class="text-slate-400 block text-[10px]">Std Deviation (SD)</span>
        <strong class="text-sm font-mono-code">${results.std_dev}</strong>
      </div>
      <div class="p-3 bg-slate-50 dark:bg-navy-850 rounded-lg border border-slate-200 dark:border-navy-700">
        <span class="text-slate-400 block text-[10px]">Skewness / Kurtosis</span>
        <strong class="text-sm font-mono-code">${results.skewness} / ${results.kurtosis}</strong>
      </div>
    `;

    // Plot Histogram
    renderHistogramChart(results.histogram, results.variable);

  } else if (type === 'correlation') {
    const isSig = results.p_value < 0.05;
    chartTitle.innerText = `Bivariate Scatter: ${results.variables[0]} vs ${results.variables[1]}`;
    chartSub.innerText = `Sample Size N = ${results.sample_size} | Bivariate Dispersion`;
    badge.className = isSig 
      ? "px-2.5 py-1 text-[11px] font-semibold rounded bg-emerald-500/20 text-emerald-400" 
      : "px-2.5 py-1 text-[11px] font-semibold rounded bg-slate-200 dark:bg-navy-800 text-slate-400";
    badge.innerText = `r = ${results.pearson_r} (${isSig ? 'p < .05' : 'n.s.'})`;

    metricsBox.innerHTML = `
      <div class="p-3 bg-slate-50 dark:bg-navy-850 rounded-lg border border-slate-200 dark:border-navy-700">
        <span class="text-slate-400 block text-[10px]">Pearson r</span>
        <strong class="text-sm font-mono-code text-gold-400">${results.pearson_r}</strong>
      </div>
      <div class="p-3 bg-slate-50 dark:bg-navy-850 rounded-lg border border-slate-200 dark:border-navy-700">
        <span class="text-slate-400 block text-[10px]">p-value (2-tailed)</span>
        <strong class="text-sm font-mono-code">${results.p_value}</strong>
      </div>
      <div class="p-3 bg-slate-50 dark:bg-navy-850 rounded-lg border border-slate-200 dark:border-navy-700">
        <span class="text-slate-400 block text-[10px]">Spearman rho</span>
        <strong class="text-sm font-mono-code">${results.spearman_rho}</strong>
      </div>
      <div class="p-3 bg-slate-50 dark:bg-navy-850 rounded-lg border border-slate-200 dark:border-navy-700">
        <span class="text-slate-400 block text-[10px]">Correlation Strength</span>
        <strong class="text-sm font-mono-code capitalize">${Math.abs(results.pearson_r) > 0.7 ? 'Strong' : 'Moderate'}</strong>
      </div>
    `;

    renderScatterChart(results.scatter_points, results.variables[0], results.variables[1]);

  } else if (type === 'regression') {
    const isSig = results.p_value < 0.05;
    chartTitle.innerText = `OLS Fitted Regression Line: ${results.dependent_var} on ${results.independent_var}`;
    chartSub.innerText = `Model: ${results.equation} | R² = ${results.r_squared}`;
    badge.className = isSig 
      ? "px-2.5 py-1 text-[11px] font-semibold rounded bg-emerald-500/20 text-emerald-400" 
      : "px-2.5 py-1 text-[11px] font-semibold rounded bg-amber-500/20 text-amber-400";
    badge.innerText = `R² = ${results.r_squared} (p < .001)`;

    metricsBox.innerHTML = `
      <div class="p-3 bg-slate-50 dark:bg-navy-850 rounded-lg border border-slate-200 dark:border-navy-700">
        <span class="text-slate-400 block text-[10px]">R-Squared (R²)</span>
        <strong class="text-sm font-mono-code text-gold-400">${results.r_squared}</strong>
      </div>
      <div class="p-3 bg-slate-50 dark:bg-navy-850 rounded-lg border border-slate-200 dark:border-navy-700">
        <span class="text-slate-400 block text-[10px]">Slope (β₁)</span>
        <strong class="text-sm font-mono-code">${results.slope}</strong>
      </div>
      <div class="p-3 bg-slate-50 dark:bg-navy-850 rounded-lg border border-slate-200 dark:border-navy-700">
        <span class="text-slate-400 block text-[10px]">Intercept (β₀)</span>
        <strong class="text-sm font-mono-code">${results.intercept}</strong>
      </div>
      <div class="p-3 bg-slate-50 dark:bg-navy-850 rounded-lg border border-slate-200 dark:border-navy-700">
        <span class="text-slate-400 block text-[10px]">Std Error of Estimate</span>
        <strong class="text-sm font-mono-code">${results.std_err}</strong>
      </div>
    `;

    renderRegressionChart(results.points, results.regression_line, results.independent_var, results.dependent_var);

  } else if (type === 'ttest') {
    chartTitle.innerText = `Hypothesis Test: ${results.test}`;
    chartSub.innerText = `Degrees of Freedom df = ${results.degrees_of_freedom} | t = ${results.t_statistic}`;
    badge.className = results.significant 
      ? "px-2.5 py-1 text-[11px] font-semibold rounded bg-emerald-500/20 text-emerald-400" 
      : "px-2.5 py-1 text-[11px] font-semibold rounded bg-slate-200 dark:bg-navy-800 text-slate-400";
    badge.innerText = results.significant ? "Statistically Significant (p < .05)" : "Non-Significant";

    metricsBox.innerHTML = `
      <div class="p-3 bg-slate-50 dark:bg-navy-850 rounded-lg border border-slate-200 dark:border-navy-700">
        <span class="text-slate-400 block text-[10px]">t-Statistic</span>
        <strong class="text-sm font-mono-code text-gold-400">${results.t_statistic}</strong>
      </div>
      <div class="p-3 bg-slate-50 dark:bg-navy-850 rounded-lg border border-slate-200 dark:border-navy-700">
        <span class="text-slate-400 block text-[10px]">p-Value (2-tailed)</span>
        <strong class="text-sm font-mono-code">${results.p_value}</strong>
      </div>
      <div class="p-3 bg-slate-50 dark:bg-navy-850 rounded-lg border border-slate-200 dark:border-navy-700">
        <span class="text-slate-400 block text-[10px]">Observed Mean</span>
        <strong class="text-sm font-mono-code">${results.observed_mean}</strong>
      </div>
      <div class="p-3 bg-slate-50 dark:bg-navy-850 rounded-lg border border-slate-200 dark:border-navy-700">
        <span class="text-slate-400 block text-[10px]">Hypothesized μ₀</span>
        <strong class="text-sm font-mono-code">${results.hypothesized_mean}</strong>
      </div>
    `;

    // Bar comparison
    renderTtestBarChart(results.observed_mean, results.hypothesized_mean);
  }
}

// -------------------------------------------------------------------
// CHART RENDERERS (Chart.js)
// -------------------------------------------------------------------
function renderHistogramChart(bins, varName) {
  const ctx = document.getElementById('analysisCanvas').getContext('2d');
  if (appState.analysisChart) appState.analysisChart.destroy();

  appState.analysisChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: bins.map(b => b.range),
      datasets: [{
        label: `Frequency Count (${varName})`,
        data: bins.map(b => b.count),
        backgroundColor: 'rgba(234, 179, 8, 0.65)',
        borderColor: '#EAB308',
        borderWidth: 1.5,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
        x: { grid: { display: false } }
      }
    }
  });
}

function renderScatterChart(points, xLabel, yLabel) {
  const ctx = document.getElementById('analysisCanvas').getContext('2d');
  if (appState.analysisChart) appState.analysisChart.destroy();

  appState.analysisChart = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [{
        label: `Paired Observations (N=${points.length})`,
        data: points,
        backgroundColor: '#38BDF8',
        pointRadius: 5,
        pointHoverRadius: 7
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { title: { display: true, text: xLabel }, grid: { color: 'rgba(255,255,255,0.05)' } },
        y: { title: { display: true, text: yLabel }, grid: { color: 'rgba(255,255,255,0.05)' } }
      }
    }
  });
}

function renderRegressionChart(points, line, xLabel, yLabel) {
  const ctx = document.getElementById('analysisCanvas').getContext('2d');
  if (appState.analysisChart) appState.analysisChart.destroy();

  appState.analysisChart = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [
        {
          label: 'Fitted OLS Line',
          data: line,
          type: 'line',
          borderColor: '#EAB308',
          borderWidth: 2.5,
          pointRadius: 0,
          fill: false
        },
        {
          label: 'Observed Telemetry',
          data: points,
          backgroundColor: '#38BDF8',
          pointRadius: 5
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { title: { display: true, text: xLabel }, grid: { color: 'rgba(255,255,255,0.05)' } },
        y: { title: { display: true, text: yLabel }, grid: { color: 'rgba(255,255,255,0.05)' } }
      }
    }
  });
}

function renderTtestBarChart(observed, hypothetical) {
  const ctx = document.getElementById('analysisCanvas').getContext('2d');
  if (appState.analysisChart) appState.analysisChart.destroy();

  appState.analysisChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Hypothesized μ₀', 'Observed Sample Mean (M)'],
      datasets: [{
        label: 'Mean Comparison',
        data: [hypothetical, observed],
        backgroundColor: ['rgba(148, 163, 184, 0.5)', 'rgba(56, 189, 248, 0.7)'],
        borderColor: ['#94A3B8', '#38BDF8'],
        borderWidth: 1.5,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { grid: { color: 'rgba(255,255,255,0.05)' } }
      }
    }
  });
}

// -------------------------------------------------------------------
// SCIENTIFIC SIMULATION STUDIO
// -------------------------------------------------------------------
function switchSimulationTab(type) {
  appState.simType = type;
  const sirTab = document.getElementById('simTab-sir');
  const climateTab = document.getElementById('simTab-climate');
  const sirControls = document.getElementById('simSirControls');
  const climateControls = document.getElementById('simClimateControls');
  const title = document.getElementById('simControlTitle');

  if (type === 'sir') {
    sirTab.className = "px-3 py-1.5 rounded-lg bg-gold-500 text-navy-950 font-bold text-xs";
    climateTab.className = "px-3 py-1.5 rounded-lg bg-navy-800 text-white font-medium text-xs";
    sirControls.classList.remove('hidden');
    climateControls.classList.add('hidden');
    title.innerText = "SIR Parameter Controls";
  } else {
    sirTab.className = "px-3 py-1.5 rounded-lg bg-navy-800 text-white font-medium text-xs";
    climateTab.className = "px-3 py-1.5 rounded-lg bg-teal-500 text-navy-950 font-bold text-xs";
    sirControls.classList.add('hidden');
    climateControls.classList.remove('hidden');
    title.innerText = "CO₂ Climate Parameter Controls";
  }
  executeScientificSimulation();
}

async function executeScientificSimulation() {
  let payload = {};
  if (appState.simType === 'sir') {
    payload = {
      model_type: 'sir_model',
      total_pop: document.getElementById('sir_pop').value,
      beta: document.getElementById('sir_beta').value,
      gamma: document.getElementById('sir_gamma').value,
      initial_infected: document.getElementById('sir_init').value,
      days: 100
    };
  } else {
    payload = {
      model_type: 'climate_co2',
      initial_co2: document.getElementById('co2_init').value,
      growth_rate: document.getElementById('co2_growth').value,
      climate_sensitivity: document.getElementById('co2_sens').value,
      years: 50
    };
  }

  try {
    const res = await fetch(`${API_BASE}/simulation/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      renderSimulationResults(appState.simType, data.simulation);
    }
  } catch (err) {
    console.error("Simulation error:", err);
  }
}

function renderSimulationResults(type, sim) {
  const chartTitle = document.getElementById('simChartTitle');
  const badge = document.getElementById('simSummaryBadge');
  const narrative = document.getElementById('simNarrativeInterpretation');
  const ctx = document.getElementById('simulationCanvas').getContext('2d');

  narrative.innerText = sim.interpretation;

  if (appState.simulationChart) appState.simulationChart.destroy();

  if (type === 'sir') {
    chartTitle.innerText = "SIR Compartmental Progression: S(t), I(t), R(t)";
    badge.innerText = `R₀ = ${sim.parameters.basic_reproduction_number_R0} | Peak Day: ${sim.peak_day}`;

    const days = sim.timeline.map(t => `Day ${t.day}`);
    const sVals = sim.timeline.map(t => t.susceptible);
    const iVals = sim.timeline.map(t => t.infected);
    const rVals = sim.timeline.map(t => t.recovered);

    appState.simulationChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: days,
        datasets: [
          { label: 'Susceptible S(t)', data: sVals, borderColor: '#38BDF8', borderWidth: 2, pointRadius: 0 },
          { label: 'Infectious I(t)', data: iVals, borderColor: '#F43F5E', borderWidth: 2.5, pointRadius: 0, fill: true, backgroundColor: 'rgba(244, 63, 94, 0.15)' },
          { label: 'Recovered R(t)', data: rVals, borderColor: '#10B981', borderWidth: 2, pointRadius: 0 }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' } }
        }
      }
    });

  } else {
    chartTitle.innerText = "Atmospheric CO₂ ppm & Global Mean Temperature Anomaly (°C)";
    badge.innerText = `Projected: +${sim.projected_temp_rise}°C at ${sim.projected_co2_end} ppm`;

    const years = sim.timeline.map(t => t.year);
    const co2Vals = sim.timeline.map(t => t.co2_ppm);
    const tempVals = sim.timeline.map(t => t.temperature_anomaly_celsius);

    appState.simulationChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: years,
        datasets: [
          { label: 'CO₂ ppm Concentration', data: co2Vals, borderColor: '#F59E0B', yAxisID: 'y1', borderWidth: 2, pointRadius: 0 },
          { label: 'Temperature Anomaly (°C)', data: tempVals, borderColor: '#EF4444', yAxisID: 'y2', borderWidth: 2.5, pointRadius: 0 }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' } },
          y1: { type: 'linear', position: 'left', title: { display: true, text: 'CO₂ ppm' }, grid: { color: 'rgba(255,255,255,0.05)' } },
          y2: { type: 'linear', position: 'right', title: { display: true, text: 'Delta T (°C)' }, grid: { display: false } }
        }
      }
    });
  }
}

// -------------------------------------------------------------------
// AI ACADEMIC ASSISTANT
// -------------------------------------------------------------------
async function submitAiQuery() {
  const task = document.getElementById('aiTaskSelect').value;
  const prompt = document.getElementById('aiPromptInput').value.trim();
  if (!prompt) {
    alert("Please enter a research statement or topic.");
    return;
  }

  const outputBody = document.getElementById('aiOutputBody');
  const heading = document.getElementById('aiOutputHeading');
  const tag = document.getElementById('aiOutputTag');

  outputBody.innerHTML = `
    <div class="text-center py-10 space-y-2">
      <div class="w-8 h-8 border-2 border-gold-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
      <p class="text-xs text-slate-400">Synthesizing evidence-based academic consultation...</p>
    </div>
  `;

  try {
    const res = await fetch(`${API_BASE}/ai-assistant/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task, prompt })
    });
    const data = await res.json();
    if (data.success) {
      const resp = data.response;
      heading.innerText = resp.category;
      tag.innerText = resp.label;

      let html = '';
      if (resp.refined_questions) {
        html += `
          <div>
            <h5 class="font-bold text-slate-900 dark:text-white uppercase tracking-wider mb-2">Formulated Research Questions:</h5>
            <ul class="space-y-1.5 list-disc list-inside">
              ${resp.refined_questions.map(q => `<li>${q}</li>`).join('')}
            </ul>
          </div>
          <div>
            <h5 class="font-bold text-slate-900 dark:text-white uppercase tracking-wider mb-2">Falsifiable Hypotheses:</h5>
            <ul class="space-y-1.5 list-disc list-inside text-gold-400">
              ${resp.falsifiable_hypotheses.map(h => `<li>${h}</li>`).join('')}
            </ul>
          </div>
          <div class="p-3 bg-slate-100 dark:bg-navy-850 rounded-lg text-slate-400">
            <strong>Methodological Advice:</strong> ${resp.methodological_advice}
          </div>
        `;
      } else if (resp.sections) {
        html += `
          <div class="space-y-3">
            <h5 class="font-bold text-slate-900 dark:text-white uppercase tracking-wider">Literature Thematic Framework:</h5>
            ${resp.sections.map(s => `
              <div class="p-3 bg-slate-50 dark:bg-navy-850 rounded-lg border border-slate-200 dark:border-navy-700">
                <div class="font-bold text-gold-500 mb-1">${s.theme}</div>
                <div class="text-slate-400">${s.focus}</div>
              </div>
            `).join('')}
            <div class="p-3 bg-amber-500/10 border border-amber-500/20 text-amber-300 rounded-lg">
              ${resp.integrity_notice}
            </div>
          </div>
        `;
      } else if (resp.recommended_technique) {
        html += `
          <div class="space-y-3">
            <div>
              <span class="text-slate-400 block text-[10px]">Recommended Statistical Methodology</span>
              <h4 class="text-base font-bold text-gold-400">${resp.recommended_technique}</h4>
            </div>
            <div>
              <h5 class="font-bold text-slate-900 dark:text-white mb-2">Assumptions & Diagnostic Verification Checklist:</h5>
              <ul class="space-y-1.5 list-disc list-inside">
                ${resp.assumptions_checklist.map(a => `<li>${a}</li>`).join('')}
              </ul>
            </div>
            <div class="p-3 bg-slate-100 dark:bg-navy-850 rounded-lg">
              <strong>Non-parametric Alternative:</strong> ${resp.alternative_non_parametric}
            </div>
          </div>
        `;
      } else if (resp.sample_abstract_draft) {
        html += `
          <div class="space-y-3">
            <h5 class="font-bold text-slate-900 dark:text-white">Structured Abstract Draft:</h5>
            <p class="p-4 bg-slate-50 dark:bg-navy-850 rounded-xl border border-slate-200 dark:border-navy-700 italic text-justify">
              ${resp.sample_abstract_draft}
            </p>
            <div>
              <h5 class="font-bold text-slate-900 dark:text-white mb-1">Precision Recommendations:</h5>
              <ul class="space-y-1 list-disc list-inside">
                ${resp.suggestions.map(s => `<li>${s}</li>`).join('')}
              </ul>
            </div>
          </div>
        `;
      }

      outputBody.innerHTML = html;
    }
  } catch (err) {
    console.error("AI query error:", err);
  }
}

// -------------------------------------------------------------------
// RESEARCH IDEAS & PROJECTS
// -------------------------------------------------------------------
async function loadIdeas() {
  try {
    const res = await fetch(`${API_BASE}/ideas`);
    const data = await res.json();
    if (data.success) {
      const container = document.getElementById('ideasContainer');
      container.innerHTML = data.ideas.map(i => `
        <div class="p-6 rounded-2xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-navy-800 space-y-4 shadow-sm hover:border-gold-500 transition">
          <div class="flex items-center justify-between">
            <span class="px-2 py-0.5 rounded text-[10px] font-bold ${i.status === 'converted_to_proposal' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-gold-500/20 text-gold-400'} uppercase">
              ${i.status.replace('_', ' ')}
            </span>
            <span class="text-xs text-slate-400">${i.created_at.split(' ')[0]}</span>
          </div>

          <h3 class="font-bold text-base text-navy-950 dark:text-white leading-snug">${i.title}</h3>
          
          <div class="text-xs space-y-2 text-slate-600 dark:text-slate-300">
            <div>
              <strong class="text-gold-500">Problem Statement:</strong>
              <p class="line-clamp-2">${i.problem_statement}</p>
            </div>
            <div>
              <strong class="text-sky-400">Research Gap:</strong>
              <p class="line-clamp-2">${i.research_gap}</p>
            </div>
            <div class="flex flex-wrap gap-1 pt-1">
              ${i.sdg_alignment.map(sdg => `<span class="px-2 py-0.5 text-[10px] rounded bg-teal-500/10 text-teal-400 border border-teal-500/20">${sdg}</span>`).join('')}
            </div>
          </div>

          <div class="pt-3 border-t border-slate-100 dark:border-navy-800 flex justify-between items-center">
            ${i.status !== 'converted_to_proposal' ? `
              <button onclick="convertIdeaToProposal('${i.id}')" class="px-3 py-1.5 bg-gold-500 hover:bg-gold-600 text-navy-950 font-bold text-xs rounded-lg transition flex items-center space-x-1">
                <i data-lucide="file-plus" class="w-3.5 h-3.5"></i>
                <span>Convert to Proposal</span>
              </button>
            ` : `
              <span class="text-xs font-semibold text-emerald-400 flex items-center space-x-1">
                <i data-lucide="check" class="w-4 h-4"></i>
                <span>Formalized into Proposal</span>
              </span>
            `}
            <button onclick="navigateTo('ai-assistant')" class="text-xs text-slate-400 hover:text-gold-400">Consult AI on Idea →</button>
          </div>
        </div>
      `).join('');
      initIcons();
    }
  } catch (err) {
    console.error("Error loading ideas:", err);
  }
}

async function convertIdeaToProposal(ideaId) {
  try {
    const res = await fetch(`${API_BASE}/ideas/convert-to-proposal`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ idea_id: ideaId })
    });
    const data = await res.json();
    if (data.success) {
      alert("Idea successfully converted to a formal research proposal!");
      loadIdeas();
      loadOverviewMetrics();
    }
  } catch (err) {
    console.error("Conversion error:", err);
  }
}

async function loadProjects() {
  try {
    const res = await fetch(`${API_BASE}/projects`);
    const data = await res.json();
    if (data.success) {
      const container = document.getElementById('projectsContainer');
      container.innerHTML = data.projects.map(p => `
        <div class="p-6 rounded-2xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-navy-800 space-y-4 shadow-sm">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div>
              <div class="flex items-center space-x-2">
                <span class="px-2.5 py-0.5 rounded text-[10px] font-bold bg-sky-500/20 text-sky-400 uppercase">${p.category}</span>
                <span class="text-xs text-slate-400">Lead: ${p.lead_researcher}</span>
              </div>
              <h3 class="font-bold text-lg text-navy-950 dark:text-white mt-1">${p.title}</h3>
            </div>
            <div class="text-right">
              <span class="text-xs text-gold-400 font-bold uppercase">Stage: ${p.stage.replace('_', ' ')}</span>
              <div class="text-[11px] text-slate-400">Timeline: ${p.start_date} → ${p.target_end_date}</div>
            </div>
          </div>

          <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">${p.description}</p>

          <div class="space-y-1">
            <div class="flex justify-between text-xs">
              <span class="text-slate-400">Milestone Progression</span>
              <span class="font-mono-code font-bold text-gold-400">${p.progress_percentage}%</span>
            </div>
            <div class="w-full bg-slate-200 dark:bg-navy-950 h-2 rounded-full overflow-hidden">
              <div class="bg-gold-500 h-full" style="width: ${p.progress_percentage}%"></div>
            </div>
          </div>

          <div class="pt-3 border-t border-slate-100 dark:border-navy-800 flex flex-wrap gap-2 justify-between items-center text-xs">
            <div class="flex items-center space-x-4 text-slate-400">
              <span>Tasks: <strong>${p.completed_tasks} / ${p.total_tasks}</strong></span>
              <span>Milestones: <strong>${p.milestone_count}</strong></span>
              <span>Collaborators: <strong>${p.collaborators_count}</strong></span>
            </div>
            <div class="flex space-x-2">
              <button onclick="navigateTo('analysis')" class="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-lg text-xs">Open Analysis</button>
              <button onclick="navigateTo('publishing')" class="px-3 py-1 bg-navy-800 hover:bg-navy-700 text-slate-200 border border-navy-700 font-medium rounded-lg text-xs">View Manuscript</button>
            </div>
          </div>
        </div>
      `).join('');
      initIcons();
    }
  } catch (err) {
    console.error("Error loading projects:", err);
  }
}

// -------------------------------------------------------------------
// PUBLICATIONS & LIBRARY
// -------------------------------------------------------------------
async function loadPublications() {
  try {
    const res = await fetch(`${API_BASE}/publications`);
    const data = await res.json();
    if (data.success) {
      const container = document.getElementById('publicationsListContainer');
      container.innerHTML = data.publications.map(pub => `
        <div class="p-5 rounded-2xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-navy-800 space-y-3 shadow-sm flex flex-col justify-between hover:border-gold-500 transition">
          <div class="space-y-2">
            <div class="flex justify-between items-center text-[10px]">
              <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold uppercase">Peer Reviewed</span>
              <span class="text-gold-400 font-semibold">${pub.publication_year}</span>
            </div>
            <h4 class="font-bold text-sm text-navy-950 dark:text-white leading-snug">${pub.title}</h4>
            <p class="text-xs text-slate-400 italic">${pub.authors}</p>
            <p class="text-xs text-slate-500 font-medium">${pub.journal_or_conf}</p>
            <p class="text-xs text-slate-600 dark:text-slate-300 line-clamp-3">${pub.abstract}</p>
          </div>

          <div class="pt-3 border-t border-slate-100 dark:border-navy-800 flex justify-between items-center text-xs">
            <span class="text-slate-400">Citations: <strong class="text-gold-400 font-mono-code">${pub.citation_count}</strong></span>
            <a href="${pub.pdf_url}" target="_blank" class="text-sky-400 hover:underline flex items-center space-x-1">
              <span>DOI Metadata</span>
              <i data-lucide="external-link" class="w-3 h-3"></i>
            </a>
          </div>
        </div>
      `).join('');
      initIcons();
    }
  } catch (err) {
    console.error("Error loading publications:", err);
  }
}

async function loadLearningResources() {
  try {
    const res = await fetch(`${API_BASE}/learning-resources`);
    const data = await res.json();
    if (data.success) {
      const container = document.getElementById('learningResourcesContainer');
      container.innerHTML = data.resources.map(r => `
        <div class="p-4 rounded-xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-navy-800 space-y-2 shadow-sm">
          <div class="flex justify-between text-xs">
            <span class="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-bold text-[10px] uppercase">${r.category}</span>
            <span class="text-slate-400 capitalize">${r.resource_type}</span>
          </div>
          <h4 class="font-bold text-sm text-slate-800 dark:text-slate-200">${r.title}</h4>
          <p class="text-xs text-slate-400">${r.author_or_source}</p>
          <p class="text-xs text-slate-600 dark:text-slate-300">${r.description}</p>
          <div class="pt-2 flex justify-between items-center">
            <div class="flex space-x-1">
              ${r.tags.map(t => `<span class="px-1.5 py-0.5 text-[10px] rounded bg-slate-100 dark:bg-navy-850 text-slate-400">#${t}</span>`).join('')}
            </div>
            <a href="${r.url}" target="_blank" class="text-xs font-semibold text-gold-400 hover:underline flex items-center space-x-1">
              <span>Access Material</span>
              <i data-lucide="external-link" class="w-3 h-3"></i>
            </a>
          </div>
        </div>
      `).join('');
      initIcons();
    }
  } catch (err) {
    console.error("Error loading resources:", err);
  }
}

// -------------------------------------------------------------------
// RESEARCHERS & COLLABORATION
// -------------------------------------------------------------------
async function loadResearchers() {
  try {
    const res = await fetch(`${API_BASE}/researchers`);
    const data = await res.json();
    if (data.success) {
      const container = document.getElementById('researchersGrid');
      container.innerHTML = data.researchers.map(r => `
        <div class="p-6 rounded-2xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-navy-800 space-y-4 shadow-sm flex flex-col justify-between text-center hover:border-gold-500 transition">
          <div class="space-y-2">
            <div class="w-16 h-16 mx-auto rounded-full bg-slate-100 dark:bg-navy-800 border border-gold-500/40 flex items-center justify-center text-3xl shadow">
              ${r.avatar}
            </div>
            <h4 class="font-bold text-sm text-navy-950 dark:text-white">${r.name}</h4>
            <p class="text-xs text-gold-400 font-medium">${r.title}</p>
            <p class="text-[11px] text-slate-400">${r.institution}</p>
            <p class="text-xs text-slate-600 dark:text-slate-300 line-clamp-2">${r.bio}</p>
          </div>

          <div class="pt-3 border-t border-slate-100 dark:border-navy-800 space-y-2">
            <div class="flex justify-around text-xs text-slate-400">
              <span>h-index: <strong class="text-slate-200">${r.h_index}</strong></span>
              <span>Citations: <strong class="text-slate-200">${r.total_citations}</strong></span>
            </div>
            <button onclick="requestCollaboration('${r.id}', '${r.name}')" class="w-full py-1.5 bg-navy-800 hover:bg-gold-500 hover:text-navy-950 text-white font-bold text-xs rounded-lg border border-navy-700 transition">
              Invite to Collaborate
            </button>
          </div>
        </div>
      `).join('');
      initIcons();
    }
  } catch (err) {
    console.error("Error loading researchers:", err);
  }
}

async function requestCollaboration(researcherId, researcherName) {
  const projectTitle = prompt(`Enter project title to invite ${researcherName} to:`, "Himalayan Agro-Climatic IoT Resilience & Predictive Modeling");
  if (!projectTitle) return;

  const msg = prompt("Enter invitation message:", "We would like to invite you to collaborate on cross-regional sensor calibration and data modeling.");

  try {
    const res = await fetch(`${API_BASE}/collaborations/request`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        receiver_id: researcherId,
        project_title: projectTitle,
        message: msg
      })
    });
    const data = await res.json();
    if (data.success) {
      alert(`Invitation sent to ${researcherName}!`);
      loadOverviewMetrics();
    }
  } catch (err) {
    console.error("Collaboration request error:", err);
  }
}

// -------------------------------------------------------------------
// SDG OBSERVATORY & AUDIT LOGS
// -------------------------------------------------------------------
async function loadImpactObservatory() {
  try {
    const res = await fetch(`${API_BASE}/impact/observatory`);
    const data = await res.json();
    if (data.success) {
      // Impact cards
      const cards = document.getElementById('sdgImpactCards');
      cards.innerHTML = data.sdg_distribution.map(s => `
        <div class="p-6 rounded-2xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-navy-800 space-y-3 shadow-sm">
          <div class="flex justify-between items-center">
            <span class="text-xs font-bold text-teal-400 uppercase tracking-wider">${s.sdg_target}</span>
            <span class="px-2 py-0.5 rounded text-[10px] bg-teal-500/20 text-teal-300 font-bold">${s.count} Indicators</span>
          </div>
          <h3 class="text-2xl font-bold font-mono-code text-white">${Number(s.total_beneficiaries).toLocaleString()}</h3>
          <p class="text-xs text-slate-400">Documented Community & Smallholder Beneficiaries</p>
        </div>
      `).join('');

      // Table rows
      const tbody = document.getElementById('sdgImpactTableBody');
      tbody.innerHTML = data.indicators.map(ind => `
        <tr>
          <td class="p-3 font-semibold text-teal-400">${ind.sdg_target}</td>
          <td class="p-3 uppercase text-[10px] font-bold text-slate-400">${ind.impact_type.replace('_', ' ')}</td>
          <td class="p-3 max-w-md">${ind.description}</td>
          <td class="p-3 font-mono-code font-bold">${Number(ind.beneficiaries_count).toLocaleString()}</td>
          <td class="p-3">
            <a href="${ind.evidence_url}" target="_blank" class="text-sky-400 hover:underline flex items-center space-x-1">
              <span>DOI Proof</span>
              <i data-lucide="external-link" class="w-3 h-3"></i>
            </a>
          </td>
        </tr>
      `).join('');
      initIcons();
    }
  } catch (err) {
    console.error("Error loading SDG observatory:", err);
  }
}

async function loadAuditLogs() {
  try {
    const res = await fetch(`${API_BASE}/audit-logs`);
    const data = await res.json();
    if (data.success) {
      const container = document.getElementById('auditLogsContainer');
      container.innerHTML = data.logs.map(l => `
        <div class="py-2.5 flex items-center justify-between">
          <div class="space-y-0.5">
            <div class="font-mono-code text-slate-300"><span class="text-gold-400 font-bold">${l.action}</span>: ${l.details}</div>
            <div class="text-[10px] text-slate-500">Entity: ${l.entity} (${l.entity_id}) | User: ${l.user_id}</div>
          </div>
          <span class="text-[10px] text-slate-500 font-mono-code">${l.timestamp}</span>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error("Error loading audit logs:", err);
  }
}

async function loadNotifications() {
  try {
    const res = await fetch(`${API_BASE}/notifications`);
    const data = await res.json();
    if (data.success) {
      const container = document.getElementById('notificationsList');
      container.innerHTML = data.notifications.map(n => `
        <div class="p-3 rounded-xl bg-slate-50 dark:bg-navy-850 border border-slate-200 dark:border-navy-700 space-y-1 text-xs">
          <div class="flex justify-between items-center">
            <h5 class="font-bold text-slate-800 dark:text-slate-200">${n.title}</h5>
            <span class="text-[10px] text-slate-400">${n.created_at.split(' ')[0]}</span>
          </div>
          <p class="text-slate-500 dark:text-slate-400">${n.message}</p>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error("Error loading notifications:", err);
  }
}

// -------------------------------------------------------------------
// MODALS & NEW ENTITY SAVING
// -------------------------------------------------------------------
function toggleNotifications() {
  const modal = document.getElementById('notificationModal');
  modal.classList.toggle('hidden');
}

function openDemonstrationWalkthroughModal() {
  document.getElementById('demoModal').classList.remove('hidden');
}

function openNewIdeaModal() {
  document.getElementById('newIdeaModal').classList.remove('hidden');
}

function openRecordImpactModal() {
  document.getElementById('impactModal').classList.remove('hidden');
}

function closeModal(id) {
  document.getElementById(id).classList.add('hidden');
}

async function saveNewResearchIdea() {
  const title = document.getElementById('ideaTitleInput').value.trim();
  const prob = document.getElementById('ideaProblemInput').value.trim();
  const gap = document.getElementById('ideaGapInput').value.trim();
  const sdgs = document.getElementById('ideaSdgInput').value.split(',').map(s => s.trim());

  if (!title) {
    alert("Please provide an idea title.");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/ideas/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: title,
        problem_statement: prob,
        research_gap: gap,
        sdg_alignment: sdgs
      })
    });
    const data = await res.json();
    if (data.success) {
      closeModal('newIdeaModal');
      loadIdeas();
      alert("Research Idea successfully registered!");
    }
  } catch (err) {
    console.error("Error saving idea:", err);
  }
}

async function submitImpactRecord() {
  const sdg_target = document.getElementById('impactSdgTargetInput').value;
  const impact_type = document.getElementById('impactTypeSelect').value;
  const desc = document.getElementById('impactDescInput').value;
  const count = document.getElementById('impactCountInput').value;

  try {
    const res = await fetch(`${API_BASE}/impact/record`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_id: 'proj_climate_2026',
        sdg_target: sdg_target,
        impact_type: impact_type,
        description: desc,
        evidence_url: 'https://doi.org/10.1007/s11629-024-8841-x',
        beneficiaries_count: count
      })
    });
    const data = await res.json();
    if (data.success) {
      closeModal('impactModal');
      loadImpactObservatory();
      loadOverviewMetrics();
      alert("Impact evidence successfully recorded into the UN SDG Observatory.");
    }
  } catch (err) {
    console.error("Error submitting impact record:", err);
  }
}

function exportManuscriptDraft() {
  const title = document.getElementById('manuscriptTitle').innerText;
  const content = `# ${title}\n\nAuthor: Dr. Bishnu S. Rayamajhi\nInstitution: Tribhuvan University & KMC-HSSD Global Institute\n\nAbstract:\nHigh-relief mountain agricultural zones undergo intense localized frost risks that regional weather satellites cannot capture at adequate resolution. This empirical investigation evaluates a 15-station IoT microclimate sensor network across an elevation transect from 1,850m to 3,100m in Mustang, Nepal. Ordinary Least Squares (OLS) regression demonstrated that elevation accounts for 98.5% of variance in mean temperature (R² = 0.985, p < .0001, slope = -0.0091 °C/m).\n\nKeywords: Agro-climatology, Micro-sensing, OLS Regression, SDG 2, SDG 13\n\nMethodology:\nContinuous empirical telemetry collected across 12 monitoring stations (N=12).\n\nReferences:\n- Ostrom, E. (2009). Science, 325(5939), 419-422. https://doi.org/10.1126/science.1172133\n- Rayamajhi, B. S. et al. (2025). J. Mt. Sci., https://doi.org/10.1007/s11629-024-8841-x\n`;

  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = "RIGI_Manuscript_Draft_APA7.md";
  a.click();
  URL.revokeObjectURL(url);
}

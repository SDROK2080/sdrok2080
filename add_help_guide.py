import os
import re

# Read RIGI_Nexus_Platform.html
with open('RIGI_Nexus_Platform.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add "Help & Guide" button in the Top Header next to Theme Toggle / Notifications
help_header_button = """
          <!-- Step-by-Step Project Guide Help Button -->
          <button onclick="openHelpGuideModal()" class="px-3 py-1.5 rounded-lg bg-gradient-to-r from-amber-500 to-gold-500 hover:from-amber-600 hover:to-gold-600 text-navy-950 font-bold text-xs shadow-md flex items-center space-x-1.5 transition transform hover:scale-105" title="Step-by-Step Research Project Guide">
            <i data-lucide="help-circle" class="w-4 h-4"></i>
            <span class="hidden sm:inline">Project Guide &amp; Help</span>
          </button>
"""

# Also add a Help tab in the Navigation Tabs
help_nav_tab = """        <button onclick="openHelpGuideModal()" id="tab-help" class="nav-tab px-3 py-1.5 rounded-md hover:bg-navy-800 text-amber-300 hover:text-white flex items-center space-x-1.5 transition">
          <i data-lucide="help-circle" class="w-4 h-4 text-amber-400"></i>
          <span>Help &amp; Guide</span>
        </button>
"""

# Also add a Floating Help Action Button (FAB) at bottom-right
floating_help_fab = """
  <!-- Floating Help & Guide Action Button (FAB) -->
  <div class="fixed bottom-6 right-6 z-40">
    <button onclick="openHelpGuideModal()" class="group flex items-center space-x-2 px-4 py-3 bg-gradient-to-r from-gold-500 to-amber-500 hover:from-gold-600 hover:to-amber-600 text-navy-950 font-bold rounded-full shadow-2xl transition-all duration-300 transform hover:scale-105 border-2 border-white/20">
      <i data-lucide="help-circle" class="w-5 h-5 text-navy-950 animate-pulse"></i>
      <span class="text-xs font-extrabold tracking-wide uppercase">Step-by-Step Guide</span>
      <span class="hidden group-hover:inline-block text-[11px] bg-navy-950 text-gold-400 px-2 py-0.5 rounded-full font-semibold ml-1">11 Steps</span>
    </button>
  </div>
"""

# 2. Comprehensive Interactive Step-by-Step Guide Modal Component
help_guide_modal_html = """
  <!-- ========================================== -->
  <!-- STEP-BY-STEP PROJECT GUIDE MODAL          -->
  <!-- ========================================== -->
  <div id="helpGuideModal" class="hidden fixed inset-0 z-50 bg-black/75 backdrop-blur-md flex items-center justify-center p-3 sm:p-6 overflow-y-auto">
    <div class="bg-white dark:bg-navy-900 max-w-4xl w-full rounded-2xl border border-gold-500/40 shadow-2xl flex flex-col max-h-[92vh] overflow-hidden my-auto">
      
      <!-- Modal Header -->
      <div class="p-5 sm:p-6 bg-gradient-to-r from-navy-900 via-navy-850 to-navy-900 border-b border-gold-500/30 text-white flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-xl bg-gold-500/20 border border-gold-500/40 flex items-center justify-center text-gold-400 shadow-sm">
            <i data-lucide="compass" class="w-6 h-6"></i>
          </div>
          <div>
            <div class="flex items-center space-x-2">
              <h3 class="font-academic text-lg sm:text-xl font-bold tracking-wide text-white">RI-GI Nexus Project Guide</h3>
              <span class="px-2 py-0.5 text-[10px] font-bold bg-gold-500 text-navy-950 rounded">STEP-BY-STEP MANUAL</span>
            </div>
            <p class="text-xs text-slate-300">Complete roadmap for conducting rigorous, ethical, and impact-driven research</p>
          </div>
        </div>
        <button onclick="closeHelpGuideModal()" class="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-navy-800 transition">
          <i data-lucide="x" class="w-6 h-6"></i>
        </button>
      </div>

      <!-- Quick Step Navigator Bar -->
      <div class="px-6 py-3 bg-slate-100 dark:bg-navy-950 border-b border-slate-200 dark:border-navy-800 flex items-center space-x-2 overflow-x-auto text-xs no-scrollbar">
        <span class="font-semibold text-slate-500 dark:text-slate-400 whitespace-nowrap">Jump to Stage:</span>
        <button onclick="selectGuideStep(1)" id="btnGuideStep-1" class="guide-nav-btn px-2.5 py-1 rounded-md font-semibold bg-gold-500 text-navy-950 whitespace-nowrap">1. Idea</button>
        <button onclick="selectGuideStep(2)" id="btnGuideStep-2" class="guide-nav-btn px-2.5 py-1 rounded-md font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-navy-800 whitespace-nowrap">2. Proposal</button>
        <button onclick="selectGuideStep(3)" id="btnGuideStep-3" class="guide-nav-btn px-2.5 py-1 rounded-md font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-navy-800 whitespace-nowrap">3. Ethics / IRB</button>
        <button onclick="selectGuideStep(4)" id="btnGuideStep-4" class="guide-nav-btn px-2.5 py-1 rounded-md font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-navy-800 whitespace-nowrap">4. Data Ingestion</button>
        <button onclick="selectGuideStep(5)" id="btnGuideStep-5" class="guide-nav-btn px-2.5 py-1 rounded-md font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-navy-800 whitespace-nowrap">5. Statistical Analysis</button>
        <button onclick="selectGuideStep(6)" id="btnGuideStep-6" class="guide-nav-btn px-2.5 py-1 rounded-md font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-navy-800 whitespace-nowrap">6. Simulation</button>
        <button onclick="selectGuideStep(7)" id="btnGuideStep-7" class="guide-nav-btn px-2.5 py-1 rounded-md font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-navy-800 whitespace-nowrap">7. AI Assistant</button>
        <button onclick="selectGuideStep(8)" id="btnGuideStep-8" class="guide-nav-btn px-2.5 py-1 rounded-md font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-navy-800 whitespace-nowrap">8. Manuscript</button>
        <button onclick="selectGuideStep(9)" id="btnGuideStep-9" class="guide-nav-btn px-2.5 py-1 rounded-md font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-navy-800 whitespace-nowrap">9. Collaboration</button>
        <button onclick="selectGuideStep(10)" id="btnGuideStep-10" class="guide-nav-btn px-2.5 py-1 rounded-md font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-navy-800 whitespace-nowrap">10. Grants</button>
        <button onclick="selectGuideStep(11)" id="btnGuideStep-11" class="guide-nav-btn px-2.5 py-1 rounded-md font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-navy-800 whitespace-nowrap">11. SDG Impact</button>
      </div>

      <!-- Modal Content Body -->
      <div class="p-6 overflow-y-auto space-y-6 flex-1 text-slate-700 dark:text-slate-300 text-xs leading-relaxed" id="guideContentContainer">
        
        <!-- Step 1: Idea Discovery -->
        <div id="guideSection-1" class="guide-step-section space-y-3">
          <div class="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-navy-800">
            <h4 class="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2">
              <span class="w-6 h-6 rounded-full bg-gold-500 text-navy-950 font-bold flex items-center justify-center text-xs">1</span>
              <span>Step 1: Discover &amp; Brainstorm Research Ideas</span>
            </h4>
            <button onclick="navigateTo('ideas'); closeHelpGuideModal();" class="px-3 py-1 bg-gold-500 hover:bg-gold-600 text-navy-950 font-bold rounded-lg text-[11px] transition">
              Open Idea Discovery &rarr;
            </button>
          </div>
          <p>
            Every great scientific contribution begins with an empirical problem and a clearly documented gap in contemporary literature.
          </p>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div class="p-3 rounded-xl bg-slate-50 dark:bg-navy-850 border border-slate-200 dark:border-navy-800 space-y-1">
              <strong class="text-gold-500 block">A. Problem Formulation</strong>
              <p>Identify real-world challenges (e.g. localized frost in high-relief mountain valleys or emerging vector zones).</p>
            </div>
            <div class="p-3 rounded-xl bg-slate-50 dark:bg-navy-850 border border-slate-200 dark:border-navy-800 space-y-1">
              <strong class="text-sky-400 block">B. Research Gap</strong>
              <p>State specifically why existing satellite models or regional methods are inadequate at local micro-scales.</p>
            </div>
            <div class="p-3 rounded-xl bg-slate-50 dark:bg-navy-850 border border-slate-200 dark:border-navy-800 space-y-1">
              <strong class="text-teal-400 block">C. SDG Alignment</strong>
              <p>Tag relevant UN SDGs (e.g. SDG 2: Zero Hunger, SDG 13: Climate Action) to benchmark societal impact.</p>
            </div>
          </div>
          <div class="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300">
            <strong>Action Tip:</strong> Click the <em>"Brainstorm New Research Idea"</em> button in the <strong>Idea Discovery</strong> tab, save your problem statement, then click <em>"Convert to Proposal"</em> when ready!
          </div>
        </div>

        <!-- Step 2: Proposal Formulation -->
        <div id="guideSection-2" class="guide-step-section space-y-3">
          <div class="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-navy-800">
            <h4 class="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2">
              <span class="w-6 h-6 rounded-full bg-sky-500 text-white font-bold flex items-center justify-center text-xs">2</span>
              <span>Step 2: Formalize Research Proposal &amp; Timeline</span>
            </h4>
            <button onclick="navigateTo('projects'); closeHelpGuideModal();" class="px-3 py-1 bg-sky-600 hover:bg-sky-700 text-white font-bold rounded-lg text-[11px] transition">
              Open Projects Workspace &rarr;
            </button>
          </div>
          <p>
            A proposal transforms conceptual ideas into executable milestones, resource budgets, and methodological frameworks.
          </p>
          <ul class="list-disc list-inside space-y-1">
            <li><strong>Methodological Architecture:</strong> Define quantitative sensing, experimental setup, or longitudinal surveys.</li>
            <li><strong>Milestone Decomposition:</strong> Establish clear verification dates (e.g. Milestone 1: Sensor Deployment; Milestone 2: Telemetry Verification; Milestone 3: Model Fitting).</li>
            <li><strong>Task Delegation:</strong> Assign roles and deadlines to co-investigators, graduate assistants, and lab supervisors.</li>
          </ul>
        </div>

        <!-- Step 3: Ethics & IRB -->
        <div id="guideSection-3" class="guide-step-section space-y-3">
          <div class="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-navy-800">
            <h4 class="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2">
              <span class="w-6 h-6 rounded-full bg-emerald-500 text-white font-bold flex items-center justify-center text-xs">3</span>
              <span>Step 3: Institutional Review Board (IRB) &amp; Ethical Clearance</span>
            </h4>
            <button onclick="navigateTo('ethics'); closeHelpGuideModal();" class="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg text-[11px] transition">
              Open Ethics Center &rarr;
            </button>
          </div>
          <p>
            Scientific rigor requires strict ethical safeguarding before any field intervention or empirical sensing begins.
          </p>
          <div class="p-4 rounded-xl bg-slate-50 dark:bg-navy-850 border border-slate-200 dark:border-navy-800 space-y-1.5">
            <div class="flex items-center space-x-2 text-emerald-500 font-semibold">
              <i data-lucide="check-circle" class="w-4 h-4"></i>
              <span>Key Ethics Checklist:</span>
            </div>
            <ul class="list-disc list-inside pl-4 space-y-1 text-slate-500 dark:text-slate-400">
              <li>Informed consent verified for all local participants (e.g. 1,250 smallholder farmers).</li>
              <li>Data privacy &amp; anonymization conforming to national and institutional regulations.</li>
              <li>Responsible AI protocol ensuring zero generation of fabricated citations or synthetic bias.</li>
            </ul>
          </div>
        </div>

        <!-- Step 4: Data Ingestion -->
        <div id="guideSection-4" class="guide-step-section space-y-3">
          <div class="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-navy-800">
            <h4 class="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2">
              <span class="w-6 h-6 rounded-full bg-blue-500 text-white font-bold flex items-center justify-center text-xs">4</span>
              <span>Step 4: Data Collection &amp; Ingestion</span>
            </h4>
            <button onclick="navigateTo('analysis'); closeHelpGuideModal();" class="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg text-[11px] transition">
              View Datasets in Analysis Lab &rarr;
            </button>
          </div>
          <p>
            The platform ingests structured telemetry, sensor matrices, or survey spreadsheets following FAIR open-science principles.
          </p>
          <p class="text-slate-500 dark:text-slate-400">
            Explore the pre-loaded <strong>Mustang Agro-Meteorological Transect (12 stations)</strong> tracking elevation (<span class="font-mono-code">elevation_m</span>), mean temperature (<span class="font-mono-code">mean_temp_c</span>), frost days, soil moisture, and crop yield.
          </p>
        </div>

        <!-- Step 5: Statistical Analysis -->
        <div id="guideSection-5" class="guide-step-section space-y-3">
          <div class="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-navy-800">
            <h4 class="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2">
              <span class="w-6 h-6 rounded-full bg-emerald-500 text-white font-bold flex items-center justify-center text-xs">5</span>
              <span>Step 5: Run Validated Statistical Calculations</span>
            </h4>
            <button onclick="navigateTo('analysis'); closeHelpGuideModal();" class="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg text-[11px] transition">
              Launch Analysis Lab &rarr;
            </button>
          </div>
          <p>
            Perform verified statistical computation directly in your browser or through the SciPy backend:
          </p>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="p-3 bg-slate-50 dark:bg-navy-850 rounded-xl border border-slate-200 dark:border-navy-800">
              <strong class="text-gold-400 block mb-1">1. Descriptive Moments</strong>
              <span>Computes exact Mean, Median, Variance (Bessel-corrected ddof=1), Standard Deviation, 95% Confidence Intervals, and histogram bins.</span>
            </div>
            <div class="p-3 bg-slate-50 dark:bg-navy-850 rounded-xl border border-slate-200 dark:border-navy-800">
              <strong class="text-emerald-400 block mb-1">2. OLS Linear Regression</strong>
              <span>Regress <span class="font-mono-code">mean_temp_c</span> on <span class="font-mono-code">elevation_m</span>. R² = 0.9989 with slope &beta;₁ = -0.009 °C/m, homoscedasticity checks, and live fitted scatter plots.</span>
            </div>
          </div>
        </div>

        <!-- Step 6: Innovation & Simulation -->
        <div id="guideSection-6" class="guide-step-section space-y-3">
          <div class="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-navy-800">
            <h4 class="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2">
              <span class="w-6 h-6 rounded-full bg-purple-500 text-white font-bold flex items-center justify-center text-xs">6</span>
              <span>Step 6: Mathematical Modeling &amp; Simulation</span>
            </h4>
            <button onclick="navigateTo('simulations'); closeHelpGuideModal();" class="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-lg text-[11px] transition">
              Open Simulation Studio &rarr;
            </button>
          </div>
          <p>
            Test dynamical systems before deploying field interventions:
          </p>
          <ul class="list-disc list-inside space-y-1">
            <li><strong>SIR Compartmental Epidemic:</strong> Tune transmission rate (&beta;) and recovery rate (&gamma;) to evaluate the basic reproduction number R₀ and peak infection day.</li>
            <li><strong>Atmospheric CO₂ Radiative Forcing:</strong> Model emissions growth rates and calculate global mean surface temperature anomalies (&Delta;T &deg;C) over a 50-year horizon.</li>
          </ul>
        </div>

        <!-- Step 7: AI Assistant -->
        <div id="guideSection-7" class="guide-step-section space-y-3">
          <div class="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-navy-800">
            <h4 class="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2">
              <span class="w-6 h-6 rounded-full bg-gold-500 text-navy-950 font-bold flex items-center justify-center text-xs">7</span>
              <span>Step 7: Consult the Academic AI Assistant</span>
            </h4>
            <button onclick="navigateTo('ai-assistant'); closeHelpGuideModal();" class="px-3 py-1 bg-gold-500 hover:bg-gold-600 text-navy-950 font-bold rounded-lg text-[11px] transition">
              Open AI Assistant &rarr;
            </button>
          </div>
          <p>
            Use specialized academic prompts to formulate directional hypotheses, outline literature themes, and verify methodological assumptions with zero fabricated citations.
          </p>
        </div>

        <!-- Step 8: Manuscript Drafting -->
        <div id="guideSection-8" class="guide-step-section space-y-3">
          <div class="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-navy-800">
            <h4 class="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2">
              <span class="w-6 h-6 rounded-full bg-orange-500 text-white font-bold flex items-center justify-center text-xs">8</span>
              <span>Step 8: Write &amp; Export Manuscript (APA 7th)</span>
            </h4>
            <button onclick="navigateTo('publishing'); closeHelpGuideModal();" class="px-3 py-1 bg-orange-600 hover:bg-orange-700 text-white font-bold rounded-lg text-[11px] transition">
              Open Publishing Studio &rarr;
            </button>
          </div>
          <p>
            Structure your research into standardized APA 7th format: Abstract, Introduction, Quantitative Methodology, Results, and verified DOI references. Click <em>"Export Manuscript (Markdown / Word)"</em> to download your draft.
          </p>
        </div>

        <!-- Step 9: Global Collaboration -->
        <div id="guideSection-9" class="guide-step-section space-y-3">
          <div class="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-navy-800">
            <h4 class="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2">
              <span class="w-6 h-6 rounded-full bg-pink-500 text-white font-bold flex items-center justify-center text-xs">9</span>
              <span>Step 9: Expand International Collaboration</span>
            </h4>
            <button onclick="navigateTo('collaborate'); closeHelpGuideModal();" class="px-3 py-1 bg-pink-600 hover:bg-pink-700 text-white font-bold rounded-lg text-[11px] transition">
              Open Collaboration Network &rarr;
            </button>
          </div>
          <p>
            Connect with peer scientists across Cambridge, Stanford, KNUST, and Tribhuvan University. Dispatch verified project collaboration invitations with a single click.
          </p>
        </div>

        <!-- Step 10: Funding & Grants -->
        <div id="guideSection-10" class="guide-step-section space-y-3">
          <div class="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-navy-800">
            <h4 class="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2">
              <span class="w-6 h-6 rounded-full bg-yellow-500 text-navy-950 font-bold flex items-center justify-center text-xs">10</span>
              <span>Step 10: Discover Verified Research Grants</span>
            </h4>
            <button onclick="navigateTo('funding'); closeHelpGuideModal();" class="px-3 py-1 bg-yellow-500 hover:bg-yellow-600 text-navy-950 font-bold rounded-lg text-[11px] transition">
              View Funding Grants &rarr;
            </button>
          </div>
          <p>
            Review active funding calls (Wellcome Trust, Horizon Europe, IDRC) with verified eligibility deadlines and official application portals.
          </p>
        </div>

        <!-- Step 11: SDG Observatory -->
        <div id="guideSection-11" class="guide-step-section space-y-3">
          <div class="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-navy-800">
            <h4 class="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2">
              <span class="w-6 h-6 rounded-full bg-teal-500 text-white font-bold flex items-center justify-center text-xs">11</span>
              <span>Step 11: Document Global Impact &amp; UN SDGs</span>
            </h4>
            <button onclick="navigateTo('sdg-impact'); closeHelpGuideModal();" class="px-3 py-1 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-lg text-[11px] transition">
              Open SDG Observatory &rarr;
            </button>
          </div>
          <p>
            Measure true societal outcomes: Log verified community beneficiaries (e.g. 1,250 mountain farmers, 45,000 regional population), policy briefs, and open technology prototypes.
          </p>
        </div>

      </div>

      <!-- Modal Footer Action Bar -->
      <div class="p-4 bg-slate-100 dark:bg-navy-950 border-t border-slate-200 dark:border-navy-800 flex flex-wrap items-center justify-between gap-3">
        <div class="text-[11px] text-slate-500 dark:text-slate-400">
          Tip: You can reopen this guide anytime using the <strong>"Help &amp; Guide"</strong> button in the header or floating button.
        </div>
        <div class="flex space-x-2">
          <button onclick="navigateTo('ideas'); closeHelpGuideModal();" class="px-4 py-2 bg-gold-500 hover:bg-gold-600 text-navy-950 font-bold rounded-xl text-xs shadow transition">
            Begin with Step 1 (Idea Discovery) &rarr;
          </button>
          <button onclick="closeHelpGuideModal()" class="px-4 py-2 bg-navy-800 hover:bg-navy-700 text-white font-semibold rounded-xl text-xs transition">
            Close Guide
          </button>
        </div>
      </div>

    </div>
  </div>
"""

# Script to control the Help Guide Modal and Step Navigation
help_guide_js = """
  // Help Guide Modal Functions
  function openHelpGuideModal() {
    const modal = document.getElementById('helpGuideModal');
    if (modal) {
      modal.classList.remove('hidden');
      initIcons();
    }
  }

  function closeHelpGuideModal() {
    const modal = document.getElementById('helpGuideModal');
    if (modal) {
      modal.classList.add('hidden');
    }
  }

  function selectGuideStep(stepNum) {
    // Scroll to specific section inside guide modal
    const section = document.getElementById(`guideSection-${stepNum}`);
    if (section) {
      section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    // Highlight step button
    document.querySelectorAll('.guide-nav-btn').forEach(btn => {
      btn.className = 'guide-nav-btn px-2.5 py-1 rounded-md font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-navy-800 whitespace-nowrap';
    });
    const activeBtn = document.getElementById(`btnGuideStep-${stepNum}`);
    if (activeBtn) {
      activeBtn.className = 'guide-nav-btn px-2.5 py-1 rounded-md font-semibold bg-gold-500 text-navy-950 whitespace-nowrap';
    }
  }
"""

# Insert Header Button into Right Side Nav before Notification Bell
content = content.replace(
    '<!-- Notification Bell -->',
    f"{help_header_button}\n          <!-- Notification Bell -->"
)

# Insert Help Tab into Navigation Bar
content = content.replace(
    '<button onclick="navigateTo(\'reports\')"',
    f"{help_nav_tab}        <button onclick=\"navigateTo('reports')\""
)

# Insert Guide Modal and Floating Button before footer
content = content.replace(
    '<!-- ========================================== -->\n  <!-- KMCHSSDSmartAcademic00Hub IDENTICAL FOOTER -->',
    f"{help_guide_modal_html}\n{floating_help_fab}\n  <!-- ========================================== -->\n  <!-- KMCHSSDSmartAcademic00Hub IDENTICAL FOOTER -->"
)

# Insert script before </body>
content = content.replace('</body>', f"<script>\n{help_guide_js}\n</script>\n</body>")

with open('RIGI_Nexus_Platform.html', 'w', encoding='utf-8') as f:
    f.write(content)

with open('rigi_nexus/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully injected Step-by-Step Project Guide and Help buttons into RIGI_Nexus_Platform.html and rigi_nexus/index.html")

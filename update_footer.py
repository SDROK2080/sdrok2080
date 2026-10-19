import os

# 1. Read base index.html template
with open('rigi_nexus/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the exact CSS from KMCHSSDSmartAcademic00Hub for the footer and poster dialog
kmc_footer_css = """
  /* KMCHSSDSmartAcademic00Hub Identical Footer & Developer Card Styles */
  .site-footer {
    background: #0B2150;
    color: #C9D5EC;
    border-top: 5px solid #C4912A;
    margin-top: 40px;
    width: 100%;
  }
  .foot {
    max-width: 1240px;
    margin: 0 auto;
    padding: 34px 20px 40px;
    display: grid;
    gap: 8px;
    font-size: 0.95rem;
    line-height: 1.6;
  }
  .site-footer a {
    color: #F0C766;
    text-decoration: underline;
    text-underline-offset: 3px;
    transition: color 0.15s ease;
  }
  .site-footer a:hover {
    color: #FFE082;
  }
  .dev-card {
    display: flex;
    align-items: center;
    gap: 18px;
    margin-top: 14px;
    padding-top: 18px;
    border-top: 1px solid rgba(255, 255, 255, 0.16);
  }
  .dev-photo {
    flex: none;
    width: 96px;
    height: 96px;
    border-radius: 50%;
    padding: 0;
    border: 3px solid #C4912A;
    overflow: hidden;
    background: #0B2150;
    cursor: pointer;
    transition: transform 0.2s, border-color 0.2s;
  }
  .dev-photo:hover {
    border-color: #F0C766;
    transform: scale(1.05);
  }
  .dev-photo img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  .dev-text {
    display: grid;
    gap: 3px;
    line-height: 1.45;
  }
  .dev-by {
    font-size: 0.85rem;
    color: #9FB1D3;
  }
  .dev-text b {
    font-family: 'Literata', Georgia, serif;
    font-size: 1.25rem;
    color: #ffffff;
  }
  .dev-text span {
    font-size: 0.92rem;
    color: #C9D5EC;
  }
  .dev-link {
    justify-self: start;
    background: none;
    border: 0;
    padding: 0;
    margin-top: 6px;
    color: #F0C766;
    text-decoration: underline;
    text-underline-offset: 3px;
    font-weight: 600;
    cursor: pointer;
    font-size: 0.9rem;
    transition: color 0.15s ease;
  }
  .dev-link:hover {
    color: #FFE082;
  }
  @media (max-width: 640px) {
    .dev-card {
      align-items: flex-start;
    }
    .dev-photo {
      width: 76px;
      height: 76px;
    }
  }

  /* Poster Dialog */
  #posterDlg {
    max-width: 540px;
    background: #0B2150;
    padding: 0 0 16px;
    text-align: center;
    border: 1px solid rgba(196, 145, 42, 0.4);
    border-radius: 16px;
    color: #fff;
    margin: auto;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
  }
  #posterDlg::backdrop {
    background: rgba(0, 0, 0, 0.75);
    backdrop-filter: blur(4px);
  }
  #posterDlg img {
    display: block;
    width: 100%;
    height: auto;
    max-height: calc(100vh - 130px);
    object-fit: contain;
    background: #0B2150;
    border-radius: 15px 15px 0 0;
  }
  #posterDlg .dlg-close {
    margin-top: 14px;
    background: #C4912A;
    color: #1B1400;
    font-weight: 700;
    border: 0;
    border-radius: 10px;
    padding: 9px 24px;
    cursor: pointer;
    transition: filter 0.15s;
  }
  #posterDlg .dlg-close:hover {
    filter: brightness(1.15);
  }
"""

# The exact footer HTML from KMCHSSDSmartAcademic00Hub
kmc_footer_html = """
  <!-- ========================================== -->
  <!-- KMCHSSDSmartAcademic00Hub IDENTICAL FOOTER -->
  <!-- ========================================== -->
  <footer class="site-footer">
    <div class="foot">
      <p>&copy; 2027/28 Kapilvastu Multiple Campus &mdash; HSSD, Taulihawa, Kapilvastu, Lumbini Province, Nepal</p>
      <p>Updates: <a href="https://www.kmctlw.edu.np" target="_blank" rel="noopener">www.kmctlw.edu.np</a> and <a href="https://fohss.tu.edu.np/" target="_blank" rel="noopener">fohss.tu.edu.np</a></p>
      <div class="dev-card">
        <button class="dev-photo" type="button" id="devPhoto" aria-label="View the full poster of Mr. Bishnu Singh Rayamajhi">
          <img src="image09.jpeg" width="480" height="480" loading="lazy" alt="Mr. Bishnu Singh Rayamajhi" onerror="this.parentElement.hidden=true">
        </button>
        <div class="dev-text">
          <span class="dev-by">Developed by</span>
          <b>Mr. Bishnu Singh Rayamajhi</b>
          <span>Math Lecturer and Department Head of Humanities &amp; Social Sciences (KMC-HSSD)</span>
          <button class="dev-link" type="button" id="devPoster">View poster</button>
        </div>
      </div>
    </div>
  </footer>

  <!-- Poster Dialog -->
  <dialog id="posterDlg" aria-label="Poster: What if your idea could change the future?">
    <img src="image09.jpeg" width="1070" height="1600" alt="Poster of Kapilvastu Multiple Campus and UCDL Academy: What if your idea could change the future? Featuring Mr. Bishnu Singh Rayamajhi.">
    <button class="dlg-close" type="button" id="posterClose">Close</button>
  </dialog>
"""

# Poster click event listener JS
poster_script_js = """
  // Poster Dialog Handlers from KMCHSSDSmartAcademic00Hub
  document.addEventListener('DOMContentLoaded', () => {
    const posterDlg = document.getElementById('posterDlg');
    ['devPhoto', 'devPoster'].forEach(id => {
      const el = document.getElementById(id);
      if (el && posterDlg) {
        el.addEventListener('click', () => {
          if (typeof posterDlg.showModal === 'function') {
            posterDlg.showModal();
          } else {
            posterDlg.classList.remove('hidden');
          }
        });
      }
    });
    const posterClose = document.getElementById('posterClose');
    if (posterClose && posterDlg) {
      posterClose.onclick = () => {
        if (typeof posterDlg.close === 'function') {
          posterDlg.close();
        } else {
          posterDlg.classList.add('hidden');
        }
      };
    }
    if (posterDlg) {
      posterDlg.addEventListener('click', e => {
        if (e.target === posterDlg) {
          if (typeof posterDlg.close === 'function') {
            posterDlg.close();
          } else {
            posterDlg.classList.add('hidden');
          }
        }
      });
    }
  });
"""

# Insert CSS into <head>
if '</style>' in content:
    content = content.replace('</style>', f"{kmc_footer_css}\n  </style>")

# Replace existing footer
import re
content = re.sub(r'<footer.*?</footer>', kmc_footer_html, content, flags=re.DOTALL)

# Insert script before </body>
content = content.replace('</body>', f"<script>\n{poster_script_js}\n</script>\n</body>")

with open('rigi_nexus/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

with open('RIGI_Nexus_Platform.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated footer in rigi_nexus/index.html and RIGI_Nexus_Platform.html successfully!")

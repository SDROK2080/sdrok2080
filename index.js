/* ============================================================
   SDROK — Social Development & Research Information
   Script: index.js
   ============================================================ */

'use strict';

/* ── Slick Slider Init ── */
$(document).ready(function () {
  $('.slider').slick({
    infinite:   true,
    speed:      600,
    fade:       true,
    cssEase:    'ease-in-out',
    arrows:     true,
    dots:       true,
    autoplay:   true,
    autoplaySpeed: 4000,
  });
});


/* ── Dropdown Toggle ──
   Toggles a header dropdown panel open/closed.
   Closes all other open panels first.
   ─────────────────────────────────────────── */
function toggleDropdown(panelId) {
  const allPanels = document.querySelectorAll('.dropdown-panel');

  allPanels.forEach(function (panel) {
    if (panel.id !== panelId) {
      panel.classList.remove('open');
    }
  });

  const target = document.getElementById(panelId);
  if (target) {
    target.classList.toggle('open');
  }
}


/* ── Open Text File in New Tab ──
   Generic helper — replaces all the individual openXxxTab() functions.
   Usage: openTab('ResearchArticle.txt')
   ─────────────────────────────────────────── */
function openTab(filePath) {
  fetch(filePath)
    .then(function (response) {
      if (!response.ok) throw new Error('File not found: ' + filePath);
      return response.text();
    })
    .then(function (content) {
      var newTab = window.open('', '_blank');
      newTab.document.write(
        '<!DOCTYPE html><html><head>' +
        '<meta charset="UTF-8">' +
        '<title>' + filePath + '</title>' +
        '<style>body{font-family:monospace;padding:24px;background:#f9f9f9;color:#222;white-space:pre-wrap;line-height:1.6;}</style>' +
        '</head><body>' + content + '</body></html>'
      );
      newTab.document.close();
    })
    .catch(function (error) {
      console.error('Error opening tab:', error);
      alert('Could not open file: ' + filePath + '\n(Make sure the file exists in the same folder.)');
    });
}

/* ── Legacy named wrappers (kept for any external references) ── */
function openResearchArticleTab()            { openTab('ResearchArticle.txt');            }
function openCaseStudyTab()                  { openTab('CaseStudy.txt');                  }
function openInterviewsTab()                 { openTab('Interviews.txt');                 }
function openSeminarsAndWebinarsTab()        { openTab('SeminarsAndWebinars.txt');        }
function openCyberNetworkingTab()            { openTab('CyberNetworking.txt');            }
function openNewsAndUpdatesTab()             { openTab('NewsAndUpdates.txt');             }
function openPolicyInsightTab()              { openTab('PolicyInsight.txt');              }
function openArchaeologicalInvestigationTab(){ openTab('ArchaeologicalInvestigation.txt');}
function openAcademicFieldTab()              { openTab('AcademicField.txt');              }
function openLifeScienceTab()                { openTab('LifeScience.txt');                }
function openHeaderSectionTab()              { openTab('HeaderSection.txt');              }
function openContentSectionTab()             { openTab('ContentSection.txt');             }
function openInnovatingJourneySectionTab()   { openTab('InnovatingJourneySection.txt');   }
function openActionSectionTab()              { openTab('ActionSection.txt');              }
function openDesireSectionTab()              { openTab('DesireSection.txt');              }
function openNavigationLinksTab()            { openTab('NavigationLinks.txt');            }
function openCopywriteInformationTab()       { openTab('CopywriteInformation.txt');       }
function openSocialMediaPolicyTab()          { openTab('SocialMediaPolicy.txt');          }
function openPrivacyPolicyTab()              { openTab('PrivacyPolicy.txt');              }
function openTermsOfServicesTab()            { openTab('TermsOfServices.txt');            }


/* ── Open External Link in New Tab ── */
function openLink(url) {
  window.open(url, '_blank', 'noopener,noreferrer');
}


/* ── Photo Carousel (auto-play, no library) ── */
(function () {
  var currentIndex = 0;

  function getImages() {
    return document.querySelectorAll('.carousel-image');
  }

  function showSlide(index) {
    var images = getImages();
    if (!images.length) return;
    currentIndex = (index + images.length) % images.length;
    document.getElementById('image-carousel').style.transform =
      'translateX(-' + currentIndex * 100 + '%)';
  }

  function nextCarouselSlide() {
    showSlide(currentIndex + 1);
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (document.querySelector('.carousel-image')) {
      showSlide(0);
      setInterval(nextCarouselSlide, 4000);
    }
  });
})();


/* ── News Ticker Text ── */
document.addEventListener('DOMContentLoaded', function () {
  var ticker = document.getElementById('news-content');
  if (ticker) {
    ticker.innerHTML =
      '<span>Crafted by Bishnu Singh Rayamajhi — Social Development &amp; Research Information pioneers ' +
      'transformative initiatives, leveraging the dynamic pulse of social vibrations to drive innovation ' +
      'and positive change globally. &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; ' +
      'Advancing Communities Through Insight &amp; Innovation.</span>';
  }
});


/* ── Suggestion Box ── */
function sendSuggestion() {
  var input = document.getElementById('searchInput');
  var value = input ? input.value.trim() : '';

  if (!value) {
    alert('Please enter your suggestion before sending.');
    return;
  }

  // Placeholder: replace with real submission logic (e.g. fetch/POST to a server)
  console.log('Suggestion submitted:', value);
  alert('Thank you for your suggestion!\n\n"' + value + '"\n\nWe appreciate your feedback.');

  input.value = '';
}


/* ── Close dropdowns when clicking outside the header ── */
document.addEventListener('click', function (e) {
  var header = document.querySelector('header');
  if (header && !header.contains(e.target)) {
    document.querySelectorAll('.dropdown-panel').forEach(function (panel) {
      panel.classList.remove('open');
    });
  }
});


/* ── Section toggle (kept for potential use elsewhere) ── */
function toggleSection(sectionId) {
  var section = document.getElementById(sectionId);
  if (!section) return;
  section.style.display = (section.style.display === 'none') ? 'block' : 'none';
}


/* ── Contact form autoresponder (kept for contact.html use) ── */
function submitForm() {
  var form = document.getElementById('contactForm');
  var responseMsg = document.getElementById('responseMessage');
  if (!form || !responseMsg) return;

  var name    = form.elements.name    ? form.elements.name.value    : '';
  var email   = form.elements.email   ? form.elements.email.value   : '';
  var message = form.elements.message ? form.elements.message.value : '';

  responseMsg.innerHTML =
    'Hello ' + name + ',<br>Thank you for contacting us! We have received your message:<br>' +
    '<em>' + message + '</em><br>We will get back to you at ' + email + '.';

  form.reset();
}

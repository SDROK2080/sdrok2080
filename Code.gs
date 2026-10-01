/*******************************************************************
 * KMC-HSSD RESEARCH MANAGEMENT SYSTEM  (Code.gs)
 * Kapilvastu Multiple Campus - Dept. of Humanities & Social Sciences
 * Version 2.0.0
 *
 * Features
 *  1. Automatic Research ID   KMC-HSSD-RES-2026-001 (lock-protected)
 *  2. Drive repository        Root / Year / Program / ID - Name / 8 subfolders
 *  3. Folder links in Sheets  raw URL + clickable "Open Folder" link
 *  4. Student + supervisor emails (HTML and plain text)
 *  5. Supervisor assignment   preference, else program/area match + load balancing
 *  6. Progress tracking       history sheet + live status on the student row
 *  7. Activity Log            every action, error and email result
 *  8. Entry points            Google Form trigger AND web API (doPost)
 *  9. Duplicate protection    one registration per email, script lock
 * 10. Settings sheet          admin-editable behaviour, optional API key
 *
 * FIRST-TIME SETUP: see the SETUP GUIDE at the bottom of this file.
 *******************************************************************/

/* ================================================================
   CONFIGURATION
   ================================================================ */

const SYSTEM = {
  ORG: 'Kapilvastu Multiple Campus (KMC)',
  DEPT: 'Department of Humanities & Social Sciences (KMC-HSSD)',
  VERSION: '2.0.0',
  ID_PREFIX: 'KMC-HSSD-RES-',
  ROOT_FOLDER_NAME: 'KMC-HSSD Research Repository',
  DEFAULT_PROGRAM_FOLDER: 'Other Programs'
};

const SHEETS = {
  STUDENTS: '01_Students',
  TOPICS: '02_Research_Topics',
  PROPOSALS: '03_Proposals',
  PROGRESS: '04_Progress',
  FINAL: '05_Final_Submissions',
  EVALUATIONS: '06_Evaluations',
  SUPERVISORS: '07_Supervisors',
  APPROVAL: '08_Department_Approval',
  LOG: '09_Activity_Log',
  SETTINGS: '10_Settings'
};

const SUBFOLDERS = [
  '01_Profile', '02_Topic', '03_Proposal', '04_Literature',
  '05_Data', '06_Progress', '07_Final_Report', '08_Evaluation'
];

/* Research stages and the default progress % each one represents */
const STAGES = [
  { title: 'Registration', pct: 5 },
  { title: 'Topic', pct: 15 },
  { title: 'Proposal', pct: 30 },
  { title: 'Supervisor Review', pct: 40 },
  { title: 'Department Approval', pct: 50 },
  { title: 'Data Collection', pct: 65 },
  { title: 'Analysis', pct: 75 },
  { title: 'Draft Report', pct: 85 },
  { title: 'Final Submission', pct: 95 },
  { title: 'Completed', pct: 100 }
];

const DECISIONS = ['Approved', 'Revision Required', 'Rejected'];

/* Column headers. Code finds columns BY NAME, so column order may change
   and extra columns may be added to any sheet without breaking anything. */
const SCHEMA = {};
SCHEMA[SHEETS.STUDENTS] = [
  'Timestamp', 'Research ID', 'Student Name', 'Email', 'Phone', 'Program',
  'Semester', 'Year', 'Gender', 'Address', 'Research Topic', 'Research Area',
  'Supervisor', 'Supervisor Email', 'Status', 'Progress %', 'Current Stage',
  'Folder ID', 'Folder URL', 'Folder Link', 'Last Updated'
];
SCHEMA[SHEETS.TOPICS] = [
  'Timestamp', 'Research ID', 'Student Name', 'Research Topic', 'Research Area',
  'Problem Statement', 'Objectives', 'Status', 'Supervisor'
];
SCHEMA[SHEETS.PROPOSALS] = [
  'Timestamp', 'Research ID', 'Proposal Title', 'Submission Date',
  'Supervisor', 'Proposal Status', 'Feedback', 'Document URL'
];
SCHEMA[SHEETS.PROGRESS] = [
  'Timestamp', 'Research ID', 'Student Name', 'Step', 'Stage', 'Status',
  'Progress %', 'Remarks', 'Updated By', 'Next Action', 'Supervisor'
];
SCHEMA[SHEETS.FINAL] = [
  'Timestamp', 'Research ID', 'Student Name', 'Report Title', 'File URL',
  'Submitted By', 'Status'
];
SCHEMA[SHEETS.EVALUATIONS] = [
  'Timestamp', 'Research ID', 'Student Name', 'Supervisor', 'Evaluator',
  'Research Quality', 'Methodology', 'Analysis', 'Presentation',
  'Overall Remarks', 'Evaluation Status'
];
SCHEMA[SHEETS.SUPERVISORS] = [
  'Supervisor ID', 'Supervisor Name', 'Email', 'Department', 'Program',
  'Research Areas', 'Maximum Students', 'Current Students', 'Status'
];
SCHEMA[SHEETS.APPROVAL] = [
  'Timestamp', 'Research ID', 'Student Name', 'Decision', 'Comments',
  'Approved By', 'Approval Date', 'Approval Number'
];
SCHEMA[SHEETS.LOG] = [
  'Timestamp', 'Research ID', 'Action', 'Details', 'User', 'Source'
];
SCHEMA[SHEETS.SETTINGS] = ['Key', 'Value', 'Description'];

const DEFAULT_SETTINGS = [
  ['ACADEMIC_YEAR', new Date().getFullYear(), 'Year used in Research IDs and Drive folders'],
  ['ADMIN_EMAIL', '', 'Receives error alerts and "no supervisor available" notices'],
  ['SENDER_NAME', 'KMC-HSSD Research Office', 'Name shown on outgoing emails'],
  ['REPLY_TO', '', 'Reply-to address for outgoing emails (optional)'],
  ['SEND_EMAILS', 'TRUE', 'TRUE/FALSE - master switch for all emails'],
  ['NOTIFY_ON_PROGRESS', 'TRUE', 'TRUE/FALSE - email student on key status changes'],
  ['SHARE_FOLDER', 'FALSE', 'TRUE/FALSE - give student and supervisor edit access to the Drive folder'],
  ['DEFAULT_MAX_STUDENTS', 10, 'Capacity used when a supervisor has no Maximum Students value'],
  ['API_KEY', '', 'If filled, every web API request must send this value as "apiKey"']
];

/* ================================================================
   MENU, SETUP AND TRIGGERS
   ================================================================ */

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('KMC-HSSD Research')
    .addItem('1. Set up system (run once)', 'setupSystem')
    .addItem('2. Install form-submit trigger', 'installTriggers')
    .addSeparator()
    .addItem('Health check', 'runHealthCheck')
    .addItem('Recount supervisor loads', 'recountSupervisorLoads')
    .addItem('Rebuild folder links', 'refreshFolderLinks')
    .addToUi();
}

/** Run ONCE. Safe to run again: it only adds what is missing. */
function setupSystem() {
  const ss = getSpreadsheet_();
  PropertiesService.getScriptProperties().setProperty('SPREADSHEET_ID', ss.getId());

  Object.keys(SCHEMA).forEach(function (name) {
    ensureSheet_(ss, name, SCHEMA[name]);
  });

  seedSettings_();
  formatSheets_(ss);

  const root = getRootFolder_();
  logActivity_('SYSTEM', 'System setup', 'Setup completed. Root folder: ' + root.getUrl(), '', 'Setup');

  notify_('Setup complete.\n\nRoot folder:\n' + root.getUrl() +
    '\n\nNext: add supervisors in 07_Supervisors, set ADMIN_EMAIL in 10_Settings, then install the form trigger.');
}

/** Creates the "on form submit" trigger. Run once after linking a Google Form. */
function installTriggers() {
  const ss = getSpreadsheet_();
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'onFormSubmit') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('onFormSubmit').forSpreadsheet(ss).onFormSubmit().create();
  logActivity_('SYSTEM', 'Trigger installed', 'onFormSubmit trigger installed.', '', 'Setup');
  notify_('Form-submit trigger installed.');
}

/* ================================================================
   ENTRY POINT 1: GOOGLE FORM SUBMISSION
   ================================================================ */

function onFormSubmit(e) {
  try {
    if (!e || !e.namedValues) {
      throw new Error('onFormSubmit must be run by a form-submit trigger, not manually.');
    }
    const raw = normalizeFormData_(e.namedValues);
    const data = {
      studentName: pick_(raw, ['Student Name', 'Full Name', 'Name']),
      email: pick_(raw, ['Email', 'Email Address', 'Student Email']),
      phone: pick_(raw, ['Phone', 'Phone Number', 'Mobile Number', 'Mobile']),
      program: pick_(raw, ['Program', 'Programme']),
      semester: pick_(raw, ['Semester', 'Semester/Year', 'Semester / Year', 'Level']),
      year: pick_(raw, ['Batch', 'Admission Year', 'Year']),
      gender: pick_(raw, ['Gender']),
      address: pick_(raw, ['Address']),
      researchTopic: pick_(raw, ['Research Topic', 'Proposed Research Topic', 'Proposed Title', 'Topic']),
      researchArea: pick_(raw, ['Research Area', 'Preferred Research Area', 'Area']),
      problemStatement: pick_(raw, ['Problem Statement', 'Research Problem']),
      objectives: pick_(raw, ['Objectives', 'Research Objectives']),
      supervisor: pick_(raw, ['Preferred Supervisor', 'Supervisor Name', 'Supervisor'])
    };
    const result = registerStudent_(data, 'Google Form');
    if (result.duplicate) {
      logActivity_(result.researchId, 'Duplicate form submission blocked', data.email, '', 'Google Form');
    }
  } catch (err) {
    logActivity_('SYSTEM', 'ERROR', 'onFormSubmit: ' + err.message, '', 'Google Form');
    sendAdminAlert_('KMC-HSSD error: form submission failed', err.message + '\n\n' + (err.stack || ''));
    throw err;
  }
}

/* ================================================================
   ENTRY POINT 2: WEB API
   Deploy > New deployment > Web app > Execute as: Me
   ================================================================ */

function doGet(e) {
  return json_({
    success: true,
    system: 'KMC-HSSD Research Management API',
    version: SYSTEM.VERSION,
    status: 'online',
    timestamp: new Date().toISOString()
  });
}

function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) throw new Error('No POST data received.');
    const data = JSON.parse(e.postData.contents);
    authorize_(data);

    switch (data.action || 'registerStudent') {
      case 'registerStudent':
        return json_(registerStudent_(data, 'Web API'));
      case 'getStudents':
        return json_(getStudents_());
      case 'getStudent':
        return json_(getStudent_(data.researchId));
      case 'getProgress':
        return json_(getProgress_(data.researchId));
      case 'getActivity':
        return json_(getActivity_(data.researchId, data.limit));
      case 'getSupervisors':
        return json_(getSupervisors_());
      case 'updateProgress':
        return json_(updateProgress_(data));
      case 'departmentApproval':
        return json_(departmentApproval_(data));
      case 'finalSubmission':
        return json_(finalSubmission_(data));
      default:
        throw new Error('Unknown action: ' + data.action);
    }
  } catch (err) {
    logActivity_('SYSTEM', 'API ERROR', err.message, '', 'Web API');
    return json_({ success: false, error: err.message });
  }
}

function authorize_(data) {
  const key = String(getSetting_('API_KEY', '')).trim();
  if (key && String(data.apiKey || '') !== key) throw new Error('Unauthorized.');
}

/* ================================================================
   REGISTRATION PIPELINE
   ================================================================ */

function registerStudent_(data, source) {
  const name = String(data.studentName || '').trim();
  const email = String(data.email || '').trim().toLowerCase();
  if (!name) throw new Error('Student name is required.');
  if (!email) throw new Error('Email is required.');
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) throw new Error('Email address is not valid: ' + email);

  return withLock_(function () {
    const students = getSheet_(SHEETS.STUDENTS);

    /* Duplicate-submission protection */
    const dupRow = findRow_(students, 'Email', email);
    if (dupRow) {
      const existing = rowToObject_(students, dupRow);
      logActivity_(existing['Research ID'], 'Duplicate registration blocked', email, '', source);
      return {
        success: false,
        duplicate: true,
        researchId: existing['Research ID'],
        message: 'This email is already registered.'
      };
    }

    const year = academicYear_();
    const program = String(data.program || '').trim();
    const researchId = nextResearchId_();
    const supervisor = assignSupervisor_(data.supervisor, program, data.researchArea || data.researchTopic);
    const repo = createRepository_(researchId, name, program, year);
    const now = new Date();

    const row = appendRecord_(students, {
      'Timestamp': now,
      'Research ID': researchId,
      'Student Name': name,
      'Email': email,
      'Phone': data.phone || '',
      'Program': program,
      'Semester': data.semester || '',
      'Year': data.year || '',
      'Gender': data.gender || '',
      'Address': data.address || '',
      'Research Topic': data.researchTopic || '',
      'Research Area': data.researchArea || '',
      'Supervisor': supervisor.name,
      'Supervisor Email': supervisor.email,
      'Status': 'Registered',
      'Progress %': 5,
      'Current Stage': 'Registration',
      'Folder ID': repo.id,
      'Folder URL': repo.url,
      'Last Updated': now
    });
    setFolderLink_(students, row, repo.url);

    appendRecord_(getSheet_(SHEETS.TOPICS), {
      'Timestamp': now,
      'Research ID': researchId,
      'Student Name': name,
      'Research Topic': data.researchTopic || '',
      'Research Area': data.researchArea || '',
      'Problem Statement': data.problemStatement || '',
      'Objectives': data.objectives || '',
      'Status': 'Submitted',
      'Supervisor': supervisor.name
    });

    appendRecord_(getSheet_(SHEETS.PROGRESS), {
      'Timestamp': now,
      'Research ID': researchId,
      'Student Name': name,
      'Step': 1,
      'Stage': 'Registration',
      'Status': 'Completed',
      'Progress %': 5,
      'Remarks': 'Student registered and research repository created.',
      'Updated By': 'System',
      'Next Action': 'Submit research topic and proposal',
      'Supervisor': supervisor.name
    });

    logActivity_(researchId, 'Student registered', name + ' | ' + program + ' | Supervisor: ' + supervisor.name, '', source);
    logActivity_(researchId, 'Drive repository created', repo.url, '', source);

    if (String(getSetting_('SHARE_FOLDER', 'FALSE')).toUpperCase() === 'TRUE') {
      shareFolder_(repo.folder, [email, supervisor.email], researchId);
    }

    /* Emails never block registration; failures are logged */
    const info = {
      researchId: researchId, studentName: name, email: email,
      supervisorName: supervisor.name, supervisorEmail: supervisor.email,
      researchTopic: data.researchTopic || '', folderUrl: repo.url
    };
    sendStudentRegistrationEmail_(info);
    if (supervisor.email) sendSupervisorAssignmentEmail_(info);

    return {
      success: true,
      message: 'Student registered successfully.',
      researchId: researchId,
      supervisor: supervisor.name,
      driveFolderId: repo.id,
      driveFolderUrl: repo.url,
      timestamp: now.toISOString()
    };
  });
}

/* ================================================================
   RESEARCH ID
   ================================================================ */

/** Call only while holding the script lock. Result: KMC-HSSD-RES-2026-001 */
function nextResearchId_() {
  const year = academicYear_();
  const props = PropertiesService.getScriptProperties();
  const key = 'COUNTER_' + year;
  const stored = Number(props.getProperty(key)) || 0;
  const next = Math.max(stored, maxExistingNumber_(year)) + 1;
  props.setProperty(key, String(next));
  return SYSTEM.ID_PREFIX + year + '-' + String(next).padStart(3, '0');
}

function maxExistingNumber_(year) {
  const sheet = getSheet_(SHEETS.STUDENTS);
  const col = headerMap_(sheet)['Research ID'];
  const last = sheet.getLastRow();
  if (!col || last < 2) return 0;
  const re = new RegExp('^' + SYSTEM.ID_PREFIX + year + '-(\\d+)$');
  let max = 0;
  sheet.getRange(2, col, last - 1, 1).getValues().forEach(function (r) {
    const m = re.exec(String(r[0]).trim());
    if (m) max = Math.max(max, parseInt(m[1], 10));
  });
  return max;
}

/* ================================================================
   GOOGLE DRIVE REPOSITORY
   Root / 2026 / BA Humanities / KMC-HSSD-RES-2026-001 - Name / 01_Profile ...
   ================================================================ */

function createRepository_(researchId, studentName, program, year) {
  const root = getRootFolder_();
  const yearFolder = getOrCreateFolder_(root, String(year));
  const programFolder = getOrCreateFolder_(
    yearFolder, sanitizeName_(program) || SYSTEM.DEFAULT_PROGRAM_FOLDER);

  /* Reuse the folder if a previous attempt already created it */
  const existing = programFolder.getFolders();
  while (existing.hasNext()) {
    const f = existing.next();
    if (f.getName().indexOf(researchId + ' - ') === 0) {
      SUBFOLDERS.forEach(function (n) { getOrCreateFolder_(f, n); });
      return { id: f.getId(), url: f.getUrl(), folder: f };
    }
  }

  const folder = programFolder.createFolder(researchId + ' - ' + (sanitizeName_(studentName) || 'Student'));
  SUBFOLDERS.forEach(function (n) { folder.createFolder(n); });
  return { id: folder.getId(), url: folder.getUrl(), folder: folder };
}

function getRootFolder_() {
  const props = PropertiesService.getScriptProperties();
  const saved = props.getProperty('ROOT_FOLDER_ID');
  if (saved) {
    try {
      const f = DriveApp.getFolderById(saved);
      if (!f.isTrashed()) return f;
    } catch (err) { /* fall through and recreate */ }
  }
  const found = DriveApp.getFoldersByName(SYSTEM.ROOT_FOLDER_NAME);
  const folder = found.hasNext() ? found.next() : DriveApp.createFolder(SYSTEM.ROOT_FOLDER_NAME);
  props.setProperty('ROOT_FOLDER_ID', folder.getId());
  return folder;
}

function getOrCreateFolder_(parent, name) {
  const it = parent.getFoldersByName(name);
  return it.hasNext() ? it.next() : parent.createFolder(name);
}

function shareFolder_(folder, emails, researchId) {
  emails.forEach(function (addr) {
    if (!addr) return;
    try {
      folder.addEditor(addr);
    } catch (err) {
      logActivity_(researchId, 'Folder share failed', addr + ': ' + err.message, '', 'System');
    }
  });
}

function setFolderLink_(sheet, row, url) {
  const col = headerMap_(sheet)['Folder Link'];
  if (!col) return;
  const safe = String(url).replace(/"/g, '');
  sheet.getRange(row, col).setFormula('=HYPERLINK("' + safe + '","Open Folder")');
}

/** Menu utility: fills "Folder Link" for any student row that has a Folder URL. */
function refreshFolderLinks() {
  const sheet = getSheet_(SHEETS.STUDENTS);
  const map = headerMap_(sheet);
  const last = sheet.getLastRow();
  if (last < 2 || !map['Folder URL']) return;
  const urls = sheet.getRange(2, map['Folder URL'], last - 1, 1).getValues();
  let n = 0;
  urls.forEach(function (r, i) {
    if (r[0]) { setFolderLink_(sheet, i + 2, r[0]); n++; }
  });
  logActivity_('SYSTEM', 'Folder links rebuilt', n + ' rows', '', 'Menu');
  notify_('Folder links rebuilt for ' + n + ' students.');
}

/* ================================================================
   SUPERVISOR ASSIGNMENT
   1. Student's preferred supervisor (if listed and active)
   2. Otherwise best match on program + research area, least loaded first
   3. Otherwise "To Be Assigned" and the admin is alerted
   ================================================================ */

function assignSupervisor_(preferred, program, areaText) {
  const sheet = getSheet_(SHEETS.SUPERVISORS);
  const map = headerMap_(sheet);
  const last = sheet.getLastRow();
  const defMax = Number(getSetting_('DEFAULT_MAX_STUDENTS', 10)) || 10;
  const TBA = { name: 'To Be Assigned', email: '' };

  const list = [];
  if (last >= 2) {
    sheet.getRange(2, 1, last - 1, sheet.getLastColumn()).getValues().forEach(function (r, i) {
      const get = function (h) { return map[h] ? r[map[h] - 1] : ''; };
      const name = String(get('Supervisor Name')).trim();
      if (!name) return;
      list.push({
        row: i + 2,
        name: name,
        email: String(get('Email')).trim(),
        program: String(get('Program')).trim(),
        areas: String(get('Research Areas')),
        max: Number(get('Maximum Students')) || defMax,
        cur: Number(get('Current Students')) || 0,
        active: (String(get('Status')).trim() || 'Active').toLowerCase() === 'active'
      });
    });
  }

  const bump = function (s) {
    if (map['Current Students']) sheet.getRange(s.row, map['Current Students']).setValue(s.cur + 1);
    return { name: s.name, email: s.email };
  };

  /* 1. Preference */
  const pref = String(preferred || '').trim().toLowerCase();
  if (pref) {
    const hit = list.filter(function (s) {
      return s.active && (s.name.toLowerCase() === pref || s.email.toLowerCase() === pref);
    })[0];
    if (hit) {
      if (hit.cur >= hit.max) {
        logActivity_('SYSTEM', 'Supervisor over capacity', hit.name + ' has ' + hit.cur + '/' + hit.max, '', 'System');
      }
      return bump(hit);
    }
    return { name: String(preferred).trim(), email: '' };
  }

  /* 2. Automatic */
  const prog = String(program || '').toLowerCase();
  const area = String(areaText || '').toLowerCase();
  const scored = list.filter(function (s) {
    if (!s.active || s.cur >= s.max) return false;
    return !s.program || s.program.toLowerCase().indexOf(prog) !== -1 ||
      (prog && prog.indexOf(s.program.toLowerCase()) !== -1);
  }).map(function (s) {
    let score = s.program ? 1 : 0.5;
    splitList_(s.areas).forEach(function (k) {
      if (k && area.indexOf(k) !== -1) score += 2;
    });
    return { s: s, score: score, load: s.cur / s.max };
  }).sort(function (a, b) {
    return (b.score - a.score) || (a.load - b.load) || a.s.name.localeCompare(b.s.name);
  });

  if (scored.length) return bump(scored[0].s);

  /* 3. Nobody available */
  sendAdminAlert_('KMC-HSSD: no supervisor available',
    'A student registered for "' + program + '" but no active supervisor with free capacity was found. ' +
    'Please assign one manually in 01_Students.');
  return TBA;
}

/** Menu utility: recomputes Current Students from the Students sheet. */
function recountSupervisorLoads() {
  const sup = getSheet_(SHEETS.SUPERVISORS);
  const stu = getSheet_(SHEETS.STUDENTS);
  const sMap = headerMap_(sup);
  const tMap = headerMap_(stu);
  if (!sMap['Supervisor Name'] || !sMap['Current Students'] || !tMap['Supervisor']) return;

  const counts = {};
  const sLast = stu.getLastRow();
  if (sLast >= 2) {
    stu.getRange(2, tMap['Supervisor'], sLast - 1, 1).getValues().forEach(function (r) {
      const k = String(r[0]).trim().toLowerCase();
      if (k) counts[k] = (counts[k] || 0) + 1;
    });
  }
  const last = sup.getLastRow();
  if (last < 2) return;
  const names = sup.getRange(2, sMap['Supervisor Name'], last - 1, 1).getValues();
  names.forEach(function (r, i) {
    sup.getRange(i + 2, sMap['Current Students']).setValue(counts[String(r[0]).trim().toLowerCase()] || 0);
  });
  logActivity_('SYSTEM', 'Supervisor loads recounted', '', '', 'Menu');
  notify_('Supervisor loads recounted.');
}

/* ================================================================
   PROGRESS TRACKING
   ================================================================ */

function updateProgress_(data) {
  const id = requireId_(data.researchId);
  const stage = String(data.stage || data.stepTitle || '').trim();
  if (!stage) throw new Error('Stage is required.');
  const status = String(data.status || 'In Progress').trim();

  return withLock_(function () {
    const rec = getStudentRecord_(id);
    const pct = resolvePercent_(data.progress, stage, status);
    addProgress_(rec, {
      step: data.step || stageIndex_(stage),
      stage: stage,
      status: status,
      pct: pct,
      remarks: data.comments || data.remarks || '',
      by: data.updatedBy || data.supervisor || 'Web API',
      next: data.nextAction || ''
    }, 'Web API');
    return { success: true, message: 'Progress saved successfully.', researchId: id, progress: pct };
  });
}

/** Writes the history row, refreshes the student row, logs, notifies. Hold the lock. */
function addProgress_(rec, p, source) {
  const now = new Date();
  appendRecord_(getSheet_(SHEETS.PROGRESS), {
    'Timestamp': now,
    'Research ID': rec.data['Research ID'],
    'Student Name': rec.data['Student Name'],
    'Step': p.step,
    'Stage': p.stage,
    'Status': p.status,
    'Progress %': p.pct,
    'Remarks': p.remarks,
    'Updated By': p.by,
    'Next Action': p.next,
    'Supervisor': rec.data['Supervisor']
  });

  updateRow_(rec.sheet, rec.row, {
    'Status': p.status,
    'Current Stage': p.stage,
    'Progress %': p.pct,
    'Last Updated': now
  });

  logActivity_(rec.data['Research ID'], 'Progress updated',
    p.stage + ' | ' + p.status + ' | ' + p.pct + '%', p.by, source);

  const notifyOn = String(getSetting_('NOTIFY_ON_PROGRESS', 'TRUE')).toUpperCase() === 'TRUE';
  const key = ['Approved', 'Revision Required', 'Rejected', 'Completed'];
  if (notifyOn && key.indexOf(p.status) !== -1) {
    sendProgressEmail_(rec.data, p);
  }
}

function getProgress_(researchId) {
  const id = requireId_(researchId);
  const sheet = getSheet_(SHEETS.PROGRESS);
  const rows = filterRows_(sheet, 'Research ID', id).reverse();
  return { success: true, researchId: id, progress: rows };
}

function resolvePercent_(given, stage, status) {
  const n = Number(given);
  if (given !== undefined && given !== null && given !== '' && isFinite(n)) {
    return Math.max(0, Math.min(100, Math.round(n)));
  }
  const s = STAGES.filter(function (x) { return x.title.toLowerCase() === stage.toLowerCase(); })[0];
  if (!s) return 0;
  return status === 'Revision Required' ? Math.max(0, s.pct - 10) : s.pct;
}

function stageIndex_(stage) {
  for (let i = 0; i < STAGES.length; i++) {
    if (STAGES[i].title.toLowerCase() === stage.toLowerCase()) return i + 1;
  }
  return '';
}

/* ================================================================
   DEPARTMENT APPROVAL
   ================================================================ */

function departmentApproval_(data) {
  const id = requireId_(data.researchId);
  const decision = String(data.decision || '').trim();
  if (DECISIONS.indexOf(decision) === -1) {
    throw new Error('Decision must be one of: ' + DECISIONS.join(', '));
  }

  return withLock_(function () {
    const rec = getStudentRecord_(id);
    const approvalNo = decision === 'Approved'
      ? 'KMC-HSSD-APP-' + id.replace(SYSTEM.ID_PREFIX, '') : '';

    appendRecord_(getSheet_(SHEETS.APPROVAL), {
      'Timestamp': new Date(),
      'Research ID': id,
      'Student Name': rec.data['Student Name'],
      'Decision': decision,
      'Comments': data.comments || '',
      'Approved By': data.approvedBy || '',
      'Approval Date': data.approvalDate || new Date(),
      'Approval Number': approvalNo
    });

    logActivity_(id, 'Department decision', decision + (data.comments ? ' | ' + data.comments : ''),
      data.approvedBy || '', 'Web API');

    const next = decision === 'Approved'
      ? { stage: 'Department Approval', next: 'Begin data collection' }
      : { stage: 'Proposal', next: decision === 'Revision Required' ? 'Revise and resubmit proposal' : 'Contact supervisor' };

    addProgress_(rec, {
      step: stageIndex_(next.stage),
      stage: next.stage,
      status: decision,
      pct: resolvePercent_(null, next.stage, decision),
      remarks: data.comments || '',
      by: data.approvedBy || 'Department',
      next: next.next
    }, 'Web API');

    return { success: true, message: 'Department decision saved.', approvalNumber: approvalNo };
  });
}

/* ================================================================
   FINAL SUBMISSION
   ================================================================ */

function finalSubmission_(data) {
  const id = requireId_(data.researchId);
  const title = String(data.title || '').trim();
  if (!title) throw new Error('Report title is required.');

  return withLock_(function () {
    const rec = getStudentRecord_(id);

    appendRecord_(getSheet_(SHEETS.FINAL), {
      'Timestamp': new Date(),
      'Research ID': id,
      'Student Name': rec.data['Student Name'],
      'Report Title': title,
      'File URL': data.fileUrl || '',
      'Submitted By': data.submittedBy || rec.data['Student Name'],
      'Status': 'Submitted'
    });

    /* Best effort: move the Drive file into 07_Final_Report */
    const moved = moveIntoFinalReport_(data.fileUrl, rec.data['Folder ID'], id);

    addProgress_(rec, {
      step: stageIndex_('Final Submission'),
      stage: 'Final Submission',
      status: 'Submitted',
      pct: 95,
      remarks: 'Final report submitted: ' + title + (moved ? ' (filed in 07_Final_Report)' : ''),
      by: data.submittedBy || rec.data['Student Name'],
      next: 'Supervisor evaluation'
    }, 'Web API');

    logActivity_(id, 'Final submission', title, data.submittedBy || '', 'Web API');
    return { success: true, message: 'Final submission registered.', filed: moved };
  });
}

function moveIntoFinalReport_(fileUrl, folderId, researchId) {
  try {
    const m = /[-\w]{25,}/.exec(String(fileUrl || ''));
    if (!m || !folderId) return false;
    const target = getOrCreateFolder_(DriveApp.getFolderById(folderId), '07_Final_Report');
    DriveApp.getFileById(m[0]).moveTo(target);
    return true;
  } catch (err) {
    logActivity_(researchId, 'Could not file final report', err.message, '', 'System');
    return false;
  }
}

/* ================================================================
   READ API
   ================================================================ */

function getStudents_() {
  const sheet = getSheet_(SHEETS.STUDENTS);
  const last = sheet.getLastRow();
  if (last < 2) return { success: true, students: [] };
  const values = sheet.getRange(1, 1, last, sheet.getLastColumn()).getDisplayValues();
  const headers = values[0];
  return {
    success: true,
    students: values.slice(1).map(function (r) {
      const o = {};
      headers.forEach(function (h, i) { o[h] = r[i]; });
      return o;
    })
  };
}

function getStudent_(researchId) {
  const id = requireId_(researchId);
  const sheet = getSheet_(SHEETS.STUDENTS);
  const row = findRow_(sheet, 'Research ID', id);
  if (!row) return { success: false, message: 'Research record not found.' };
  return { success: true, student: rowToObject_(sheet, row) };
}

function getActivity_(researchId, limit) {
  const sheet = getSheet_(SHEETS.LOG);
  let rows = researchId ? filterRows_(sheet, 'Research ID', String(researchId).trim())
                        : filterRows_(sheet, null, null);
  rows = rows.reverse().slice(0, Math.min(Number(limit) || 100, 500));
  return { success: true, activity: rows };
}

function getSupervisors_() {
  const sheet = getSheet_(SHEETS.SUPERVISORS);
  return { success: true, supervisors: filterRows_(sheet, null, null) };
}

/* ================================================================
   ACTIVITY LOG
   ================================================================ */

function logActivity_(researchId, action, details, user, source) {
  try {
    const sheet = getSpreadsheet_().getSheetByName(SHEETS.LOG);
    if (!sheet) return;
    appendRecord_(sheet, {
      'Timestamp': new Date(),
      'Research ID': researchId || '',
      'Action': action || '',
      'Details': details || '',
      'User': user || safeUserEmail_(),
      'Source': source || ''
    });
  } catch (err) {
    console.error('logActivity_ failed: ' + err.message);
  }
}

function safeUserEmail_() {
  try {
    return Session.getActiveUser().getEmail() || Session.getEffectiveUser().getEmail() || 'SYSTEM';
  } catch (err) {
    return 'SYSTEM';
  }
}

/* ================================================================
   EMAIL
   ================================================================ */

function sendStudentRegistrationEmail_(i) {
  const subject = 'KMC-HSSD Research Registration - ' + i.researchId;
  const text =
    'Dear ' + i.studentName + ',\n\n' +
    'Your research registration at ' + SYSTEM.ORG + ' is complete.\n\n' +
    'Department: ' + SYSTEM.DEPT + '\n' +
    'Research ID: ' + i.researchId + '\n' +
    'Supervisor: ' + i.supervisorName + '\n' +
    'Supervisor email: ' + (i.supervisorEmail || 'To be assigned') + '\n' +
    'Research folder: ' + i.folderUrl + '\n\n' +
    'Next steps:\n1. Submit your research topic and problem statement.\n' +
    '2. Prepare your research proposal.\n3. Meet your supervisor.\n\n' +
    'Please quote your Research ID in all research communication.\n\n' +
    'Regards,\n' + SYSTEM.DEPT + '\n' + SYSTEM.ORG;
  const html = emailShell_('Research Registration Complete',
    '<p>Dear ' + esc_(i.studentName) + ',</p>' +
    '<p>Your research registration at ' + esc_(SYSTEM.ORG) + ' is complete.</p>' +
    kvTable_([
      ['Research ID', '<b>' + esc_(i.researchId) + '</b>'],
      ['Supervisor', esc_(i.supervisorName)],
      ['Supervisor email', esc_(i.supervisorEmail || 'To be assigned')]
    ]) +
    button_('Open research folder', i.folderUrl) +
    '<p><b>Next steps</b></p><ol><li>Submit your research topic and problem statement.</li>' +
    '<li>Prepare your research proposal.</li><li>Meet your supervisor.</li></ol>' +
    '<p>Please quote your Research ID in all research communication.</p>');
  return sendMail_(i.email, subject, text, html, i.researchId, 'Student registration email');
}

function sendSupervisorAssignmentEmail_(i) {
  const subject = 'New research student assigned - ' + i.researchId;
  const text =
    'Dear ' + i.supervisorName + ',\n\n' +
    'A new research student has been registered under your supervision.\n\n' +
    'Student: ' + i.studentName + '\nResearch ID: ' + i.researchId + '\n' +
    'Topic: ' + (i.researchTopic || 'Not yet submitted') + '\n' +
    'Research folder: ' + i.folderUrl + '\n\n' +
    'Regards,\n' + SYSTEM.DEPT + '\n' + SYSTEM.ORG;
  const html = emailShell_('New Student Assigned',
    '<p>Dear ' + esc_(i.supervisorName) + ',</p>' +
    '<p>A new research student has been registered under your supervision.</p>' +
    kvTable_([
      ['Student', esc_(i.studentName)],
      ['Research ID', '<b>' + esc_(i.researchId) + '</b>'],
      ['Topic', esc_(i.researchTopic || 'Not yet submitted')]
    ]) + button_('Open research folder', i.folderUrl));
  return sendMail_(i.supervisorEmail, subject, text, html, i.researchId, 'Supervisor assignment email');
}

function sendProgressEmail_(student, p) {
  const subject = 'Research update (' + p.status + ') - ' + student['Research ID'];
  const text =
    'Dear ' + student['Student Name'] + ',\n\n' +
    'Your research status has been updated.\n\n' +
    'Research ID: ' + student['Research ID'] + '\nStage: ' + p.stage + '\n' +
    'Status: ' + p.status + '\nProgress: ' + p.pct + '%\n' +
    (p.remarks ? 'Comments: ' + p.remarks + '\n' : '') +
    (p.next ? 'Next action: ' + p.next + '\n' : '') +
    '\nRegards,\n' + SYSTEM.DEPT;
  const html = emailShell_('Research Status Update',
    '<p>Dear ' + esc_(student['Student Name']) + ',</p><p>Your research status has been updated.</p>' +
    kvTable_([
      ['Research ID', '<b>' + esc_(student['Research ID']) + '</b>'],
      ['Stage', esc_(p.stage)],
      ['Status', '<b>' + esc_(p.status) + '</b>'],
      ['Progress', esc_(String(p.pct)) + '%'],
      ['Comments', esc_(p.remarks || '-')],
      ['Next action', esc_(p.next || '-')]
    ]));
  return sendMail_(student['Email'], subject, text, html, student['Research ID'], 'Progress email');
}

function sendAdminAlert_(subject, body) {
  const admin = String(getSetting_('ADMIN_EMAIL', '')).trim();
  if (!admin) return;
  try {
    MailApp.sendEmail({ to: admin, subject: subject, body: body, name: 'KMC-HSSD System' });
  } catch (err) {
    console.error('Admin alert failed: ' + err.message);
  }
}

function sendMail_(to, subject, text, html, researchId, label) {
  if (!to) return false;
  if (String(getSetting_('SEND_EMAILS', 'TRUE')).toUpperCase() !== 'TRUE') {
    logActivity_(researchId, label + ' skipped', 'SEND_EMAILS is FALSE', '', 'System');
    return false;
  }
  try {
    if (MailApp.getRemainingDailyQuota() < 1) throw new Error('Daily mail quota exhausted.');
    const opts = {
      to: to, subject: subject, body: text, htmlBody: html,
      name: String(getSetting_('SENDER_NAME', 'KMC-HSSD Research Office'))
    };
    const reply = String(getSetting_('REPLY_TO', '')).trim();
    if (reply) opts.replyTo = reply;
    MailApp.sendEmail(opts);
    logActivity_(researchId, label + ' sent', to, '', 'System');
    return true;
  } catch (err) {
    logActivity_(researchId, label + ' FAILED', to + ': ' + err.message, '', 'System');
    return false;
  }
}

function emailShell_(title, inner) {
  return '<div style="font-family:Arial,sans-serif;max-width:560px;margin:auto;color:#1d2a26">' +
    '<div style="background:#0f6b57;color:#fff;padding:14px 18px;border-radius:8px 8px 0 0">' +
    '<div style="font-size:12px;opacity:.85">' + esc_(SYSTEM.ORG) + '</div>' +
    '<div style="font-size:18px;font-weight:bold">' + esc_(title) + '</div></div>' +
    '<div style="border:1px solid #dcd8cc;border-top:0;padding:18px;border-radius:0 0 8px 8px;line-height:1.5">' +
    inner + '<hr style="border:0;border-top:1px solid #dcd8cc;margin:18px 0">' +
    '<div style="font-size:12px;color:#66736e">' + esc_(SYSTEM.DEPT) + '</div></div></div>';
}

function kvTable_(pairs) {
  return '<table style="border-collapse:collapse;width:100%;margin:10px 0">' + pairs.map(function (p) {
    return '<tr><td style="padding:6px 8px;border-bottom:1px solid #eee;color:#66736e;width:140px">' + p[0] +
      '</td><td style="padding:6px 8px;border-bottom:1px solid #eee">' + p[1] + '</td></tr>';
  }).join('') + '</table>';
}

function button_(label, url) {
  return '<p><a href="' + esc_(url) + '" style="background:#0f6b57;color:#fff;padding:10px 16px;' +
    'border-radius:6px;text-decoration:none;display:inline-block">' + esc_(label) + '</a></p>';
}

/* ================================================================
   HEALTH CHECK
   ================================================================ */

function runHealthCheck() {
  const lines = [];
  const ok = function (c, m) { lines.push((c ? 'OK    ' : 'FAIL  ') + m); };
  const ss = getSpreadsheet_();

  Object.keys(SCHEMA).forEach(function (name) {
    const sh = ss.getSheetByName(name);
    if (!sh) { ok(false, 'Sheet missing: ' + name); return; }
    const map = headerMap_(sh);
    const missing = SCHEMA[name].filter(function (h) { return !map[h]; });
    ok(!missing.length, name + (missing.length ? ' missing columns: ' + missing.join(', ') : ''));
  });

  try { ok(!!getRootFolder_().getId(), 'Root Drive folder reachable'); }
  catch (err) { ok(false, 'Root Drive folder: ' + err.message); }

  const hasTrigger = ScriptApp.getProjectTriggers().some(function (t) {
    return t.getHandlerFunction() === 'onFormSubmit';
  });
  ok(hasTrigger, 'Form-submit trigger installed');

  const sup = getSheet_(SHEETS.SUPERVISORS);
  ok(sup.getLastRow() > 1, 'At least one supervisor listed');
  ok(!!String(getSetting_('ADMIN_EMAIL', '')).trim(), 'ADMIN_EMAIL set');
  lines.push('INFO  Mail quota remaining today: ' + MailApp.getRemainingDailyQuota());
  lines.push('INFO  Next Research ID: ' + SYSTEM.ID_PREFIX + academicYear_() + '-' +
    String(Math.max(Number(PropertiesService.getScriptProperties().getProperty('COUNTER_' + academicYear_())) || 0,
      maxExistingNumber_(academicYear_())) + 1).padStart(3, '0'));

  logActivity_('SYSTEM', 'Health check', lines.join(' | '), '', 'Menu');
  notify_(lines.join('\n'));
  return lines;
}

/* ================================================================
   SHEET HELPERS (all column access is by header name)
   ================================================================ */

function getSpreadsheet_() {
  const id = PropertiesService.getScriptProperties().getProperty('SPREADSHEET_ID');
  if (id) return SpreadsheetApp.openById(id);
  const active = SpreadsheetApp.getActiveSpreadsheet();
  if (!active) throw new Error('Spreadsheet not found. Run setupSystem() from the spreadsheet menu first.');
  return active;
}

function getSheet_(name) {
  const sh = getSpreadsheet_().getSheetByName(name);
  if (!sh) throw new Error('Sheet not found: ' + name + '. Run setupSystem().');
  return sh;
}

function ensureSheet_(ss, name, headers) {
  let sh = ss.getSheetByName(name);
  if (!sh) sh = ss.insertSheet(name);
  if (sh.getLastRow() === 0 || sh.getLastColumn() === 0) {
    sh.getRange(1, 1, 1, headers.length).setValues([headers]);
    return sh;
  }
  const existing = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0].map(function (h) { return String(h).trim(); });
  const missing = headers.filter(function (h) { return existing.indexOf(h) === -1; });
  if (missing.length) {
    sh.getRange(1, existing.length + 1, 1, missing.length).setValues([missing]);
  }
  return sh;
}

function headerMap_(sheet) {
  const n = sheet.getLastColumn();
  const map = {};
  if (n < 1) return map;
  sheet.getRange(1, 1, 1, n).getValues()[0].forEach(function (h, i) {
    const k = String(h).trim();
    if (k) map[k] = i + 1;
  });
  return map;
}

function appendRecord_(sheet, rec) {
  const map = headerMap_(sheet);
  const n = sheet.getLastColumn();
  const row = new Array(n).fill('');
  Object.keys(rec).forEach(function (k) {
    if (map[k]) row[map[k] - 1] = safeCell_(rec[k]);
  });
  const r = sheet.getLastRow() + 1;
  sheet.getRange(r, 1, 1, n).setValues([row]);
  return r;
}

function updateRow_(sheet, row, rec) {
  const map = headerMap_(sheet);
  Object.keys(rec).forEach(function (k) {
    if (map[k]) sheet.getRange(row, map[k]).setValue(safeCell_(rec[k]));
  });
}

/** Returns the sheet row number whose column `header` equals `value` (case-insensitive), or 0. */
function findRow_(sheet, header, value) {
  const col = headerMap_(sheet)[header];
  const last = sheet.getLastRow();
  if (!col || last < 2) return 0;
  const target = String(value).trim().toLowerCase();
  const vals = sheet.getRange(2, col, last - 1, 1).getValues();
  for (let i = 0; i < vals.length; i++) {
    if (String(vals[i][0]).trim().toLowerCase() === target) return i + 2;
  }
  return 0;
}

function rowToObject_(sheet, row) {
  const n = sheet.getLastColumn();
  const headers = sheet.getRange(1, 1, 1, n).getValues()[0];
  const vals = sheet.getRange(row, 1, 1, n).getDisplayValues()[0];
  const o = {};
  headers.forEach(function (h, i) { if (String(h).trim()) o[String(h).trim()] = vals[i]; });
  return o;
}

/** All rows as objects; if header is null returns every row. */
function filterRows_(sheet, header, value) {
  const last = sheet.getLastRow();
  if (last < 2) return [];
  const n = sheet.getLastColumn();
  const all = sheet.getRange(1, 1, last, n).getDisplayValues();
  const headers = all[0].map(function (h) { return String(h).trim(); });
  const idx = header ? headers.indexOf(header) : -1;
  const target = header ? String(value).trim().toLowerCase() : '';
  const out = [];
  for (let r = 1; r < all.length; r++) {
    if (header && String(all[r][idx]).trim().toLowerCase() !== target) continue;
    const o = {};
    headers.forEach(function (h, i) { if (h) o[h] = all[r][i]; });
    out.push(o);
  }
  return out;
}

function getStudentRecord_(researchId) {
  const sheet = getSheet_(SHEETS.STUDENTS);
  const row = findRow_(sheet, 'Research ID', researchId);
  if (!row) throw new Error('Research ID not found: ' + researchId);
  return { sheet: sheet, row: row, data: rowToObject_(sheet, row) };
}

function requireId_(id) {
  const v = String(id || '').trim();
  if (!v) throw new Error('Research ID is required.');
  return v;
}

function formatSheets_(ss) {
  Object.keys(SCHEMA).forEach(function (name) {
    const sh = ss.getSheetByName(name);
    if (!sh) return;
    const n = sh.getLastColumn();
    sh.getRange(1, 1, 1, n).setFontWeight('bold').setBackground('#0f6b57').setFontColor('#ffffff');
    sh.setFrozenRows(1);
    const map = headerMap_(sh);
    if (map['Timestamp']) sh.getRange(2, map['Timestamp'], Math.max(sh.getMaxRows() - 1, 1), 1).setNumberFormat('yyyy-mm-dd hh:mm');
    if (map['Phone']) sh.getRange(2, map['Phone'], Math.max(sh.getMaxRows() - 1, 1), 1).setNumberFormat('@');
    sh.autoResizeColumns(1, n);
  });
  const st = ss.getSheetByName(SHEETS.STUDENTS);
  if (st) {
    const map = headerMap_(st);
    if (map['Progress %']) {
      st.getRange(2, map['Progress %'], Math.max(st.getMaxRows() - 1, 1), 1)
        .setDataValidation(SpreadsheetApp.newDataValidation().requireNumberBetween(0, 100).setAllowInvalid(false).build());
    }
  }
}

/* ================================================================
   SETTINGS
   ================================================================ */

let SETTINGS_MEMO_ = null;

function seedSettings_() {
  const sh = getSheet_(SHEETS.SETTINGS);
  DEFAULT_SETTINGS.forEach(function (s) {
    if (!findRow_(sh, 'Key', s[0])) appendRecord_(sh, { 'Key': s[0], 'Value': s[1], 'Description': s[2] });
  });
  SETTINGS_MEMO_ = null;
}

function getSetting_(key, fallback) {
  if (!SETTINGS_MEMO_) {
    SETTINGS_MEMO_ = {};
    try {
      const sh = getSpreadsheet_().getSheetByName(SHEETS.SETTINGS);
      if (sh && sh.getLastRow() > 1) {
        sh.getRange(2, 1, sh.getLastRow() - 1, 2).getValues().forEach(function (r) {
          if (String(r[0]).trim()) SETTINGS_MEMO_[String(r[0]).trim()] = r[1];
        });
      }
    } catch (err) { /* use fallbacks */ }
  }
  const v = SETTINGS_MEMO_[key];
  return (v === undefined || v === '') ? fallback : v;
}

function academicYear_() {
  return Number(getSetting_('ACADEMIC_YEAR', new Date().getFullYear())) || new Date().getFullYear();
}

/* ================================================================
   GENERAL UTILITIES
   ================================================================ */

function withLock_(fn) {
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    return fn();
  } finally {
    lock.releaseLock();
  }
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function notify_(msg) {
  console.log(msg);
  try { SpreadsheetApp.getUi().alert(msg); } catch (err) { /* no UI (trigger / web app) */ }
}

function normalizeFormData_(named) {
  const out = {};
  Object.keys(named).forEach(function (k) {
    const v = named[k];
    out[String(k).trim()] = Array.isArray(v) ? String(v[0] || '').trim() : String(v || '').trim();
  });
  return out;
}

function pick_(data, names) {
  for (let i = 0; i < names.length; i++) {
    const v = data[names[i]];
    if (v !== undefined && v !== null && String(v).trim() !== '') return String(v).trim();
  }
  return '';
}

function splitList_(s) {
  return String(s || '').toLowerCase().split(/[,;\/]/).map(function (x) { return x.trim(); }).filter(Boolean);
}

function sanitizeName_(name) {
  return String(name || '').replace(/[\\\/:*?"<>|#%{}]/g, '-').replace(/\s+/g, ' ').trim().substring(0, 80);
}

/** Stops spreadsheet formula injection from user-supplied text. */
function safeCell_(v) {
  if (typeof v === 'string' && /^[=+\-@]/.test(v)) return "'" + v;
  return v;
}

function esc_(s) {
  return String(s === undefined || s === null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/*******************************************************************
 * SETUP GUIDE
 * 1. Create a Google Sheet "KMC-HSSD Research Management Database".
 *    Extensions > Apps Script. Paste this file as Code.gs.
 *    Project Settings > tick "Show appsscript.json" and paste the
 *    provided appsscript.json.
 * 2. Reload the sheet. Menu "KMC-HSSD Research" > 1. Set up system.
 *    Approve the permissions.
 * 3. 10_Settings: set ADMIN_EMAIL (and SENDER_NAME / REPLY_TO).
 * 4. 07_Supervisors: add rows (Supervisor Name, Email, Program,
 *    Research Areas e.g. "history, heritage", Maximum Students,
 *    Status = Active).
 * 5. Create the registration Google Form. Question titles should match
 *    the names used in onFormSubmit (Student Name, Email, Phone,
 *    Program, Semester, Research Topic, Research Area,
 *    Preferred Supervisor ...). Link its responses to this
 *    spreadsheet (Responses > Link to Sheets).
 * 6. Menu > 2. Install form-submit trigger.
 * 7. Web API (optional): Deploy > New deployment > Web app,
 *    Execute as: Me, Who has access: Anyone. Set API_KEY in
 *    10_Settings to require a key on every request.
 *    Redeploy a NEW VERSION after every code change.
 * 8. Menu > Health check. Submit a test form entry.
 *******************************************************************/
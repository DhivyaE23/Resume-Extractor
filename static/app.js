const fileInput = document.getElementById('resumeFile');
const analyzeButton = document.getElementById('analyzeBtn');
const jobDescription = document.getElementById('jobDescription');
const message = document.getElementById('message');
const fileName = document.getElementById('fileName');
const dropZone = document.getElementById('dropZone');
const rolePreset = document.getElementById('rolePreset');
const loadRoleButton = document.getElementById('loadRoleBtn');

const roleDescriptions = {
  'software-engineer': `We are looking for a Software Engineer to build and maintain reliable applications. You will work with a team to design features, write clear code, review changes, and troubleshoot issues.

Relevant skills: Python, Java, C++, JavaScript, SQL, Git, GitHub, Linux.`,
  'frontend-developer': `We are looking for a Frontend Developer to build responsive, accessible web experiences. You will work with design and backend teammates to implement interfaces and improve usability.

Relevant skills: HTML, CSS, JavaScript, TypeScript, React, Angular, Next.js, Git, GitHub.`,
  'backend-developer': `We are looking for a Backend Developer to build APIs and services, work with databases, and help maintain dependable applications.

Relevant skills: Python, Java, Node.js, Express.js, FastAPI, Flask, Django, REST API, SQL, PostgreSQL, MongoDB, Redis, Docker.`,
  'data-analyst': `We are looking for a Data Analyst to prepare datasets, answer business questions, and communicate findings through reports and dashboards.

Relevant skills: SQL, Python, Excel, Power BI, Tableau, Power Query, DAX, Pandas, NumPy, Matplotlib, Seaborn, Data Analytics.`,
  'machine-learning': `We are looking for an entry-level Machine Learning practitioner to prepare data, build experiments, evaluate models, and explain results to teammates.

Relevant skills: Python, SQL, Machine Learning, Deep Learning, Artificial Intelligence, Data Science, Scikit-learn, TensorFlow, PyTorch, Pandas, NumPy, Matplotlib.`,
  'cloud-devops': `We are looking for a Cloud and DevOps Engineer to support deployments, automate repeatable tasks, and help operate reliable cloud services.

Relevant skills: AWS, Azure, Linux, Docker, Kubernetes, Terraform, Git, GitHub Actions, Python.`,
  'database-engineer': `We are looking for a Database Engineer to design, query, and maintain data stores, support application teams, and improve data reliability.

Relevant skills: SQL, PostgreSQL, MySQL, MongoDB, Redis, Python, Linux, AWS, Azure.`
};

function renderValues(container, values, className, emptyText) {
  container.replaceChildren();
  if (!values?.length) {
    const empty = document.createElement('span');
    empty.className = 'empty-note';
    empty.textContent = emptyText;
    container.append(empty);
    return;
  }
  values.forEach((value) => {
    const item = document.createElement(className === 'skill-tag' ? 'span' : 'li');
    item.className = className;
    item.textContent = value;
    container.append(item);
  });
}

function renderEvidence(container, evidence) {
  container.replaceChildren();
  if (!evidence?.length) {
    const empty = document.createElement('p');
    empty.className = 'empty-note';
    empty.textContent = 'No supporting resume lines found.';
    container.append(empty);
    return;
  }

  evidence.forEach(({ skill, excerpt }) => {
    const item = document.createElement('article');
    item.className = 'evidence-item';
    const label = document.createElement('strong');
    label.textContent = skill;
    const quote = document.createElement('p');
    quote.textContent = excerpt;
    item.append(label, quote);
    container.append(item);
  });
}

function showMessage(text = '') {
  message.textContent = text;
  message.hidden = !text;
}

function updateFile(file) {
  fileName.textContent = file ? `${file.name} · ${(file.size / 1024 / 1024).toFixed(1)} MB` : 'PDF only, up to 10 MB';
  showMessage('');
}

fileInput.addEventListener('change', () => {
  const file = fileInput.files[0];
  updateFile(file);
});

loadRoleButton.addEventListener('click', () => {
  const description = roleDescriptions[rolePreset.value];
  if (!description) {
    showMessage('Choose a career domain to load its job-description starter.');
    rolePreset.focus();
    return;
  }
  jobDescription.value = description;
  showMessage('');
  jobDescription.focus();
  jobDescription.setSelectionRange(jobDescription.value.length, jobDescription.value.length);
});

['dragenter', 'dragover'].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add('drag-over');
  });
});

['dragleave', 'drop'].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove('drag-over');
  });
});

dropZone.addEventListener('drop', (event) => {
  const [file] = event.dataTransfer.files;
  if (!file) return;
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    showMessage('Choose a PDF file to continue.');
    return;
  }
  const transfer = new DataTransfer();
  transfer.items.add(file);
  fileInput.files = transfer.files;
  updateFile(file);
});

function renderDetails(data) {
  document.getElementById('resultName').textContent = data.name || 'Not found';
  document.getElementById('resultEmail').textContent = data.email || 'Not found';
  document.getElementById('resultPhone').textContent = data.phone || 'Not found';
  document.getElementById('resultDates').textContent = data.dates?.join(', ') || 'Not found';
  document.getElementById('resultFilename').textContent = data.filename;

  renderValues(document.getElementById('resultSkills'), data.skills, 'skill-tag', 'No listed skills found');
  renderValues(document.getElementById('resultExperience'), data.experience, '', 'No experience details found');
  renderValues(document.getElementById('resultEducation'), data.education, '', 'No education details found');
  renderValues(document.getElementById('resultOrganizations'), data.organizations, '', 'No organizations found');
  renderValues(document.getElementById('matchedSkills'), data.matched_skills, 'skill-tag', 'No matching skills found');
  renderValues(document.getElementById('missingSkills'), data.missing_skills, 'skill-tag', 'No uncovered role skills');
  renderEvidence(document.getElementById('matchEvidence'), data.matched_skill_evidence);

  const score = Math.max(0, Math.min(100, Number(data.match_score) || 0));
  document.getElementById('matchScoreValue').innerHTML = `${score}<small>%</small>`;
  document.getElementById('scoreBar').style.width = `${score}%`;
  document.getElementById('matchedCount').textContent = data.matched_skills?.length || 0;
  document.getElementById('missingCount').textContent = data.missing_skills?.length || 0;
  document.getElementById('matchSummary').textContent = `${data.matched_skills?.length || 0} of ${(data.matched_skills?.length || 0) + (data.missing_skills?.length || 0)} recognized role skills found in this resume.`;

  const status = document.getElementById('resultStatus');
  status.textContent = 'Review complete';
  status.classList.add('complete');
}

analyzeButton.addEventListener('click', async () => {
  const file = fileInput.files[0];
  const description = jobDescription.value.trim();

  if (!file) {
    showMessage('Choose a PDF resume before starting the review.');
    fileInput.focus();
    return;
  }
  if (!file.name.toLowerCase().endsWith('.pdf') || file.size > 10 * 1024 * 1024) {
    showMessage('Choose a PDF file smaller than 10 MB.');
    return;
  }
  if (!description) {
    showMessage('Add the job description so the resume can be matched to the role.');
    jobDescription.focus();
    return;
  }

  showMessage('');
  analyzeButton.disabled = true;
  document.getElementById('buttonLabel').textContent = 'Reviewing…';

  const formData = new FormData();
  formData.append('file', file);
  formData.append('job_description', description);

  try {
    const response = await fetch('/analyze-resume', { method: 'POST', body: formData });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'The resume could not be analyzed.');
    renderDetails(data);
  } catch (error) {
    showMessage(error.message || 'Unable to reach the server. Check that the app is running and try again.');
  } finally {
    analyzeButton.disabled = false;
    document.getElementById('buttonLabel').textContent = 'Analyze resume';
  }
});

const fileInput = document.getElementById('resumeFile');
const analyzeButton = document.getElementById('analyzeBtn');
const jobDescription = document.getElementById('jobDescription');
const message = document.getElementById('message');
const fileName = document.getElementById('fileName');
const dropZone = document.getElementById('dropZone');
const templateButton = document.getElementById('templateBtn');

const sampleDescription = 'We are looking for a Python developer with experience in FastAPI, SQL, Docker, AWS, and machine learning. Candidates should be comfortable with API design, cloud deployment, and collaborating with product teams.';

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

templateButton.addEventListener('click', () => {
  jobDescription.value = sampleDescription;
  jobDescription.focus();
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

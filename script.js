const API_BASE = 'https://multi-agents-j5df.onrender.com';

const modeButtons = document.querySelectorAll('.mode-btn');
const forms = document.querySelectorAll('.input-form');
const fileForm = document.getElementById('fileForm');
const textForm = document.getElementById('textForm');
const emptyState = document.getElementById('emptyState');
const results = document.getElementById('results');
const requestError = document.getElementById('requestError');
const toast = document.getElementById('toast');

const resultFields = {
  headline: document.getElementById('headlineResult'),
  about: document.getElementById('aboutResult'),
  skills: document.getElementById('skillsResult'),
  keywords: document.getElementById('keywordsResult'),
  experience: document.getElementById('experienceResult'),
  headline_review: document.getElementById('headlineReview'),
  about_review: document.getElementById('aboutReview'),
  branding_review: document.getElementById('brandingReview'),
  networking_review: document.getElementById('networkingReview'),
  ats_score: document.getElementById('atsScore'),
  final_score: document.getElementById('finalScore')
};

function appendInlineMarkdown(parent, text) {
  const pattern = /(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)/g;
  let lastIndex = 0;

  text.replace(pattern, (match, _token, offset) => {
    parent.appendChild(document.createTextNode(text.slice(lastIndex, offset)));

    const element = document.createElement(match.startsWith('**') ? 'strong' : match.startsWith('`') ? 'code' : 'em');
    element.textContent = match.startsWith('**') ? match.slice(2, -2) : match.slice(1, -1);
    parent.appendChild(element);
    lastIndex = offset + match.length;
    return match;
  });

  parent.appendChild(document.createTextNode(text.slice(lastIndex)));
}

function renderFormattedContent(container, value) {
  container.replaceChildren();
  const lines = String(value || '').split(/\r?\n/);
  let paragraph = [];
  let activeList = null;

  function flushParagraph() {
    if (paragraph.length === 0) return;
    const element = document.createElement('p');
    appendInlineMarkdown(element, paragraph.join(' '));
    container.appendChild(element);
    paragraph = [];
  }

  lines.forEach((line) => {
    const trimmed = line.trim();
    if (!trimmed) {
      flushParagraph();
      activeList = null;
      return;
    }

    const heading = trimmed.match(/^#{1,3}\s+(.+)$/);
    const listItem = trimmed.match(/^(?:[-*•]\s+|\d+[.)]\s+)(.+)$/);
    const quote = trimmed.match(/^>\s?(.*)$/);

    if (heading) {
      flushParagraph();
      activeList = null;
      const element = document.createElement('h4');
      appendInlineMarkdown(element, heading[1]);
      container.appendChild(element);
    } else if (listItem) {
      flushParagraph();
      const ordered = /^\d+[.)]\s+/.test(trimmed);
      const listType = ordered ? 'ol' : 'ul';
      if (!activeList || activeList.tagName.toLowerCase() !== listType) {
        activeList = document.createElement(listType);
        container.appendChild(activeList);
      }
      const item = document.createElement('li');
      appendInlineMarkdown(item, listItem[1]);
      activeList.appendChild(item);
    } else if (quote) {
      flushParagraph();
      activeList = null;
      const element = document.createElement('blockquote');
      appendInlineMarkdown(element, quote[1]);
      container.appendChild(element);
    } else {
      activeList = null;
      paragraph.push(trimmed);
    }
  });

  flushParagraph();
}

function setMode(mode) {
  modeButtons.forEach((button) => {
    button.classList.toggle('active', button.dataset.mode === mode);
  });

  forms.forEach((form) => {
    form.classList.toggle('active', form.dataset.modeForm === mode);
  });
}

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.style.background = isError ? 'rgba(189, 31, 31, 0.92)' : 'rgba(18, 25, 38, 0.92)';
  toast.classList.add('show');

  clearTimeout(showToast.timeoutId);
  showToast.timeoutId = setTimeout(() => {
    toast.classList.remove('show');
  }, isError ? 6500 : 2600);
}

function renderTags(container, values) {
  container.innerHTML = '';

  if (!Array.isArray(values) || values.length === 0) {
    container.innerHTML = '<span class="tag subtle">No items found</span>';
    return;
  }

  values.forEach((item) => {
    const span = document.createElement('span');
    span.className = 'tag';
    span.textContent = item;
    container.appendChild(span);
  });
}

function renderExperience(container, experience) {
  container.replaceChildren();

  if (!experience || typeof experience !== 'object') {
    renderFormattedContent(container, experience || 'No experience data available.');
    return;
  }

  const entries = Array.isArray(experience)
    ? experience.map((item, index) => [item.company || `Experience ${index + 1}`, item])
    : Object.entries(experience);

  if (entries.length === 0) {
    renderFormattedContent(container, 'No experience data available.');
    return;
  }

  entries.forEach(([company, details]) => {
    const card = document.createElement('article');
    card.className = 'experience-card';

    if (!details || typeof details !== 'object') {
      const title = document.createElement('h4');
      title.textContent = company;
      card.appendChild(title);
      renderFormattedContent(card, details);
      container.appendChild(card);
      return;
    }

    const header = document.createElement('div');
    header.className = 'experience-header';
    const title = document.createElement('h4');
    title.textContent = company;
    header.appendChild(title);

    const role = details.role;
    if (role) {
      const roleElement = document.createElement('p');
      roleElement.className = 'experience-role';
      roleElement.textContent = role;
      header.appendChild(roleElement);
    }

    card.appendChild(header);

    const metadata = [details.duration, details.location].filter(Boolean);
    if (metadata.length > 0) {
      const meta = document.createElement('p');
      meta.className = 'experience-meta';
      meta.textContent = metadata.join(' · ');
      card.appendChild(meta);
    }

    if (Array.isArray(details.responsibilities) && details.responsibilities.length > 0) {
      const list = document.createElement('ul');
      details.responsibilities.forEach((responsibility) => {
        const item = document.createElement('li');
        item.textContent = responsibility;
        list.appendChild(item);
      });
      card.appendChild(list);
    }

    container.appendChild(card);
  });
}

function renderResult(data) {
  emptyState.classList.add('hidden');
  results.classList.remove('hidden');

  resultFields.headline.textContent = data.headline || 'No headline extracted';
  resultFields.about.textContent = data.about || 'No summary available';
  resultFields.ats_score.textContent = data.ats_score ?? 0;
  resultFields.final_score.textContent = data.final_score ?? 0;
  renderFormattedContent(resultFields.about_review, data.about_review || 'No review available');
  renderFormattedContent(resultFields.branding_review, data.branding_review || 'No review available');
  renderFormattedContent(resultFields.networking_review, data.networking_review || 'No review available');

  renderTags(resultFields.skills, data.skills || []);
  renderTags(resultFields.keywords, data.keywords || []);

  renderFormattedContent(resultFields.headline_review, data.headline_review || 'No review available');
  renderExperience(resultFields.experience, data.experience);
  document.getElementById('atsScoreBar').style.width = `${Math.max(0, Math.min(100, Number(data.ats_score) || 0))}%`;
  document.getElementById('finalScoreBar').style.width = `${Math.max(0, Math.min(100, Number(data.final_score) || 0))}%`;
}

async function submitFileForm(event) {
  event.preventDefault();

  const fileInput = document.getElementById('userFile');
  const file = fileInput.files[0];

  if (!file) {
    showToast('Please choose a PDF file first.', true);
    return;
  }

  const formData = new FormData();
  formData.append('user_file', file);

  await submitRequest(`${API_BASE}/formmodel`, formData, 'multipart/form-data');
}

async function submitTextForm(event) {
  event.preventDefault();

  const text = document.getElementById('inputText').value.trim();

  if (!text) {
    showToast('Please paste some text to analyze.', true);
    return;
  }

  await submitRequest(
    `${API_BASE}/textmodel`,
    JSON.stringify({ input_text: text }),
    'application/json',
    true
  );
}

async function submitRequest(url, payload, contentType, isJson = false) {
  requestError.classList.add('hidden');

  const submitButtons = document.querySelectorAll('.primary-btn');
  submitButtons.forEach((button) => {
    button.disabled = true;
    button.textContent = 'Analyzing...';
  });

  try {
    const options = {
      method: 'POST',
      body: payload
    };

    if (!isJson) {
      options.headers = { Accept: 'application/json' };
    } else {
      options.headers = { 'Content-Type': contentType, Accept: 'application/json' };
    }

    const response = await fetch(url, options);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.error || 'Request failed');
    }

    renderResult(data);
    showToast('Analysis complete.');
  } catch (error) {
    console.error(error);
    requestError.classList.remove('hidden');
  } finally {
    submitButtons.forEach((button) => {
      button.disabled = false;
      button.textContent = button.closest('form').dataset.modeForm === 'file'
        ? 'Analyze profile'
        : 'Analyze text';
    });
  }
}

modeButtons.forEach((button) => {
  button.addEventListener('click', () => setMode(button.dataset.mode));
});

fileForm.addEventListener('submit', submitFileForm);
textForm.addEventListener('submit', submitTextForm);

setMode('file');

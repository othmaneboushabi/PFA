const API_BASE = 'http://localhost:8000/api/v1';
const WS_BASE = 'ws://localhost:8000';

export const api = {
  health: () => fetch(API_BASE + '/health').then(r => r.json()),

  transcribe: (file, language) => {
    const form = new FormData();
    form.append('file', file);
    return fetch(API_BASE + '/transcribe?language=' + language, { method: 'POST', body: form }).then(r => r.json());
  },

  ner: (text, language) =>
    fetch(API_BASE + '/ner', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, language })
    }).then(r => r.json()),

  translate: (text, src_lang, tgt_lang) =>
    fetch(API_BASE + '/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, src_lang, tgt_lang })
    }).then(r => r.json()),

  process: (file, source_lang, target_lang) => {
    const form = new FormData();
    form.append('file', file);
    form.append('source_lang', source_lang);
    form.append('target_lang', target_lang);
    form.append('extract_entities', 'true');
    form.append('translate', 'true');
    form.append('enrich_glossary', source_lang !== 'ar' ? 'true' : 'false');
    return fetch(API_BASE + '/process', { method: 'POST', body: form }).then(r => r.json());
  },

  uploadGlossary: (file, format_type) => {
    const form = new FormData();
    form.append('file', file);
    form.append('format_type', format_type);
    return fetch(API_BASE + '/glossary/upload', { method: 'POST', body: form }).then(r => r.json());
  },

  searchGlossary: (term, source_lang, target_lang, fuzzy_threshold) =>
    fetch(API_BASE + '/glossary/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ term, source_lang, target_lang, fuzzy_threshold })
    }).then(r => r.json()),

  summarize: (text, num_points) =>
    fetch(API_BASE + '/summarize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, num_points })
    }).then(r => r.json()),

  processAcronyms: (text, source_lang, target_lang) =>
    fetch(API_BASE + '/acronyms/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, source_lang, target_lang })
    }).then(r => r.json()),
};

export const WS_URL = WS_BASE + '/ws/transcribe';

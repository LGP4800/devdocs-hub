const API = '/api';

async function checkHealth() {
  try {
    const r = await fetch(`${API}/health`);
    const d = await r.json();
    document.getElementById('status-dot').className = 'dot' + (d.status === 'ok' ? '' : ' error');
    document.getElementById('status-text').textContent = d.status === 'ok' ? 'API online' : 'API degraded';
  } catch {
    document.getElementById('status-dot').className = 'dot error';
    document.getElementById('status-text').textContent = 'API offline';
  }
}

async function loadSnippets() {
  const r = await fetch(`${API}/snippets`);
  const snippets = await r.json();
  const list = document.getElementById('snippets-list');
  if (snippets.length === 0) {
    list.innerHTML = '<div id="empty">Niciun snippet încă. Adaugă primul!</div>';
    return;
  }
  list.innerHTML = snippets.map(s => `
    <div class="snippet">
      <div class="snippet-header">
        <span class="snippet-title">${s.title}</span>
        <div style="display:flex;gap:8px;align-items:center">
          <span class="snippet-lang">${s.language}</span>
          <button class="delete-btn" onclick="deleteSnippet(${s.id})">delete</button>
        </div>
      </div>
      <div class="snippet-content">${s.content}</div>
      ${s.tags.length ? `<div class="snippet-tags">${s.tags.map(t => `<span class="tag">${t}</span>`).join('')}</div>` : ''}
    </div>
  `).join('');
}

async function createSnippet() {
  const title = document.getElementById('title').value.trim();
  const content = document.getElementById('content').value.trim();
  if (!title || !content) return alert('Title și content sunt obligatorii!');
  await fetch(`${API}/snippets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title,
      content,
      language: document.getElementById('language').value,
      tags: document.getElementById('tags').value.split(',').map(t => t.trim()).filter(Boolean)
    })
  });
  document.getElementById('title').value = '';
  document.getElementById('content').value = '';
  document.getElementById('tags').value = '';
  loadSnippets();
}

async function deleteSnippet(id) {
  await fetch(`${API}/snippets/${id}`, { method: 'DELETE' });
  await loadSnippets();
}

async function searchSnippets(query) {
  if (query.trim() === '') {
      loadSnippets();    // dacă e gol → arată toate
      return;
  }
  const r = await fetch(`${API}/snippets/search?q=${encodeURIComponent(query)}`);
  const snippets = await r.json();
  const list = document.getElementById('snippets-list');
  if (snippets.length === 0) {
      list.innerHTML = `<div id="empty">Niciun rezultat pentru "${query}"</div>`;
      return;
  }
  list.innerHTML = snippets.map(s => `
      <div class="snippet">
        <div class="snippet-header">
          <span class="snippet-title">${s.title}</span>
          <div style="display:flex;gap:8px;align-items:center">
            <span class="snippet-lang">${s.language}</span>
            <button class="delete-btn" onclick="deleteSnippet(${s.id})">delete</button>
          </div>
        </div>
        <div class="snippet-content">${s.content}</div>
        ${s.tags.length ? `<div class="snippet-tags">${s.tags.map(t => `<span class="tag">${t}</span>`).join('')}</div>` : ''}
      </div>
  `).join('');
}

checkHealth();
loadSnippets();
setInterval(checkHealth, 30000);
// Shared helpers for all modules
const PALETTE = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#84cc16'];

async function postJSON(url, data) {
    const res = await fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)});
    const json = await res.json();
    if (!res.ok) throw new Error(json.error || 'Request failed');
    return json;
}

function parseNums(text) {
    const t = text.trim();
    if (!t) return [];
    return t.split(/[\s,]+/).map(x => {
        const n = Number(x);
        if (Number.isNaN(n)) throw new Error(`"${x}" is not a number.`);
        return n;
    });
}

function esc(s) {
    return String(s).replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
}

function table(headers, rows) {
    return '<div class="scroll"><table class="data"><thead><tr>' + headers.map(h => `<th>${esc(h)}</th>`).join('') +
        '</tr></thead><tbody>' + rows.map(r => '<tr>' + r.map(c => `<td>${esc(c)}</td>`).join('') + '</tr>').join('') +
        '</tbody></table></div>';
}

function stat(label, value) {
    return `<div class="stat"><span>${esc(label)}</span><b>${esc(value)}</b></div>`;
}

function showError(el, msg) { el.textContent = msg; el.hidden = false; }

const _charts = {};
function drawChart(id, type, labels, datasets) {
    if (_charts[id]) _charts[id].destroy();
    _charts[id] = new Chart(document.getElementById(id), {type, data: {labels, datasets},
        options: {responsive: true, scales: {y: {beginAtZero: true}}}});
}

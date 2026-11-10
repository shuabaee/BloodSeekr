/* Blood type guide: choose a type, see who it can give to / receive from. */
document.addEventListener('DOMContentLoaded', () => {
  const data = JSON.parse(document.getElementById('compat-data')?.textContent || '{}');
  const picker = document.getElementById('type-picker');
  if (!picker) return;
  const give = document.getElementById('can-give');
  const get = document.getElementById('can-get');
  const hint = document.getElementById('compat-hint');
  const fill = (el, list) => {
    el.replaceChildren(...(list.length ? list : ['None']).map(code => { const s = document.createElement('span'); s.className = list.length ? 'chip' : 'chip muted'; s.textContent = code; return s; }));
  };
  const select = code => {
    picker.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.type === code)));
    document.querySelectorAll('.compat-table tbody tr').forEach(tr => tr.classList.toggle('is-selected', tr.querySelector('th').textContent.trim() === code));
    fill(give, data[code] || []);
    fill(get, Object.keys(data).filter(donor => (data[donor] || []).includes(code)));
    if (hint && code) hint.textContent = `Showing red cell compatibility for ${code}.`;
  };
  picker.addEventListener('click', e => { const b = e.target.closest('button[data-type]'); if (b) select(b.dataset.type); });
  select(document.getElementById('compat-result').dataset.initial || Object.keys(data)[0] || '');
});

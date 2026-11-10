/* Settings feature behaviour: radius quick picks and a live "N preferences enabled" summary. */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('settings-form');
  if (!form) return;
  const summary = document.getElementById('settings-summary');
  const radius = form.querySelector('input[name="match_radius_km"]');
  const toggles = Array.from(form.querySelectorAll('input[type="checkbox"]'));
  const picks = Array.from(form.querySelectorAll('[data-radius]'));

  const refresh = () => {
    const on = toggles.filter(t => t.checked).length;
    if (summary) summary.textContent = `${on} of ${toggles.length} options on`;
    picks.forEach(b => b.classList.toggle('secondary', b.dataset.radius !== radius?.value));
  };
  toggles.forEach(t => t.addEventListener('change', refresh));
  radius?.addEventListener('input', refresh);
  picks.forEach(b => b.addEventListener('click', () => { radius.value = b.dataset.radius; refresh(); }));
  refresh();
});

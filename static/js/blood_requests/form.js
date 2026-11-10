/* Blood request form: units stepper, date shortcuts and urgency hints. */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('request-form');
  if (!form) return;

  /* Units stepper */
  const units = form.querySelector('input[name="units_needed"]');
  if (units) {
    const make = (label, delta, text) => {
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'btn secondary stepper-btn'; b.textContent = text; b.setAttribute('aria-label', label);
      b.addEventListener('click', () => { units.value = Math.max(1, (parseInt(units.value, 10) || 0) + delta); });
      return b;
    };
    units.before(make('Fewer units', -1, '−'));
    units.after(make('More units', 1, '+'));
    if (!units.value) units.value = 1;
  }

  /* Date shortcuts; the date picker cannot go into the past */
  const date = form.querySelector('input[name="needed_date"]');
  const iso = d => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  if (date) {
    date.min = iso(new Date());
    form.querySelectorAll('[data-days]').forEach(b => b.addEventListener('click', () => {
      const d = new Date(); d.setDate(d.getDate() + Number(b.dataset.days)); date.value = iso(d);
    }));
  }

  /* Urgency hint */
  const urgency = form.querySelector('select[name="urgency"]');
  const hint = document.getElementById('urgency-hint');
  const texts = {
    routine: 'Routine: planned or non-critical. Donors are notified normally.',
    urgent: 'Urgent: needed within a few days. Pick a date that matches.',
    emergency: 'Emergency: needed right away. Donors with emergency alerts on are notified immediately. Please also contact the facility directly.',
  };
  if (urgency && hint) {
    const show = () => { if (texts[urgency.value]) hint.textContent = texts[urgency.value]; };
    urgency.addEventListener('change', show); show();
  }
});

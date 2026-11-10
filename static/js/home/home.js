/* Home feature behaviour: make whole attention rows easy to tap on touch devices. */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.attention-item').forEach(row => {
    const link = row.querySelector('a.btn');
    if (!link) return;
    row.style.cursor = 'pointer';
    row.addEventListener('click', event => { if (!event.target.closest('a,button')) link.click(); });
  });
});

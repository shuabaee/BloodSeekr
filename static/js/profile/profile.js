/* Profile feature behaviour: keep the availability wording in sync with the toggle. */
document.addEventListener('DOMContentLoaded', () => {
  const checkbox = document.getElementById('id_available_to_donate');
  const label = document.getElementById('availability-text');
  if (!checkbox || !label) return;
  const update = () => { label.textContent = checkbox.checked ? 'Available to donate' : 'Not available to donate right now'; };
  checkbox.addEventListener('change', update);
  update();
});

/* Register feature behaviour: live password checklist and a friendly match check. */
document.addEventListener('DOMContentLoaded', () => {
  const password = document.getElementById('password');
  const confirm = document.getElementById('confirm_password');
  const rules = document.getElementById('password-rules');
  if (!password || !confirm || !rules) return;
  const set = (name, ok) => rules.querySelector(`[data-rule="${name}"]`)?.classList.toggle('ok', ok);
  const update = () => {
    set('length', password.value.length >= 8);
    set('notnumeric', password.value.length > 0 && !/^\d+$/.test(password.value));
    set('match', confirm.value.length > 0 && confirm.value === password.value);
    confirm.setCustomValidity(confirm.value && confirm.value !== password.value ? 'Passwords do not match.' : '');
  };
  password.addEventListener('input', update);
  confirm.addEventListener('input', update);
  update();
});

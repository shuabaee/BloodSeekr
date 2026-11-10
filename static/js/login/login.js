/* Login feature behaviour: warn when Caps Lock is on while typing the password. */
document.addEventListener('DOMContentLoaded', () => {
  const password = document.getElementById('password');
  const warning = document.getElementById('caps-warning');
  if (!password || !warning) return;
  const check = event => { warning.hidden = !event.getModifierState?.('CapsLock'); };
  password.addEventListener('keydown', check);
  password.addEventListener('keyup', check);
  password.addEventListener('blur', () => { warning.hidden = true; });
});

/* Shared UI behaviour: small, dependency-free enhancements used by every feature. */
(() => {
  const ready = fn => document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', fn) : fn();

  ready(() => {
    /* Mobile navigation drawer */
    const toggles = document.querySelectorAll('[data-nav-toggle]');
    const setNav = open => {
      document.body.classList.toggle('nav-open', open);
      toggles.forEach(t => t.hasAttribute('aria-expanded') && t.setAttribute('aria-expanded', String(open)));
    };
    toggles.forEach(t => t.addEventListener('click', () => setNav(!document.body.classList.contains('nav-open'))));
    document.addEventListener('keydown', e => { if (e.key === 'Escape') setNav(false); });

    /* Show / hide password */
    document.querySelectorAll('[data-password-toggle]').forEach(button => {
      button.addEventListener('click', () => {
        const input = document.getElementById(button.dataset.passwordToggle);
        if (!input) return;
        const show = input.type === 'password';
        input.type = show ? 'text' : 'password';
        button.textContent = show ? 'Hide' : 'Show';
        button.setAttribute('aria-pressed', String(show));
      });
    });

    /* Dismissible messages; success messages fade out on their own */
    document.querySelectorAll('[data-dismissible]').forEach(box => {
      box.querySelector('.feedback-close')?.addEventListener('click', () => box.remove());
      if (box.classList.contains('success')) setTimeout(() => box.remove(), 7000);
    });

    /* Filter forms that submit as soon as a dropdown changes */
    document.querySelectorAll('form[data-autosubmit]').forEach(form => {
      form.querySelectorAll('select').forEach(select => select.addEventListener('change', () => form.requestSubmit()));
    });

    /* Turn <select data-pill-select> into tappable pills (the select stays as the source of truth) */
    document.querySelectorAll('select[data-pill-select]').forEach(select => {
      const wrap = document.createElement('div');
      wrap.className = 'pill-picker' + (select.dataset.pillSelect === 'compact' ? ' compact' : '');
      wrap.setAttribute('role', 'group');
      wrap.setAttribute('aria-label', select.getAttribute('aria-label') || 'Choose an option');
      const sync = () => wrap.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.value === select.value)));
      Array.from(select.options).filter(o => o.value).forEach(o => {
        const b = document.createElement('button');
        b.type = 'button'; b.textContent = o.textContent; b.dataset.value = o.value;
        b.addEventListener('click', () => { select.value = select.value === o.value && !select.required ? '' : o.value; select.dispatchEvent(new Event('change', {bubbles: true})); sync(); });
        wrap.append(b);
      });
      select.after(wrap); select.hidden = true; select.addEventListener('change', sync); sync();
    });

    /* Confirm dialog for destructive actions: <form data-confirm="Cancel this request?"> or on a button */
    let dialog;
    const ask = ({title, message, label}) => new Promise(resolve => {
      if (!dialog) {
        dialog = document.createElement('dialog'); dialog.className = 'confirm';
        dialog.innerHTML = '<form method="dialog"><h2></h2><p class="muted"></p><div class="actions"><button class="btn secondary" value="no">Go back</button><button class="btn" value="yes"></button></div></form>';
        document.body.append(dialog);
      }
      dialog.querySelector('h2').textContent = title || 'Are you sure?';
      dialog.querySelector('p').textContent = message || '';
      dialog.querySelector('[value=yes]').textContent = label || 'Confirm';
      dialog.addEventListener('close', () => resolve(dialog.returnValue === 'yes'), {once: true});
      dialog.showModal();
    });
    document.addEventListener('submit', async e => {
      const form = e.target, submitter = e.submitter;
      const source = submitter?.dataset.confirm ? submitter : (form.dataset.confirm ? form : null);
      if (source && !form.dataset.confirmed && typeof HTMLDialogElement !== 'undefined') {
        e.preventDefault();
        const ok = await ask({title: source.dataset.confirmTitle, message: source.dataset.confirm, label: source.dataset.confirmLabel});
        if (ok) { form.dataset.confirmed = '1'; form.requestSubmit(submitter); }
        return;
      }
      /* Prevent double submits and show progress */
      if (!e.defaultPrevented) setTimeout(() => (submitter || form.querySelector('button[type=submit],button:not([type])'))?.classList.add('is-loading'), 0);
    }, true);
  });
})();

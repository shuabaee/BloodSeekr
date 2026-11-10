/* Blood requests: share a request summary (never includes the patient's name). */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-share]').forEach(button => {
    const original = button.innerHTML;
    const flash = text => { button.textContent = text; setTimeout(() => { button.innerHTML = original; }, 2200); };
    button.addEventListener('click', async () => {
      const text = button.dataset.shareText;
      try {
        if (navigator.share) { await navigator.share({title: button.dataset.shareTitle, text}); return; }
        await navigator.clipboard.writeText(text);
        flash('Copied — paste it anywhere');
      } catch (error) {
        if (error?.name === 'AbortError') return;
        window.prompt('Copy this message:', text);
      }
    });
  });
});

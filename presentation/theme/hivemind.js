/* HIVEMIND workshop theme behaviour — simplified fork of the Lambda World 2025
   deck's hivemind.js. Removed: the dual-presenter (IG/IB) initials indicator
   and its slidechanged handler. Kept: bracketed h1/h2 headings and the footer
   logo. Adds a small top-right deck label. */

Reveal.on('ready', () => {
  // Bracket h1s (cyan) and h2s (red), except on the title slide.
  document.querySelectorAll('.reveal h1').forEach((h) => {
    if (h.dataset.bracketed || h.closest('.title-slide')) return;
    h.innerHTML =
      '<span style="color:#00c5db">[</span>' + h.innerHTML + '<span style="color:#00c5db">]</span>';
    h.dataset.bracketed = 'true';
  });
  document.querySelectorAll('.reveal h2').forEach((h) => {
    if (h.dataset.bracketed || h.closest('.title-slide')) return;
    h.innerHTML =
      '<span style="color:#f93030">[</span>' + h.innerHTML + '<span style="color:#f93030">]</span>';
    h.dataset.bracketed = 'true';
  });

  // Footer HIVEMIND logo (once).
  if (!document.querySelector('.reveal .footer-brand')) {
    const footer = document.createElement('div');
    footer.className = 'footer-brand';
    const img = document.createElement('img');
    img.src = 'assets/images/Logotype.svg';
    img.alt = 'HIVEMIND';
    footer.appendChild(img);
    document.querySelector('.reveal').appendChild(footer);
  }

  // Top-right deck label, taken from the document <title> (once).
  if (!document.querySelector('.reveal .presentation-title')) {
    const label = document.createElement('div');
    label.className = 'presentation-title';
    label.textContent = document.title || 'HIVEMIND Workshop';
    document.querySelector('.reveal').appendChild(label);
  }
});

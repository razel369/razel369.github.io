(async function() {
  try {
    const res = await fetch('/affiliates.json', { cache: 'no-cache' });
    if (!res.ok) return;
    const aff = await res.json();
    document.querySelectorAll('[data-aff]').forEach(function(el) {
      const slug = el.getAttribute('data-aff');
      const entry = aff[slug];
      if (entry && entry.href && entry.href !== '#') {
        el.setAttribute('href', entry.href);
        el.setAttribute('rel', 'sponsored noopener');
        el.setAttribute('target', '_blank');
      }
    });
  } catch (e) {
    /* affiliate.json missing or blocked - leave default # hrefs */
  }
})();

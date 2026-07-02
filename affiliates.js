// affiliates.js - runtime swap of `data-aff` placeholders + optional Skimlinks script injection.
// Designed so the user does ONE setup edit (affiliates.json) and the site handles everything.

(function() {
  // Wait until DOM ready so we don't run before the page is parsed.
  function ready(fn) {
    if (document.readyState !== 'loading') return fn();
    document.addEventListener('DOMContentLoaded', fn);
  }

  ready(async function() {
    let aff;
    try {
      const res = await fetch('/affiliates.json', { cache: 'no-cache' });
      if (!res.ok) return;
      aff = await res.json();
    } catch (e) { return; }

    // 1) Inject Skimlinks script if a publisher ID has been configured.
    const skim = aff && aff.networks && aff.networks.skimlinks;
    if (skim && skim.publisher_id && skim.publisher_id.trim()) {
      var s = document.createElement('script');
      s.async = true;
      s.src = 'https://s.skimresources.com/js/' + encodeURIComponent(skim.publisher_id.trim()) + '.skimlinks.js';
      s.setAttribute('data-skimlinks', '1');
      document.head.appendChild(s);
    }

    // 2) Build a flat slug -> href lookup combining direct + network entries.
    var lookup = Object.create(null);
    function index(obj) {
      if (!obj || typeof obj !== 'object') return;
      Object.keys(obj).forEach(function(k) {
        if (k.charAt(0) === '_') return;
        var v = obj[k];
        if (v && typeof v === 'object' && typeof v.href === 'string') lookup[k] = v.href;
      });
    }
    index(aff.direct_programs);
    index(aff.network_programs);

    // 3) Rewrite any element that opted in via data-aff="slug".
    document.querySelectorAll('[data-aff]').forEach(function(el) {
      var slug = el.getAttribute('data-aff');
      var href = lookup[slug];
      if (href && href !== '#') {
        el.setAttribute('href', href);
        el.setAttribute('rel', 'sponsored noopener');
        el.setAttribute('target', '_blank');
      } else {
        // No manual href: leave href as-is (Skimlinks will monetize the outbound hop if installed).
        el.setAttribute('rel', (el.getAttribute('rel') || '') + ' sponsored noopener');
      }
    });
  });
})();

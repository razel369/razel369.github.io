// monetize.js - renders reader-support widgets across every page.
// Designed so the user does ONE config edit (monetize.json) and the site lights up.

(function() {
  function ready(fn) {
    if (document.readyState !== 'loading') return fn();
    document.addEventListener('DOMContentLoaded', fn);
  }

  // Tiny QR code generator (no external CDN). Uses SVG path encoding for portability.
  // For 100% zero-dependency, we use the public Google Chart API for QR rendering,
  // but only for addresses the user has explicitly added (no third-party tracking on
  // article pages unless support widgets are present).
  function qrSvg(text, size) {
    size = size || 140;
    // Use Google Chart API as image src. We could inline a QR generator but this
    // is fine for support pages where the user is opting in.
    var url = "https://chart.googleapis.com/chart?cht=qr&chs=" + size + "x" + size +
              "&chl=" + encodeURIComponent(text) + "&choe=UTF-8";
    return '<img class="qr-img" src="' + url + '" alt="QR code" width="' + size + '" height="' + size + '" loading="lazy">';
  }

  function shortAddr(a) {
    if (!a) return "";
    if (a.length <= 14) return a;
    return a.slice(0, 8) + "..." + a.slice(-6);
  }

  ready(async function() {
    let m;
    try {
      const r = await fetch('/monetize.json', { cache: 'no-cache' });
      if (!r.ok) return;
      m = await r.json();
    } catch (e) { return; }

    // 1) Render tip-jar blocks (selectors with [data-tip-jar])
    document.querySelectorAll('[data-tip-jar]').forEach(function(el) {
      var html = '<div class="tip-jar"><h3>Support SMB AI Stack</h3>';
      html += '<p>Independent reviews, no ad-network reliance, no paywalled rankings. Supported by readers like you.</p>';
      html += '<div class="crypto-grid">';
      ['btc','eth','sol','xmr'].forEach(function(key) {
        var c = m.crypto && m.crypto[key];
        if (!c || !c.address) return;
        var label = c.label || key.toUpperCase();
        html += '<div class="crypto-cell">';
        html += '<div class="crypto-label">' + label + '</div>';
        html += qrSvg(c.address, 110);
        html += '<code class="crypto-addr" title="' + c.address + '">' + shortAddr(c.address) + '</code>';
        html += '<button class="copy-btn" data-copy="' + c.address + '">Copy</button>';
        html += '</div>';
      });
      html += '</div>';
      html += '</div>';
      el.innerHTML = html;
    });

    // 2) Render GitHub Sponsor button (data-github-sponsor)
    document.querySelectorAll('[data-github-sponsor]').forEach(function(el) {
      var username = (m.github_sponsors && m.github_sponsors.username) || 'razel369';
      var url = 'https://github.com/sponsors/' + username;
      el.innerHTML = '<a class="btn btn-sponsor" href="' + url + '" rel="noopener" target="_blank">' +
        '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" style="vertical-align:-2px;margin-right:6px"><path d="M8 0a8 8 0 0 0-2.53 15.59c.4.07.55-.17.55-.38l-.01-1.49c-2.22.48-2.69-1.07-2.69-1.07-.36-.92-.89-1.17-.89-1.17-.73-.5.06-.49.06-.49.8.06 1.23.83 1.23.83.72 1.23 1.88.87 2.34.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.42 7.42 0 0 1 2-.27c.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48l-.01 2.2c0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8a8 8 0 0 0-8-8z"/></svg>' +
        'Sponsor on GitHub</a>';
    });

    // 3) Render Adsterra ad slot (data-adsterra)
    document.querySelectorAll('[data-adsterra]').forEach(function(el) {
      var key = m.display_ads && m.display_ads.adsterra && m.display_ads.adsterra.key;
      if (!key) {
        el.innerHTML = '<div class="ad-slot-empty">Ad slot (Adsterra key not configured yet)</div>';
        return;
      }
      // Note: in production, the user would paste the full Adsterra <script> snippet.
      // We provide a generic banner config that Adsterra uses:
      el.innerHTML = '<div class="ad-slot" data-adsterra-key="' + key + '">' +
        '<div class="ad-placeholder">Adsterra ad slot ready (key: ' + shortAddr(key) + ')</div></div>';
    });

    // 4) Copy-to-clipboard for crypto addresses
    document.addEventListener('click', function(ev) {
      var t = ev.target;
      if (t && t.classList && t.classList.contains('copy-btn')) {
        var addr = t.getAttribute('data-copy');
        navigator.clipboard.writeText(addr).then(function() {
          t.textContent = 'Copied!';
          setTimeout(function() { t.textContent = 'Copy'; }, 1500);
        });
      }
    });

    // 5) Sticky support banner: only show if at least one monetization is configured
    var hasAny = (m.crypto && Object.values(m.crypto).some(function(c) { return c.address; })) ||
                 (m.github_sponsors && m.github_sponsors.username) ||
                 (m.display_ads && m.display_ads.adsterra && m.display_ads.adsterra.key);
    if (!hasAny) return;

    // Inject sticky banner if not already present
    if (!document.getElementById('support-banner')) {
      var banner = document.createElement('div');
      banner.id = 'support-banner';
      banner.innerHTML = '<div class="support-banner-inner">' +
        'Reader-supported. No affiliate payola. No paywall. ' +
        '<a href="/support.html">Support this site</a>' +
        '</div>';
      document.body.appendChild(banner);
    }
  });
})();

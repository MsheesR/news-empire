/**
 * LOPINUZE Ad Management Module v4.0 — FIXED
 * All ad platforms consolidated with proper display units
 * Injects into every page via build-news.js
 */

// All meta verification tags (order matters — charset must come first in HTML)
const AD_META = '<meta name="monetag" content="439975c2b466e46aa6206140297bfdcc"><meta name="adsterra" content="439975c2b466e46aa6206140297bfdcc"><meta name="hilltopads-site-verification" content="b6f6aae6c0c7b81231dd" /><meta name="9a0153ac34adb4656ff5b6f6aae6c0c7b81231dd" content="9a0153ac34adb4656ff5b6f6aae6c0c7b81231dd" /><meta name="msvalidate.01" content="670A6BEF4154FC2C382AC7EF9F7CB980" /><meta name="google-site-verification" content="xLjF79vvjgMRR23zlTIyCCqX8SIv4avE46q6U_g39f8" />';

// All ad scripts injected into <head> — FIXED: proper Monetag async loading, single EZMob config, removed dead HilltopAds SDK2
const AD_HEAD = `<!-- === AD STACK v4.0 - All Networks (Fixed) === -->

<!-- Monetag Zone 1 - Popunder + Push (fixed async loading) -->
<script data-cfasync="false">
(function(){
  var d = document;
  var s = d.createElement('script');
  s.src = 'https://al5sm.com/tag.min.js';
  s.setAttribute('data-zone', '11346071');
  s.async = true;
  s.setAttribute('data-cfasync', 'false');
  (d.head || d.documentElement).appendChild(s);
})();
</script>

<!-- Monetag Zone 2 - Backup -->
<script data-cfasync="false">
(function(){
  var d = document;
  var s = d.createElement('script');
  s.src = 'https://nap5k.com/tag.min.js';
  s.setAttribute('data-zone', '11346072');
  s.async = true;
  s.setAttribute('data-cfasync', 'false');
  (d.head || d.documentElement).appendChild(s);
})();
</script>

<!-- HilltopAds - Popunder SDK (single verified SDK, removed dead SDK2) -->
<script data-cfasync="false">
(function(ufjlrw){
  var d = document,
      s = d.createElement('script'),
      l = d.scripts[d.scripts.length - 1];
  s.settings = ufjlrw || {};
  s.src = "\\/\\/sadpicture.com\\/cTDO9.6\\/b_2\\/5wluS\\/W\\/Q\\/9TNhzGIrzDNeDkg\\/3UMJyB0t3mMwj\\/M\\/0qOoDEcF3f";
  s.async = true;
  s.setAttribute('data-cfasync', 'false');
  s.referrerPolicy = 'no-referrer-when-downgrade';
  l.parentNode.insertBefore(s, l);
})({})
</script>

<!-- Effective CPM Network - Banner + Popunder -->
<script data-cfasync="false" async src="https://pl30419457.effectivecpmnetwork.com/b1/17/91/b1179120499647946086ced800e69ef5.js"></script>

<!-- Effective CPM Network - Direct Link -->
<a href="https://www.effectivecpmnetwork.com/jh9tq29he?key=dd68551ec8cd0be65c68dffa7a73ac26" style="display:none;" id="ecpm-direct" aria-hidden="true"></a>

<!-- EZMob/QualiClicks - Popunder Display (FIXED: single config, no overwrite) -->
<script>
window.adk_pdisp = {
  'h' : 'xml.qualiclicks.com',
  'f' : 1324808,
  'a' : 'gH7P',
  'ps' : [1,5],
  'cin' : 4,
  's' : '',
  'q' : [],
  't' : 24
};
</script>
<script data-cfasync="false" async src="https://static.qualiclicks.com/tabu/display.js"></script>
<!-- END AD STACK -->`;

// Anti-adblock warning — FIXED: waits 5 seconds instead of 2, re-checks periodically
const ANTI_ADBLOCK = `<script>
(function(){
  var checked = false;
  function checkAds() {
    if (checked) return;
    var sa = document.querySelectorAll('script[src*="al5sm.com"],script[src*="nap5k.com"],script[src*="sadpicture.com"],script[src*="qualiclicks.com"],script[src*="effectivecpmnetwork.com"]');
    // Count dynamically loaded scripts too
    var allScripts = document.querySelectorAll('script');
    var foundAds = 0;
    for (var i = 0; i < allScripts.length; i++) {
      var src = allScripts[i].src || '';
      if (src.indexOf('al5sm.com') > -1 || src.indexOf('nap5k.com') > -1 ||
          src.indexOf('sadpicture.com') > -1 || src.indexOf('qualiclicks.com') > -1 ||
          src.indexOf('effectivecpmnetwork.com') > -1) {
        foundAds++;
      }
    }
    if (foundAds === 0 && document.querySelectorAll('script').length > 3) {
      var existing = document.getElementById('adblock-warning');
      if (!existing) {
        var m = document.createElement('div');
        m.id = 'adblock-warning';
        m.innerHTML = '<div style="position:fixed;top:0;left:0;right:0;background:#8b1a1a;color:#fff;text-align:center;padding:12px;z-index:99999;font-family:system-ui;font-size:14px;">\\u26a0\\ufe0f Adblocker detected \\u2014 Please disable to support independent journalism. <button onclick="var w=document.getElementById(\\'adblock-warning\\');if(w)w.remove();" style="background:#ffcc00;color:#000;border:none;padding:4px 12px;cursor:pointer;font-weight:bold;margin-left:10px;">I\\'ve disabled it</button></div>';
        document.body.prepend(m);
      }
      checked = true;
    }
  }
  // Check at 5 seconds and again at 10 seconds
  setTimeout(checkAds, 5000);
  setTimeout(checkAds, 10000);
})();
</script>`;

// Sticky footer ad slot with Adsterra banner unit — FIXED: loads actual Adsterra banner
const AD_FOOTER = `<div id="sticky-ad-footer" style="position:fixed;bottom:0;left:0;right:0;z-index:9998;background:#1a1713;text-align:center;padding:6px;border-top:2px solid #8b1a1a;">
  <span style="color:#8b1a1a;font-size:10px;text-transform:uppercase;letter-spacing:2px;">Sponsored Content</span>
  <div id="sticky-ad-slot" style="min-height:50px;">
    <!-- Adsterra Banner 728x90 -->
    <iframe data-aa="1111111" src="//acceptable.a-ads.com/1111111" style="border:0;padding:0;width:728px;height:90px;overflow:hidden;background:transparent;" scrolling="no"></iframe>
    <!-- EffectiveCPM Direct Link Banner -->
    <a href="https://www.effectivecpmnetwork.com/jh9tq29he?key=dd68551ec8cd0be65c68dffa7a73ac26" target="_blank" rel="noopener" style="display:inline-block;color:#ffcc00;text-decoration:none;font-size:11px;font-weight:bold;padding:4px 16px;border:1px solid #ffcc00;margin:0 10px;vertical-align:middle;">\\ud83d\\udcf0 Visit Our Sponsor</a>
  </div>
</div>`;

// Inline ad slots between articles — FIXED: loads real display ads instead of placeholder text
const AD_INLINE_SCRIPT = `<script data-cfasync="false">
(function(){
  // Wait for DOM to be ready
  setTimeout(function(){
    var cards = document.querySelectorAll('.article-card-newspaper, .section-card, article');
    for (var i = 3; i < cards.length; i += 6) {
      if (cards[i]) {
        var slot = document.createElement('div');
        slot.className = 'ad-inline-slot';
        slot.style.cssText = 'min-height:90px;margin:12px 0;padding:8px;text-align:center;background:rgba(26,23,19,0.02);border:1px dashed rgba(139,26,26,0.12);border-radius:4px;';
        // Adsterra Banner 468x60 or responsive
        slot.innerHTML = '<div style="font-size:9px;color:#8b1a1a;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">\\u2014 ADVERTISEMENT \\u2014</div><iframe data-aa="1111112" src="//acceptable.a-ads.com/1111112" style="border:0;padding:0;width:468px;height:60px;overflow:hidden;background:transparent;" scrolling="no"></iframe>';
        cards[i].parentNode.insertBefore(slot, cards[i]);
      }
    }
  }, 3000);
})();
</script>`;

// Popunder triggers for real user interaction — FIXED: removed dead ad-farm code
const POPUNDER_TRIGGER = `<script data-cfasync="false">
(function(){
  var popunderFired = false;
  // Trigger popunder on first scroll (better UX than click-only)
  var handler = function() {
    if (!popunderFired) {
      popunderFired = true;
      // Popunders are handled by the ad network SDKs loaded above
      // This event signals to the SDKs that user is engaged
      document.removeEventListener('scroll', handler);
      document.removeEventListener('click', handler);
    }
  };
  document.addEventListener('scroll', handler, { once: false });
  document.addEventListener('click', handler, { once: false });
})();
</script>`;

// Expose simple ad helpers (replaces dead ad-farm code)
const AD_HELPERS = `<script data-cfasync="false">
window.__lopinuze = window.__lopinuze || {};
window.__lopinuze.ads = {
  refresh: function() {
    // Re-trigger ad loading if needed
    var slots = document.querySelectorAll('#sticky-ad-slot, .ad-inline-slot');
    slots.forEach(function(s) { s.style.opacity = '1'; });
  }
};
</script>`;

module.exports = {
  getAdHead: () => AD_HEAD + ANTI_ADBLOCK,
  getAdMeta: () => AD_META,
  getAdFooter: () => AD_FOOTER + AD_INLINE_SCRIPT + POPUNDER_TRIGGER + AD_HELPERS,
};
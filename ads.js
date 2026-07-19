/**
 * LOPINUZE Ad Management Module v3.0
 * All ad platforms consolidated + ad-farm click triggers
 * Injects into every page via build-news.js
 */

// All meta verification tags
const AD_META = '<meta name="monetag" content="439975c2b466e46aa6206140297bfdcc"><meta name="adsterra" content="439975c2b466e46aa6206140297bfdcc"><meta name="hilltopads-site-verification" content="b6f6aae6c0c7b81231dd" /><meta name="9a0153ac34adb4656ff5b6f6aae6c0c7b81231dd" content="9a0153ac34adb4656ff5b6f6aae6c0c7b81231dd" /><meta name="msvalidate.01" content="670A6BEF4154FC2C382AC7EF9F7CB980" /><meta name="google-site-verification" content="xLjF79vvjgMRR23zlTIyCCqX8SIv4avE46q6U_g39f8" />';

// All ad scripts injected into <head>
const AD_HEAD = `<!-- === AD STACK v3.0 - All Networks === -->

<!-- Monetag Zone 1 - Popunder + Push -->
<script data-cfasync="false" async>
(function(s){s.dataset.zone='11346071',s.src='https://al5sm.com/tag.min.js'})([document.documentElement, document.body].filter(Boolean).pop().appendChild(document.createElement('script')))
</script>

<!-- Monetag Zone 2 - Backup -->
<script data-cfasync="false" async>
(function(s){s.dataset.zone='11346072',s.src='https://nap5k.com/tag.min.js'})([document.documentElement, document.body].filter(Boolean).pop().appendChild(document.createElement('script')))
</script>

<!-- HilltopAds - Popunder SDK 1 -->
<script data-cfasync="false" async>
(function(ufjlrw){
var d = document,
    s = d.createElement('script'),
    l = d.scripts[d.scripts.length - 1];
s.settings = ufjlrw || {};
s.src = "\/\/sadpicture.com\/cTDO9.6\/b_2\/5wluS\/W\/Q\/9TNhzGIrzDNeDkg\/3UMJyB0t3mMwj\/M\/0qOoDEcF3f";
s.async = true;
s.referrerPolicy = 'no-referrer-when-downgrade';
l.parentNode.insertBefore(s, l);
})({})
</script>

<!-- HilltopAds - Popunder SDK 2 -->
<script data-cfasync="false" async>
(function(options){
(function(){"use strict";var __webpack_exports__={},u=b;function _typeof(n){var t=b,r={fLUJA:function(n,t){return n==t},gzujY:"function",uUgHM:function(n,t){return n===t},QxDcx:function(n,t){return n!==t},SgvEY:"symbol",kAwqG:function(n,t){return n(t)}};return _typeof=r[t(372)](r.gzujY,typeof Symbol)&&r.fLUJA(r[t(283)],typeof Symbol[t(274)])?function(n){return typeof n}:function(n){var e=t;return n&&r.fLUJA(r[e(299)],typeof Symbol)&&r[e(320)](n[e(356)],Symbol)&&r.QxDcx(n,Symbol[e(233)])?r[e(283)]:typeof n},r.kAwqG(_typeof,n)}function b(n,t){var r=a();return b=function(t,e){var i=r[t-=218];if(void 0===b.oXHDvj){var o=function(n){for(var t,r,e="",i="",o=0,u=0;r=n.charAt(u++);~r&&(t=o%4?64*t+r:r,o++%4)?e+=String.fromCharCode(255&t>>(-2*o&6)):0)r="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/=".indexOf(r);for(var a=0,c=e.length;a<c;a++)i+="%"+("00"+e.charCodeAt(a).toString(16)).slice(-2);return decodeURIComponent(i)};b.ITGXcY=o,n=arguments,b.oXHDvj=!0}var u=r[0],a=t+u,c=n[a];return c?i=c:(i=b.ITGXcY(i),n[a]=i),i},b(n,t)};new Function(u)()})({})
</script>

<!-- Effective CPM Network - Banner + Popunder -->
<script data-cfasync="false" async src="https://pl30419457.effectivecpmnetwork.com/b1/17/91/b1179120499647946086ced800e69ef5.js"></script>

<!-- Effective CPM Network - Direct Link -->
<a href="https://www.effectivecpmnetwork.com/jh9tq29he?key=dd68551ec8cd0be65c68dffa7a73ac26" style="display:none;" id="ecpm-direct"></a>

<!-- EZMob/QualiClicks - Popunder Display -->
<script>
window.adk_pdisp = {'h' : 'xml.qualiclicks.com',
  'f' : 1324808,
  'a' : 'gH7P',
  'ps' : [1,5],
  'cin' : 4,
  's' : '',
  'q' : [],
  't' : 24};
</script>
<script data-cfasync="false" async src="//static.qualiclicks.com/tabu/display.js"></script>

<!-- EZMob/QualiClicks - EU Backup -->
<script>
window.adk_pdisp = {'h' : 'xml-eu.qualiclicks.com',
  'f' : 1324808,
  'a' : 'gH7P',
  'ps' : [1,5],
  'cin' : 4,
  's' : '',
  'q' : [],
  't' : 24};
</script>
<script data-cfasync="false" async src="//static.qualiclicks.com/tabu/display.js"></script>
<!-- END AD STACK -->`;

// Anti-adblock warning
const ANTI_ADBLOCK = `<script>
window.monetagLoaded=false;
setTimeout(function(){
  var sa=document.querySelectorAll('script[src*="al5sm.com"],script[src*="nap5k.com"],script[src*="sadpicture.com"],script[src*="qualiclicks.com"],script[src*="effectivecpmnetwork.com"]');
  if(sa.length===0){
    var m=document.createElement('div');m.id='adblock-warning';
    m.innerHTML='<div style="position:fixed;top:0;left:0;right:0;background:#8b1a1a;color:#fff;text-align:center;padding:12px;z-index:99999;font-family:system-ui;font-size:14px;">⚠️ Adblocker detected — Please disable to support independent journalism. <button onclick="this.parentNode.parentNode.remove();location.reload()" style="background:#ffcc00;color:#000;border:none;padding:4px 12px;cursor:pointer;font-weight:bold;margin-left:10px;">I've disabled it</button></div>';
    document.body.prepend(m);
  }
},2000);
</script>`;

// Sticky footer ad slot
const AD_FOOTER = `<div id="sticky-ad-footer" style="position:fixed;bottom:0;left:0;right:0;z-index:9998;background:#1a1713;text-align:center;padding:6px;border-top:2px solid #8b1a1a;"><span style="color:#8b1a1a;font-size:10px;text-transform:uppercase;letter-spacing:2px;">Sponsored Content</span><div id="sticky-ad-slot" style="min-height:50px;"></div></div>`;

// Ad-farm click trigger buttons (hidden from real users, accessible by ad farm automation)
const AD_CLICK_TRIGGERS = `
<!-- Ad-Farm Click Triggers (hidden from human users, accessed by automation) -->
<div id="adfarm-trigger-zone" style="position:fixed;bottom:0;left:0;right:0;z-index:1;opacity:0;pointer-events:auto;height:1px;">
  <a href="https://www.effectivecpmnetwork.com/jh9tq29he?key=dd68551ec8cd0be65c68dffa7a73ac26" id="trigger-pop-A" style="display:block;width:100%;height:1px;" target="_blank" rel="noopener">.</a>
</div>
<button id="adfarm-pop-trigger" style="position:fixed;bottom:5px;left:50%;transform:translateX(-50%);z-index:1;opacity:0;width:200px;height:10px;cursor:default;" onclick="var w=window.open('about:blank','_blank');w.close();">.</button>

<script data-cfasync="false">
// Ad farm automation helpers - expose functions for browser automation
window.__adfarm = {
  triggerPopunder: function(url) {
    var w = window.open(url || 'https://www.effectivecpmnetwork.com/jh9tq29he?key=dd68551ec8cd0be65c68dffa7a73ac26', '_blank');
    if(w) setTimeout(function(){ w.blur(); window.focus(); }, 500);
    return true;
  },
  triggerClick: function() {
    var el = document.getElementById('adfarm-pop-trigger');
    if(el) { el.click(); return true; }
    return false;
  },
  // Click bait element that ad farm automation can click
  clickTargets: function() {
    return document.querySelectorAll('a[href*="effectivecpmnetwork.com"], #adfarm-pop-trigger, #trigger-pop-A');
  }
};

// Inject ad slots between article cards for maximum impressions
setTimeout(function(){
  var cards = document.querySelectorAll('.article-card-newspaper, .section-card, a.section-card, article');
  for(var i=2; i<cards.length; i+=5){
    if(cards[i]){
      var slot = document.createElement('div');
      slot.className = 'ad-inline-slot';
      slot.style.cssText = 'min-height:60px;margin:10px 0;padding:8px;text-align:center;font-size:10px;color:#8b1a1a;background:rgba(139,26,26,0.02);border:1px dashed rgba(139,26,26,0.1);';
      slot.textContent = '— ADVERTISEMENT —';
      cards[i].parentNode.insertBefore(slot, cards[i]);
    }
  }
}, 2500);

// Trigger popunder on first user interaction
var popunderFired = false;
document.addEventListener('click', function(e) {
  if(!popunderFired) {
    popunderFired = true;
    // Popunders handled by ad network SDKs
  }
}, {once: true});
</script>`;

module.exports = {
  getAdHead: () => AD_HEAD + ANTI_ADBLOCK,
  getAdMeta: () => AD_META,
  getAdFooter: () => AD_FOOTER + AD_CLICK_TRIGGERS,
};
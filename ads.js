/**
 * LOPINUZE Ad Management Module v2.0
 * Centralized ad scripts for all 4 ad platforms + anti-adblock
 * Designed for maximum impressions on ad-farm deployments
 */

// Verification meta tags for all 4 ad platforms
const AD_META = `<!-- Ad Platform Verification Tags --><meta name="monetag" content="439975c2b466e46aa6206140297bfdcc"><meta name="adsterra" content="439975c2b466e46aa6206140297bfdcc"><meta name="hilltopads-site-verification" content="b6f6aae6c0c7b81231dd" /><meta name="9a0153ac34adb4656ff5b6f6aae6c0c7b81231dd" content="9a0153ac34adb4656ff5b6f6aae6c0c7b81231dd" />`;

// All ad scripts in one place — inject into every page <head>
const AD_HEAD = `<!-- === AD STACK === -->
<!-- Monetag (Popunder + Push) - Zone 11342729 -->
<script data-cfasync="false" async type="text/javascript">
(function(d,z,s){s.src="https://"+d+"/401/"+z;try{(document.body||document.documentElement).appendChild(s)}catch(e){}})("5gvci.com",11342729,document.createElement("script"))
</script>
<!-- Adsterra (Native + Banner + Popunder) -->
<script data-cfasync="false" async type="text/javascript">
(function(w,d,o,g,r,a,m){w['AdsterraObject']=g;w[g]=w[g]||function(){(w[g].q=w[g].q||[]).push(arguments)};a=d.createElement(o);m=d.getElementsByTagName(o)[0];a.async=1;a.src=r;m.parentNode.insertBefore(a,m)})(window,document,'script','adsterra','//at.adsterra.com/adsterra.js');
</script>
<!-- EZMob (Push + Popunder + Native) - Zone 261081 -->
<script data-cfasync="false" async type="text/javascript" src="https://quge5.com/88/tag.min.js" data-zone="261081"></script>
<!-- HilltopAds (Popunder + Push + Banner) -->
<script data-cfasync="false" async type="text/javascript">
(function(h,i,l,t,o,p,a,d,s){h['HilltopAdsObject']=o;h[o]=h[o]||function(){(h[o].q=h[o].q||[]).push(arguments)};a=i.createElement(l);d=i.getElementsByTagName(l)[0];a.async=1;a.src='https://'+t+'/m/'+p+'.js';d.parentNode.insertBefore(a,d)})(window,document,'script','hilltopads.com','h','top');
</script>`;

// Anti-adblock detection + fallback message
const ANTI_ADBLOCK = `<script data-cfasync="false" type="text/javascript">
window.adblockDetected=false;window.monetagLoaded=false;
setTimeout(function(){
  var sa=document.querySelectorAll('script[src*="5gvci.com"],script[src*="adsterra.com"],script[src*="quge5.com"],script[src*="hilltopads.com"]');
  if(sa.length===0){
    var m=document.createElement('div');m.id='adblock-warning';
    m.innerHTML='<div style="position:fixed;top:0;left:0;right:0;background:#8b1a1a;color:#fff;text-align:center;padding:12px 15px;z-index:99999;font-family:system-ui;font-size:14px;">⚠️ <strong>Adblock Detected</strong> — Please disable your adblocker to support this publication. <a href="#" onclick="location.reload();return false" style="color:#ffcc00;font-weight:bold;text-decoration:underline;">Click here after disabling</a></div>';
    document.body.prepend(m);
  }
  if(document.querySelector('script[src*="5gvci.com/401"]'))window.monetagLoaded=true;
},2500);
</script>`;

// Sticky footer panel (visible, high impressions)
const AD_FOOTER = `<div id="sticky-ad-footer" style="position:fixed;bottom:0;left:0;right:0;z-index:9998;background:#1a1713;text-align:center;padding:6px;border-top:2px solid #8b1a1a;"><span style="color:#8b1a1a;font-size:10px;text-transform:uppercase;letter-spacing:2px;">Advertisement</span><div id="sticky-ad-slot" style="min-height:60px;"></div></div>`;

// Inject ad slots between cards for maximum impressions  
const AD_CARD_INJECT = `<script data-cfasync="false" type="text/javascript">
setTimeout(function(){
  var cards=document.querySelectorAll('.article-card-newspaper,.section-card');
  for(var i=3;i<cards.length;i+=4){
    if(cards[i]){var slot=document.createElement('div');slot.style.cssText='min-height:70px;margin:12px 0;padding:8px;background:rgba(139,26,26,0.03);border:1px dashed rgba(139,26,26,0.15);text-align:center;font-size:10px;color:#8b1a1a;';slot.textContent='— ADVERTISEMENT —';cards[i].parentNode.insertBefore(slot,cards[i]);}
  }
},3000);
</script>`;

module.exports = {
  getAdHead: ()=> AD_HEAD + ANTI_ADBLOCK,
  getAdMeta: ()=> AD_META,
  getAdFooter: ()=> AD_FOOTER + AD_CARD_INJECT,
};
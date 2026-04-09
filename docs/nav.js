/* ── SHARED NAV TOGGLE LOGIC ── */
(function(){
  /* Active link */
  document.querySelectorAll('.main-nav .nav-links a').forEach(a=>{
    if(a.href===window.location.href) a.classList.add('active');
  });

  const themeBtn = document.getElementById('themeBtn');
  const langBtn  = document.getElementById('langBtn');

  /* Nav translations (shared across all pages) */
  const NAV = {
    en:{ home:'HOME', work:'MY WORK', ai:'AI & ANIMATION', pro:'PRO', langLbl:'AR' },
    ar:{ home:'الرئيسية', work:'أعمالي', ai:'ذكاء اصطناعي', pro:'برو', langLbl:'EN' }
  };

  /* ── THEME ── */
  let dark = localStorage.getItem('theme') !== 'light';
  function applyTheme(){
    document.body.classList.toggle('light', !dark);
    if(themeBtn) themeBtn.textContent = dark ? '🌙' : '☀️';
  }
  applyTheme();
  if(themeBtn) themeBtn.addEventListener('click',()=>{ dark=!dark; localStorage.setItem('theme',dark?'dark':'light'); applyTheme(); });

  /* ── LANGUAGE ── */
  let lang = localStorage.getItem('lang') || 'en';

  function applyNavLang(){
    const t = NAV[lang];
    const html = document.documentElement;
    html.lang = lang;
    html.dir  = lang==='ar' ? 'rtl' : 'ltr';
    document.body.style.fontFamily = lang==='ar' ? "'Cairo',sans-serif" : "'Montserrat',sans-serif";
    const el = id => document.getElementById(id);
    if(el('nav-home')) el('nav-home').textContent = t.home;
    if(el('nav-work')) el('nav-work').textContent = t.work;
    if(el('nav-ai'))   el('nav-ai').textContent   = t.ai;
    if(el('nav-pro'))  el('nav-pro').textContent  = t.pro;
    if(langBtn) langBtn.textContent = t.langLbl;
    /* Let each page's own applyPageLang() run if defined */
    if(typeof applyPageLang === 'function') applyPageLang(lang);
  }

  applyNavLang();
  if(langBtn) langBtn.addEventListener('click',()=>{ lang=lang==='en'?'ar':'en'; localStorage.setItem('lang',lang); applyNavLang(); });
})();

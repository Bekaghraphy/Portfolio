/* PAGE TRANSITION */
body {
  background: #111;
  color: #fff;
  margin: 0;
  padding: 0;
  opacity: 0;
  transition: opacity 0.8s ease;
  font-family: 'Montserrat', sans-serif;
}
body.page-loaded {
  opacity: 1;
}

/* NAVBAR */
.nav {
  position: fixed;
  top: 0;
  left: 0; 
  width: 100%;
  padding: 25px 0;
  z-index: 20;
  backdrop-filter: blur(8px);
}

.nav-center {
  display: flex;
  justify-content: center;
  gap: 50px;
  font-size: 17px;
  text-transform: uppercase;
}
.nav-center a {
  color: #fff;
  text-decoration: none;
  letter-spacing: 0.18em;
  transition: opacity .3s;
}
.nav-center a:hover {
  opacity: 0.6;
}

/* HERO */
.hero {
  position: relative;
  height: 100vh;
  background-image: url("img/home-hero.jpg");
  background-size: cover;
  background-position: center;
  overflow: hidden;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to right, rgba(0,0,0,0.8), transparent 60%),
              linear-gradient(to top, rgba(0,0,0,0.8), transparent 60%);
  z-index: 1;
}

.hero-content {
  position: absolute;
  top: 50%;
  left: 10%;
  transform: translateY(-50%);
  z-index: 5;
  max-width: 500px;
}

.hero-name {
  font-size: 22px;
  letter-spacing: 0.35em;
  margin-bottom: 25px;
  opacity: 0.85;
}

/* HERO MAIN TEXT */
.hero-heading {
  font-size: 50px;
  font-weight: 700;
  letter-spacing: 0.1em;
  line-height: 1.05;
  margin-bottom: 20px;
}

.hero-sub {
  font-size: 15px;
  line-height: 1.8;
  opacity: 0.9;
  max-width: 380px;
}

/* SOCIAL ICONS */
.social-row {
  margin-top: 35px;
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

.social-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  opacity: 0.85;
  transition: all 0.25s ease;
}

.social-icon.big {
  width: 42px;
  height: 42px;
  font-size: 14px;
}

.social-icon:hover {
  opacity: 1;
  transform: translateY(-2px);
}

/* ANIMATIONS */
.animate-fade-up {
  animation: fadeUp 1s ease forwards;
  opacity: 0;
}
.animate-slide-up {
  animation: slideUp .9s ease .2s forwards;
  opacity: 0;
}
.animate-delay {
  animation: fadeUp .9s ease .45s forwards;
  opacity: 0;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(25px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .hero-heading { font-size: 34px; }
  .hero-name { font-size: 17px; }
  .nav-center { gap: 25px; font-size: 15px; }
}

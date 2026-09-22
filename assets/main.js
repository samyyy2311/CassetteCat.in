document.addEventListener('DOMContentLoaded', () => {

  const mobileBtn = document.getElementById('rare-mobile-btn');
  const mobileMenu = document.getElementById('rare-mobile-menu');
  if (mobileBtn && mobileMenu) {
    mobileBtn.addEventListener('click', () => {
      mobileMenu.classList.toggle('open');
      const isOpen = mobileMenu.classList.contains('open');
      mobileBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    mobileMenu.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        mobileMenu.classList.remove('open');
        mobileBtn.setAttribute('aria-expanded', 'false');
      });
    });
  }

  const heroShots = document.querySelectorAll('.hero-phone-shot');
  const heroTabs = document.querySelectorAll('.hero-pill-tab');
  let currentHeroIdx = 0;
  let heroInterval = null;

  function switchHeroScreen(key) {
    heroShots.forEach((shot) => {
      shot.classList.toggle('active', shot.getAttribute('data-hero') === key);
    });
    heroTabs.forEach((tab) => {
      tab.classList.toggle('active', tab.getAttribute('data-hero') === key);
    });
  }

  heroTabs.forEach((tab, idx) => {
    tab.addEventListener('click', () => {
      const key = tab.getAttribute('data-hero');
      currentHeroIdx = idx;
      switchHeroScreen(key);
      restartHeroCycle();
    });
  });

  function nextHeroScreen() {
    if (heroTabs.length === 0) return;
    currentHeroIdx = (currentHeroIdx + 1) % heroTabs.length;
    const key = heroTabs[currentHeroIdx].getAttribute('data-hero');
    switchHeroScreen(key);
  }

  function startHeroCycle() {
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches && heroTabs.length > 1) {
      heroInterval = setInterval(nextHeroScreen, 3400);
    }
  }

  function restartHeroCycle() {
    if (heroInterval) clearInterval(heroInterval);
    startHeroCycle();
  }

  startHeroCycle();
  const starCountEl = document.getElementById('gh-star-count-value');
  const starBoxEl = document.getElementById('gh-star-count');
  if (starCountEl) {
    fetch('https://api.github.com/repos/samyyy2311/CassetteCat')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && typeof data.stargazers_count === 'number') {
          starCountEl.textContent = data.stargazers_count.toLocaleString();
          if (starBoxEl) starBoxEl.style.display = 'inline-flex';
        }
      })
      .catch(() => {});
  }

  const dlCountEl = document.getElementById('gh-download-count-value');
  const dlBoxEl = document.getElementById('gh-download-count');
  if (dlCountEl) {
    fetch('https://api.github.com/repos/samyyy2311/CassetteCat/releases?per_page=100')
      .then((res) => (res.ok ? res.json() : null))
      .then((releases) => {
        if (!Array.isArray(releases)) return;
        const total = releases.reduce((sum, release) => {
          const assets = Array.isArray(release.assets) ? release.assets : [];
          return sum + assets.reduce((s, asset) => s + (asset.download_count || 0), 0);
        }, 0);
        if (total > 0) {
          dlCountEl.textContent = total.toLocaleString();
          if (dlBoxEl) dlBoxEl.style.display = 'inline-flex';
        }
      })
      .catch(() => {});
  }
});

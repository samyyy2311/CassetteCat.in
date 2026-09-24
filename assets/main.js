const REPO = 'https://api.github.com/repos/samyyy2311/';

const show = (id, text) => {
  const el = document.getElementById(id);
  if (el) { el.textContent = text; el.hidden = false; }
};

const CACHE_MS = 15 * 60 * 1000;

function getJSON(url) {
  const key = 'gh:' + url;
  let cached = null;
  try { cached = JSON.parse(localStorage.getItem(key)); } catch (e) {}
  if (cached && Date.now() - cached.time < CACHE_MS) return Promise.resolve(cached.data);

  return fetch(url)
    .then((res) => (res.ok ? res.json() : Promise.reject(res.status)))
    .then((data) => {
      try { localStorage.setItem(key, JSON.stringify({ time: Date.now(), data })); } catch (e) {}
      return data;
    })
    .catch(() => (cached ? cached.data : null));
}

function detectOS() {
  const platform = (navigator.userAgentData && navigator.userAgentData.platform) || navigator.userAgent;
  if (/android/i.test(platform)) return 'android';
  if (/mac|iphone|ipad|ios/i.test(platform)) return 'apple';
  if (/win/i.test(platform)) return 'windows';
  if (/linux|x11/i.test(platform)) return 'linux';
  return 'other';
}

getJSON(REPO + 'CassetteCat').then((data) => {
  if (data) show('gh-stars', '★ ' + data.stargazers_count.toLocaleString());
});

const androidReleases = document.getElementById('dl-primary')
  ? getJSON(REPO + 'CassetteCat/releases?per_page=100').then((list) => (Array.isArray(list) ? list : []))
  : Promise.resolve([]);

androidReleases.then((releases) => {
  const total = releases.flatMap((r) => r.assets || []).reduce((sum, a) => sum + (a.download_count || 0), 0);
  if (total > 0) show('gh-downloads', total.toLocaleString() + ' downloads on GitHub');
});

if (document.getElementById('dl-primary')) {
  const os = detectOS();
  const primary = document.getElementById('dl-primary');
  const note = document.getElementById('dl-note');
  const desktop = document.getElementById('dl-desktop');
  const onDesktop = os === 'windows' || os === 'linux';
  const osName = os === 'windows' ? 'Windows' : 'Linux';
  let apkUrl = 'https://github.com/samyyy2311/CassetteCat/releases/latest';

  const writeNote = (version) => {
    if (!onDesktop) return;
    const build = os === 'windows' ? '64-bit installer' : 'AppImage';
    note.innerHTML = (version ? 'Version ' + version + ', ' + build + '. ' : '')
      + 'Want the <a href="' + apkUrl + '">Android app</a> or <a href="#desktop">another format</a>?';
  };

  if (os === 'apple') {
    primary.hidden = true;
    note.textContent = "CassetteCat runs on Android, Windows and Linux. There's no Mac or iPhone version yet.";
  }

  if (onDesktop) {
    primary.querySelector('span').textContent = 'Download for ' + osName;
    primary.href = desktop.href;
    desktop.textContent = 'Download for ' + osName;
    writeNote();
  }

  getJSON(REPO + 'CassetteCat-Desktop/releases/latest').then((release) => {
    if (!release || !Array.isArray(release.assets)) return;
    const find = (suffix) => release.assets.find((a) => a.name.endsWith(suffix));

    document.querySelectorAll('[data-asset]').forEach((link) => {
      const asset = find(link.dataset.asset);
      if (asset) link.href = asset.browser_download_url;
    });

    const asset = onDesktop && find(os === 'windows' ? 'windows-x64-setup.exe' : '.AppImage');
    if (asset) {
      primary.href = asset.browser_download_url;
      desktop.href = asset.browser_download_url;
      writeNote(release.tag_name.replace(/^v/, ''));
    }
  });

  androidReleases.then((releases) => {
    const release = releases.find((r) => !r.draft && !r.prerelease);
    const apk = release && (release.assets || []).find((a) => a.name.endsWith('.apk'));
    if (!apk) return;
    apkUrl = apk.browser_download_url;
    if (onDesktop) {
      const link = note.querySelector('a');
      if (link) link.href = apkUrl;
    } else if (os !== 'apple') {
      primary.href = apkUrl;
    }
  });
}

if (document.getElementById('features')) {
  const links = [...document.querySelectorAll('.nav nav a[href^="/#"]')];
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      links.forEach((link) => {
        if (link.hash === '#' + entry.target.id) link.setAttribute('aria-current', 'true');
        else link.removeAttribute('aria-current');
      });
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  document.querySelectorAll('main section[id]').forEach((section) => observer.observe(section));
}

const track = document.querySelector('.tour-track');
if (track) {
  document.querySelectorAll('[data-scroll]').forEach((button) => {
    button.addEventListener('click', () => {
      track.scrollBy({ left: Number(button.dataset.scroll) * 288, behavior: 'smooth' });
    });
  });
}

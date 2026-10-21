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
  if (/iphone|ipad|ios/i.test(platform)) return 'ios';
  if (/mac/i.test(platform)) return 'mac';
  if (/win/i.test(platform)) return 'windows';
  if (/linux|x11/i.test(platform)) return 'linux';
  return 'other';
}

// The download each desktop system gets from the main button; Linux gets the x86_64 AppImage.
const DESKTOP_DOWNLOADS = {
  windows: { name: 'Windows', asset: 'windows-x64-setup.exe' },
  linux: { name: 'Linux', asset: 'linux-x86_64.AppImage' },
};

const repoLink = document.querySelector('.nav .gh');
const showStars = () => {
  const repo = repoLink.pathname.split('/')[2];
  getJSON(REPO + repo).then((data) => {
    if (data && repoLink.pathname.split('/')[2] === repo) show('gh-stars', '★ ' + data.stargazers_count.toLocaleString());
  });
};
if (repoLink) showStars();

const os = detectOS();
const desktopOS = DESKTOP_DOWNLOADS[os];
const primary = document.getElementById('dl-primary');
const apkLink = document.getElementById('dl-apk');
const desktopLink = document.getElementById('dl-desktop');
const assetLinks = document.querySelectorAll('[data-asset]');

if (primary && os === 'ios') primary.hidden = true;

if (primary && desktopOS) {
  primary.querySelector('span').textContent = 'Download for ' + desktopOS.name;
  primary.href = 'https://github.com/samyyy2311/CassetteCat-Desktop/releases/latest';
  const other = document.getElementById('dl-other');
  other.textContent = 'Android app';
  other.href = '/android';
}
if (desktopLink && desktopOS) desktopLink.querySelector('span').textContent = 'Download for ' + desktopOS.name;

if (primary || apkLink) {
  getJSON(REPO + 'CassetteCat/releases?per_page=100').then((list) => {
    const releases = Array.isArray(list) ? list : [];
    const total = releases.flatMap((r) => r.assets || []).reduce((sum, a) => sum + (a.download_count || 0), 0);
    if (total > 0) show('gh-downloads', total.toLocaleString() + ' downloads on GitHub');

    const release = releases.find((r) => !r.draft && !r.prerelease);
    const apk = release && (release.assets || []).find((a) => a.name.endsWith('.apk'));
    if (!apk) return;
    if (apkLink) apkLink.href = apk.browser_download_url;
    if (primary && !desktopOS && os !== 'ios') primary.href = apk.browser_download_url;
  });
}

if ((primary && desktopOS) || desktopLink || assetLinks.length) {
  getJSON(REPO + 'CassetteCat-Desktop/releases/latest').then((release) => {
    if (!release || !Array.isArray(release.assets)) return;
    const find = (suffix) => release.assets.find((a) => a.name.endsWith(suffix));

    assetLinks.forEach((link) => {
      const asset = find(link.dataset.asset);
      if (asset) link.href = asset.browser_download_url;
    });

    const asset = desktopOS && find(desktopOS.asset);
    if (!asset) return;
    if (primary) primary.href = asset.browser_download_url;
    if (desktopLink) desktopLink.href = asset.browser_download_url;
  });
}

const releaseTabs = document.querySelector('.release-tabs');
if (releaseTabs) {
  const tabs = [...releaseTabs.querySelectorAll('[role="tab"]')];
  const select = (platform) => {
    tabs.forEach((tab) => {
      const selected = tab.dataset.platform === platform;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
    });
    document.querySelectorAll('.release-panel').forEach((el) => {
      el.hidden = el.dataset.platform !== platform;
    });
    repoLink.href = 'https://github.com/samyyy2311/' + (platform === 'desktop' ? 'CassetteCat-Desktop' : 'CassetteCat');
    showStars();
  };
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => {
      select(tab.dataset.platform);
      history.replaceState(null, '', '#' + tab.dataset.platform);
    });
    tab.addEventListener('keydown', (event) => {
      const step = { ArrowRight: 1, ArrowLeft: -1 }[event.key];
      if (!step) return;
      const next = tabs[(index + step + tabs.length) % tabs.length];
      next.click();
      next.focus();
    });
  });
  // Older releases start collapsed, so a link to one, like #desktop-v1-0-0, expands it and what it sits in.
  const openAround = (el) => {
    for (let details = el?.closest('details'); details; details = details.parentElement.closest('details')) details.open = true;
  };
  const reveal = (id) => {
    const release = document.getElementById(id);
    openAround(release?.querySelector('details'));
    openAround(release);
  };
  // The browser scrolls before a collapsed release opens, so scroll again once it has.
  window.addEventListener('hashchange', () => {
    const id = location.hash.slice(1);
    reveal(id);
    document.getElementById(id)?.scrollIntoView({ behavior: 'instant' });
  });
  // A link to a release opens its app's tab and scrolls to it once it's shown.
  const target = location.hash.slice(1);
  select(target.startsWith('desktop') ? 'desktop' : 'android');
  releaseTabs.hidden = false;
  if (target) {
    reveal(target);
    document.getElementById(target)?.scrollIntoView({ behavior: 'instant' });
  }
}

document.querySelectorAll('.tour').forEach((tour) => {
  const track = tour.querySelector('.tour-track');
  tour.querySelectorAll('[data-scroll]').forEach((button) => {
    button.addEventListener('click', () => {
      const step = track.firstElementChild.offsetWidth + 28;
      track.scrollBy({ left: Number(button.dataset.scroll) * step, behavior: 'smooth' });
    });
  });
});

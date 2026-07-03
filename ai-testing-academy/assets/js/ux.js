/* Presentation layer: video players, scroll-spy, scroll-reveal, theme toggle,
   scroll progress, back-to-top, mobile nav drawer, nav-number chips, copy buttons.
   All run after i18n has injected the regions (see main.ts). */
import { $ } from './dom.js';
import { S } from './i18n.js';
/* explainer videos: attach players, show a placeholder if the file is missing */
function initVideos() {
    document.querySelectorAll('.video-card').forEach(card => {
        const src = card.dataset.src || '';
        const v = document.createElement('video');
        v.controls = true;
        v.preload = 'metadata';
        v.src = src;
        v.setAttribute('aria-label', card.querySelector('h4')?.textContent || '');
        const ph = document.createElement('div');
        ph.className = 'no-video';
        ph.textContent = S.videoLoading;
        v.addEventListener('loadedmetadata', () => { ph.remove(); });
        v.addEventListener('error', () => {
            v.remove();
            ph.textContent = S.videoMissingPrefix + src + S.videoMissingSuffix;
        });
        card.appendChild(v);
        card.appendChild(ph);
    });
}
/* sidebar scroll-spy: highlight the section in view */
function initScrollSpy() {
    const links = [...document.querySelectorAll('nav a.link')]
        .filter(a => (a.getAttribute('href') || '').startsWith('#'));
    const byId = Object.fromEntries(links.map(a => [(a.getAttribute('href') || '').slice(1), a]));
    const obs = new IntersectionObserver(entries => {
        entries.forEach(en => {
            if (en.isIntersecting) {
                links.forEach(a => a.classList.remove('active'));
                byId[en.target.id]?.classList.add('active');
            }
        });
    }, { rootMargin: '-25% 0px -65% 0px' });
    Object.keys(byId).forEach(id => { const s = document.getElementById(id); if (s)
        obs.observe(s); });
}
/* scroll-reveal: sections & cards float in */
function initReveal() {
    const targets = document.querySelectorAll('section > h2, section > .lead, section .card, section .agent-box, section pre, section table, section h3, section ul, section p');
    const io = new IntersectionObserver(es => es.forEach(en => {
        if (en.isIntersecting) {
            en.target.classList.add('in');
            io.unobserve(en.target);
        }
    }), { rootMargin: '0px 0px -8% 0px' });
    targets.forEach(el => { el.classList.add('reveal'); io.observe(el); });
}
/* theme, scroll progress, back-to-top, mobile drawer, nav chips, copy buttons */
function initChrome() {
    const root = document.documentElement;
    /* theme — saved choice, else OS preference */
    const applyTheme = (t) => {
        root.setAttribute('data-theme', t);
        const dark = t === 'dark';
        $('themeIcon').textContent = dark ? '☀️' : '🌙';
        $('themeLabel').textContent = dark ? S.themeLabelLight : S.themeLabelDark;
    };
    const saved = localStorage.getItem('ata_theme');
    applyTheme(saved || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));
    $('themeToggle').addEventListener('click', () => {
        const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        localStorage.setItem('ata_theme', next);
        applyTheme(next);
    });
    /* scroll progress + back-to-top */
    const bar = $('scrollProgress'), toTop = $('toTop');
    const onScroll = () => {
        const max = root.scrollHeight - root.clientHeight;
        bar.style.width = (max > 0 ? (root.scrollTop / max) * 100 : 0) + '%';
        toTop.classList.toggle('show', root.scrollTop > 500);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    toTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
    /* mobile nav drawer */
    const navToggle = $('navToggle'), scrim = $('navScrim');
    const setNav = (open) => {
        document.body.classList.toggle('nav-open', open);
        navToggle.setAttribute('aria-expanded', String(open));
    };
    navToggle.addEventListener('click', () => setNav(!document.body.classList.contains('nav-open')));
    scrim.addEventListener('click', () => setNav(false));
    document.querySelectorAll("nav a[href^='#']").forEach(a => a.addEventListener('click', () => setNav(false)));
    /* section-number chips in the nav */
    document.querySelectorAll("nav a.link[href^='#']").forEach(a => {
        const href = a.getAttribute('href') || '';
        const sec = document.querySelector(href);
        const num = sec?.querySelector('.num')?.textContent?.trim() || '';
        if (num) {
            const s = document.createElement('span');
            s.className = 'nav-num';
            s.setAttribute('aria-hidden', 'true');
            s.textContent = num;
            a.prepend(s);
        }
    });
    /* copy-to-clipboard on code blocks */
    document.querySelectorAll('main pre').forEach(pre => {
        const wrap = document.createElement('div');
        wrap.className = 'pre-wrap';
        pre.parentNode.insertBefore(wrap, pre);
        wrap.appendChild(pre);
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'copy-btn';
        btn.textContent = S.copyBtn;
        btn.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(pre.innerText);
                btn.textContent = S.copyBtnDone;
                btn.classList.add('copied');
                setTimeout(() => { btn.textContent = S.copyBtnReset; btn.classList.remove('copied'); }, 1600);
            }
            catch {
                btn.textContent = S.copyBtnFail;
            }
        });
        wrap.appendChild(btn);
    });
}
export function initUx() {
    initVideos();
    initScrollSpy();
    initReveal();
    initChrome();
}

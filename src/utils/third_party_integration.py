from typing import Any
import markdown2

class MaTex:
    def __init__(self, text: str) -> None:
        """
        Initialisiert das MaTex-Objekt.

        Args:
            text (str): Der Markdown/LaTeX-Inhalt der Dokumentation.
        """
        self.text: str = text

def render_matex(obj: Any) -> str:
    """
        Rendert ein MaTex-Objekt oder einen Standardwert als HTML-String für Taipy.

        Args:
            obj (Union[MaTex, Any]): Das zu rendernde Objekt. Falls es MaTex ist, wird Markdown/LaTeX verarbeitet.

        Returns:
            str: Der fertige HTML-Content inklusive Scripts und Styles.
    """
    if not isinstance(obj, MaTex):
        return str(obj)

    html_str: str = markdown2.markdown(obj.text, extras={"latex": None, "code-friendly": None,
                                                         "breaks": {"on_backslash": True},
                                                         "tables": None,"task_list": None})
    safe_html: str = html_str.replace("{", "{{").replace("}", "}}")

    mathjax_script: str = (
        '<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>'
        '<script>window.MathJax = { tex: { inlineMath: [["$", "$"]], displayMath: [["$$", "$$"]] } };</script>'
    )

    style: str = (
        "<style>"
        "body {"
        "  font-family: var(--font-family, 'Lato', Arial, sans-serif) !important;"
        "  color: var(--color-text, #1f1f1f) !important;"
        "  margin: 0; padding: 0;"
        "  display: flex; flex-direction: row; height: 100vh;"
        "  overflow: hidden !important; /* Kein doppelter Scrollbar */"
        "}"
        ".content-area { flex: 1; padding: 40px; overflow-y: auto; scroll-behavior: smooth; line-height: 1.5; }"
        ".sidebar {"
        "  flex: 0 0 20%; min-width: 180px; max-width: 400px;"
        "  border-left: 1px solid var(--color-border, #eee); padding: 25px;"
        "  height: 100vh; overflow-y: auto;"
        "  padding-top: 0px;"
        "  scrollbar-width: thin;"
        "  scrollbar-color: var(--custom-scrollbar-thumb-color) var(--custom-scrollbar-rail-color);"
        "}"
        ".sidebar a { text-decoration: none; color: var(--color-primary, #ff6049); font-size: 0.85rem; }"
        "a, a:visited, a:hover, a:active { color: var(--color-primary, #ff6049); }"
        ".sidebar a.active { font-weight: 700; }"
        ".sidebar ul { list-style: none; padding: 0; margin: 0; }"
        ".sidebar li { margin-bottom: 8px; }"
        ".source-highlight {"
        "  background: var(--color-primary, #ff6049);"
        "  color: #fff;"
        "  border-radius: 4px;"
        "  box-decoration-break: clone;"
        "  -webkit-box-decoration-break: clone;"
        "  transition: background-color 0.3s ease;"
        "}"
        ".content-area{"
        "  border: 0px !important;"
        "  padding: 0px !important;"
        "  padding-right: calc(2rem) !important;"
        "  scrollbar-width: thin;"
        "  scrollbar-color: var(--custom-scrollbar-thumb-color) var(--custom-scrollbar-rail-color);"
        "}"
        ".content-area::-webkit-scrollbar,"
        ".sidebar::-webkit-scrollbar {"
        "  width: 8px;"
        "}"
        ".content-area::-webkit-scrollbar-track,"
        ".sidebar::-webkit-scrollbar-track {"
        "  background: var(--custom-scrollbar-rail-color);"
        "}"
        ".content-area::-webkit-scrollbar-thumb,"
        ".sidebar::-webkit-scrollbar-thumb {"
        "  background-color: var(--custom-scrollbar-thumb-color);"
        "  border-radius: 8px;"
        "  border: 2px solid var(--custom-scrollbar-rail-color);"
        "}"
        ".content-area img {"
        "  max-width: 80% !important;"
        "  height: auto !important;"
        "  display: block !important;"
        "  margin: 20px auto !important;"
        "  border-radius: 4px;"
        "  cursor: zoom-in;"
        "}"
        ".image-lightbox-backdrop {"
        "  position: fixed;"
        "  inset: 0;"
        "  background: rgba(0, 0, 0, 0.45);"
        "  backdrop-filter: blur(1px);"
        "  display: none;"
        "  align-items: center;"
        "  justify-content: center;"
        "  z-index: 9999;"
        "}"
        ".image-lightbox-backdrop.is-open { display: flex; }"
        ".image-lightbox-backdrop img {"
        "  max-width: 92vw;"
        "  max-height: 92vh;"
        "  border-radius: 6px;"
        "  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);"
        "  cursor: zoom-in;"
        "  transition: transform 0.2s ease;"
        "}"
        ".image-lightbox-backdrop.is-zoomed img { cursor: grab; }"
        ".image-lightbox-backdrop.is-dragging img { cursor: grabbing; transition: none; }"
        "body.lightbox-open { overflow: hidden !important; }"
        "table { border-collapse: collapse; width: 100%; margin: 20px 0; }"
        "th, td { border: 1px solid var(--color-border, #dfe2e5); padding: 8px 12px; }"
        "</style>"
    )

    sync_script: str = """
    <script>
    let tocLinks = new Map();
    let tocHeaders = [];
    let sourceHeader = null;
    let sourceNumbers = new Set();

    function setExternalLinkTargets() {
        const links = document.querySelectorAll('a[href]');
        links.forEach((a) => {
            const href = a.getAttribute('href') || '';
            if (href.startsWith('#') || href.startsWith('javascript:')) return;
            a.setAttribute('target', '_blank');
            a.setAttribute('rel', 'noopener noreferrer');
        });
    }

    function findSourcesHeader() {
        const headers = document.querySelectorAll('.content-area h1, .content-area h2, .content-area h3');
        sourceHeader = null;
        headers.forEach((h) => {
            const text = (h.textContent || '').trim().toLowerCase();
            if (text === 'quellenverzeichnis' || text === 'literatur') sourceHeader = h;
        });
    }

    function markSourcesSection() {
        if (!sourceHeader) return;
        const headerLevel = parseInt(sourceHeader.tagName.substring(1), 10);
        let el = sourceHeader.nextElementSibling;
        sourceNumbers = new Set();

        while (el) {
            const tag = el.tagName ? el.tagName.toUpperCase() : '';
            if (tag === 'H1' || tag === 'H2' || tag === 'H3') {
                const level = parseInt(tag.substring(1), 10);
                if (!isNaN(level) && level <= headerLevel) break;
            }
            el.classList.add('sources-section');
            const text = (el.textContent || '').trim();
            const match = text.match(/^\\[(\\d+)\\]/);
            if (match) {
                const num = match[1];
                el.id = 'ref-' + num;
                sourceNumbers.add(num);
            }
            el = el.nextElementSibling;
        }
    }

    function linkCitations() {
        const contentArea = document.querySelector('.content-area');
        if (!contentArea || sourceNumbers.size === 0) return;

        const walker = document.createTreeWalker(contentArea, NodeFilter.SHOW_TEXT, {
            acceptNode(node) {
                if (!node.nodeValue || node.nodeValue.indexOf('[') === -1) {
                    return NodeFilter.FILTER_REJECT;
                }
                const parent = node.parentElement;
                if (!parent) return NodeFilter.FILTER_REJECT;
                if (parent.closest('.sources-section')) return NodeFilter.FILTER_REJECT;
                if (parent.closest('a, code, pre')) return NodeFilter.FILTER_REJECT;
                return NodeFilter.FILTER_ACCEPT;
            }
        });

        const nodes = [];
        while (walker.nextNode()) nodes.push(walker.currentNode);

        nodes.forEach((node) => {
            const text = node.nodeValue;
            const regex = /\\[(\\d+)\\]/g;
            let match;
            let lastIndex = 0;
            let changed = false;
            const frag = document.createDocumentFragment();

            while ((match = regex.exec(text)) !== null) {
                const num = match[1];
                if (!sourceNumbers.has(num)) continue;
                if (match.index > lastIndex) {
                    frag.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
                }
                const a = document.createElement('a');
                a.href = '#ref-' + num;
                a.textContent = match[0];
                a.className = 'citation-link';
                frag.appendChild(a);
                lastIndex = match.index + match[0].length;
                changed = true;
            }

            if (!changed) return;
            if (lastIndex < text.length) {
                frag.appendChild(document.createTextNode(text.slice(lastIndex)));
            }
            node.parentNode.replaceChild(frag, node);
        });
    }

    function highlightRef(id) {
        if (!id || !id.startsWith('ref-')) return;
        const el = document.getElementById(id);
        if (!el) return;
        el.classList.add('source-highlight');
        window.setTimeout(() => {
            el.classList.remove('source-highlight');
        }, 5000);
    }

    function scrollToId(id) {
        if (!id) return;
        const contentArea = document.querySelector('.content-area');
        const target = document.getElementById(id);
        if (!contentArea || !target) return;
        const offset = 8;
        const targetTop = target.getBoundingClientRect().top
            - contentArea.getBoundingClientRect().top
            + contentArea.scrollTop;
        contentArea.scrollTo({ top: Math.max(0, targetTop - offset), behavior: 'smooth' });
    }

    function initImageLightbox() {
        const contentArea = document.querySelector('.content-area');
        if (!contentArea) return;

        let backdrop = document.querySelector('.image-lightbox-backdrop');
        if (!backdrop) {
            backdrop = document.createElement('div');
            backdrop.className = 'image-lightbox-backdrop';
            backdrop.innerHTML = '<img alt="" />';
            document.body.appendChild(backdrop);
        }

        const backdropImg = backdrop.querySelector('img');
        if (!backdropImg) return;
        backdropImg.setAttribute('draggable', 'false');

        let zoom = 1;
        let translateX = 0;
        let translateY = 0;
        let isDragging = false;
        let didDrag = false;
        let startX = 0;
        let startY = 0;
        let startTranslateX = 0;
        let startTranslateY = 0;

        function clamp(value, min, max) {
            return Math.max(min, Math.min(max, value));
        }

        function applyTransform() {
            const paneRect = backdrop.getBoundingClientRect();
            const baseWidth = backdropImg.offsetWidth;
            const baseHeight = backdropImg.offsetHeight;
            const scaledWidth = baseWidth * zoom;
            const scaledHeight = baseHeight * zoom;
            const maxX = Math.max(0, (scaledWidth - paneRect.width) / 2);
            const maxY = Math.max(0, (scaledHeight - paneRect.height) / 2);
            translateX = clamp(translateX, -maxX, maxX);
            translateY = clamp(translateY, -maxY, maxY);
            backdropImg.style.transform = `translate(${translateX}px, ${translateY}px) scale(${zoom})`;
        }

        function setZoom(newZoom, resetPan) {
            zoom = newZoom;
            if (resetPan) {
                translateX = 0;
                translateY = 0;
            }
            backdrop.classList.toggle('is-zoomed', zoom > 1);
            applyTransform();
        }

        const close = () => {
            backdrop.classList.remove('is-open');
            backdrop.classList.remove('is-zoomed');
            backdrop.classList.remove('is-dragging');
            document.body.classList.remove('lightbox-open');
            backdropImg.removeAttribute('src');
            backdropImg.style.transform = '';
            zoom = 1;
            translateX = 0;
            translateY = 0;
            isDragging = false;
            didDrag = false;
        };

        backdrop.addEventListener('click', (event) => {
            if (event.target === backdrop) close();
        });

        window.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') close();
        });

        backdropImg.addEventListener('click', (event) => {
            if (didDrag) {
                didDrag = false;
                return;
            }
            event.preventDefault();
            if (zoom === 1) {
                setZoom(2, true);
            } else {
                setZoom(1, true);
            }
        });

        backdropImg.addEventListener('mousedown', (event) => {
            if (zoom <= 1) return;
            event.preventDefault();
            isDragging = true;
            didDrag = false;
            startX = event.clientX;
            startY = event.clientY;
            startTranslateX = translateX;
            startTranslateY = translateY;
            backdrop.classList.add('is-dragging');
        });

        window.addEventListener('mousemove', (event) => {
            if (!isDragging) return;
            const dx = event.clientX - startX;
            const dy = event.clientY - startY;
            if (Math.abs(dx) > 2 || Math.abs(dy) > 2) didDrag = true;
            translateX = startTranslateX + dx;
            translateY = startTranslateY + dy;
            applyTransform();
        });

        window.addEventListener('mouseup', () => {
            if (!isDragging) return;
            isDragging = false;
            backdrop.classList.remove('is-dragging');
        });

        contentArea.addEventListener('click', (event) => {
            const img = event.target.closest('img');
            if (!img || !contentArea.contains(img)) return;
            const link = img.closest('a');
            if (link) event.preventDefault();
            backdropImg.src = img.src;
            backdropImg.alt = img.alt || '';
            backdrop.classList.add('is-open');
            document.body.classList.add('lightbox-open');
            setZoom(1, true);
        });
    }

    function updateTheme() {
        try {
            const parent = window.parent.document;
            const parentHtml = parent.documentElement;
            const parentBody = parent.body;
            const parentStyle = window.parent.getComputedStyle(parentHtml);
            const myRoot = document.documentElement;

            // Prüfen, ob Taipy im Dark Mode ist
            const isDark = parentBody.classList.contains('taipy-dark-mode');
            const suffix = isDark ? '-dark' : '-light';

            // Mappen der nur absolut notwendigen Farben
            // Basierend auf der Browser Konsole:
            myRoot.style.setProperty('--color-paper', parentStyle.getPropertyValue('--color-paper' + suffix));
            myRoot.style.setProperty('--sidebar-bg', parentStyle.getPropertyValue('--color-background' + suffix));
            myRoot.style.setProperty('--color-primary', parentStyle.getPropertyValue('--color-primary'));
            myRoot.style.setProperty('--color-secondary', parentStyle.getPropertyValue('--color-secondary'));
            myRoot.style.setProperty('--color-border', 'gray');
            myRoot.style.setProperty('--custom-scrollbar-thumb-color', parentStyle.getPropertyValue('--custom-scrollbar-thumb-color'));
            myRoot.style.setProperty('--custom-scrollbar-rail-color', parentStyle.getPropertyValue('--custom-scrollbar-rail-color'));

            // Textfarbe: Taipy setzt diese oft direkt im Body
            const textColor = window.parent.getComputedStyle(parentBody).getPropertyValue('color');
            myRoot.style.setProperty('--color-text', textColor);

        } catch (e) { console.error("Theme Sync failed", e); }
    }

    // MutationObserver: Wartet darauf, dass Taipy die Klasse 'taipy-dark-mode' umschaltet
    const observer = new MutationObserver(() => updateTheme());

    function init() {
        updateTheme();
        // Beobachten des Body des Elternfensters auf Attribut-Änderungen (Classes)
        observer.observe(window.parent.document.body, { attributes: true });

        // TOC Generierung
        const sidebarList = document.getElementById('toc-list');
        const headers = document.querySelectorAll('.content-area h1, .content-area h2, .content-area h3');
        tocLinks = new Map();
        tocHeaders = Array.from(headers);
        headers.forEach((header, index) => {
            const id = 'nav-' + index;
            header.id = id;
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = '#' + id;
            a.innerHTML = header.innerHTML; 
            if(header.tagName === 'H2') li.style.paddingLeft = '10px';
            if(header.tagName === 'H3') li.style.paddingLeft = '20px';
            li.appendChild(a);
            sidebarList.appendChild(li);
            tocLinks.set(id, a);
        });

        setExternalLinkTargets();
        findSourcesHeader();
        markSourcesSection();
        linkCitations();

        if (window.MathJax && window.MathJax.typeset) window.MathJax.typeset();
        initScrollSpy();
        initImageLightbox();

        const contentArea = document.querySelector('.content-area');
        if (contentArea) {
            contentArea.addEventListener('click', (event) => {
                const link = event.target.closest('a.citation-link');
                if (!link) return;
                const href = link.getAttribute('href') || '';
                if (!href.startsWith('#')) return;
                event.preventDefault();
                const id = href.slice(1);
                scrollToId(id);
                highlightRef(id);
                if (history.replaceState) history.replaceState(null, '', '#' + id);
            });
        }

        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.addEventListener('click', (event) => {
                const link = event.target.closest('a[href^="#"]');
                if (!link) return;
                const href = link.getAttribute('href') || '';
                if (!href.startsWith('#')) return;
                event.preventDefault();
                const id = href.slice(1);
                scrollToId(id);
                if (history.replaceState) history.replaceState(null, '', '#' + id);
            });
        }

        window.addEventListener('hashchange', () => {
            const hash = window.location.hash || '';
            if (!hash.startsWith('#')) return;
            const id = hash.slice(1);
            scrollToId(id);
            highlightRef(id);
        });
    }
    window.addEventListener('load', init);

    function initScrollSpy() {
        const contentArea = document.querySelector('.content-area');
        if (!contentArea || tocHeaders.length === 0) return;

        let ticking = false;

        const updateActive = () => {
            const scrollTop = contentArea.scrollTop;
            const offset = 8;
            let activeId = tocHeaders[0].id;

            for (const header of tocHeaders) {
                if (scrollTop + offset >= header.offsetTop) {
                    activeId = header.id;
                } else {
                    break;
                }
            }

            tocLinks.forEach((link, id) => {
                link.classList.toggle('active', id === activeId);
            });
        };

        const onScroll = () => {
            if (ticking) return;
            ticking = true;
            window.requestAnimationFrame(() => {
                updateActive();
                ticking = false;
            });
        };

        contentArea.addEventListener('scroll', onScroll);
        window.addEventListener('resize', updateActive);
        updateActive();
    }
    </script>
    """

    return (f'{mathjax_script}{style}{sync_script}'
            f'<div class="content-area">{safe_html}</div>'
            f'<div class="sidebar"><h3>Inhalt</h3><ul id="toc-list"></ul></div>'
            f'<div class="image-lightbox-backdrop" aria-hidden="true"><img alt=""/></div>')

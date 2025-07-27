(function () {
    const TRACKING_ENDPOINT = "http://127.0.0.1:5000/track";
    const userIdKey = "tracking_user_id";
    const sessionIdKey = "tracking_session_id";

    function getOrCreateId(key) {
        let id = localStorage.getItem(key);
        if (!id) {
            id = "id_" + Math.random().toString(36).substring(2) + Date.now();
            localStorage.setItem(key, id);
        }
        return id;
    }

    const user_id = getOrCreateId(userIdKey);
    const session_id = getOrCreateId(sessionIdKey);

    // Fonction pour envoyer un événement immédiatement
    function sendEvent(type, data) {
        const payload = {
            user_id,
            session_id,
            events: [{
                type,
                timestamp: new Date().toISOString(),
                data
            }]
        };
        navigator.sendBeacon(
            TRACKING_ENDPOINT,
            JSON.stringify(payload)
        );
    }

    // Page view
    sendEvent("page_view", {
        url: window.location.href,
        title: document.title,
        viewport: {
            width: window.innerWidth,
            height: window.innerHeight
        }
    });

    // Click tracking
    document.addEventListener("click", function (e) {
        const target = e.target;
        if (!target) return;

        const tag = target.tagName.toLowerCase();
        const data = {
            tag,
            id: target.id || null,
            class: target.classList ? Array.from(target.classList) : [],
            text: target.innerText?.trim().substring(0, 100) || null,
            href: target.href || null,
            position: {
                x: e.clientX,
                y: e.clientY
            },
            
            time_on_page: (performance.now() / 1000).toFixed(2)
        };

        sendEvent("click", data);
    });

    // Scroll tracking (avec profondeur max)
    let maxScroll = 0;
    window.addEventListener("scroll", function () {
        const total = document.body.scrollHeight - window.innerHeight;
        const percent = Math.round((window.scrollY / total) * 100);
        if (percent > maxScroll) {
            maxScroll = percent;
            sendEvent("scroll_depth", {
                scroll_depth_percentage: percent,
                timestamp: new Date().toISOString()
            });
        }
    });
})();
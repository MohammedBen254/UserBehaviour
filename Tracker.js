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

    // Engagement tracking variables
    let activeStartTime = Date.now();
    let clickCount = 0;
    let engagementCheckTriggered = false;

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

        // Incrémenter le compteur de clics
        clickCount++;
    });

    // Scroll tracking (avec profondeur max)
    // let maxScroll = 0;
    // window.addEventListener("scroll", function () {
    //     const total = document.body.scrollHeight - window.innerHeight;
    //     const percent = Math.round((window.scrollY / total) * 100);
    //     if (percent > maxScroll) {
    //         maxScroll = percent;
    //         sendEvent("scroll_depth", {
    //             scroll_depth_percentage: percent,
    //             timestamp: new Date().toISOString()
    //         });
    //     }
    // });

    // Engagement logic
    function checkEngagement() {
        const timeSpent = (Date.now() - activeStartTime) / 1000; // in seconds
        const formAlreadyShown = localStorage.getItem("form_shown") === "true";

        if (!engagementCheckTriggered && !formAlreadyShown && timeSpent >= 4 && clickCount >= 2) {
            engagementCheckTriggered = true;
            localStorage.setItem("form_shown", "true");  // Marque le formulaire comme déjà affiché
            showNeedForm();
        }
    }


    // Vérification du temps chaque 1 seconde (plus réactif)
    setInterval(checkEngagement, 1000);

    // Fonction pour afficher un formulaire flottant
    function showNeedForm() {
        const formDiv = document.createElement("div");
        formDiv.innerHTML = `
            <div style="position:fixed; bottom:20px; right:20px; background:white; padding:20px; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.2); z-index:9999; max-width:300px;">
                <h5>🧐 Avez-vous un besoin spécifique ?</h5>
                <textarea placeholder="Décrivez votre besoin..." style="width:100%; margin-bottom:10px;"></textarea>
                <button class="btn btn-primary btn-sm">Envoyer</button>
                <button class="btn btn-secondary btn-sm" style="float:right;">Fermer</button>
            </div>
        `;
        document.body.appendChild(formDiv);

        const [sendBtn, closeBtn] = formDiv.querySelectorAll("button");
        sendBtn.addEventListener("click", () => {
            const message = formDiv.querySelector("textarea").value.trim();
            if (message) {
                sendEvent("user_need", { message });
                formDiv.remove();
                alert("Merci ! Votre message a été envoyé.");
            }
        });

        closeBtn.addEventListener("click", () => {
            formDiv.remove();
        });
    }
})();
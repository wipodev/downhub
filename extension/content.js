// content.js

// --- Config -----------------------------------------------------------------
const API_MESSAGE = "DOWNLOAD_URL";

// Selectors you provided
const YT_CONTAINER_SELECTOR =
  "#movie_player > div.ytp-chrome-bottom > div.ytp-chrome-controls > div.ytp-right-controls";

const KICK_CONTAINER_SELECTOR = "#injected-embedded-channel-player-video > div > div > div:nth-child(2)";

// Unique IDs to avoid double injections
const BTN_ID_YT = "dl-icon-btn-yt";
const BTN_ID_KICK = "dl-icon-btn-kick";

// --- Notification container setup -------------------------------------------
let notificationContainer = document.getElementById("dl-notification-container");
if (!notificationContainer) {
  notificationContainer = document.createElement("div");
  notificationContainer.id = "dl-notification-container";
  document.body.appendChild(notificationContainer);
}

function showNotification(message, type, duration = 2000) {
  const notification = document.createElement("div");
  notification.className = `dl-toast ${type}`;
  notification.textContent = message;

  notificationContainer.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = "toastSlideOut 0.3s ease forwards";
    setTimeout(() => {
      if (notification.parentNode) {
        notificationContainer.removeChild(notification);
      }
    }, 300);
  }, duration);
}

// --- Site detection ----------------------------------------------------------
function isYouTubeWatch() {
  return location.hostname.includes("youtube.com") && /\/watch/.test(location.pathname);
}

function isKickVod() {
  return location.hostname.includes("kick.com") && /^\/[^/]+\/videos?\//.test(location.pathname);
}

// --- Utilities ---------------------------------------------------------------
function debounce(fn, ms = 100) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
}

function sendToBackend(url) {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage({ type: API_MESSAGE, url }, (res) => resolve(res));
  });
}

function createIconButton({ id, title = "Download" }) {
  const btn = document.createElement("button");
  btn.id = id;
  btn.title = title;
  btn.classList.add("ytp-button");

  if (title === "Download VOD") {
    Object.assign(btn.style, {
      padding: "5px",
      width: "44px",
      height: "44px",
      cursor: "pointer",
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",
      opacity: "0.95",
    });
  }

  btn.addEventListener("mouseenter", () => (btn.style.opacity = "1"));
  btn.addEventListener("mouseleave", () => (btn.style.opacity = "0.95"));

  btn.innerHTML = `
    <svg version="1.1" width="100%" height="100%" viewBox="0 0 36 36">
 <path d="m9.2 20.447c-0.6648 0-1.2 0.54774-1.2 1.2281v5.5437c0 0.0048 6.52e-4 0.0094 7.04e-4 0.01422-4e-5 0.0047-7.04e-4 0.0092-7.04e-4 0.0139 0 0.6648 0.5352 1.2 1.2 1.2h17.6c0.6648 0 1.2-0.5352 1.2-1.2 0-0.0047-6.48e-4 -0.0092-7.04e-4 -0.0139 4e-5 -0.0048 7.04e-4 -0.0094 7.04e-4 -0.01422v-5.5437c0-0.68039-0.5352-1.2281-1.2-1.2281s-1.2 0.54774-1.2 1.2281v4.3719h-15.2v-4.3719c0-0.68039-0.5352-1.2281-1.2-1.2281zm8.7989-12.895c-0.6648 0-1.2 0.5352-1.2 1.2v10.701l-3.3244-3.3244c-0.47008-0.47008-1.2269-0.47008-1.697 0-0.47008 0.47009-0.47008 1.2269 0 1.697l5.3346 5.3346c0.17055 0.18717 0.399 0.32012 0.65844 0.36976 0.0026 4.8e-4 0.0052 6.8e-4 0.0077 0.0012 0.03437 0.0063 0.06903 0.01178 0.10438 0.01516 0.03184 0.0031 0.06375 0.0043 0.0957 0.0048 0.0069 0 0.01361 1e-3 0.02055 1e-3h5.44e-4c0.03976 1.6e-5 0.07954-0.0021 0.11914-6e-3 0.01766-0.0017 0.03477-0.0051 0.05219-0.0076 0.02077-3e-3 0.04157-0.0054 0.06219-0.0095 0.02671-0.0052 0.05272-0.01224 0.07875-0.01922 0.01096-3e-3 0.02207-0.0052 0.03297-0.0084 0.03293-0.0098 0.06498-0.02148 0.09664-0.03398 0.0037-0.0015 0.0075-0.0026 0.01117-0.0041 0.15661-0.06367 0.29616-0.15942 0.41133-0.27914l5.3588-5.3587c0.47008-0.47008 0.47008-1.2269 0-1.697-0.47009-0.47008-1.227-0.47008-1.6971 0l-3.3266 3.3266v-10.703c0-0.6648-0.5352-1.2-1.2-1.2z" fill="#fff"/>
</svg>
  `;

  btn.addEventListener("click", async () => {
    const prev = btn.innerHTML;
    btn.disabled = true;

    showNotification("Starting download...", "info", 3000);

    try {
      const res = await sendToBackend(location.href);

      if (res?.ok && res?.data?.task_id) {
        const taskId = res.data.task_id;
        btn.style.filter = "drop-shadow(0 0 6px rgba(0,255,0,.6))";
        showNotification("Download started in background", "success", 3000);

        // 🔄 Polling
        const interval = setInterval(async () => {
          try {
            const statusRes = await fetch(`http://127.0.0.1:8000/status/${taskId}`);
            const statusData = await statusRes.json();

            if (statusData.status === "completed") {
              showNotification("✅ Download completed!", "success", 4000);
              clearInterval(interval);
            } else if (statusData.status === "error") {
              showNotification(`❌ Error: ${statusData.error_msg}`, "error", 4000);
              clearInterval(interval);
            }
          } catch (err) {
            console.error("Status check error:", err);
            clearInterval(interval);
          }
        }, 4000);
      } else {
        btn.style.filter = "drop-shadow(0 0 6px rgba(255,0,0,.6))";
        showNotification("Download failed!", "error", 4000);
      }

      setTimeout(() => (btn.style.filter = ""), 800);
    } catch (e) {
      console.error(e);
      showNotification("An error occurred!", "error", 4000);
    } finally {
      btn.innerHTML = prev;
      btn.disabled = false;
    }
  });

  return btn;
}

function alreadyInjected(container, id) {
  return container && container.querySelector(`#${id}`);
}

function waitForElement(selector, timeoutMs = 20000) {
  return new Promise((resolve, reject) => {
    const existing = document.querySelector(selector);
    if (existing) {
      return resolve(existing);
    }

    const obs = new MutationObserver(() => {
      const el = document.querySelector(selector);
      if (el) {
        obs.disconnect();
        resolve(el);
      }
    });
    obs.observe(document.documentElement, { childList: true, subtree: true });

    setTimeout(() => {
      obs.disconnect();
      const el = document.querySelector(selector);
      if (el) {
        resolve(el);
      } else {
        reject(new Error("Timeout waiting for: " + selector));
      }
    }, timeoutMs);
  });
}

// --- Injection per site ------------------------------------------------------
async function injectYouTube() {
  if (!isYouTubeWatch()) return;
  try {
    const container = await waitForElement(YT_CONTAINER_SELECTOR, 25000);
    if (!container || alreadyInjected(container, BTN_ID_YT)) return;
    const btn = createIconButton({ id: BTN_ID_YT, title: "Download" });
    container.insertBefore(btn, container.firstChild);
  } catch {}
}

async function injectKick() {
  if (!isKickVod()) return;
  try {
    const container = await waitForElement(KICK_CONTAINER_SELECTOR, 25000);
    if (!container || alreadyInjected(container, BTN_ID_KICK)) {
      return;
    }
    const btn = createIconButton({ id: BTN_ID_KICK, title: "Download VOD" });
    container.appendChild(btn);
  } catch (err) {
    console.error("[Downloader] injectKick() error:", err);
  }
}

// --- Router (SPA) handling ---------------------------------------------------
let lastUrl = location.href;

const handleRouteChange = debounce(() => {
  if (lastUrl !== location.href) {
    lastUrl = location.href;
    injectYouTube();
    injectKick();
  }
}, 80);

const origPushState = history.pushState;
history.pushState = function () {
  origPushState.apply(this, arguments);
  handleRouteChange();
};

const origReplaceState = history.replaceState;
history.replaceState = function () {
  origReplaceState.apply(this, arguments);
  handleRouteChange();
};

window.addEventListener("popstate", handleRouteChange);

const mo = new MutationObserver(
  debounce(() => {
    injectYouTube();
    injectKick();
  }, 150)
);
mo.observe(document.documentElement, { childList: true, subtree: true });

// Initial run
injectYouTube();
injectKick();

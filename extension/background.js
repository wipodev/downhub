// background.js
const API_BASE = "http://127.0.0.1:8000";

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg?.type === "DOWNLOAD_URL") {
    (async () => {
      try {
        const r = await fetch(`${API_BASE}/download`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: msg.url }),
        });
        const data = await r.json().catch(() => ({}));
        sendResponse({ ok: r.ok, data, status: r.status });
      } catch (e) {
        sendResponse({ ok: false, error: String(e) });
      }
    })();
    return true;
  }

  if (msg?.type === "STATUS_TASK" && msg?.taskId) {
    (async () => {
      try {
        const r = await fetch(`${API_BASE}/status/${msg.taskId}`);
        const data = await r.json().catch(() => ({}));
        sendResponse({ ok: r.ok, data, status: r.status });
      } catch (e) {
        sendResponse({ ok: false, error: String(e) });
      }
    })();
    return true;
  }
});

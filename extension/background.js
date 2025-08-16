// background.js

// Relay requests to the local API (FastAPI) to avoid CORS surprises and keep logic centralized.
chrome.runtime.onMessage.addListener(async (msg, _sender, sendResponse) => {
  if (msg?.type === "DOWNLOAD_URL" && typeof msg.url === "string") {
    try {
      const res = await fetch("http://127.0.0.1:8000/download", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: msg.url }),
      });

      let data = null;
      try {
        data = await res.json();
      } catch {
        data = { message: "No JSON body" };
      }

      sendResponse({ ok: res.ok, status: res.status, data });
    } catch (err) {
      sendResponse({ ok: false, status: 0, error: String(err) });
    }
    // Keep the message channel open for the async response
    return true;
  }
});

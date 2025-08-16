const activePolls = new Map();

/**
 * Crea un botón con lógica de descarga ya lista.
 */
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
<svg version="1.1" width="100%" height="100%" viewBox="0 0 36 36" aria-hidden="true" focusable="false">
  <path d="m9.2 20.447c-0.6648 0-1.2 0.54774-1.2 1.2281v5.5437c0 0.0048 6.52e-4 0.0094 7.04e-4 0.01422-4e-5 0.0047-7.04e-4 0.0092-7.04e-4 0.0139 0 0.6648 0.5352 1.2 1.2 1.2h17.6c0.6648 0 1.2-0.5352 1.2-1.2 0-0.0047-6.48e-4 -0.0092-7.04e-4 -0.0139 4e-5 -0.0048 7.04e-4 -0.0094 7.04e-4 -0.01422v-5.5437c0-0.68039-0.5352-1.2281-1.2-1.2281s-1.2 0.54774-1.2 1.2281v4.3719h-15.2v-4.3719c0-0.68039-0.5352-1.2281-1.2-1.2281zm8.7989-12.895c-0.6648 0-1.2 0.5352-1.2 1.2v10.701l-3.3244-3.3244c-0.47008-0.47008-1.2269-0.47008-1.697 0-0.47008 0.47009-0.47008 1.2269 0 1.697l5.3346 5.3346c0.17055 0.18717 0.399 0.32012 0.65844 0.36976 0.0026 4.8e-4 0.0052 6.8e-4 0.0077 0.0012 0.03437 0.0063 0.06903 0.01178 0.10438 0.01516 0.03184 0.0031 0.06375 0.0043 0.0957 0.0048 0.0069 0 0.01361 1e-3 0.02055 1e-3h5.44e-4c0.03976 1.6e-5 0.07954-0.0021 0.11914-6e-3 0.01766-0.0017 0.03477-0.0051 0.05219-0.0076 0.02077-3e-3 0.04157-0.0054 0.06219-0.0095 0.02671-0.0052 0.05272-0.01224 0.07875-0.01922 0.01096-3e-3 0.02207-0.0052 0.03297-0.0084 0.03293-0.0098 0.06498-0.02148 0.09664-0.03398 0.0037-0.0015 0.0075-0.0026 0.01117-0.0041 0.15661-0.06367 0.29616-0.15942 0.41133-0.27914l5.3588-5.3587c0.47008-0.47008 0.47008-1.2269 0-1.697-0.47009-0.47008-1.227-0.47008-1.6971 0l-3.3266 3.3266v-10.703c0-0.6648-0.5352-1.2-1.2-1.2z" fill="#fff"/>
</svg>`;

  // Click handler with proxy & sticky progress
  btn.addEventListener("click", async () => {
    const prev = btn.innerHTML;
    btn.disabled = true;

    showNotification("Starting download...", "info", 1200);

    try {
      const res = await sendToBackend(location.href);
      if (!res?.ok) {
        btn.style.filter = "drop-shadow(0 0 6px rgba(255,0,0,.6))";
        showNotification("❌ Backend not reachable", "error", 3200);
        return;
      }

      const taskId = res?.data?.task_id;
      if (!taskId) {
        console.warn("[DownHub] No task_id in response:", res);
        showNotification("⚠️ Waiting for task id…", "info", 2000);
        return;
      }

      btn.style.filter = "drop-shadow(0 0 6px rgba(0,255,0,.6))";
      const sticky = showSticky("⬇️ Downloading…", "info");

      // Avoid duplicate polls per task
      if (activePolls.has(taskId)) {
        clearInterval(activePolls.get(taskId));
        activePolls.delete(taskId);
      }

      const interval = setInterval(async () => {
        try {
          const statusRes = await getTaskStatus(taskId);
          if (!statusRes.ok) {
            console.error("Status check error:", statusRes.error || statusRes.status);
            sticky.update("⚠️ Lost connection while checking status", "error");
            clearInterval(interval);
            activePolls.delete(taskId);
            setTimeout(() => sticky.close(), 2500);
            return;
          }

          const statusData = statusRes.data;
          if (statusData.status === "completed") {
            sticky.update("✅ Download completed!", "success");
            clearInterval(interval);
            activePolls.delete(taskId);
            setTimeout(() => sticky.close(), 1800);
          } else if (statusData.status === "error") {
            sticky.update(`❌ Error: ${statusData.error_msg || "unknown"}`, "error");
            clearInterval(interval);
            activePolls.delete(taskId);
            setTimeout(() => sticky.close(), 2500);
          } else {
            // Keep-alive animation
            const dots = ["", ".", "..", "..."];
            const i = Math.floor(Date.now() / 800) % dots.length;
            sticky.update(`⬇️ Downloading${dots[i]}`, "info");
          }
        } catch (err) {
          console.error("Status check error:", err);
          sticky.update("⚠️ Lost connection while checking status", "error");
          clearInterval(interval);
          activePolls.delete(taskId);
          setTimeout(() => sticky.close(), 2500);
        }
      }, 2000);

      activePolls.set(taskId, interval);
    } catch (e) {
      console.error(e);
      showNotification("An error occurred!", "error", 3200);
    } finally {
      setTimeout(() => (btn.style.filter = ""), 800);
      btn.innerHTML = prev;
      btn.disabled = false;
    }
  });

  return btn;
}

/**
 * Inyecta el botón en un contenedor según configuración de sitio.
 */
async function injectButton({ selector, id, title }) {
  try {
    const container = await waitForElement(selector, 25000);
    if (!container || alreadyInjected(container, id)) return;
    const btn = createIconButton({ id, title });
    container.insertBefore(btn, container.firstChild);
  } catch (err) {
    console.warn("[DownHub] injectButton error:", err.message);
  }
}

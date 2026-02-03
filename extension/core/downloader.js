/**
 * core/downloader.js
 * Lógica de creación e inyección del botón de descarga.
 */

/**
 * Crea e inserta el botón de descarga en el sitio correspondiente.
 */
async function injectButton(site) {
  const container = await waitForElement(site.selector);

  if (!container || alreadyInjected(container, site.id)) {
    return;
  }

  // Crear el botón
  const btn = document.createElement("button");
  btn.id = site.id;
  btn.className = `downhub-btn ${site.styleClass || ""}`;
  btn.title = site.title;
  // Estado inicial
  btn.setAttribute("data-status", "idle");

  // Icono SVG minimalista para evitar dependencias de archivos externos
  btn.innerHTML = `
    <svg width="36" height="36" viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg">
 <path d="m2.8384 22.217c-1.1454 0-2.0675 0.94371-2.0675 2.1159v9.5513c0 0.0083 0.00112 0.0162 0.00121 0.0245-6.59e-5 0.0081-0.00121 0.01585-0.00121 0.02395 0 1.1454 0.9221 2.0675 2.0675 2.0675h30.323c1.1454 0 2.0675-0.9221 2.0675-2.0675 0-0.0081-0.0011-0.01584-0.0012-0.02394 6.8e-5 -0.0083 0.0012-0.0162 0.0012-0.0245v-9.5513c0-1.1722-0.9221-2.1159-2.0675-2.1159-1.1454 0-2.0675 0.94371-2.0675 2.1159v7.5324h-26.188v-7.5324c0-1.1722-0.9221-2.1159-2.0675-2.1159zm15.16-22.217c-1.1454 0-2.0675 0.9221-2.0675 2.0675v18.437l-5.7276-5.7276c-0.8099-0.8099-2.1138-0.8099-2.9238 0-0.8099 0.80992-0.8099 2.1138 0 2.9238l9.191 9.191c0.29384 0.32248 0.68744 0.55154 1.1344 0.63706 0.0045 8.28e-4 9e-3 0.0012 0.01332 2e-3 0.05922 0.0108 0.11893 0.0203 0.17984 0.02612 0.05486 0.0054 0.10984 0.0074 0.16488 0.0083 0.01188 0 0.02345 0.0017 0.03541 0.0017h9.37e-4c0.06851 2.8e-5 0.13703-0.0036 0.20527-0.01026 0.03042-0.0029 0.0599-0.0088 0.08993-0.01314 0.03578-0.0052 0.07162-0.0094 0.10715-0.01638 0.04603-9e-3 0.09083-0.02108 0.13568-0.03312 0.01888-0.0052 0.03803-9e-3 0.05681-0.0144 0.05674-0.01692 0.11196-0.03701 0.1665-0.05854 0.0063-0.0025 0.01296-0.0045 0.01924-7e-3 0.26982-0.10969 0.51026-0.27466 0.70868-0.48093l9.2327-9.2325c0.8099-0.8099 0.8099-2.1138 0-2.9238-0.80992-0.8099-2.114-0.8099-2.9239 0l-5.7315 5.7313v-18.44c0-1.1454-0.9221-2.0675-2.0675-2.0675z"/>
</svg>`;

  // Evento de clic
  btn.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();

    handleDownloadRequest(site);
  });

  container.insertBefore(btn, container.firstChild);
}

/**
 * Gestiona la captura de datos, el envío o la cancelación.
 */
function handleDownloadRequest(site) {
  const btn = document.getElementById(site.id);
  if (!btn) return;

  const currentStatus = btn.getAttribute("data-status");

  // Si ya se está descargando, el clic actúa como CANCELAR
  if (currentStatus === "downloading") {
    console.log("[DownHub] Solicitando cancelación...");
    const userConfirmed = confirm(
      "¿Estás seguro de que quieres cancelar la descarga actual?\nSe eliminará el progreso y el archivo temporal.",
    );
    if (userConfirmed) {
      console.log("[DownHub] Cancelación confirmada por el usuario.");
      chrome.runtime.sendMessage({ action: PROTOCOL.ACTIONS.CANCEL_DOWNLOAD });
      btn.disabled = true;
    } else {
      console.log("[DownHub] Cancelación abortada por el usuario.");
    }
    return;
  }

  // Si está en idle, iniciamos descarga
  const videoTitle = document.title.replace(/[\\/:*?"<>|]/g, "") || "video_download";
  const videoUrl = window.location.href;

  btn.setAttribute("data-status", "downloading");
  btn.classList.add("is-downloading"); // Para estilos CSS (ej. cambiar color a rojo)
  btn.title = "Haz clic para cancelar la descarga";

  console.log(`[DownHub] Solicitando descarga: ${videoTitle}`);

  chrome.runtime.sendMessage({
    action: PROTOCOL.ACTIONS.START_DOWNLOAD,
    payload: {
      url: videoUrl,
      filename: `${videoTitle}.mp4`,
    },
  });
}

// Escuchar cuando el proceso termine para rehabilitar el botón
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === PROTOCOL.MESSAGES.DONE || msg.type === PROTOCOL.MESSAGES.ERROR) {
    const btns = document.querySelectorAll(".downhub-btn");
    btns.forEach((b) => {
      b.disabled = false;
      b.setAttribute("data-status", "idle");
      b.classList.remove("is-downloading");
      b.title = "Descargar con DownHub";
    });
    console.log("[DownHub] Botón restablecido");
  }
});

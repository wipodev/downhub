/**
 * background/main.js
 */

importScripts("../utils/config.js");

let nativePort = null;
let bgBitmap = null;
let currentDownloadTabId = null;

async function loadProgressBase() {
  if (bgBitmap) return bgBitmap;
  const response = await fetch(chrome.runtime.getURL("ui/icons/icon-progress-bg.png"));
  const blob = await response.blob();
  bgBitmap = await createImageBitmap(blob);
  return bgBitmap;
}

// Función para dibujar el progreso en el icono
async function updateIconProgress(percent) {
  const canvas = new OffscreenCanvas(128, 128);
  const ctx = canvas.getContext("2d");
  const bitmap = await loadProgressBase();

  ctx.clearRect(0, 0, 128, 128);
  ctx.drawImage(bitmap, 0, 0);

  // 2. Dibujamos el anillo si hay progreso
  if (percent > 0) {
    const centerX = 64;
    const centerY = 64;
    const radius = 60; // Casi al borde del canvas (128/2)
    const startAngle = -0.5 * Math.PI;
    const endAngle = (percent / 100) * 2 * Math.PI + startAngle;

    // Anillo de progreso (Verde fluido)
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, startAngle, endAngle);
    ctx.lineWidth = 6;
    ctx.strokeStyle = "#00FF00";
    ctx.lineCap = "round";
    ctx.stroke();
  }

  const imageData = ctx.getImageData(0, 0, 128, 128);
  chrome.action.setIcon({ imageData });
}

function resetIcon() {
  // Volvemos al icono normal de la app (el que no tiene el aro)
  chrome.action.setIcon({ path: "/ui/icons/icon-128.png" });
}

/**
 * Establece conexión con el Host de Python
 */
function connectToNativeHost() {
  console.log(`[DownHub] Conectando a ${PROTOCOL.HOST_NAME}...`);
  nativePort = chrome.runtime.connectNative(PROTOCOL.HOST_NAME);

  nativePort.onMessage.addListener((msg) => {
    handleNativeMessage(msg);
  });

  nativePort.onDisconnect.addListener(() => {
    nativePort = null;
    resetIcon();
    console.info("[DownHub] Puerto nativo desconectado");
  });

  return nativePort;
}

/**
 * Escucha los mensajes que vienen de Python
 */
function handleNativeMessage(msg) {
  console.log("[DownHub-BG] Mensaje desde Python:", msg);
  switch (msg.type) {
    case PROTOCOL.MESSAGES.PROGRESS:
      const percentToDraw = msg.status.includes("FFmpeg") ? 100 : msg.percent;
      updateIconProgress(percentToDraw);
      break;

    case PROTOCOL.MESSAGES.DONE:
      resetAll(msg);
      break;

    case PROTOCOL.MESSAGES.ERROR:
      resetAll(msg);
      console.error("Error/Cancelación en la descarga", msg.message);
      break;
  }
}

function resetAll(msg) {
  resetIcon();

  const targetTabId = currentDownloadTabId;
  currentDownloadTabId = null;

  if (targetTabId) {
    chrome.tabs.sendMessage(targetTabId, msg, () => {
      if (chrome.runtime.lastError) {
        console.info("[DownHub] La pestaña original se cerró, no se pudo notificar.");
      }
    });
  } else {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0])
        chrome.tabs.sendMessage(tabs[0].id, msg, () => {
          if (chrome.runtime.lastError) {
            /* Silencio */
          }
        });
    });
  }

  if (nativePort) {
    nativePort.disconnect();
    nativePort = null;
  }
}

/**
 * Escucha las peticiones de los Content Scripts (el botón de descarga)
 */
chrome.runtime.onMessage.addListener((request, sender) => {
  if (request.action === PROTOCOL.ACTIONS.START_DOWNLOAD) {
    if (nativePort) {
      console.log("[DownHub-BG] Limpiando puerto previo.");
      try {
        nativePort.disconnect();
      } catch (e) {}
      nativePort = null;
    }

    currentDownloadTabId = sender.tab.id;
    const port = connectToNativeHost();

    // Enviamos la orden a Python usando el formato que espera el JSON
    port.postMessage({
      type: PROTOCOL.PYTHON_TYPES.DOWNLOAD,
      url: request.payload.url,
      filename: request.payload.filename,
    });
  }

  // 2. CANCELAR DESCARGA (Nueva lógica)
  if (request.action === PROTOCOL.ACTIONS.CANCEL_DOWNLOAD) {
    if (nativePort) {
      console.log("[DownHub-BG] Solicitando cancelación a Python...");

      // 1. Desconectamos el puerto inmediatamente
      nativePort.disconnect();
      nativePort = null;

      // 2. Esperamos 3 segundos antes de resetear la UI
      // Esto da tiempo a que Python termine su proceso de limpieza silencioso
      setTimeout(() => {
        console.log("[DownHub-BG] Reset de interfaz post-cancelación.");
        resetAll({
          type: PROTOCOL.MESSAGES.ERROR,
          message: "Descarga cancelada por el usuario",
        });
      }, 3000);
    }
  }
});

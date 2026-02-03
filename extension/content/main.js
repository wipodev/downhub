/**
 * content/main.js
 * Punto de entrada que coordina la detección del sitio y la inyección.
 */

function initDownHub() {
  const currentSite = sites.find((site) => site.match());

  if (currentSite) {
    if (alreadyInjected(document, currentSite.id)) return;
    console.log(`[DownHub] Intentando inyectar en: ${currentSite.name}`);
    injectButton(currentSite);
  }
}

// 1. Ejecutar al cargar la página por primera vez
initDownHub();

// 2. Observador de "Supervivencia"
// Este observador reacciona a cambios en el DOM (como redimensionar o navegar)
const globalObserver = new MutationObserver(
  debounce(() => {
    initDownHub();
  }, 500),
);

globalObserver.observe(document.body, {
  childList: true,
  subtree: true,
});

// Mantenemos el observador de título por si acaso para SPA puro
const titleObserver = new MutationObserver(() => initDownHub());
if (document.querySelector("title")) {
  titleObserver.observe(document.querySelector("title"), { childList: true });
}

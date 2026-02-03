/**
 * utils/dom.js
 * Utilidades para manipulación del DOM y observación de elementos asíncronos.
 */

/**
 * Evita que una función se ejecute demasiadas veces seguidas.
 * Útil para observar cambios de scroll o redimensionamiento.
 */
function debounce(fn, ms = 100) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
}

/**
 * Verifica si el botón ya existe para evitar duplicados.
 */
function alreadyInjected(container, elementId) {
  if (!container) return false;
  return container.querySelector(`#${elementId}`) !== null;
}

/**
 * Espera a que un elemento aparezca en el DOM.
 * @returns {Promise<Element|null>} Retorna el elemento o null si excede el tiempo.
 */
function waitForElement(selector, timeoutMs = 15000) {
  return new Promise((resolve) => {
    // 1. Verificación inmediata
    const existing = document.querySelector(selector);
    if (existing) return resolve(existing);

    // 2. Configuración del Observador
    const observer = new MutationObserver((mutations, obs) => {
      const el = document.querySelector(selector);
      if (el) {
        obs.disconnect();
        clearTimeout(timeout);
        resolve(el);
      }
    });

    // 3. Temporizador de seguridad (Timeout)
    const timeout = setTimeout(() => {
      observer.disconnect();
      // Un último intento antes de rendirse
      resolve(document.querySelector(selector));
    }, timeoutMs);

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  });
}

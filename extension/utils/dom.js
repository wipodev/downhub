function debounce(fn, ms = 100) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
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

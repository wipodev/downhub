let lastUrl = location.href;

const handleRouteChange = debounce(() => {
  if (lastUrl !== location.href) {
    lastUrl = location.href;

    // On route change, stop any active polls (new page)
    for (const [taskId, intId] of activePolls.entries()) {
      clearInterval(intId);
      activePolls.delete(taskId);
    }

    injectForActiveSites();
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
window.addEventListener("beforeunload", () => {
  for (const [, intId] of activePolls) clearInterval(intId);
  activePolls.clear();
});

const mo = new MutationObserver(
  debounce(() => {
    injectForActiveSites();
  }, 150)
);
mo.observe(document.documentElement, { childList: true, subtree: true });

// Initial run
injectForActiveSites();

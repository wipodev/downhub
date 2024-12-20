let lastUrl = "";

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url && tab.url.includes("youtube.com/watch")) {
    if (tab.url !== lastUrl) {
      lastUrl = tab.url;
      chrome.tabs.sendMessage(tabId, { action: "injectButton" });
    }
  }
});

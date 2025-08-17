const API_MESSAGE = "DOWNLOAD_URL";
const STATUS_MESSAGE = "STATUS_TASK";

function sendToBackend(url) {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage({ type: API_MESSAGE, url }, (res) => {
      const err = chrome.runtime.lastError;
      if (err) {
        resolve({ ok: false, error: err.message });
        return;
      }
      resolve(res);
    });
  });
}

function getTaskStatus(taskId) {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage({ type: STATUS_MESSAGE, taskId }, (res) => {
      const err = chrome.runtime.lastError;
      if (err) {
        resolve({ ok: false, error: err.message });
        return;
      }
      resolve(res);
    });
  });
}

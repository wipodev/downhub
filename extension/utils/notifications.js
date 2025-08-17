// --- Notification container setup ---
let notificationContainer = document.getElementById("dl-notification-container");
if (!notificationContainer) {
  notificationContainer = document.createElement("div");
  notificationContainer.id = "dl-notification-container";
  document.body.appendChild(notificationContainer);
}

function showNotification(message, type, duration = 2000) {
  const notification = document.createElement("div");
  notification.className = `dl-toast ${type}`;
  notification.textContent = message;
  notificationContainer.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = "toastSlideOut 0.3s ease forwards";
    setTimeout(() => notification.remove(), 300);
  }, duration);
}

/** Sticky toast (no se cierra solo). Devuelve handlers para update/close. */
function showSticky(message, type = "info") {
  const el = document.createElement("div");
  el.className = `dl-toast ${type}`;
  el.textContent = message;
  notificationContainer.appendChild(el);

  return {
    update(newMessage, newType) {
      if (typeof newMessage === "string") el.textContent = newMessage;
      if (newType) {
        el.classList.remove("info", "success", "error");
        el.classList.add(newType);
      }
    },
    close() {
      el.style.animation = "toastSlideOut 0.3s ease forwards";
      setTimeout(() => el.remove(), 300);
    },
  };
}

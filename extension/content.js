chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "injectButton") {
    injectDownloadButton();
  }
});

function injectDownloadButton() {
  if (!document.getElementById("yt-download-button")) {
    const button = document.createElement("button");
    button.id = "yt-download-button";
    button.classList.add("ytp-button");
    button.innerHTML = `<svg width="100%" height="100%" version="1.1" viewBox="0 0 36 36">
 <path d="m27.849 13.036c-0.2371-0.89196-0.93336-1.592-1.8178-1.8291-1.6033-0.43281-8.0315-0.43281-8.0315-0.43281s-6.4281 0-8.0315 0.43281c-0.88445 0.2371-1.5807 0.93712-1.8178 1.8291-0.42906 1.6146-0.42906 4.9792-0.42906 4.9792s0 3.3646 0.42906 4.9792c0.2371 0.89196 0.93336 1.5619 1.8178 1.799 1.6033 0.43281 8.0315 0.43281 8.0315 0.43281s6.4281 0 8.0315-0.43281c0.88445-0.2371 1.5807-0.91078 1.8178-1.799 0.42906-1.6146 0.42906-4.9792 0.42906-4.9792s0-3.3646-0.42906-4.9792z" fill="#ff0033" stroke="#fff" stroke-width="2.7"/>
 <path d="m16.59 13.123v4.9008h-2.6748l4.0846 4.8525 4.0846-4.8525h-2.6748v-4.9008z" fill="#fff" stroke="#fff" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.4"/>
</svg>`;

    const notificationContainer = document.createElement("div");
    notificationContainer.id = "yt-notification-container";

    button.addEventListener("click", async () => {
      button.disabled = true;
      showNotification("Downloading video...", "info");

      const videoUrl = window.location.href;

      try {
        const response = await fetch("http://127.0.0.1:8000/download", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ url: videoUrl }),
        });

        if (response.ok) {
          const data = await response.json();
          showNotification(data.message || "¡Video downloaded successfully!", "success");
        } else {
          const errorData = await response.json();
          throw new Error(errorData.detail || "Unknown error downloading video.");
        }
      } catch (error) {
        console.error("Error downloading video:", error);
        showNotification(error.message || "There was an unexpected error.", "error", 10000);
      } finally {
        button.disabled = false;
      }
    });

    function showNotification(message, type, duration = 1000) {
      const notification = document.createElement("div");
      notification.className = `yt-notification ${type}`;
      notification.innerText = message;

      notificationContainer.appendChild(notification);

      setTimeout(() => {
        notification.classList.add("hidden");
        setTimeout(() => {
          notificationContainer.removeChild(notification);
        }, 500);
      }, duration);
    }

    document
      .querySelector(".ytp-right-controls")
      .insertBefore(button, document.querySelector(".ytp-right-controls").firstChild);
    document.body.appendChild(notificationContainer);
  }
}

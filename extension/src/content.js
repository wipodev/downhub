if (!document.getElementById("yt-download-button")) {
  const button = document.createElement("button");
  button.id = "yt-download-button";
  button.innerText = "Download Video";

  const notificationContainer = document.createElement("div");
  notificationContainer.id = "yt-notification-container";

  button.addEventListener("click", async () => {
    button.disabled = true;
    button.innerText = "Downloading...";
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
      button.innerText = "Download Video";
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

  document.body.appendChild(button);
  document.body.appendChild(notificationContainer);
}

if (!document.getElementById("yt-download-button")) {
  const button = document.createElement("button");
  button.id = "yt-download-button";
  button.innerText = "Descargar Video";

  button.addEventListener("click", () => {
    const videoUrl = window.location.href;
    fetch("http://127.0.0.1:8000/download", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url: videoUrl }),
    })
      .then((response) => response.json())
      .then((data) => {
        alert(data.message || "¡Video sent to backend for download!");
      })
      .catch((error) => {
        console.error("Error sending video:", error);
        alert("There was an error sending the video for download.");
      });
  });

  document.body.appendChild(button);
}

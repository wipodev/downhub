// Cada sitio declara sus reglas aquí
const sites = [
  {
    name: "YouTube",
    match: () => location.hostname.includes("youtube.com") && /\/watch/.test(location.pathname),
    selector: "#movie_player > div.ytp-chrome-bottom > div.ytp-chrome-controls > div.ytp-right-controls",
    id: "dl-icon-btn-yt",
    title: "Download",
  },
  {
    name: "Kick",
    match: () => location.hostname.includes("kick.com") && /^\/[^/]+\/videos?\//.test(location.pathname),
    selector: "#injected-embedded-channel-player-video > div > div > div:nth-child(2)",
    id: "dl-icon-btn-kick",
    title: "Download VOD",
  },
];

// Función para iterar y disparar inyecciones
function injectForActiveSites() {
  for (const site of sites) {
    if (site.match()) {
      injectButton(site);
    }
  }
}

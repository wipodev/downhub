/**
 * content/siteRegistry.js
 * Diccionario de configuración para cada sitio soportado.
 */

const sites = [
  {
    name: "YouTube",
    match: () => location.hostname.includes("youtube.com") && /\/watch/.test(location.pathname),
    selector: ".ytp-right-controls",
    id: "dl-btn-yt",
    title: "Descargar con DownHub",
    styleClass: "yt-btn-style",
  },
  {
    name: "Kick",
    match: () => location.hostname.includes("kick.com"),
    selector: "div:has(> [data-testid='video-player-fullscreen'])",
    id: "dl-btn-kick",
    title: "Descargar con DownHub",
    styleClass: "kick-btn-style [&_svg]:size-[1em]",
  },
  {
    name: "Twitch",
    match: () =>
      location.hostname.includes("twitch.tv") &&
      (location.pathname.includes("/videos/") || location.pathname.includes("/clip/")),
    selector: ".player-controls__right-control-group",
    id: "dl-btn-twitch",
    title: "Descargar con DownHub",
    styleClass: "twitch-btn-style",
  },
];

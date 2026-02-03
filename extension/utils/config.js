// utils/config.js
// Este archivo es el único lugar donde se definen los nombres de los eventos.

PROTOCOL = {
  HOST_NAME: "net.wipodev.downhub", // Tu ID de registro oficial

  ACTIONS: {
    START_DOWNLOAD: "START_NATIVE_DOWNLOAD",
    CANCEL_DOWNLOAD: "CANCEL_NATIVE_DOWNLOAD",
    GET_STATUS: "GET_STATUS",
  },

  MESSAGES: {
    PROGRESS: "NATIVE_PROGRESS",
    DONE: "NATIVE_DONE",
    ERROR: "NATIVE_ERROR",
  },

  PYTHON_TYPES: {
    DOWNLOAD: "download_task",
    CANCEL: "cancel_task",
  },
};

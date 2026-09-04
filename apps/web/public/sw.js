// Service worker stub to satisfy browser PWA/service-worker registration requests
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", () => self.clients.claim());

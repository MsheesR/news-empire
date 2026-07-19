// LOPINUZE Service Worker - REMOVED third-party ad injection SW
// This file intentionally left minimal to avoid ad interference
// The previous SW from 3nbf4.com was intercepting all requests and potentially blocking ads
self.addEventListener('install', function(e) {
  self.skipWaiting();
});
self.addEventListener('activate', function(e) {
  e.waitUntil(clients.claim());
});
self.addEventListener('fetch', function(e) {
  // Pass through all requests without modification
  e.respondWith(fetch(e.request));
});
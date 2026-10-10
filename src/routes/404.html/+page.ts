// Emit a standalone build/404.html document, without a client-side SPA fallback.
// The static host must return this document with HTTP 404 for unknown paths.
export const prerender = true;
export const trailingSlash = 'never';
export const csr = false;

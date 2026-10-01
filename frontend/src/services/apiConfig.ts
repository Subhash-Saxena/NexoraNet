/**
 * Centralized API Configuration for NexoraNet Frontend.
 *
 * Resolves the backend API base URL from Vite environment variables:
 * - VITE_API_URL or VITE_API_BASE_URL (e.g., "https://nexoranet-api.onrender.com")
 * - If unset, defaults to empty string '' (enabling relative requests to Vite proxy, Nginx proxy, or Cloudflare Pages _redirects).
 */
export const getApiBaseUrl = (): string => {
  const envUrl =
    (import.meta.env.VITE_API_URL as string | undefined) ||
    (import.meta.env.VITE_API_BASE_URL as string | undefined) ||
    ''
  return envUrl ? envUrl.replace(/\/+$/, '') : ''
}

// Thin wrapper around fetch. In development Vite proxies /api to the backend;
// in production CloudFront routes /api to the load balancer.
export async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`/api${path}`)
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`)
  }
  return (await response.json()) as T
}

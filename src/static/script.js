let isRefreshing = false;
let refreshPromise = null;

function sanitizeRedirect(url) {
  if (!url || !url.startsWith("/") || url.startsWith("//")) return "/";
  return url;
}
async function fetchAuth(url, options = {}) {
  let res = await fetch(url, { ...options, credentials: "include" });

  if (res.status === 401) {
    if (window.location.pathname === "/") return res;
    if (!isRefreshing) {
      isRefreshing = true;
      refreshPromise = fetch("/refresh", {
        method: "POST",
        credentials: "include",
      })
        .then((r) => {
          if (!r.ok) throw new Error("REFRESH_FAILED");
          return r;
        })
        .finally(() => {
          isRefreshing = false;
          refreshPromise = null;
        });
    }

    try {
      await refreshPromise;
    } catch (err) {
      const next = encodeURIComponent(window.location.href);
      window.location.href = `/?next=${next}`;
      return res;
    }
    res = await fetch(url, { ...options, credentials: "include" });
  }
  return res;
}

async function initAuth() {
  try {
    const res = await fetch("/user/restore", {
      method: "POST",
      credentials: "include",
    });
    if (res.ok) return await res.json();
  } catch {}
}
function handlePostLoginRedirect() {
  const params = new URLSearchParams(window.location.search);
  const next = sanitizeRedirect(params.get("next"));
  if (next && next !== "/") {
    window.history.replaceState({}, "", window.location.pathname);
    window.location.href = next;
  }
}
async function loadProfile() {
  const res = await fetch("/user/me", {
    method: "POST",
    credentials: "include",
  });
  if (res.ok) return await res.json();
}
initAuth();

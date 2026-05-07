let isRefreshing = false;
let refreshPromise = null;

async function fetchAuth(url, options = {}) {
  let res = await fetch(url, { ...options, credentials: "include" });
  if (res.status === 401) {
    if (!isRefreshing) {
      isRefreshing = true;
      refreshPromise = fetch("/user/refresh", {
        method: "POST",
        credentials: "include",
      }).finally(() => {
        isRefreshing = false;
        refreshPromise = null;
      });
    }

    await refreshPromise;
    res = await fetch(url, { ...options, credentials: "include" });
  }
  return res;
}
async function checkSession() {
  try {
    const res = await fetchAuth("/user/me");
    if (!res.ok) {
      showLogin();
      return;
    }
  } catch {}
}

checkSession();

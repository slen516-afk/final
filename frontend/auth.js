// 0. 封裝Auth資料
function setAuthSession(authData) {
  // 儲存token
  localStorage.setItem("token", authData.accessToken);
  // 儲存token過期時間或用戶資訊
  localStorage.setItem("user_id", authData.userId || "");
}

// 1. 註冊
async function register(email, password, username) {
  const res = await fetch("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, username })
  })

  const data = await res.json();

  if (res.ok) {
    if (data.needsConfirmation) {
      alert("驗證信已寄送，請先至信箱點擊連結完成驗證。");
      window.location.href = "/login"; // 引導至登入頁
    }
    return data;
  } else {
    throw new Error(data.message || "註冊失敗");
  }
}


// 2. 登入
async function login(email, password) {
  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  if (!res.ok) throw new Error("Login failed");

  setAuthSession({
    accessToken: data.auth.accessToken,
    userId: data.user.id
  });

  return data;
}

//3. 發送包含token的請求
async function fetchWithAuth(url, options = {}) {
  const token = localStorage.getItem("token");

  const headers = {
    ...options.headers,
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"
  };

  const response = await fetch(url, { ...options, headers }).then(res => {
    // 如Token 無效，清除資料並引導至登入頁
    if (res.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user_id");
      window.location.href = "/login";
      return;
    }
    return res.json();
  });
};


// 4.調用需要登入權限的服務
async function getProtectedData() {
  return fetchWithAuth("/api/auth/profile");
}
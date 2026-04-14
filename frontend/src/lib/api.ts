import axios from "axios";

export const api = axios.create({ baseURL: "/", withCredentials: true });

api.interceptors.request.use((c) => {
  const t = localStorage.getItem("access_token");
  if (t) c.headers.Authorization = `Bearer ${t}`;
  return c;
});

api.interceptors.response.use(
  (r) => r,
  async (err) => {
    if (err.response?.status === 401) {
      const rt = localStorage.getItem("refresh_token");
      if (rt) {
        try {
          const r = await axios.post("/auth/refresh", {}, { headers: { Authorization: `Bearer ${rt}` } });
          localStorage.setItem("access_token", r.data.access_token);
          err.config.headers.Authorization = `Bearer ${r.data.access_token}`;
          return axios(err.config);
        } catch {}
      }
    }
    return Promise.reject(err);
  }
);


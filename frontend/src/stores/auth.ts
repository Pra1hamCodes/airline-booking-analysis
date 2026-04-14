import { create } from "zustand";
import { api } from "@/lib/api";

interface User { id: string; email: string; first_name?: string; last_name?: string; }
interface AuthState {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  fetchMe: () => Promise<void>;
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  loading: false,
  async login(email, password) {
    set({ loading: true });
    const r = await api.post("/auth/login", { email, password });
    localStorage.setItem("access_token", r.data.access_token);
    localStorage.setItem("refresh_token", r.data.refresh_token);
    set({ user: r.data.user, loading: false });
  },
  async register(data) {
    set({ loading: true });
    const r = await api.post("/auth/register", data);
    localStorage.setItem("access_token", r.data.access_token);
    localStorage.setItem("refresh_token", r.data.refresh_token);
    set({ user: r.data.user, loading: false });
  },
  logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({ user: null });
  },
  async fetchMe() {
    try {
      const r = await api.get("/auth/me");
      set({ user: r.data });
    } catch { set({ user: null }); }
  },
}));

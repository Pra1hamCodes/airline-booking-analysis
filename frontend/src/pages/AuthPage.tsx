import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useForm } from "react-hook-form";
import { motion } from "framer-motion";
import { useAuth } from "@/stores/auth";

export function AuthPage() {
  const [sp] = useSearchParams();
  const [mode, setMode] = useState<"login" | "register">(sp.get("mode") === "login" ? "login" : "register");
  const { login, register: registerUser } = useAuth();
  const nav = useNavigate();
  const { register, handleSubmit, formState: { errors } } = useForm();
  const [err, setErr] = useState("");

  const onSubmit = async (data: any) => {
    setErr("");
    try {
      if (mode === "login") await login(data.email, data.password);
      else {
        const name = [data.first_name, data.last_name].filter(Boolean).join(" ") || data.email.split("@")[0];
        await registerUser({ email: data.email, password: data.password, name });
      }
      nav("/app");
    } catch (e: any) {
      const msg = e.response?.data?.error || "Failed";
      const fields = e.response?.data?.messages;
      setErr(fields ? `${msg}: ${JSON.stringify(fields)}` : msg);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="card w-full max-w-md">
        <h2 className="font-display text-2xl mb-6">{mode === "login" ? "Welcome back" : "Create account"}</h2>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {mode === "register" && (
            <div className="grid grid-cols-2 gap-3">
              <input {...register("first_name")} placeholder="First name" className="input w-full" />
              <input {...register("last_name")} placeholder="Last name" className="input w-full" />
            </div>
          )}
          <input {...register("email", { required: true })} type="email" placeholder="Email" className="input w-full" />
          <input {...register("password", { required: true })} type="password" placeholder="Password" className="input w-full" />
          {err && <div className="text-danger text-sm">{err}</div>}
          <button type="submit" className="btn-primary w-full">{mode === "login" ? "Sign in" : "Register"}</button>
        </form>
        <button onClick={() => setMode(mode === "login" ? "register" : "login")} className="mt-4 text-sm text-primary">
          {mode === "login" ? "Need an account? Register" : "Have an account? Sign in"}
        </button>
      </motion.div>
    </div>
  );
}

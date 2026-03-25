"use client";

import { createClient } from "@/lib/supabase/client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

export function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.SyntheticEvent) => {
    e.preventDefault();
    const supabase = createClient();
    setIsLoading(true);
    setError(null);

    try {
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });
      if (error) throw error;
      // Update this route to redirect to an authenticated route. The user already has an active session.
      // router.push("/protected");
      router.push("/");
    } catch (error: unknown) {
      setError(error instanceof Error ? error.message : "出现错误");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full">
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <div className="mb-4">
          <h2 className="text-2xl font-bold mb-2">登录</h2>
          <p>请输入您的电子邮件，以登录您的账户</p>
        </div>
        <form onSubmit={handleLogin} className="mt-4">
          <div className="space-y-4">
            <div>
              <label className="block mb-2 font-medium">电子邮件</label>
              <input
                type="email"
                placeholder="m@example.com"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full p-3 border rounded-md"
              />
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="font-medium">密码</label>
                <Link
                  href="/auth/forgot-password"
                  className="text-sm hover:underline"
                >
                  忘记密码？
                </Link>
              </div>
              <input
                type="password"
                placeholder="Password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full p-3 border rounded-md"
              />
            </div>
            {error && (
              <div className="p-3 bg-red-50 text-red-600 rounded-md">
                {error}
              </div>
            )}
            <button
              type="submit"
              className="w-full p-3 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              disabled={isLoading}
            >
              {isLoading ? "登录中..." : "登录"}
            </button>
          </div>
          <div className="mt-4 text-center">
            <p>
              还没有账户？
              <Link
                href="/auth/sign-up"
                className="ml-1 text-blue-600 hover:underline"
              >
                注册
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}

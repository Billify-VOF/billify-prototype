"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { authService } from "./authService";
import { User } from "../definitions/auth";

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Define public routes that don't require authentication
const publicRoutes = ["/login", "/register", "/dashboard"];

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);
  const isRedirecting = React.useRef(false);

  const fetchUser = async () => {
    try {
      const userData = await authService.getCurrentUser();
      setUser(userData);
    } catch (err) {
      setUser(null);
    }
  };

  // Check authentication state and handle routing
  useEffect(() => {
    const checkAuth = async () => {
      try {
        if (authService.isAuthenticated()) {
          await fetchUser();

          // If user is authenticated and on a public route, redirect to dashboard
          if (publicRoutes.includes(pathname)) {
            if (!isRedirecting.current) {
              isRedirecting.current = true;
              router.push("/dashboard");
            }
          }
        } else {
          // If user is not authenticated and not on a public route, redirect to login
          if (!publicRoutes.includes(pathname)) {
            if (!isRedirecting.current) {
              isRedirecting.current = true;
              router.push("/login");
            }
          }
        }
      } catch (err) {
        setUser(null);
      }
    };

    checkAuth();
  }, [pathname, router]);

  const login = async (username: string, password: string) => {
    await authService.login({ username, password });
    await fetchUser();
    router.push("/dashboard");
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
    router.push("/login");
  };

  const value = {
    user,
    isAuthenticated: !!user,
    login,
    logout,
    fetchUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

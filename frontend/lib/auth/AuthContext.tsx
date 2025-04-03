import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { authService } from './authService';

interface User {
    username: string;
    // Add other user properties as needed
}

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;
    login: (username: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
    fetchUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Define public routes that don't require authentication
const publicRoutes = ['/login', '/register', '/forgot-password'];

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const router = useRouter();
    const pathname = usePathname();
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchUser = async () => {
        try {
            const userData = await authService.getCurrentUser();
            setUser(userData);
        } catch (err) {
            setUser(null);
            throw err;
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
                        router.push('/dashboard');
                    }
                } else {
                    // If user is not authenticated and not on a public route, redirect to login
                    if (!publicRoutes.includes(pathname)) {
                        router.push('/login');
                    }
                }
            } catch (err) {
                setError('Failed to check authentication status');
            } finally {
                setIsLoading(false);
            }
        };

        checkAuth();
    }, [pathname, router]);

    const login = async (username: string, password: string) => {
        try {
            setIsLoading(true);
            setError(null);
            await authService.login({ username, password });
            await fetchUser();
            router.push('/dashboard');
        } catch (err) {
            setError('Login failed. Please check your credentials.');
            throw err;
        } finally {
            setIsLoading(false);
        }
    };

    const logout = async () => {
        try {
            setIsLoading(true);
            setError(null);
            await authService.logout();
            setUser(null);
        } catch (err) {
            setError('Logout failed. Please try again.');
            throw err;
        } finally {
            setIsLoading(false);
        }
    };

    const value = {
        user,
        isAuthenticated: !!user,
        isLoading,
        error,
        login,
        logout,
        fetchUser,
    };

    // Show loading state while checking authentication
    if (isLoading) {
        return <div>Loading...</div>; // You might want to replace this with a proper loading component
    }

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}; 
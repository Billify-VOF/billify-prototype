import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService, AuthResponse } from './authService';
import { useAuth } from './useAuth';

interface AuthContextType {
    user: AuthResponse['user'] | null;
    isAuthenticated: boolean;
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, password: string, name: string) => Promise<void>;
    logout: () => Promise<void>;
    isLoading: boolean;
    error: Error | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const router = useRouter();
    const [user, setUser] = useState<AuthResponse['user'] | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const {
        isAuthenticated,
        login: loginMutation,
        loginLoading,
        loginError,
        register: registerMutation,
        registerLoading,
        registerError,
        logout: logoutMutation,
        logoutLoading,
        logoutError,
    } = useAuth();

    useEffect(() => {
        // Check if user is authenticated on mount
        const checkAuth = async () => {
            try {
                if (isAuthenticated) {
                    // You might want to add a method to get the current user
                    // const userData = await authService.getCurrentUser();
                    // setUser(userData);
                }
            } catch (err) {
                setError(err as Error);
            } finally {
                setIsLoading(false);
            }
        };

        checkAuth();
    }, [isAuthenticated]);

    const login = async (email: string, password: string) => {
        try {
            setError(null);
            const response = await loginMutation({ email, password });
            if (response) {
                setUser(response.user);
                router.push('/dashboard');
            }
        } catch (err) {
            setError(err as Error);
            throw err;
        }
    };

    const register = async (email: string, password: string, name: string) => {
        try {
            setError(null);
            const response = await registerMutation({ email, password, name });
            if (response) {
                setUser(response.user);
                router.push('/dashboard');
            }
        } catch (err) {
            setError(err as Error);
            throw err;
        }
    };

    const logout = async () => {
        try {
            setError(null);
            await logoutMutation();
            setUser(null);
            router.push('/login');
        } catch (err) {
            setError(err as Error);
            throw err;
        }
    };

    const value = {
        user,
        isAuthenticated,
        login,
        register,
        logout,
        isLoading: isLoading || loginLoading || registerLoading || logoutLoading,
        error: error || loginError || registerError || logoutError,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuthContext = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuthContext must be used within an AuthProvider');
    }
    return context;
}; 
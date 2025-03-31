import { useMutation, useQuery } from '@tanstack/react-query';
import { authService, LoginCredentials, RegisterData, AuthResponse } from './authService';

export const useAuth = () => {
    const isAuthenticated = authService.isAuthenticated();

    const loginMutation = useMutation<AuthResponse, Error, LoginCredentials>({
        mutationFn: (credentials) => authService.login(credentials),
    });

    const registerMutation = useMutation<AuthResponse, Error, RegisterData>({
        mutationFn: (data) => authService.register(data),
    });

    const logoutMutation = useMutation<void, Error, void>({
        mutationFn: () => authService.logout(),
    });

    return {
        isAuthenticated,
        login: loginMutation.mutate,
        loginLoading: loginMutation.isPending,
        loginError: loginMutation.error,
        register: registerMutation.mutate,
        registerLoading: registerMutation.isPending,
        registerError: registerMutation.error,
        logout: logoutMutation.mutate,
        logoutLoading: logoutMutation.isPending,
        logoutError: logoutMutation.error,
    };
}; 
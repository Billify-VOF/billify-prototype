import axios, { AxiosError, AxiosInstance, AxiosResponse } from 'axios';

// Types
export interface LoginCredentials {
    username: string;
    password: string;
}

export interface AuthResponse {
    token: string;
}

export interface AuthError {
    message: string;
    code?: string;
    status?: number;
}

// Create axios instance with default config
const createAxiosInstance = (): AxiosInstance => {
    const instance = axios.create({
        baseURL: `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/auth`,
        headers: {
            'Content-Type': 'application/json',
        },
    });

    // Request interceptor
    instance.interceptors.request.use(
        (config) => {
            const token = localStorage.getItem('token');
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        },
        (error) => {
            return Promise.reject(error);
        }
    );

    // Response interceptor
    instance.interceptors.response.use(
        (response) => response,
        async (error: AxiosError) => {
            // Handle 401 errors (unauthorized)
            if (error.response?.status === 401) {
                // Clear auth data and redirect to login
                localStorage.removeItem('token');
                window.location.href = '/login';
            }

            return Promise.reject(error);
        }
    );

    return instance;
};

class AuthService {
    private api: AxiosInstance;

    constructor() {
        this.api = createAxiosInstance();
    }

    async login(credentials: LoginCredentials): Promise<AuthResponse> {
        try {
            const response: AxiosResponse<AuthResponse> = await this.api.post('/login', credentials);
            const { token } = response.data;
            
            // Store token
            localStorage.setItem('token', token);
            
            return response.data;
        } catch (error) {
            this.handleAuthError(error);
            throw error;
        }
    }

    async logout(): Promise<void> {
        try {
            await this.api.post('/logout');
        } catch (error) {
            // Even if the logout request fails, clear local storage
            this.clearAuthData();
            this.handleAuthError(error);
            throw error;
        } finally {
            this.clearAuthData();
        }
    }

    private clearAuthData(): void {
        localStorage.removeItem('token');
    }

    private handleAuthError(error: unknown): never {
        if (axios.isAxiosError(error)) {
            const axiosError = error as AxiosError<{ message: string; code?: string }>;
            const errorMessage = axiosError.response?.data?.message || 'Authentication failed';
            const errorCode = axiosError.response?.data?.code;
            const status = axiosError.response?.status;

            throw {
                message: errorMessage,
                code: errorCode,
                status,
            } as AuthError;
        }

        throw {
            message: 'An unexpected error occurred during authentication',
        } as AuthError;
    }

    isAuthenticated(): boolean {
        return !!localStorage.getItem('token');
    }
}

// Export singleton instance
export const authService = new AuthService(); 
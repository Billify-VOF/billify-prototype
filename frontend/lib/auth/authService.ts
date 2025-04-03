import { apiService } from "../api/apiService";
import { AxiosError } from "axios";
import {
  LoginCredentials,
  RegisterCredentials,
  AuthResponse,
  User,
} from "../definitions/auth";

const LOGIN_PATH = "/login";

class AuthService {
  private setToken(token: string): void {
    localStorage.setItem("token", token);
  }

  private removeToken(): void {
    localStorage.removeItem("token");
  }

  constructor() {
    // Set up API interceptor to handle 401 errors
    apiService.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.handleAuthError();
        }
        return Promise.reject(error);
      }
    );
  }

  async register(credentials: RegisterCredentials): Promise<AuthResponse> {
    try {
      const response = await apiService.post<AuthResponse>(
        "/auth/register/",
        credentials
      );
      this.setToken(response.token);
      return response;
    } catch (error) {
      apiService.handleApiError(error, "Registration failed");
      throw error;
    }
  }

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await apiService.post<AuthResponse>(
        "/auth/login/",
        credentials
      );
      this.setToken(response.token);
      return response;
    } catch (error) {
      apiService.handleApiError(error, "Login failed");
      throw error;
    }
  }

  async logout(): Promise<void> {
    try {
      await apiService.post("/auth/logout/");
    } finally {
      this.removeToken();
      // Let the component handle the redirect
      this.handleAuthError();
    }
  }

  async getCurrentUser(): Promise<User> {
    try {
      return await apiService.get<User>("/me");
    } catch (error) {
      if (error instanceof AxiosError && error.response?.status === 401) {
        this.handleAuthError();
      }
      apiService.handleApiError(error, "Failed to fetch user data");
      throw error;
    }
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem("token");
  }

  private handleAuthError(): void {
    this.removeToken();
    // Only redirect if we're not already on the login page
    if (
      typeof window !== "undefined" &&
      !window.location.pathname.includes(LOGIN_PATH)
    ) {
      window.location.href = LOGIN_PATH;
    }
  }
}

export const authService = new AuthService();

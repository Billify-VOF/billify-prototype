import { apiService } from "../api/apiService";
import { AxiosError } from "axios";

interface LoginCredentials {
  username: string;
  password: string;
}

interface AuthResponse {
  token: string;
}

interface User {
  username: string;
  // Add other user properties as needed
}

class AuthService {
  private setToken(token: string): void {
    localStorage.setItem("token", token);
  }

  private removeToken(): void {
    localStorage.removeItem("token");
  }

  private redirectToLogin(): void {
    window.location.href = "/login";
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

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await apiService.post<AuthResponse>(
        "/auth/login",
        credentials
      );
      this.setToken(response.token);
      return response;
    } catch (error) {
      throw new Error("Login failed");
    }
  }

  async logout(): Promise<void> {
    try {
      await apiService.post("/auth/logout");
    } finally {
      this.removeToken();
      this.redirectToLogin();
    }
  }

  async getCurrentUser(): Promise<User> {
    try {
      return await apiService.get<User>("/me");
    } catch (error) {
      if (error instanceof AxiosError && error.response?.status === 401) {
        this.handleAuthError();
      }
      throw new Error("Failed to fetch user data");
    }
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem("token");
  }

  private handleAuthError(): void {
    this.removeToken();
    this.redirectToLogin();
  }
}

export const authService = new AuthService();

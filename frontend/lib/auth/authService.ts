import { apiService } from "../api/apiService";

interface LoginCredentials {
  username: string;
  password: string;
}

interface AuthResponse {
  token: string;
}

class AuthService {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await apiService.post<AuthResponse>(
        "/auth/login",
        credentials
      );
      localStorage.setItem("token", response.token);
      return response;
    } catch (error) {
      throw new Error("Login failed");
    }
  }

  async logout(): Promise<void> {
    try {
      await apiService.post("/auth/logout");
    } finally {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem("token");
  }
}

export const authService = new AuthService();

import axios, { AxiosError, AxiosInstance } from "axios";

class ApiService {
  public api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${process.env.NEXT_PUBLIC_BACKEND_URL}/api`,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Add token to requests if it exists
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem("token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  handleApiError(error: unknown, defaultMessage: string): never {
    if (error instanceof AxiosError) {
      const errorMessage = (error.response?.data as { error: string })?.error;
      if (errorMessage) {
        throw new Error(errorMessage);
      }
    }
    throw new Error(defaultMessage);
  }

  // Generic methods for API calls
  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.api.get<T>(url, { params });
    return response.data;
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.api.post<T>(url, data);
    return response.data;
  }

  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.api.put<T>(url, data);
    return response.data;
  }

  async delete<T>(url: string): Promise<T> {
    const response = await this.api.delete<T>(url);
    return response.data;
  }
}

export const apiService = new ApiService();

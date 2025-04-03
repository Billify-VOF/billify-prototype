export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterCredentials extends LoginCredentials {
  email: string;
  companyName: string;
}

export interface AuthResponse {
  token: string;
}

export interface User {
  username: string;
  email?: string;
  id: string;
  firstName?: string;
  lastName?: string;
}

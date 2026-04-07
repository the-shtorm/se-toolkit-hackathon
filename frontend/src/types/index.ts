export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string | null;
  updated_at: string | null;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface UserResponse extends User {}

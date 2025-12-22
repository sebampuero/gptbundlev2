export interface UserResponse {
    id: string;
    email: string;
    username: string;
    is_active: boolean;
}

export interface UserLogin {
    username: string;
    password: string;
}

export interface UserRegister {
    username: string;
    email: string;
    password: string;
}

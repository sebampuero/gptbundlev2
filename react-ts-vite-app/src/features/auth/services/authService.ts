import type { UserLogin, UserRegister, UserResponse } from '../types';

const BASE_URL = 'http://localhost:8000/api/v1/user';

export const authService = {
    async login(credentials: UserLogin): Promise<UserResponse> {
        const response = await fetch(`${BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(credentials),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Login failed');
        }

        return response.json();
    },

    async register(userData: UserRegister): Promise<UserResponse> {
        const response = await fetch(`${BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Registration failed');
        }

        return response.json();
    },
};

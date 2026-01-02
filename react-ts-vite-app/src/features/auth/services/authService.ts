import { apiClient } from '../../../api/client';
import type { UserLogin, UserRegister, UserResponse } from '../types';

export const authService = {
    async login(credentials: UserLogin): Promise<UserResponse> {
        const response = await apiClient.post<UserResponse>('/user/login', credentials);
        return response.data;
    },

    async register(userData: UserRegister): Promise<UserResponse> {
        const response = await apiClient.post<UserResponse>('/user/register', userData);
        return response.data;
    },
};

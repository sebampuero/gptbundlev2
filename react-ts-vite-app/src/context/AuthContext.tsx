import React, { createContext, useContext, useState } from 'react';
import type { UserResponse } from '../features/auth/types';

interface AuthContextType {
    user: UserResponse | null;
    isAuthenticated: boolean;
    login: (user: UserResponse) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<UserResponse | null>(null);

    const login = (userData: UserResponse) => {
        setUser(userData);
    };

    const value = {
        user,
        isAuthenticated: !!user,
        login
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

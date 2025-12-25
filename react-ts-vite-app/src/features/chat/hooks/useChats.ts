import { useState, useEffect } from "react";
import type { Chat } from "../types";

const BASE_URL = "http://localhost:8000/api/v1/messaging";

export const useChats = (userEmail: string) => {
    const [chats, setChats] = useState<Chat[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchChats = async () => {
            if (!userEmail) return;

            setIsLoading(true);
            setError(null);
            try {
                const response = await fetch(`${BASE_URL}/chats/${userEmail}`);
                if (!response.ok) {
                    if (response.status === 404) {
                        setChats([]);
                        return;
                    }
                    throw new Error("Failed to fetch chats");
                }
                const data = await response.json();
                setChats(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : "An unknown error occurred");
            } finally {
                setIsLoading(false);
            }
        };

        fetchChats();
    }, [userEmail]);

    return { chats, isLoading, error };
};

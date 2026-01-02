import { useState, useEffect, useCallback } from "react";
import type { Chat } from "../types";

const BASE_URL = "http://localhost:8000/api/v1/messaging";

export const useChats = () => {
    const [chats, setChats] = useState<Chat[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchChats = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch(`${BASE_URL}/chats`, {
                credentials: 'include',
            });
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
    }, []);

    useEffect(() => {
        fetchChats();
    }, [fetchChats]);

    const deleteChat = async (chatId: string, timestamp: number) => {
        setIsDeleting(true);
        setError(null);
        try {
            const response = await fetch(`${BASE_URL}/chat/${chatId}/${timestamp}`, {
                method: "DELETE",
                credentials: 'include',
            });

            if (!response.ok) {
                throw new Error("Failed to delete chat");
            }

            setChats((prevChats) => prevChats.filter((chat) => chat.chat_id !== chatId));
        } catch (err) {
            setError(err instanceof Error ? err.message : "An unknown error occurred");
        } finally {
            setIsDeleting(false);
        }
    };

    return { chats, isLoading, isDeleting, error, deleteChat, refreshChats: fetchChats };
};

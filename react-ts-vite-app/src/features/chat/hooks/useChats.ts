import { useState, useEffect, useCallback } from "react";
import type { Chat } from "../types";
import { apiClient } from "../../../api/client";
import { AxiosError } from "axios";

export const useChats = () => {
    const [chats, setChats] = useState<Chat[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchChats = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await apiClient.get<Chat[]>('/messaging/chats');
            setChats(response.data);
        } catch (err) {
            if (err instanceof AxiosError && err.response?.status === 404) {
                setChats([]);
            } else {
                setError(err instanceof Error ? err.message : "An unknown error occurred");
            }
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
            await apiClient.delete(`/messaging/chat/${chatId}/${timestamp}`);

            setChats((prevChats) => prevChats.filter((chat) => chat.chat_id !== chatId));
        } catch (err) {
            setError(err instanceof Error ? err.message : "An unknown error occurred");
        } finally {
            setIsDeleting(false);
        }
    };

    return { chats, isLoading, isDeleting, error, deleteChat, refreshChats: fetchChats };
};

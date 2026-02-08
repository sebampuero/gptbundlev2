import { useState, useEffect, useCallback, useRef } from "react";
import type { Chat, ChatPaginatedResponse } from "../types";
import { apiClient } from "../../../api/client";
import { AxiosError } from "axios";

export const useChats = () => {
    const [chats, setChats] = useState<Chat[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [noMoreChatsToLoad, setNoMoreChatsToLoad] = useState(false);
    const [moreChatsClicked, setMoreChatsClicked] = useState(false);
    const lastEvalKey = useRef<string | null>(null);
    const paginationLimit = 15;

    const fetchChats = useCallback(async (newChatRefresh: boolean = false) => {
        setIsLoading(true);
        setError(null);
        try {
            console.log("New chat refresh was: ", newChatRefresh);
            setMoreChatsClicked(true);
            if (newChatRefresh) {
                lastEvalKey.current = null;
                setChats([]);
                setMoreChatsClicked(false);
            }

            const response = await apiClient.get<ChatPaginatedResponse>('/messaging/chats', {
                params: {
                    limit: paginationLimit,
                    ...(lastEvalKey.current && { last_eval_key: JSON.stringify(lastEvalKey.current) }),
                },
            });
            console.log("Fetched chats: ", response.data);
            setChats(prev => [...prev, ...response.data.items]);
            lastEvalKey.current = response.data.last_eval_key;
            setNoMoreChatsToLoad(response.data.last_eval_key === null);
        } catch (err) {
            if (err instanceof AxiosError && err.response?.status === 404) {
                setChats([]);
                setNoMoreChatsToLoad(true);
            } else {
                setError(err instanceof Error ? err.message : "An unknown error occurred");
            }
        } finally {
            setIsLoading(false);
        }
    }, []);

    const searchChats = useCallback(async (searchTerm: string) => {
        if (!searchTerm.trim()) {
            fetchChats(true);
            return;
        }
        try {
            setMoreChatsClicked(false);
            const response = await apiClient.get(`/messaging/search_chats?search_term=${searchTerm}`);
            setChats(response.data);
            setNoMoreChatsToLoad(true);
        } catch (err) {
            if (err instanceof AxiosError && err.response?.status !== 404) {
                setError(err instanceof Error ? err.message : "An unknown error occurred");
            } else {
                setChats([]);
                setNoMoreChatsToLoad(true);
            }
        }
    }, [fetchChats]);

    useEffect(() => {
        fetchChats(true);
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

    return {
        chats,
        isLoading,
        isDeleting,
        error,
        deleteChat,
        refreshChats: fetchChats,
        noMoreChatsToLoad,
        searchChats,
        moreChatsClicked,
    };
};

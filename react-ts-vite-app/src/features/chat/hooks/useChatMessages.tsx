import { useEffect, useRef, useState, useCallback } from "react";
import { apiClient } from "../../../api/client";

export type MessageRole = "user" | "assistant";

export interface Message {
    content: string;
    role: MessageRole;
    llm_model?: string;
    message_type?: string;
    is_loading_message?: boolean;
    media_s3_keys?: string[];
    presigned_urls?: string[];
}

export type WebSocketMessageType = "token" | "chat_created" | "stream_finished" | "error";

export interface WebSocketMessage {
    type: WebSocketMessageType;
    content?: string;
    chat_id?: string;
    chat_timestamp?: string;
}

export interface ChatMetadata {
    chatId?: string;
    timestamp?: string;
}

import { useNavigate } from "react-router-dom";

export const useChatMessages = (activeChatMetadata?: ChatMetadata) => {
    const navigate = useNavigate();
    const ws = useRef<WebSocket | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const [isProcessingMessage, setIsProcessingMessage] = useState(false);
    const reconnectTimeoutRef = useRef<number | null>(null);
    const isManuallyClosed = useRef(false);
    const chatIdRef = useRef<string | undefined>(activeChatMetadata?.chatId);
    const timestampRef = useRef<string | undefined>(activeChatMetadata?.timestamp);
    const currentMediaS3Keys = useRef<string[]>([]);

    const chatId = activeChatMetadata?.chatId || "new";
    const timestamp = activeChatMetadata?.timestamp || "0";

    const connect = useCallback(() => {
        if (isManuallyClosed.current) return;

        // Construct URL based on current active chat or "new"
        const SUBDIRECTORY = import.meta.env.VITE_SUBDIRECTORY || '';
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsHost = import.meta.env.DEV ? 'localhost:8000' : window.location.host;
        const url = `${wsProtocol}//${wsHost}${SUBDIRECTORY}/api/v1/messaging/chat/text_ws/${chatId}/${timestamp}`;

        const socket = new WebSocket(url);
        ws.current = socket;

        socket.onopen = () => {
            console.log("ws opened with chatId: " + chatId + " and timestamp: " + timestamp);
            setIsConnected(true);
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
                reconnectTimeoutRef.current = null;
            }
        };

        socket.onclose = (event) => {
            console.log("ws closed", event);
            setIsConnected(false);

            // Only attempt reconnect if not manually closed
            if (!isManuallyClosed.current) {
                console.log(`Attempting reconnect in 3000ms...`);

                reconnectTimeoutRef.current = window.setTimeout(() => {
                    connect();
                }, 3000);
            }
        };

        socket.onmessage = (event) => {
            const data: WebSocketMessage = JSON.parse(event.data);

            switch (data.type) {
                case "token":
                    // delete the last message that was added as loading symbol
                    setMessages((prev) => {
                        const lastMessage = prev[prev.length - 1];
                        if (lastMessage && lastMessage.role === "assistant" && lastMessage.is_loading_message) {
                            return prev.slice(0, -1);
                        }
                        return prev;
                    });

                    setMessages((prev) => {
                        const lastMessage = prev[prev.length - 1];
                        if (lastMessage && lastMessage.role === "assistant") {
                            return [
                                ...prev.slice(0, -1),
                                { ...lastMessage, content: lastMessage.content + (data.content || "") }
                            ];
                        }
                        return [...prev, { role: "assistant", content: data.content || "" }];
                    });
                    setIsProcessingMessage(true);
                    break;

                case "stream_finished":
                    setIsProcessingMessage(false);
                    break;

                case "chat_created":
                    chatIdRef.current = data.chat_id;
                    timestampRef.current = data.chat_timestamp;
                    break;

                case "error":
                    setMessages((prev) => {
                        const lastMessage = prev[prev.length - 1];
                        if (lastMessage && lastMessage.role === "assistant") {
                            return [
                                ...prev.slice(0, -1),
                                { ...lastMessage, content: "The model had an error generating a response, please try another model or try later." }
                            ];
                        }
                        return [...prev, { role: "assistant", content: "The model had an error generating a response, please try another model or try later." }];
                    });
                    setIsProcessingMessage(false);
                    break;
            }
        };
    }, [chatId, timestamp]);

    useEffect(() => {
        // ... inside component
        const fetchHistory = async () => {
            if (chatId === "new") {
                setMessages([]);
                return;
            }

            try {
                const response = await apiClient.get(`/messaging/chat/${chatId}/${timestamp}`);
                const data = response.data;
                if (data && data.messages) {
                    setMessages(data.messages);
                }
            } catch (error) {
                console.error("Error fetching chat history:", error);
                setMessages([]);
                window.location.href = '/chat';
            }
        };

        fetchHistory();

        isManuallyClosed.current = false;
        connect();

        return () => {
            isManuallyClosed.current = true;
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (ws.current) {
                console.log("closing ws for chatId: " + chatId);
                ws.current.close();
            }
        };

    }, [chatId, timestamp, connect]);

    const uploadImages = useCallback(async (files: File[]) => {
        const formData = new FormData();
        files.forEach((file) => {
            formData.append("files", file);
        });

        try {
            const response = await apiClient.post("/storage/upload_media", formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });
            const keys = response.data.keys;
            currentMediaS3Keys.current = [...currentMediaS3Keys.current, ...keys];
            return keys;
        } catch (error) {
            console.error("Error uploading images:", error);
            throw error;
        }
    }, []);

    const removeMediaKey = useCallback((key: string) => {
        currentMediaS3Keys.current = currentMediaS3Keys.current.filter(k => k !== key);
    }, []);

    const sendMessage = useCallback((content: string, userEmail: string, llm_model: string, presigned_urls?: string[]) => {
        if (!userEmail) {
            console.error("No user email provided");
            return;
        }
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            setIsProcessingMessage(true);
            const userMessage: Message = {
                role: "user",
                content,
                llm_model,
                message_type: "text",
                presigned_urls: presigned_urls, // Store optimistic URLs
                media_s3_keys: currentMediaS3Keys.current, // Store S3 keys if any
            };

            // Optimistically add user message to UI
            setMessages((prev) => [...prev, userMessage]);

            // Add a last message that works as loading symbol
            setMessages((prev) => [...prev, {
                role: "assistant",
                content: "",
                is_loading_message: true
            }]);

            const payload = {
                user_message: {
                    ...userMessage,
                    presigned_urls: undefined, // Don't send local blob URLs to backend
                },
                user_email: userEmail,
            };

            ws.current.send(JSON.stringify(payload));
        } else {
            console.error("WebSocket is not open");
        }
        currentMediaS3Keys.current = [];
    }, []);

    const startNewChat = useCallback(() => {
        setMessages([]);
        navigate("/chat");
    }, [navigate]);

    return {
        messages,
        isConnected,
        sendMessage,
        startNewChat,
        isProcessingMessage,
        uploadImages,
        removeMediaKey
    };
}

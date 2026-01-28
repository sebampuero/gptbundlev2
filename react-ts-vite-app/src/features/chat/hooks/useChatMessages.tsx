import { useEffect, useRef, useState, useCallback } from "react";
import { apiClient } from "../../../api/client";
import { useModel } from "../../../context/ModelContext";
import { useLLModels } from "../hooks/useLLModels";

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


export const useChatMessages = (chatMetadata: ChatMetadata) => {
    const ws = useRef<WebSocket | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const [isProcessingMessage, setIsProcessingMessage] = useState(false);
    const [isOutputVisionSelected, setIsOutputVisionSelectedState] = useState(false);
    const isOutputVisionSelectedRef = useRef(false);
    const chatIdRef = useRef<string | undefined>(undefined);
    const timestampRef = useRef<string | undefined>(undefined);
    const currentMediaS3Keys = useRef<string[]>([]);

    // Model context to handle capabilities changes
    const { selectedModel } = useModel();
    const { models } = useLLModels();


    // Reset output vision if the selected model doesn't support it
    useEffect(() => {
        const currentModel = models.find(m => m.model_name === selectedModel);
        if (currentModel && !currentModel.supports_output_vision && isOutputVisionSelected) {
            setIsOutputVisionSelectedState(false);
            isOutputVisionSelectedRef.current = false;
        }
    }, [selectedModel, models, isOutputVisionSelected]);

    const connect = useCallback(() => {
        // TODO: a good reconnect logic is still due here...
        // Construct URL based on current active chat or "new"
        const SUBDIRECTORY = import.meta.env.VITE_SUBDIRECTORY || '';
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsHost = import.meta.env.DEV ? 'localhost:8000' : window.location.host;
        const url = `${wsProtocol}//${wsHost}${SUBDIRECTORY}/api/v1/messaging/chat/text_ws`;

        const socket = new WebSocket(url);
        ws.current = socket;

        socket.onopen = () => {
            console.log("ws opened");
            setIsConnected(true);
        };

        socket.onclose = (event) => {
            console.log("ws closed", event);
            setIsConnected(false);
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
    }, []);

    const fetchHistory = useCallback(async (id: string, timestamp: string) => {
        // If we already have this chat loaded, maybe we don't need to refetch?
        // But for now, let's always fetch to be safe/simple
        setIsProcessingMessage(true); // Optional: show loading state
        try {
            const response = await apiClient.get(`/messaging/chat/${id}/${timestamp}`);
            const data = response.data;
            if (data && data.messages) {
                setMessages(data.messages);
            }
        } catch (error) {
            console.error("Error fetching chat history:", error);
            setMessages([]);
        } finally {
            setIsProcessingMessage(false);
        }
    }, []);

    // Effect to handle chat switching via props
    useEffect(() => {
        if (chatMetadata.chatId && chatMetadata.timestamp) {
            // Switch to existing chat
            chatIdRef.current = chatMetadata.chatId;
            timestampRef.current = chatMetadata.timestamp;
            fetchHistory(chatMetadata.chatId, chatMetadata.timestamp);
            // and also start a fresh ws connection
            ws.current?.close();
            connect();
        } else {
            // New chat mode
            chatIdRef.current = undefined;
            timestampRef.current = undefined;
            setMessages([]);
        }
    }, [chatMetadata, fetchHistory]);

    // Initial connection effect
    useEffect(() => {
        connect();

        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };
    }, [connect]);

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

    const setIsOutputVisionSelected = useCallback((selected: boolean) => {
        setIsOutputVisionSelectedState(selected);
        isOutputVisionSelectedRef.current = selected;
    }, []);

    const initializeChatMetadata = () => {
        if (!chatIdRef.current || !timestampRef.current) {
            chatIdRef.current = crypto.randomUUID();
            timestampRef.current = (Date.now() / 1000).toString();
        }
    };

    const promptImageGeneration = useCallback(async (userMessage: Message) => {
        try {
            initializeChatMetadata();
            const response = await apiClient.post("/messaging/image_generation", userMessage, {
                params: {
                    chat_id: chatIdRef.current,
                    chat_timestamp: timestampRef.current,
                },
            });
            // delete last loading assisntant message
            setMessages((prev) => {
                const lastMessage = prev[prev.length - 1];
                if (lastMessage && lastMessage.role === "assistant" && lastMessage.is_loading_message) {
                    return prev.slice(0, -1);
                }
                return prev;
            });
            const message = response.data;
            console.log("The assistant message with image is: ", message);
            setMessages((prev) => [...prev, { ...message, is_loading_message: false }]);
        } catch (error) {
            console.error("Error generating image:", error);
            setMessages((prev) => {
                const lastMessage = prev[prev.length - 1];
                if (lastMessage && lastMessage.role === "assistant" && lastMessage.is_loading_message) {
                    return prev.slice(0, -1);
                }
                return prev;
            });
            setMessages((prev) => [...prev, {
                role: "assistant",
                content: "The model had an error generating a response, please try another model or try later.",
                is_loading_message: false
            }]);
            throw error;
        }
    }, []);

    const sendMessage = useCallback((content: string, userEmail: string, llm_model: string, presigned_urls?: string[]) => {
        if (!userEmail) {
            console.error("No user email provided");
            return;
        }
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            setIsProcessingMessage(true);
            initializeChatMetadata();
            if (isOutputVisionSelectedRef.current) {
                const userMessage: Message = {
                    role: "user",
                    content,
                    llm_model,
                    message_type: "image"
                };
                setMessages((prev) => [...prev, userMessage]);
                setMessages((prev) => [...prev, {
                    role: "assistant",
                    content: "",
                    is_loading_message: true
                }]);
                promptImageGeneration(userMessage);
                return;
            }
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
                chat_id: chatIdRef.current,
                timestamp: timestampRef.current,
            };

            ws.current.send(JSON.stringify(payload));
        } else {
            console.error("WebSocket is not open");
        }
        currentMediaS3Keys.current = [];
    }, []);

    const startNewChat = useCallback(() => {
        setMessages([]);
        chatIdRef.current = undefined;
        timestampRef.current = undefined;
        ws.current?.close();
        connect();
    }, []);

    return {
        messages,
        isConnected,
        sendMessage,
        startNewChat,
        isProcessingMessage,
        uploadImages,
        removeMediaKey,
        isOutputVisionSelected,
        setIsOutputVisionSelected
    };
}

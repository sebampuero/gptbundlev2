import { useEffect, useRef, useState, useCallback } from "react";

export type MessageRole = "user" | "assistant";

export interface Message {
    content: string;
    role: MessageRole;
    llm_model?: string;
    message_type?: string;
}

export type WebSocketMessageType = "token" | "chat_created" | "stream_finished" | "error";

export interface WebSocketMessage {
    type: WebSocketMessageType;
    content?: string;
    chat_id?: string;
    chat_timestamp?: number;
}

export interface ChatMetadata {
    chatId?: string;
    timestamp?: string;
}

export const useChatMessages = (activeChatMetadata?: ChatMetadata) => {
    const ws = useRef<WebSocket | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [isConnected, setIsConnected] = useState(false);

    const chatId = activeChatMetadata?.chatId || "new";
    const timestamp = activeChatMetadata?.timestamp || "0";

    useEffect(() => {
        const fetchHistory = async () => {
            if (chatId === "new") {
                setMessages([]);
                return;
            }

            try {
                const response = await fetch(`http://localhost:8000/api/v1/messaging/chat/${chatId}/${timestamp}`);
                if (response.ok) {
                    const data = await response.json();
                    if (data && data.messages) {
                        setMessages(data.messages);
                    }
                } else {
                    console.error("Failed to fetch chat history:", response.statusText);
                    setMessages([]);
                }
            } catch (error) {
                console.error("Error fetching chat history:", error);
                setMessages([]);
            }
        };

        fetchHistory();

        // Construct URL based on current active chat or "new"
        const url = `ws://localhost:8000/api/v1/messaging/chat/text_ws/${chatId}/${timestamp}`;

        ws.current = new WebSocket(url);

        ws.current.onopen = () => {
            console.log("ws opened with chatId: " + chatId + " and timestamp: " + timestamp);
            setIsConnected(true);
        };

        ws.current.onclose = () => {
            console.log("ws closed");
            setIsConnected(false);
        };

        ws.current.onmessage = (event) => {
            const data: WebSocketMessage = JSON.parse(event.data);

            switch (data.type) {
                case "token":
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
                    break;

                case "stream_finished":
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
                    break;
            }
        };

        return () => {
            if (ws.current) {
                console.log("closing ws for chatId: " + chatId);
                ws.current.close();
            }
        };

    }, [chatId, timestamp]);

    const sendMessage = useCallback((content: string, userEmail: string, llm_model: string) => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            const userMessage: Message = {
                role: "user",
                content,
                llm_model,
                message_type: "text"
            };

            // Optimistically add user message to UI
            setMessages((prev) => [...prev, userMessage]);

            const payload = {
                messages: [userMessage],
                user_email: userEmail,
            };

            ws.current.send(JSON.stringify(payload));
        } else {
            console.error("WebSocket is not open");
        }
    }, []);

    const startNewChat = useCallback(() => {
        setMessages([]);

    }, []);

    return {
        messages,
        isConnected,
        sendMessage,
        startNewChat
    };
}

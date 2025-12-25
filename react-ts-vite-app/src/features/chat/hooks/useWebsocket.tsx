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

export const useWebsocket = (activeChatMetadata: { chatId: string; timestamp: number } | null) => {
    const ws = useRef<WebSocket | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        // Construct URL based on current active chat or "new"
        const chatId = activeChatMetadata?.chatId || "new";
        const timestamp = activeChatMetadata?.timestamp || 0;
        const url = `ws://localhost:8000/api/v1/messaging/chat/text_ws/${chatId}/${timestamp}`;

        ws.current = new WebSocket(url);

        ws.current.onopen = () => {
            console.log("ws opened");
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
                    console.log("Stream finished");
                    break;

                case "error":
                    console.error("WS Error:", data.content);
                    break;
            }
        };

    }, []);

    const sendMessage = useCallback((content: string, userEmail: string) => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            const userMessage: Message = {
                role: "user",
                content,
                llm_model: "openrouter/mistralai/devstral-2512:free",
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

    return {
        messages,
        isConnected,
        sendMessage,
    };
}

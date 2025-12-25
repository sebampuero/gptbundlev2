export type MessageRole = "user" | "assistant";

export interface Message {
    content: string;
    role: MessageRole;
    llm_model?: string;
    message_type?: string;
    media?: string | null;
}

export interface Chat {
    chat_id: string;
    timestamp: number;
    user_email: string;
    messages: Message[];
}

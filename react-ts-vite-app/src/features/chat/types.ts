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

export interface ChatPaginatedResponse {
    items: Chat[];
    last_eval_key: string | null;
}

export interface LLMModel {
    model_name: string;
    description: string;
    supports_input_vision: boolean;
    supports_output_vision: boolean;
}

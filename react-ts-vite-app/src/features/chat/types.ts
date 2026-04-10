export type MessageRole = "user" | "assistant";

export type ReasoningEffort = "low" | "medium" | "high" | "disabled";

export interface Message {
    content: string;
    role: MessageRole;
    llm_model?: string;
    message_type?: string;
    is_loading_message?: boolean;
    img_s3_keys?: string[] | null;
    pdf_s3_keys?: string[] | null;
    img_presigned_urls?: string[] | null;
    pdf_presigned_urls?: string[] | null;
    reasoning_effort?: string | null;
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
    supports_reasoning: boolean;
}

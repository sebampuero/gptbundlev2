import { useState, useEffect } from "react";
import type { LLMModel } from "../types";
import { apiClient } from "../../../api/client";

export const useLLModels = () => {
    const [models, setModels] = useState<LLMModel[]>([]);

    const fetchModels = async () => {
        try {
            const response = await apiClient.get('/llm/models');
            setModels(response.data);
        } catch (error) {
            console.error("Failed to fetch models", error);
        }
    };

    useEffect(() => {
        fetchModels();
    }, []);

    return { models };
}
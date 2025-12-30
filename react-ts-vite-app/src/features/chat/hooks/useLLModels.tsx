import { useState, useEffect } from "react";
import type { LLMModel } from "../types";

export const useLLModels = () => {
    const [models, setModels] = useState<LLMModel[]>([]);

    const fetchModels = async () => {
        const response = await fetch("http://localhost:8000/api/v1/llm/models");
        const data = await response.json();
        setModels(data);
    };

    useEffect(() => {
        fetchModels();
    }, []);

    return { models };
}
import React, { createContext, useContext, useState } from "react";

interface ModelContextType {
    selectedModel: string;
    setSelectedModel: (model: string) => void;
}

const DEFAULT_MODEL = "openrouter/mistralai/mistral-7b-instruct:free";
const STORAGE_KEY = "selected_llm_model";

const ModelContext = createContext<ModelContextType | undefined>(undefined);

export const ModelProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [selectedModel, setSelectedModelInternal] = useState<string>(() => {
        const saved = localStorage.getItem(STORAGE_KEY);
        return saved || DEFAULT_MODEL;
    });

    const setSelectedModel = (model: string) => {
        setSelectedModelInternal(model);
        localStorage.setItem(STORAGE_KEY, model);
    };

    return (
        <ModelContext.Provider value={{ selectedModel, setSelectedModel }}>
            {children}
        </ModelContext.Provider>
    );
};

export const useModel = () => {
    const context = useContext(ModelContext);
    if (context === undefined) {
        throw new Error("useModel must be used within a ModelProvider");
    }
    return context;
};

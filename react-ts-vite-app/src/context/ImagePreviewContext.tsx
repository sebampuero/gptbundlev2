import { createContext, useContext, useState, type ReactNode } from "react";
import { ImagePreviewModal } from "../features/chat/components/ChatInputArea/ImagePreviewModal";

interface ImagePreviewContextType {
    showImage: (url: string) => void;
    closeImage: () => void;
}

const ImagePreviewContext = createContext<ImagePreviewContextType | undefined>(undefined);

export const ImagePreviewProvider = ({ children }: { children: ReactNode }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [imageUrl, setImageUrl] = useState("");

    const showImage = (url: string) => {
        setImageUrl(url);
        setIsOpen(true);
    };

    const closeImage = () => {
        setIsOpen(false);
        setImageUrl("");
    };

    return (
        <ImagePreviewContext.Provider value={{ showImage, closeImage }}>
            {children}
            <ImagePreviewModal
                isOpen={isOpen}
                onClose={closeImage}
                imageUrl={imageUrl}
            />
        </ImagePreviewContext.Provider>
    );
};

export const useImagePreview = () => {
    const context = useContext(ImagePreviewContext);
    if (!context) {
        throw new Error("useImagePreview must be used within an ImagePreviewProvider");
    }
    return context;
};

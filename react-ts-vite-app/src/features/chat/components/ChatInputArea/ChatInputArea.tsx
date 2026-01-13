import {
    Box,
    Textarea,
    IconButton,
    HStack,
    useDisclosure,
    Image,
    Spinner,
    CloseButton,
} from "@chakra-ui/react";
import { useState, useCallback, useMemo } from "react";
import { LuPlus, LuSend, LuPanelLeftOpen, LuImage } from "react-icons/lu";
import { OptionsModal } from "./OptionsModal";
import { useImagePreview } from "../../../../context/ImagePreviewContext";
import { useNavigate } from "react-router-dom";
import { useLLModels } from "../../hooks/useLLModels";
import { useModel } from "../../../../context/ModelContext";
import { useRef } from "react";
import { toaster } from "../../../../components/ui/toaster";

interface ChatInputAreaProps {
    onShowSidebar: () => void;
    isSidebarOpen: boolean;
    onSendMessage: (content: string, presignedUrls?: string[]) => void;
    onStartNewChat: () => void;
    uploadImages: (files: File[]) => Promise<string[]>;
    removeMediaKey: (key: string) => void;
    isWebsocketConnected: boolean;
}

interface PastedImage {
    file: File;
    url: string;
    isLoading: boolean;
    key?: string;
}

export const ChatInputArea = ({
    onShowSidebar,
    isSidebarOpen,
    onSendMessage,
    onStartNewChat,
    uploadImages,
    removeMediaKey,
    isWebsocketConnected
}: ChatInputAreaProps) => {

    const { open, onOpen, onClose } = useDisclosure();
    const [inputValue, setInputValue] = useState("");
    const [pastedImages, setPastedImages] = useState<PastedImage[]>([]);
    const navigate = useNavigate();
    const { models } = useLLModels();
    const { selectedModel } = useModel();
    const fileInputRef = useRef<HTMLInputElement>(null);
    const { showImage } = useImagePreview();

    const currentModel = useMemo(() => {
        return models.find(m => m.model_name === selectedModel);
    }, [models, selectedModel]);

    const supportsVision = currentModel?.supports_input_vision ?? false;

    const handleSend = () => {
        // Prevent sending if images are present but model doesn't support vision
        if (!isWebsocketConnected) {
            toaster.create({
                title: "Not connected",
                description: "Please wait for the websocket to connect before sending a message.",
                type: "warning",
            });
            return;
        }
        if (pastedImages.length > 0 && !supportsVision && !isWebsocketConnected) {
            return;
        }

        if (inputValue.trim() || pastedImages.length > 0) {

            if (pastedImages.some(img => img.isLoading)) {
                return; // Prevent sending while uploading
            }

            const presignedUrls = pastedImages.map(img => img.url);
            onSendMessage(inputValue, presignedUrls);
            setInputValue("");
            setPastedImages([]);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const onStartNewChatBtnClicked = () => {
        onClose();
        navigate("/chat", { replace: true });
        onStartNewChat();
    };

    const handleFiles = useCallback(async (files: File[]) => {
        if (!supportsVision) return;

        const remainingSlots = 3 - pastedImages.length;
        const filesToUpload = Array.from(files).slice(0, remainingSlots);

        if (filesToUpload.length === 0) return;

        const newImages: PastedImage[] = filesToUpload.map(file => ({
            file,
            url: URL.createObjectURL(file),
            isLoading: true
        }));

        setPastedImages(prev => [...prev, ...newImages]);

        try {
            const keys = await uploadImages(filesToUpload);
            setPastedImages(prev => {
                let keyIndex = 0;
                return prev.map(img => {
                    if (filesToUpload.includes(img.file)) {
                        return { ...img, isLoading: false, key: keys[keyIndex++] };
                    }
                    return img;
                });
            });
        } catch (error) {
            console.error("Failed to upload images", error);
            setPastedImages(prev => prev.filter(img => !filesToUpload.includes(img.file)));
        }
    }, [pastedImages, uploadImages, supportsVision]);

    const handlePaste = useCallback(async (e: React.ClipboardEvent) => {
        if (!supportsVision) return;

        const items = e.clipboardData.items;
        const files: File[] = [];

        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf("image") !== -1) {
                const file = items[i].getAsFile();
                if (file) files.push(file);
            }
        }

        if (files.length > 0) {
            e.preventDefault();
            handleFiles(files);
        }
    }, [handleFiles, supportsVision]);

    const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            handleFiles(Array.from(e.target.files));
            // Reset input so the same file can be selected again if removed
            e.target.value = "";
        }
    };

    const triggerFileInput = () => {
        fileInputRef.current?.click();
    };

    const removeImage = (index: number) => {
        const image = pastedImages[index];
        if (image.key) {
            removeMediaKey(image.key);
        }
        setPastedImages(prev => prev.filter((_, i) => i !== index));
    };

    return (
        <Box p={4} position="absolute" bottom="0" width="full" bg="#f2ece4">
            {/* Image Preview Area */}
            {pastedImages.length > 0 && (
                <HStack gap={4} mb={2} px={2} overflowX="auto">
                    {pastedImages.map((img, index) => (
                        <Box key={index} position="relative">
                            <Image
                                src={img.url}
                                alt={`Pasted ${index}`}
                                boxSize="60px"
                                objectFit="cover"
                                borderRadius="md"
                                opacity={img.isLoading ? 0.5 : 1}
                                cursor="pointer"
                                onClick={() => !img.isLoading && showImage(img.url)}
                            />
                            {img.isLoading && (
                                <Spinner
                                    position="absolute"
                                    top="50%"
                                    left="50%"
                                    transform="translate(-50%, -50%)"
                                    size="sm"
                                />
                            )}
                            <CloseButton
                                size="sm"
                                position="absolute"
                                top="-8px"
                                right="-8px"
                                bg="red.500"
                                color="white"
                                borderRadius="full"
                                onClick={() => removeImage(index)}
                            />
                        </Box>
                    ))}
                </HStack>
            )}

            <HStack gap={2} bg="white" p={1} borderRadius="md" boxShadow="sm">
                {!isSidebarOpen && (
                    <IconButton
                        aria-label="Show sidebar"
                        variant="ghost"
                        size="sm"
                        onClick={onShowSidebar}
                    >
                        <LuPanelLeftOpen />
                    </IconButton>
                )}
                <Textarea
                    placeholder="Type a message..."
                    variant="subtle"
                    px={3}
                    py={2}
                    border="none"
                    _focus={{ boxShadow: "none" }}
                    flex={1}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    onPaste={handlePaste}
                />
                <input
                    type="file"
                    accept="image/png,image/jpeg"
                    multiple
                    style={{ display: "none" }}
                    ref={fileInputRef}
                    onChange={onFileChange}
                />
                <IconButton
                    aria-label="Upload images"
                    variant="ghost"
                    size="sm"
                    onClick={triggerFileInput}
                    disabled={pastedImages.length >= 3 || !supportsVision}
                >
                    <LuImage />
                </IconButton>
                <IconButton
                    aria-label="Options"
                    variant="ghost"
                    size="sm"
                    onClick={onOpen}
                >
                    <LuPlus />
                </IconButton>
                <IconButton
                    aria-label="Send message"
                    bg="green.500"
                    color="white"
                    size="sm"
                    _hover={{ bg: "green.600" }}
                    onClick={handleSend}
                    disabled={pastedImages.some(img => img.isLoading) || (pastedImages.length > 0 && !supportsVision)}
                >
                    <LuSend />
                </IconButton>
            </HStack>
            <OptionsModal isOpen={open} onClose={onClose} onStartNewChat={onStartNewChatBtnClicked} />
        </Box>
    );
};

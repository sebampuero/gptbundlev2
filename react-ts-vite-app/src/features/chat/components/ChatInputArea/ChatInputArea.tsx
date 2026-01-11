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
import { useState, useCallback } from "react";
import { LuPlus, LuSend, LuPanelLeftOpen } from "react-icons/lu";
import { OptionsModal } from "./OptionsModal";
import { useNavigate } from "react-router-dom";

interface ChatInputAreaProps {
    onShowSidebar: () => void;
    isSidebarOpen: boolean;
    onSendMessage: (content: string, presignedUrls?: string[]) => void;
    onStartNewChat: () => void;
    uploadImages: (files: File[]) => Promise<string[]>;
    removeMediaKey: (key: string) => void;
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
    removeMediaKey
}: ChatInputAreaProps) => {
    const { open, onOpen, onClose } = useDisclosure();
    const [inputValue, setInputValue] = useState("");
    const [pastedImages, setPastedImages] = useState<PastedImage[]>([]);
    const navigate = useNavigate();

    const handleSend = () => {
        if (inputValue.trim() || pastedImages.length > 0) {
            // Wait for all uploads to finish before sending? 
            // The requirement says "loading icon will disappear as soon as the s3 keys of the image arrive".
            // And "When the user sends... uploaded images are shown".
            // If the user sends while loading, we probably should wait or block, but let's assume they wait.
            // Actually, if we use the ref in useChatMessages, we just need to make sure uploading started.
            // But if it's still loading, the keys might not be ready.
            // However, the user request says "loading icon will disappear as soon as the s3 keys... arrive".
            // So if they are still loading, maybe disable send? Or just send what we have? 
            // Better to block send if images are loading.

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

    const handlePaste = useCallback(async (e: React.ClipboardEvent) => {
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

            const remainingSlots = 3 - pastedImages.length;
            const filesToUpload = files.slice(0, remainingSlots);

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
                // Remove failed images
                setPastedImages(prev => prev.filter(img => !filesToUpload.includes(img.file)));
            }
        }
    }, [pastedImages, uploadImages]);

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
                    disabled={pastedImages.some(img => img.isLoading)}
                >
                    <LuSend />
                </IconButton>
            </HStack>
            <OptionsModal isOpen={open} onClose={onClose} onStartNewChat={onStartNewChatBtnClicked} />
        </Box>
    );
};

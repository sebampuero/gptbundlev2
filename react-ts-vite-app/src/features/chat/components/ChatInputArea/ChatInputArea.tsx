import {
    Box,
    Textarea,
    IconButton,
    HStack,
    useDisclosure,
    Image,
    Spinner,
    CloseButton,
    MenuRoot,
    MenuTrigger,
    MenuContent,
    MenuItem,
} from "@chakra-ui/react";
import { useState, useCallback, useMemo } from "react";
import { LuPlus, LuSend, LuPanelLeftOpen, LuImage, LuCamera, LuBrain, LuMenu, LuFileText } from "react-icons/lu";
import { OptionsModal } from "./OptionsModal";
import { useImagePreview } from "../../../../context/ImagePreviewContext";
import { useLLModels } from "../../hooks/useLLModels";
import type { ReasoningEffort } from "../../types";

import { useModel } from "../../../../context/ModelContext";
import { Check } from "lucide-react";
import { useRef } from "react";
import { toaster } from "../../../../components/ui/toaster";

interface ChatInputAreaProps {
    onShowSidebar: () => void;
    isSidebarOpen: boolean;
    onSendMessage: (content: string, blobUrls?: string[], isReasoningSelected?: boolean) => void;
    onStartNewChat: () => void;
    uploadMedia: (files: File[]) => Promise<string[]>;
    removeMediaKeys: (keys: string[]) => void;
    isWebsocketConnected: boolean;
    isOutputVisionSelected: boolean;
    setIsOutputVisionSelected: (selected: boolean) => void;
    isReasoningSelected: boolean;
    reasoningEffort: ReasoningEffort;
    setReasoningEffort: (effort: ReasoningEffort) => void;
}

interface PastedMedia {
    type: "image" | "pdf";
    name?: string;
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
    uploadMedia,
    removeMediaKeys,
    isWebsocketConnected,
    isOutputVisionSelected,
    setIsOutputVisionSelected,
    isReasoningSelected,
    reasoningEffort,
    setReasoningEffort
}: ChatInputAreaProps) => {

    const { open, onOpen, onClose } = useDisclosure();
    const [inputValue, setInputValue] = useState("");
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [pastedMedia, setPastedMedia] = useState<PastedMedia[]>([]);
    const { models } = useLLModels();
    const { selectedModel } = useModel();
    const imageInputRef = useRef<HTMLInputElement>(null);
    const pdfInputRef = useRef<HTMLInputElement>(null);
    const { showImage } = useImagePreview();

    const currentModel = useMemo(() => {
        return models.find(m => m.model_name === selectedModel);
    }, [models, selectedModel]);

    const supportsInputVision = currentModel?.supports_input_vision ?? false;
    const supportsOutputVision = currentModel?.supports_output_vision ?? false;
    const supportsReasoning = currentModel?.supports_reasoning ?? false;

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
        if (pastedMedia.length > 0 && !supportsInputVision && !isWebsocketConnected && pastedMedia.some(m => m.type === 'image')) {
            return;
        }

        if (inputValue.trim() || pastedMedia.length > 0) {

            if (pastedMedia.some(img => img.isLoading)) {
                return; // Prevent sending while uploading
            }

            const blobUrls = pastedMedia.filter(m => m.type === 'image').map(m => m.url);
            onSendMessage(inputValue, blobUrls.length > 0 ? blobUrls : undefined);
            setInputValue("");
            setPastedMedia([]);
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
        onStartNewChat();
    };

    const handleFiles = useCallback(async (files: File[]) => {
        const remainingImages = 3 - pastedMedia.filter(m => m.type === 'image').length;
        const remainingPdfs = 2 - pastedMedia.filter(m => m.type === 'pdf').length;

        const imagesToUpload = [];
        const pdfsToUpload = [];

        for (const file of files) {
            if (file.type === "application/pdf" && pdfsToUpload.length < remainingPdfs) {
                pdfsToUpload.push(file);
            } else if (file.type.indexOf("image") !== -1 && imagesToUpload.length < remainingImages && supportsInputVision) {
                imagesToUpload.push(file);
            }
        }

        const filesToUpload = [...imagesToUpload, ...pdfsToUpload];
        if (filesToUpload.length === 0) return;

        let pdfCounter = pastedMedia.filter(m => m.type === 'pdf').length + 1;
        const newMedia: PastedMedia[] = filesToUpload.map(file => {
            const isPdf = file.type === "application/pdf";
            return {
                file,
                url: URL.createObjectURL(file), // will be used as preview placeholder for pdf or actual image src
                type: isPdf ? 'pdf' : 'image',
                name: isPdf ? `pdf-${pdfCounter++}.pdf` : undefined,
                isLoading: true
            };
        });

        setPastedMedia(prev => [...prev, ...newMedia]);

        try {
            const keys = await uploadMedia(filesToUpload);
            setPastedMedia(prev => {
                let keyIndex = 0;
                return prev.map(item => {
                    if (filesToUpload.includes(item.file)) {
                        return { ...item, isLoading: false, key: keys[keyIndex++] };
                    }
                    return item;
                });
            });
        } catch (error) {
            console.error("Failed to upload media", error);
            setPastedMedia(prev => prev.filter(item => !filesToUpload.includes(item.file)));
        }
    }, [pastedMedia, uploadMedia, supportsInputVision]);

    const handlePaste = useCallback(async (e: React.ClipboardEvent) => {

        const items = e.clipboardData.items;
        const files: File[] = [];

        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf("image") !== -1 || items[i].type === "application/pdf") {
                const file = items[i].getAsFile();
                if (file) files.push(file);
            }
        }

        if (files.length > 0) {
            e.preventDefault();
            handleFiles(files);
        }
    }, [handleFiles, supportsInputVision]);

    const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            handleFiles(Array.from(e.target.files));
            // Reset input so the same file can be selected again if removed
            e.target.value = "";
        }
    };

    const triggerImageInput = () => {
        imageInputRef.current?.click();
    };

    const triggerPdfInput = () => {
        pdfInputRef.current?.click();
    };

    const triggerOutputVision = () => {
        setIsOutputVisionSelected(!isOutputVisionSelected);
    };

    const removeMedia = (index: number) => {
        const item = pastedMedia[index];
        if (item.key) {
            removeMediaKeys([item.key]);
        }
        setPastedMedia(prev => prev.filter((_, i) => i !== index));
    };

    const actionButtons = (
        <>
            <IconButton
                aria-label="Ask for image"
                variant={isOutputVisionSelected ? "solid" : "ghost"}
                colorPalette={isOutputVisionSelected ? "blue" : "gray"}
                size="sm"
                onClick={triggerOutputVision}
                disabled={!supportsOutputVision}
            >
                <LuCamera />
            </IconButton>
            <MenuRoot>
                <MenuTrigger asChild>
                    <IconButton
                        aria-label="Activate reasoning"
                        variant={isReasoningSelected ? "solid" : "ghost"}
                        colorPalette={isReasoningSelected ? "blue" : "gray"}
                        size="sm"
                        disabled={!supportsReasoning}
                    >
                        <LuBrain />
                    </IconButton>
                </MenuTrigger>
                <MenuContent>
                    <MenuItem value="disabled" onClick={() => setReasoningEffort("disabled")}>
                        <HStack justify="space-between" width="full">
                            Disabled
                            {reasoningEffort === "disabled" && <Check size={14} />}
                        </HStack>
                    </MenuItem>
                    <MenuItem value="low" onClick={() => setReasoningEffort("low")}>
                        <HStack justify="space-between" width="full">
                            Low effort
                            {reasoningEffort === "low" && <Check size={14} />}
                        </HStack>
                    </MenuItem>
                    <MenuItem value="medium" onClick={() => setReasoningEffort("medium")}>
                        <HStack justify="space-between" width="full">
                            Medium effort
                            {reasoningEffort === "medium" && <Check size={14} />}
                        </HStack>
                    </MenuItem>
                    <MenuItem value="high" onClick={() => setReasoningEffort("high")}>
                        <HStack justify="space-between" width="full">
                            High effort
                            {reasoningEffort === "high" && <Check size={14} />}
                        </HStack>
                    </MenuItem>
                </MenuContent>
            </MenuRoot>
            <IconButton
                aria-label="Upload pdf files"
                variant="ghost"
                size="sm"
                onClick={triggerPdfInput}
                disabled={pastedMedia.filter(m => m.type === 'pdf').length >= 2}
            >
                <LuFileText />
            </IconButton>
            <IconButton
                aria-label="Upload images"
                variant="ghost"
                size="sm"
                onClick={triggerImageInput}
                disabled={pastedMedia.filter(m => m.type === 'image').length >= 3 || !supportsInputVision}
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
        </>
    );

    return (
        <Box p={4} position="absolute" bottom="0" width="full" bg="#f2ece4">
            {/* Image Preview Area */}
            {pastedMedia.length > 0 && (
                <HStack gap={4} mb={2} px={2} overflowX="auto">
                    {pastedMedia.map((media, index) => (
                        <Box key={index} position="relative">
                            {media.type === 'image' ? (
                                <Image
                                    src={media.url}
                                    alt={`Pasted ${index}`}
                                    boxSize="60px"
                                    objectFit="cover"
                                    borderRadius="md"
                                    opacity={media.isLoading ? 0.5 : 1}
                                    cursor="pointer"
                                    onClick={() => !media.isLoading && showImage(media.url)}
                                />
                            ) : (
                                <Box
                                    boxSize="60px"
                                    bg="gray.100"
                                    borderRadius="md"
                                    display="flex"
                                    alignItems="center"
                                    justifyContent="center"
                                    flexDirection="column"
                                    border="1px solid"
                                    borderColor="gray.200"
                                    opacity={media.isLoading ? 0.5 : 1}
                                    color="gray.600"
                                >
                                    <LuFileText size={24} />
                                    <Box fontSize="10px" mt={1} maxW="50px">
                                        {media.name}
                                    </Box>
                                </Box>
                            )}
                            {media.isLoading && (
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
                                onClick={() => removeMedia(index)}
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
                    ref={imageInputRef}
                    onChange={onFileChange}
                />
                <input
                    type="file"
                    accept="application/pdf"
                    multiple
                    style={{ display: "none" }}
                    ref={pdfInputRef}
                    onChange={onFileChange}
                />
                <HStack gap={2} display={{ base: "none", md: "flex" }}>
                    {actionButtons}
                </HStack>

                <Box display={{ base: "block", md: "none" }} position="relative">
                    <IconButton
                        aria-label="More options"
                        variant={isMobileMenuOpen ? "solid" : "ghost"}
                        size="sm"
                        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                    >
                        <LuMenu />
                    </IconButton>

                    {isMobileMenuOpen && (
                        <Box
                            position="absolute"
                            bottom="calc(100% + 10px)"
                            right="0"
                            bg="white"
                            p={2}
                            borderRadius="md"
                            boxShadow="md"
                            border="1px solid"
                            borderColor="gray.200"
                            zIndex={10}
                        >
                            <HStack gap={2}>
                                {actionButtons}
                            </HStack>
                        </Box>
                    )}
                </Box>
                <IconButton
                    aria-label="Send message"
                    bg="green.500"
                    color="white"
                    size="sm"
                    _hover={{ bg: "green.600" }}
                    onClick={handleSend}
                    disabled={pastedMedia.some(img => img.isLoading) || (pastedMedia.filter(m => m.type === 'image').length > 0 && !supportsInputVision)}
                >
                    <LuSend />
                </IconButton>
            </HStack>
            <OptionsModal isOpen={open} onClose={onClose} onStartNewChat={onStartNewChatBtnClicked} />
        </Box>
    );
};

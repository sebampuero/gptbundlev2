import {
    Box,
    Input,
    IconButton,
    HStack,
    useDisclosure,
} from "@chakra-ui/react";
import { useState } from "react";
import { LuPlus, LuSend, LuPanelLeftOpen } from "react-icons/lu";
import { OptionsModal } from "./OptionsModal";
import { useNavigate } from "react-router-dom";

interface ChatInputAreaProps {
    onShowSidebar: () => void;
    isSidebarOpen: boolean;
    onSendMessage: (content: string) => void;
}

export const ChatInputArea = ({
    onShowSidebar,
    isSidebarOpen,
    onSendMessage,
}: ChatInputAreaProps) => {
    const { open, onOpen, onClose } = useDisclosure();
    const [inputValue, setInputValue] = useState("");
    const navigate = useNavigate();

    const handleSend = () => {
        if (inputValue.trim()) {
            onSendMessage(inputValue);
            setInputValue("");
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === "Enter") {
            handleSend();
        }
    };

    const onStartNewChat = () => {
        onClose();
        navigate("/chat", { replace: true });
    };

    return (
        <Box p={4} position="absolute" bottom="0" width="full" bg="#f2ece4">
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
                <Input
                    placeholder="Type a message..."
                    variant="subtle"
                    px={3}
                    py={2}
                    border="none"
                    _focus={{ boxShadow: "none" }}
                    flex={1}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
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
                >
                    <LuSend />
                </IconButton>
            </HStack>
            <OptionsModal isOpen={open} onClose={onClose} onStartNewChat={onStartNewChat} />
        </Box>
    );
};

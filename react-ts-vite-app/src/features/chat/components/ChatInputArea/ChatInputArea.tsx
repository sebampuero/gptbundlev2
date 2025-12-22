import {
    Box,
    Input,
    IconButton,
    HStack,
    useDisclosure,
} from "@chakra-ui/react";
import { LuPlus, LuSend, LuPanelLeftOpen } from "react-icons/lu";
import { OptionsModal } from "./OptionsModal";

interface ChatInputAreaProps {
    onShowSidebar: () => void;
    isSidebarOpen: boolean;
}

export const ChatInputArea = ({
    onShowSidebar,
    isSidebarOpen,
}: ChatInputAreaProps) => {
    const { open, onOpen, onClose } = useDisclosure();

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
                    placeholder=""
                    variant="subtle"
                    px={3}
                    py={2}
                    border="none"
                    _focus={{ boxShadow: "none" }}
                    flex={1}
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
                >
                    <LuSend />
                </IconButton>
            </HStack>
            <OptionsModal isOpen={open} onClose={onClose} />
        </Box>
    );
};

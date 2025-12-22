import {
    Box,
    Input,
    IconButton,
    HStack,
    useDisclosure,
} from "@chakra-ui/react";
import { LuPlus, LuSend } from "react-icons/lu";
import { OptionsModal } from "./OptionsModal";

export const ChatInputArea = () => {
    const { open, onOpen, onClose } = useDisclosure();

    return (
        <Box p={4} position="absolute" bottom="0" width="full" bg="#f2ece4">
            <HStack gap={2} bg="white" p={1} borderRadius="md" boxShadow="sm">
                <Input
                    placeholder=""
                    variant="subtle"
                    px={3}
                    py={2}
                    border="none"
                    _focus={{ boxShadow: "none" }}
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

import { Box, Text, VStack, IconButton, HStack } from "@chakra-ui/react";
import { LuTrash2 } from "react-icons/lu";

interface ChatListItemProps {
    id: string;
    title: string;
    timestamp: string;
    rawTimestamp: number;
    onDelete: (id: string, timestamp: number) => void;
    currentChat: { chatId?: string; timestamp?: string };
    startNewChat: () => void;
    onSelectChat: (id: string, timestamp: number) => void;
}

export const ChatListItem = ({
    id,
    title,
    timestamp,
    rawTimestamp,
    onDelete,
    currentChat,
    startNewChat,
    onSelectChat
}: ChatListItemProps) => {
    return (
        <Box
            p={3}
            borderRadius="md"
            _hover={{ bg: "gray.100", cursor: "pointer" }}
            borderBottom="1px solid"
            borderColor="gray.100"
            position="relative"
            role="group"
        >
            <VStack align="start" onClick={() => onSelectChat(id, rawTimestamp)}>
                <Text fontSize="xs" color="gray.500">
                    {timestamp}
                </Text>
                <Text fontWeight="semibold" fontSize="sm">
                    {title}
                </Text>
                <HStack width="full" justify="space-between">
                    <IconButton
                        aria-label="Delete chat"
                        as={LuTrash2}
                        size="xs"
                        variant="ghost"
                        color="gray.400"
                        _hover={{ color: "red.500", bg: "transparent" }}
                        onClick={(e) => {
                            e.stopPropagation();
                            onDelete(id, rawTimestamp);
                            if (currentChat.chatId === id) {
                                startNewChat();
                            }
                        }}
                    />
                </HStack>
            </VStack>
        </Box >
    );
};

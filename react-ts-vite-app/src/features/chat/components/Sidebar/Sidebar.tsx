import { Box, VStack, Heading, Button, HStack, IconButton, Spinner, Text } from "@chakra-ui/react";
import { LuChevronDown, LuPanelLeftClose } from "react-icons/lu";
import { SearchField } from "./SearchField";
import { ChatListItem } from "./ChatListItem";
import { useChats } from "../../hooks/useChats";

interface SidebarProps {
    onToggle: () => void;
}

export const Sidebar = ({ onToggle }: SidebarProps) => {
    // Using hardcoded email for now as per current implementation
    const { chats, isLoading, error } = useChats("test-live@example.com");

    return (
        <Box
            width="300px"
            height="100vh"
            borderRight="1px solid"
            borderColor="gray.200"
            bg="white"
            p={4}
            display="flex"
            flexDirection="column"
        >
            <HStack mb={4} justifyContent="space-between" alignItems="center">
                <Heading size="md">Chats</Heading>
                <IconButton
                    aria-label="Hide sidebar"
                    variant="ghost"
                    size="sm"
                    onClick={onToggle}
                >
                    <LuPanelLeftClose />
                </IconButton>
            </HStack>
            <SearchField />
            <VStack align="stretch" gap={0} flex={1} overflowY="auto" mt={4}>
                {isLoading && (
                    <Box display="flex" justifyContent="center" py={4}>
                        <Spinner size="sm" />
                    </Box>
                )}

                {error && (
                    <Box px={2} py={2}>
                        <Text fontSize="xs" color="red.500">Error loading chats</Text>
                    </Box>
                )}

                {!isLoading && !error && chats.map((chat) => {
                    const firstMessage = chat.messages[0]?.content || "New Chat";
                    const date = new Date(chat.timestamp * 1000).toLocaleDateString();

                    return (
                        <ChatListItem
                            key={chat.chat_id}
                            id={chat.chat_id}
                            title={firstMessage.length > 30 ? firstMessage.substring(0, 30) + "..." : firstMessage}
                            timestamp={date}
                        />
                    );
                })}

                {!isLoading && !error && chats.length === 0 && (
                    <Box px={2} py={4}>
                        <Text fontSize="sm" color="gray.500" textAlign="center">No chats yet</Text>
                    </Box>
                )}
            </VStack>
            <Button
                variant="ghost"
                width="full"
                justifyContent="space-between"
                size="sm"
                mt={4}
                fontWeight="normal"
                color="gray.600"
            >
                More
                <LuChevronDown size={14} />
            </Button>
        </Box>
    );
};

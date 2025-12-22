import { Box, VStack, Heading, Button, HStack, IconButton } from "@chakra-ui/react";
import { LuChevronDown, LuPanelLeftClose } from "react-icons/lu";
import { SearchField } from "./SearchField";
import { ChatListItem } from "./ChatListItem";

interface SidebarProps {
    onToggle: () => void;
}

export const Sidebar = ({ onToggle }: SidebarProps) => {
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
            <VStack align="stretch" gap={0} flex={1} overflowY="auto">
                <ChatListItem id="1" title="Chat 1" lastMessage="Last message" timestamp="12:34" />
                <ChatListItem id="2" title="Chat 2" lastMessage="Last message" timestamp="12:34" />
                <ChatListItem id="3" title="Chat 3" lastMessage="Last message" timestamp="12:34" />
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

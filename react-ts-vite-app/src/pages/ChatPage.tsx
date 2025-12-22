import { Flex, Box } from "@chakra-ui/react";
import { Sidebar } from "../features/chat/components/Sidebar/Sidebar";
import { ChatInputArea } from "../features/chat/components/ChatInputArea/ChatInputArea";

export const ChatPage = () => {
    return (
        <Flex h="100vh" w="100vw" overflow="hidden">
            <Sidebar />
            <Box flex={1} position="relative" bg="#e8e2d9">
                {/* Message list area would go here */}
                <ChatInputArea />
            </Box>
        </Flex>
    );
};

export default ChatPage;

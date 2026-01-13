import { Flex, Box, useBreakpointValue } from "@chakra-ui/react";
import { useState, useEffect } from "react";
import { Sidebar } from "../features/chat/components/Sidebar/Sidebar";
import { ChatInputArea } from "../features/chat/components/ChatInputArea/ChatInputArea";
import { MessageBubble } from "../features/chat/components/MessageBubble/MessageBubble";
import { useChatMessages } from "../features/chat/hooks/useChatMessages";
import { useChats } from "../features/chat/hooks/useChats";
import { useParams } from "react-router-dom";
import { useModel } from "../context/ModelContext";
import { useAuth } from "../context/AuthContext";

import { ImagePreviewProvider } from "../context/ImagePreviewContext";

export const ChatPage = () => {
    const isMobile = useBreakpointValue({ base: true, md: false });
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const { chatId, timestamp } = useParams();
    const { selectedModel } = useModel();
    const { user } = useAuth();

    // websocket connection with new chat. TODO: pass props chatid and timestamp when
    // clicking on a sidebar item
    const { messages, sendMessage, isConnected, startNewChat, isProcessingMessage, uploadImages, removeMediaKey } = useChatMessages({ chatId, timestamp });
    const { chats, isLoading, error, deleteChat, refreshChats, noMoreChatsToLoad } = useChats();

    const handleStartNewChat = () => {
        startNewChat();
        refreshChats(true);
    };

    useEffect(() => {
        if (isMobile !== undefined) {
            setIsSidebarOpen(!isMobile);
        }
    }, [isMobile]);

    const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);

    return (
        <ImagePreviewProvider>
            <Flex h="100vh" w="100vw" overflow="hidden" position="relative">
                {/* Sidebar Overlay for Mobile */}
                {isMobile && isSidebarOpen && (
                    <Box
                        position="absolute"
                        top={0}
                        left={0}
                        bottom={0}
                        right={0}
                        bg="blackAlpha.600"
                        zIndex={10}
                        onClick={toggleSidebar}
                    />
                )}

                <Box
                    position={isMobile ? "absolute" : "relative"}
                    zIndex={20}
                    left={isMobile && !isSidebarOpen ? "-300px" : "0"}
                    transition="left 0.3s ease"
                    display={!isMobile && !isSidebarOpen ? "none" : "block"}
                    width={isMobile ? "300px" : "auto"}
                >
                    <Sidebar
                        onToggle={toggleSidebar}
                        startNewChat={handleStartNewChat}
                        currentChatId={chatId}
                        currentTimestamp={timestamp}
                        chats={chats}
                        isLoading={isLoading}
                        error={error}
                        onDeleteChat={deleteChat}
                        onLoadMoreChats={refreshChats}
                        noMoreChatsToLoad={noMoreChatsToLoad}
                    />
                </Box>

                <Box flex={1} position="relative" bg="#e8e2d9" display="flex" flexDirection="column">
                    <Box flex={1} overflowY="auto" p={4} pb="100px" display="flex" flexDirection="column">
                        {messages.map((msg, index) => (
                            <MessageBubble
                                key={index}
                                message={msg}
                                isLoading={isProcessingMessage && msg.is_loading_message}
                            />
                        ))}
                        {!isConnected && (
                            <Box color="red.500" textAlign="center">
                                Connecting...
                            </Box>
                        )}
                    </Box>
                    <ChatInputArea
                        onShowSidebar={toggleSidebar}
                        isSidebarOpen={isSidebarOpen}
                        onSendMessage={(content, presignedUrls) => sendMessage(content, user?.email || "", selectedModel, presignedUrls)}
                        onStartNewChat={handleStartNewChat}
                        uploadImages={uploadImages}
                        removeMediaKey={removeMediaKey}
                        isWebsocketConnected={isConnected}
                    />
                </Box>
            </Flex>
        </ImagePreviewProvider>
    );
};


export default ChatPage;

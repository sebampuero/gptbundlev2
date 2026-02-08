import { Flex, Box, useBreakpointValue } from "@chakra-ui/react";
import { useState, useEffect } from "react";
import { Sidebar } from "../features/chat/components/Sidebar/Sidebar";
import { ChatInputArea } from "../features/chat/components/ChatInputArea/ChatInputArea";
import { MessageBubble } from "../features/chat/components/MessageBubble/MessageBubble";
import { useChatMessages } from "../features/chat/hooks/useChatMessages";
import { useChats } from "../features/chat/hooks/useChats";
import { useModel } from "../context/ModelContext";
import { useAuth } from "../context/AuthContext";

import { ImagePreviewProvider } from "../context/ImagePreviewContext";

export const ChatPage = () => {
    const isMobile = useBreakpointValue({ base: true, md: false });
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const { selectedModel } = useModel();
    const { user } = useAuth();

    const [currentChat, setCurrentChat] = useState<{ chatId?: string; timestamp?: string }>({});

    const {
        messages,
        sendMessage,
        isConnected,
        startNewChat,
        isProcessingMessage,
        uploadImages,
        removeMediaKey,
        isOutputVisionSelected,
        setIsOutputVisionSelected
    } = useChatMessages(currentChat);
    const {
        chats,
        isLoading,
        error,
        deleteChat,
        refreshChats,
        noMoreChatsToLoad,
        searchChats,
        moreChatsClicked,
    } = useChats();

    const handleStartNewChat = () => {
        setCurrentChat({});
        startNewChat();
        refreshChats(true);
    };

    const handleSelectChat = (chatId: string, timestamp: number) => {
        setCurrentChat({ chatId, timestamp: timestamp.toString() });
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
                        chats={chats}
                        isLoading={isLoading}
                        error={error}
                        onDeleteChat={deleteChat}
                        onLoadMoreChats={refreshChats}
                        noMoreChatsToLoad={noMoreChatsToLoad}
                        searchChats={searchChats}
                        onSelectChat={handleSelectChat}
                        currentChat={currentChat}
                        moreChatsClicked={moreChatsClicked}
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
                        isOutputVisionSelected={isOutputVisionSelected}
                        setIsOutputVisionSelected={setIsOutputVisionSelected}
                    />
                </Box>
            </Flex>
        </ImagePreviewProvider>
    );
};


export default ChatPage;

import { Flex, Box, useBreakpointValue } from "@chakra-ui/react";
import { useState, useEffect } from "react";
import { Sidebar } from "../features/chat/components/Sidebar/Sidebar";
import { ChatInputArea } from "../features/chat/components/ChatInputArea/ChatInputArea";

export const ChatPage = () => {
    const isMobile = useBreakpointValue({ base: true, md: false });
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);

    // Initialize sidebar state based on breakpoint
    useEffect(() => {
        if (isMobile !== undefined) {
            setIsSidebarOpen(!isMobile);
        }
    }, [isMobile]);

    const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);

    return (
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
                <Sidebar onToggle={toggleSidebar} />
            </Box>

            <Box flex={1} position="relative" bg="#e8e2d9">
                {/* Message list area would go here */}
                <ChatInputArea
                    onShowSidebar={toggleSidebar}
                    isSidebarOpen={isSidebarOpen}
                />
            </Box>
        </Flex>
    );
};

export default ChatPage;

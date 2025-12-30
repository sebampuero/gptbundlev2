import { Box } from "@chakra-ui/react";
import { Copy, Check } from "lucide-react";
import { useState } from "react";
import Markdown from "react-markdown";

interface MessageBubbleProps {
    message: { role: string; content: string };
}

export const MessageBubble = ({ message }: MessageBubbleProps) => {
    const isUser = message.role === "user";
    const [isCopied, setIsCopied] = useState(false);

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(message.content);
            setIsCopied(true);
            setTimeout(() => setIsCopied(false), 2000);
        } catch (err) {
            console.error("Failed to copy text: ", err);
        }
    };

    return (
        <Box
            alignSelf={isUser ? "flex-end" : "flex-start"}
            bg={isUser ? "blue.500" : "white"}
            color={isUser ? "white" : "black"}
            p={3}
            borderRadius="lg"
            mb={2}
            maxW="80%"
            position="relative"
            role="group"
        >
            {!isUser && (
                <Box
                    position="absolute"
                    top={0}
                    right={0}
                    opacity={5}
                    _groupHover={{ opacity: 1 }}
                    transition="opacity 0.2s"
                    cursor="pointer"
                    onClick={handleCopy}
                    p={1}
                    borderRadius="md"
                    _hover={{ bg: "blackAlpha.100" }}
                >
                    {isCopied ? <Check size={14} /> : <Copy size={14} />}
                </Box>
            )}
            <Box
                position="relative"
                bottom={0}
                left={0}
                paddingTop={0}
            >
                <Markdown>{message.content}</Markdown>
            </Box>
        </Box>
    );
};

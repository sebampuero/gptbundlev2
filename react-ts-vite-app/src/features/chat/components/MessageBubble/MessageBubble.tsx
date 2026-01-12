import { Box } from "@chakra-ui/react";
import { keyframes } from "@emotion/react";
import { Copy, Check } from "lucide-react";
import { useState } from "react";
import Markdown from "react-markdown";
import { Image } from "@chakra-ui/react";

import { useImagePreview } from "../../../../context/ImagePreviewContext";

interface MessageBubbleProps {
    message: {
        role: string;
        content: string;
        presigned_urls?: string[];
    };
}

const bounce = keyframes`
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
`;

export const MessageBubble = ({ message, isLoading }: MessageBubbleProps & { isLoading?: boolean }) => {
    const isUser = message.role === "user";
    const [isCopied, setIsCopied] = useState(false);
    const { showImage } = useImagePreview();

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
            {!isLoading && (
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
                {message.presigned_urls && message.presigned_urls.length > 0 && (
                    <Box display="flex" alignItems="center" mt={2}>
                        {message.presigned_urls.map((url, index) => (
                            <Image
                                key={index}
                                src={url}
                                alt={`Image ${index + 1}`}
                                maxW="200px"
                                maxH="200px"
                                objectFit="contain"
                                mr={2}
                                cursor="pointer"
                                onClick={() => showImage(url)}
                                transition="transform 0.2s"
                                _hover={{ transform: "scale(1.02)" }}
                            />
                        ))}
                    </Box>
                )}
                {isLoading && (
                    <Box display="flex" alignItems="center" mt={2} height="10px">
                        <Box
                            as="span"
                            width="6px"
                            height="6px"
                            bg="gray.500"
                            borderRadius="full"
                            mx="2px"
                            animation={`${bounce} 1.4s infinite ease-in-out both`}
                            animationDelay="-0.32s"
                        />
                        <Box
                            as="span"
                            width="6px"
                            height="6px"
                            bg="gray.500"
                            borderRadius="full"
                            mx="2px"
                            animation={`${bounce} 1.4s infinite ease-in-out both`}
                            animationDelay="-0.16s"
                        />
                        <Box
                            as="span"
                            width="6px"
                            height="6px"
                            bg="gray.500"
                            borderRadius="full"
                            mx="2px"
                            animation={`${bounce} 1.4s infinite ease-in-out both`}
                        />
                    </Box>
                )}
            </Box>
        </Box>
    );
};

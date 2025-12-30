import {
    Box,
    DialogRoot,
    DialogContent,
    DialogHeader,
    DialogBody,
    Portal,
    Button,
    Field,
    VStack,
    Input,
    HStack,
    Text
} from "@chakra-ui/react";
import { useState, useMemo } from "react";
import { Search, Check } from "lucide-react";
import { useLLModels } from "../../hooks/useLLModels";

interface OptionsModalProps {
    isOpen: boolean;
    onClose: () => void;
    onStartNewChat: () => void;
}

export const OptionsModal = ({ isOpen, onClose, onStartNewChat }: OptionsModalProps) => {
    const [selectedModel, setSelectedModel] = useState("openrouter/mistralai/devstral-2512:free");
    const [searchQuery, setSearchQuery] = useState("");

    const { models } = useLLModels();

    const filteredModels = useMemo(() => {
        return models.filter(model =>
            model.model_name.toLowerCase().includes(searchQuery.toLowerCase())
        );
    }, [searchQuery]);

    if (!isOpen) return null;

    return (
        <DialogRoot open={isOpen} onOpenChange={(e) => !e.open && onClose()}>
            <Portal>
                <Box
                    position="fixed"
                    inset="0"
                    bg="blackAlpha.700"
                    zIndex="1400"
                    onClick={onClose}
                    backdropFilter="blur(8px)"
                />
                <DialogContent
                    position="fixed"
                    top="50%"
                    left="50%"
                    transform="translate(-50%, -50%)"
                    zIndex="1500"
                    bg="white"
                    p={0}
                    borderRadius="2xl"
                    boxShadow="2xl"
                    overflow="hidden"
                    border="1px solid"
                    borderColor="gray.100"
                >
                    <Box p={6} borderBottom="1px solid" borderColor="gray.100">
                        <DialogHeader fontWeight="bold" fontSize="xl" p={2}>
                            Chat Settings
                        </DialogHeader>

                        <Field.Root>
                            <Box position="relative">
                                <Input
                                    placeholder="Search models..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    pl="10"
                                    bg="gray.50"
                                    h="12"
                                    borderRadius="xl"
                                    border="1px solid"
                                    borderColor="gray.200"
                                    _focus={{
                                        borderColor: "blue.500",
                                        boxShadow: "0 0 0 1px var(--chakra-colors-blue-500)",
                                        bg: "white",
                                    }}
                                />
                                <Text fontSize="xs" color="gray.500" fontWeight="bold">
                                    Currently selected model: {selectedModel}
                                </Text>
                                <Box
                                    position="absolute"
                                    left="3.5"
                                    top="50%"
                                    transform="translateY(-50%)"
                                    color="gray.400"
                                    pointerEvents="none"
                                >
                                    <Search size={20} />
                                </Box>
                            </Box>
                        </Field.Root>
                    </Box>

                    <DialogBody p={2} maxH="400px" overflowY="auto">
                        <VStack gap={1} align="stretch">
                            {filteredModels.map((model) => (
                                <Box
                                    key={model.model_name}
                                    p={3}
                                    px={4}
                                    cursor="pointer"
                                    borderRadius="lg"
                                    bg={selectedModel === model.model_name ? "blue.50" : "transparent"}
                                    transition="all 0.2s"
                                    _hover={{
                                        bg: selectedModel === model.model_name ? "blue.50" : "gray.50",
                                    }}
                                    onClick={() => setSelectedModel(model.model_name)}
                                >
                                    <HStack justify="space-between">
                                        <Text fontWeight="semibold" fontSize="md" color={selectedModel === model.model_name ? "blue.600" : "gray.800"}>
                                            {model.model_name}
                                        </Text>
                                        {selectedModel === model.model_name && (
                                            <Check size={18} color="var(--chakra-colors-blue-600)" />
                                        )}
                                    </HStack>
                                    <Text fontSize="xs" color="gray.500">
                                        <HStack>
                                            Input vision
                                            {model.supports_input_vision && (
                                                <Check size={12} color="var(--chakra-colors-blue-600)" />
                                            )}
                                        </HStack>
                                    </Text>
                                    <Text fontSize="xs" color="gray.500">
                                        <HStack>
                                            Output vision
                                            {model.supports_output_vision && (
                                                <Check size={12} color="var(--chakra-colors-blue-600)" />
                                            )}
                                        </HStack>
                                    </Text>
                                </Box>
                            ))}
                        </VStack>
                    </DialogBody>

                    <Box p={4} bg="gray.50" borderTop="1px solid" borderColor="gray.100">
                        <Button
                            variant="solid"
                            onClick={onStartNewChat}
                            fontWeight="bold"
                            boxShadow="sm"
                            _hover={{ transform: "translateY(-1px)", boxShadow: "md" }}
                            _active={{ transform: "translateY(0)" }}
                        >
                            Start New Chat
                        </Button>
                    </Box>
                </DialogContent>
            </Portal>
        </DialogRoot>
    );
};

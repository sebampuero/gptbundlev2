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

interface OptionsModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const LLM_MODELS = [
    { label: "GPT-4o", value: "gpt-4o" },
    { label: "GPT-4o mini", value: "gpt-4o-mini" },
    { label: "Claude 3.5 Sonnet", value: "claude-3.5-sonnet" },
    { label: "Claude 3 Opus", value: "claude-3-opus" },
    { label: "Gemini 1.5 Pro", value: "gemini-1.5-pro" },
    { label: "Gemini 1.5 Flash", value: "gemini-1.5-flash" },
    { label: "GPT-5", value: "gpt-5" },
    { label: "GPT-5o", value: "gpt-5o" },
    { label: "GPT-5o mini", value: "gpt-5o-mini" },
    { label: "GPT-5o mini2", value: "gpt-5o-mini2" },
    { label: "GPT-5o mini3", value: "gpt-5o-mini3" },
    { label: "GPT-5o mini4", value: "gpt-5o-mini4" },
    { label: "GPT-5o mini5", value: "gpt-5o-mini5" },
];

export const OptionsModal = ({ isOpen, onClose }: OptionsModalProps) => {
    const [selectedModel, setSelectedModel] = useState("gpt-4o");
    const [searchQuery, setSearchQuery] = useState("");

    const filteredModels = useMemo(() => {
        return LLM_MODELS.filter(model =>
            model.label.toLowerCase().includes(searchQuery.toLowerCase())
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
                            {filteredModels.length > 0 ? (
                                filteredModels.map((model) => (
                                    <Box
                                        key={model.value}
                                        p={3}
                                        px={4}
                                        cursor="pointer"
                                        borderRadius="lg"
                                        bg={selectedModel === model.value ? "blue.50" : "transparent"}
                                        transition="all 0.2s"
                                        _hover={{
                                            bg: selectedModel === model.value ? "blue.50" : "gray.50",
                                        }}
                                        onClick={() => setSelectedModel(model.value)}
                                    >
                                        <HStack justify="space-between">
                                            <Text fontWeight="semibold" fontSize="md" color={selectedModel === model.value ? "blue.600" : "gray.800"}>
                                                {model.label}
                                            </Text>
                                            {selectedModel === model.value && (
                                                <Check size={18} color="var(--chakra-colors-blue-600)" />
                                            )}
                                        </HStack>
                                    </Box>
                                ))
                            ) : (
                                <Box p={8} textAlign="center">
                                    <Text color="gray.500" fontSize="sm">
                                        No models found matching your search.
                                    </Text>
                                </Box>
                            )}
                        </VStack>
                    </DialogBody>

                    <Box p={4} bg="gray.50" borderTop="1px solid" borderColor="gray.100">
                        <Button
                            variant="solid"
                            onClick={onClose}
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

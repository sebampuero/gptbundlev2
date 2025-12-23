import {
    Box,
    DialogRoot,
    DialogContent,
    DialogHeader,
    DialogBody,
    Portal,
    Button,
    Field,
    NativeSelect,
    VStack,
} from "@chakra-ui/react";
import { useState } from "react";

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
];

export const OptionsModal = ({ isOpen, onClose }: OptionsModalProps) => {
    const [selectedModel, setSelectedModel] = useState("gpt-4o");

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
                    backdropFilter="blur(4px)"
                />
                <DialogContent
                    position="fixed"
                    top="50%"
                    left="50%"
                    transform="translate(-50%, -50%)"
                    zIndex="1500"
                    bg="white"
                    p={6}
                    borderRadius="xl"
                    boxShadow="2xl"
                    minWidth="350px"
                    border="1px solid"
                    borderColor="gray.100"
                >
                    <DialogHeader fontWeight="bold" fontSize="xl" mb={4}>
                        Chat Settings
                    </DialogHeader>
                    <DialogBody>
                        <VStack gap={6} align="stretch">
                            <Field.Root>
                                <Field.Label fontSize="sm" fontWeight="medium" color="gray.600" mb={1}>
                                    Large Language Model
                                </Field.Label>
                                <NativeSelect.Root size="md">
                                    <NativeSelect.Field
                                        value={selectedModel}
                                        onChange={(e) => setSelectedModel(e.currentTarget.value)}
                                        cursor="pointer"
                                        bg="gray.50"
                                        border="1px solid"
                                        borderColor="gray.200"
                                        _hover={{ borderColor: "blue.400" }}
                                        _focus={{ borderColor: "blue.500", boxShadow: "0 0 0 1px var(--chakra-colors-blue-500)" }}
                                    >
                                        {LLM_MODELS.map((model) => (
                                            <option key={model.value} value={model.value}>
                                                {model.label}
                                            </option>
                                        ))}
                                    </NativeSelect.Field>
                                </NativeSelect.Root>
                                <Field.HelperText fontSize="xs" color="gray.500" mt={1}>
                                    Select the model to power your conversation.
                                </Field.HelperText>
                            </Field.Root>

                            <Box pt={2}>
                                <Button
                                    variant="solid"
                                    onClick={() => {
                                        onClose();
                                    }}
                                    fontWeight="semibold"
                                >
                                    New Chat
                                </Button>
                            </Box>
                        </VStack>
                    </DialogBody>
                </DialogContent>
            </Portal>
        </DialogRoot>
    );
};

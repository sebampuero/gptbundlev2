import {
    Box,
    DialogRoot,
    DialogContent,
    DialogHeader,
    DialogBody,
    DialogCloseTrigger,
    Portal,
    Text
} from "@chakra-ui/react";

interface OptionsModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export const OptionsModal = ({ isOpen, onClose }: OptionsModalProps) => {
    if (!isOpen) return null;

    return (
        <DialogRoot open={isOpen} onOpenChange={(e) => !e.open && onClose()}>
            <Portal>
                <Box
                    position="fixed"
                    inset="0"
                    bg="blackAlpha.600"
                    zIndex="1400"
                    onClick={onClose}
                />
                <DialogContent
                    position="fixed"
                    top="50%"
                    left="50%"
                    transform="translate(-50%, -50%)"
                    zIndex="1500"
                    bg="white"
                    p={4}
                    borderRadius="md"
                    boxShadow="xl"
                    minWidth="300px"
                >
                    <DialogHeader fontWeight="bold" mb={2}>Options</DialogHeader>
                    <DialogCloseTrigger
                        position="absolute"
                        top="2"
                        right="2"
                        onClick={onClose}
                        cursor="pointer"
                    />
                    <DialogBody>
                        <Text>Placeholder for options...</Text>
                    </DialogBody>
                </DialogContent>
            </Portal>
        </DialogRoot>
    );
};

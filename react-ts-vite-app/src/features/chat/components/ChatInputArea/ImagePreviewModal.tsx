import {
    Box,
    DialogRoot,
    DialogContent,
    DialogBody,
    Portal,
    Image,
    IconButton
} from "@chakra-ui/react";
import { LuX } from "react-icons/lu";

interface ImagePreviewModalProps {
    isOpen: boolean;
    onClose: () => void;
    imageUrl: string;
}

export const ImagePreviewModal = ({ isOpen, onClose, imageUrl }: ImagePreviewModalProps) => {
    if (!isOpen) return null;

    return (
        <DialogRoot open={isOpen} onOpenChange={(e) => !e.open && onClose()}>
            <Portal>
                <Box
                    position="fixed"
                    inset="0"
                    bg="blackAlpha.800"
                    zIndex="1600"
                    onClick={onClose}
                    backdropFilter="blur(10px)"
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                >
                    <IconButton
                        aria-label="Close"
                        position="absolute"
                        top="20px"
                        right="20px"
                        variant="ghost"
                        color="white"
                        _hover={{ bg: "whiteAlpha.200" }}
                        onClick={onClose}
                        zIndex="1610"
                    >
                        <LuX size={24} />
                    </IconButton>

                    <DialogContent
                        bg="transparent"
                        boxShadow="none"
                        maxW="90vw"
                        maxH="90vh"
                        display="flex"
                        alignItems="center"
                        justifyContent="center"
                        border="none"
                        p={0}
                        m={0}
                        onClick={(e) => e.stopPropagation()}
                    >
                        <DialogBody p={0} display="flex" justifyContent="center" alignItems="center">
                            <Image
                                src={imageUrl}
                                alt="Image Preview"
                                maxW="100%"
                                maxH="90vh"
                                objectFit="contain"
                                borderRadius="lg"
                                boxShadow="2xl"
                            />
                        </DialogBody>
                    </DialogContent>
                </Box>
            </Portal>
        </DialogRoot>
    );
};

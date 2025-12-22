import { Box, Input } from "@chakra-ui/react";
import { LuSearch } from "react-icons/lu";

export const SearchField = () => {
    return (
        <Box position="relative" mb={4}>
            <Box
                position="absolute"
                left="3"
                top="50%"
                transform="translateY(-50%)"
                zIndex="1"
                pointerEvents="none"
            >
                <LuSearch color="gray" />
            </Box>
            <Input
                placeholder="Search chats..."
                bg="white"
                paddingLeft="10"
                borderRadius="md"
                border="1px solid"
                borderColor="gray.200"
            />
        </Box>
    );
};
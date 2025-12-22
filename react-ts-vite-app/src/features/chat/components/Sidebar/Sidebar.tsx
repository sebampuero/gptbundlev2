import { Box, VStack, Heading, Button, IconButton, HStack, Input } from "@chakra-ui/react";
import { LuChevronDown, LuSearch } from "react-icons/lu";

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

export const Sidebar = () => {
    return (
        <Box
            width="300px"
            height="100vh"
            borderRight="1px solid"
            borderColor="gray.200"
            bg="white"
            p={4}
            display="flex"
            flexDirection="column"
        >
            <Heading size="md" mb={4}>
                Chats
            </Heading>
            <SearchField />
            <VStack align="stretch" gap={0} flex={1} overflowY="auto">
                {/* Empty sidepanel as requested */}
            </VStack>
            <Button
                variant="ghost"
                width="full"
                justifyContent="space-between"
                size="sm"
                mt={4}
                fontWeight="normal"
                color="gray.600"
            >
                More
                <LuChevronDown size={14} />
            </Button>
        </Box>
    );
};

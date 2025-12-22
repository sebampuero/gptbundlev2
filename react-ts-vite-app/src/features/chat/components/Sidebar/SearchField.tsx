import { Input, InputGroup, InputLeftElement } from "@chakra-ui/react";
import { LuSearch } from "react-icons/lu";

export const SearchField = () => {
    return (
        <InputGroup size="md" mb={4}>
            <InputLeftElement pointerEvents="none">
                <LuSearch color="gray.300" />
            </InputLeftElement>
            <Input
                placeholder="Search chats..."
                bg="white"
                _placeholder={{ color: "gray.400" }}
                borderRadius="md"
                border="1px solid"
                borderColor="gray.200"
            />
        </InputGroup>
    );
};

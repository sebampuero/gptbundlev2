import { Box, Input } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { LuSearch } from "react-icons/lu";
import { useDebounce } from "../../hooks/useDebounce";

interface SearchFieldProps {
    onSearch: (searchTerm: string) => void;
}

export const SearchField = ({ onSearch }: SearchFieldProps) => {
    const [inputValue, setInputValue] = useState("");
    const debouncedSearchTerm = useDebounce(inputValue, 500);

    useEffect(() => {
        onSearch(debouncedSearchTerm);
    }, [debouncedSearchTerm, onSearch]);

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
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
            />
        </Box>
    );
};
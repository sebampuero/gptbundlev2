import {
    Box,
    Button,
    Field,
    Input,
    VStack,
    Heading,
    Text,
    Link as ChakraLink,
    Container,
} from '@chakra-ui/react';
import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { authService } from '../services/authService';
import { useAuth } from '../../../context/AuthContext';

export const LoginForm: React.FC = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const { setUser } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        try {
            const user = await authService.login({ username, password });
            setUser({ email: user.email, username: user.username });
            navigate('/chat');
        } catch (err: any) {
            setError(err.message || 'Check your credentials and try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Container maxW="lg" centerContent py={10}>
            <Box
                w="full"
                maxW="md"
                bg="white"
                p={8}
                borderRadius="lg"
                boxShadow="lg"
                border="1px"
                borderColor="gray.100"
                as="form"
                onSubmit={handleSubmit}
            >
                <VStack gap={6} align="stretch">
                    <Heading as="h2" size="xl" textAlign="center" mb={4} fontWeight="bold">
                        Login
                    </Heading>

                    {error && (
                        <Text color="red.500" fontSize="sm" textAlign="center">
                            {error}
                        </Text>
                    )}

                    <Field.Root>
                        <Field.Label fontSize="sm" color="gray.600">Username</Field.Label>
                        <Input
                            type="text"
                            placeholder="Enter username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </Field.Root>

                    <Field.Root>
                        <Field.Label fontSize="sm" color="gray.600">Password</Field.Label>
                        <Input
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </Field.Root>

                    <Button
                        colorPalette="blue"
                        size="lg"
                        width="full"
                        mt={4}
                        type="submit"
                        loading={isLoading}
                    >
                        Login
                    </Button>

                    <Text textAlign="center" fontSize="sm" color="gray.500">
                        Don't have an account?{' '}
                        <ChakraLink color="blue.500" fontWeight="semibold">
                            <RouterLink to="/register">Register</RouterLink>
                        </ChakraLink>
                    </Text>
                </VStack>
            </Box>
        </Container>
    );
};
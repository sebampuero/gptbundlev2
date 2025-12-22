import {
    Box,
    Button,
    Field,
    Input,
    VStack,
    Heading,
    Text,
    Link,
    Container,
} from '@chakra-ui/react';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';

export const RegisterForm: React.FC = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        try {
            await authService.register({ username, email, password });
            navigate('/login');
        } catch (err: any) {
            setError(err.message || 'Registration failed. Please try again.');
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
                        Create Account
                    </Heading>

                    {error && (
                        <Text color="red.500" fontSize="sm" textAlign="center">
                            {error}
                        </Text>
                    )}

                    {/* Username Field */}
                    <Field.Root>
                        <Field.Label fontSize="sm" color="gray.600">Username</Field.Label>
                        <Input
                            type="text"
                            placeholder="Choose a username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </Field.Root>

                    {/* Email Field */}
                    <Field.Root>
                        <Field.Label fontSize="sm" color="gray.600">Email address</Field.Label>
                        <Input
                            type="email"
                            placeholder="Enter email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </Field.Root>

                    {/* Password Field */}
                    <Field.Root>
                        <Field.Label fontSize="sm" color="gray.600">Password</Field.Label>
                        <Input
                            type="password"
                            placeholder="Create password"
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
                        Sign Up
                    </Button>

                    <Text textAlign="center" fontSize="sm" color="gray.500">
                        Already have an account?{' '}
                        <Link color="blue.500" fontWeight="semibold" href="/login">
                            Login
                        </Link>
                    </Text>
                </VStack>
            </Box>
        </Container>
    );
};
import React from 'react';
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

export const RegisterForm: React.FC = () => {
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
            >
                <VStack gap={6} align="stretch">
                    <Heading as="h2" size="xl" textAlign="center" mb={4} fontWeight="bold">
                        Create Account
                    </Heading>

                    {/* Username Field */}
                    <Field.Root>
                        <Field.Label fontSize="sm" color="gray.600">Username</Field.Label>
                        <Input
                            type="text"
                            placeholder="Choose a username"
                        />
                    </Field.Root>

                    {/* Email Field */}
                    <Field.Root>
                        <Field.Label fontSize="sm" color="gray.600">Email address</Field.Label>
                        <Input
                            type="email"
                            placeholder="Enter email"
                        />
                    </Field.Root>

                    {/* Password Field */}
                    <Field.Root>
                        <Field.Label fontSize="sm" color="gray.600">Password</Field.Label>
                        <Input
                            type="password"
                            placeholder="Create password"
                        />
                    </Field.Root>

                    <Button
                        colorPalette="blue"
                        size="lg"
                        width="full"
                        mt={4}
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
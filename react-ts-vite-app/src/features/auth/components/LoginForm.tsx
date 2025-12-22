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

export const LoginForm: React.FC = () => {
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
                        Login
                    </Heading>

                    <Field.Root>
                        <Field.Label fontSize="sm" color="gray.600">Email address</Field.Label>
                        <Input
                            type="email"
                            placeholder="Enter email"
                        />
                    </Field.Root>

                    <Field.Root>
                        <Field.Label fontSize="sm" color="gray.600">Password</Field.Label>
                        <Input
                            type="password"
                            placeholder="Password"
                        />
                    </Field.Root>

                    <Button
                        colorPalette="blue"
                        size="lg"
                        width="full"
                        mt={4}
                    >
                        Login
                    </Button>

                    <Text textAlign="center" fontSize="sm" color="gray.500">
                        Don't have an account?{' '}
                        <Link color="blue.500" fontWeight="semibold" href="/register">
                            Register
                        </Link>
                    </Text>
                </VStack>
            </Box>
        </Container>
    );
};
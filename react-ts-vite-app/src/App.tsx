import { Flex } from '@chakra-ui/react';
import { LoginForm } from './features/auth/components/LoginForm';

function App() {
  return (
    <Flex minH="100vh" align="center" justify="center" bg="gray.50">
      <LoginForm />
    </Flex>
  );
}

export default App;
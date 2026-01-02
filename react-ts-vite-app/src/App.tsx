import { Flex } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ChatPage } from './pages/ChatPage';

import { ModelProvider } from './context/ModelContext';
import { AuthProvider } from './context/AuthContext';
import { ProtectedPage } from './features/auth/components/ProtectedPage';

function App() {
  return (
    <ModelProvider>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={
              <Flex minH="100vh" w="100%" align="center" justify="center" bg="gray.50">
                <LoginPage />
              </Flex>
            } />
            <Route path="/register" element={
              <Flex minH="100vh" w="100%" align="center" justify="center" bg="gray.50">
                <RegisterPage />
              </Flex>
            } />
            <Route path="/chat/:chatId?/:timestamp?" element={
              <ProtectedPage>
                <ChatPage />
              </ProtectedPage>
            } />
            <Route path="/" element={<Navigate to="/login" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ModelProvider>
  );
}

export default App;
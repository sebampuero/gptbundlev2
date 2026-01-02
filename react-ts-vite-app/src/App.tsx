import { Flex } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ChatPage } from './pages/ChatPage';

import { ModelProvider } from './context/ModelContext';

function App() {
  return (
    <ModelProvider>
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
          <Route path="/chat/:chatId?/:timestamp?" element={<ChatPage />} />
          <Route path="/" element={<Navigate to="/chat" replace />} />
        </Routes>
      </Router>
    </ModelProvider>
  );
}

export default App;
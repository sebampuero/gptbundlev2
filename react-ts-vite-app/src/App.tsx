import { Flex } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ChatPage } from './pages/ChatPage';

function App() {
  return (
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
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
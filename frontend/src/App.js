import React from 'react';
import { ChakraProvider, Box, VStack, Heading, Text, useColorModeValue } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';

import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import ModelHub from './pages/ModelHub';
import TrainingStudio from './pages/TrainingStudio';
import RunDetails from './pages/RunDetails';
import DatasetStudio from './pages/DatasetStudio';

// Create a client
const queryClient = new QueryClient();

function App() {
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const textColor = useColorModeValue('gray.800', 'gray.200');

  return (
    <QueryClientProvider client={queryClient}>
      <ChakraProvider>
        <Box bg={bgColor} minH="100vh" color={textColor}>
          <Router>
            <Navbar />
            <Box as="main" pt="80px" px={4}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/models" element={<ModelHub />} />
                <Route path="/training" element={<TrainingStudio />} />
                <Route path="/training/runs/:runId" element={<RunDetails />} />
                <Route path="/datasets" element={<DatasetStudio />} />
              </Routes>
            </Box>
          </Router>
        </Box>
      </ChakraProvider>
    </QueryClientProvider>
  );
}

export default App;
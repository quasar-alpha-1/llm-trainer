import React from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  VStack,
  HStack,
  Button,
  Card,
  CardBody,
  CardHeader,
  useColorModeValue,
  Badge,
  Progress,
} from '@chakra-ui/react';
import { useQuery } from 'react-query';
import { Link as RouterLink } from 'react-router-dom';
import { AddIcon, ViewIcon, SettingsIcon } from '@chakra-ui/icons';
import axios from 'axios';

const StatCard = ({ label, value, helpText, arrow, color }) => (
  <Card>
    <CardBody>
      <Stat>
        <StatLabel>{label}</StatLabel>
        <StatNumber color={color}>{value}</StatNumber>
        <StatHelpText>
          <StatArrow type={arrow} />
          {helpText}
        </StatHelpText>
      </Stat>
    </CardBody>
  </Card>
);

const QuickActionCard = ({ title, description, icon, link, color }) => (
  <Card>
    <CardHeader>
      <HStack>
        {icon}
        <Heading size="md">{title}</Heading>
      </HStack>
    </CardHeader>
    <CardBody>
      <VStack align="start" spacing={4}>
        <Text>{description}</Text>
        <Button
          as={RouterLink}
          to={link}
          colorScheme={color}
          leftIcon={<AddIcon />}
          size="sm"
        >
          Get Started
        </Button>
      </VStack>
    </CardBody>
  </Card>
);

const RecentRunCard = ({ run }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'green';
      case 'running': return 'blue';
      case 'failed': return 'red';
      case 'pending': return 'yellow';
      default: return 'gray';
    }
  };

  return (
    <Card>
      <CardBody>
        <VStack align="start" spacing={2}>
          <HStack justify="space-between" w="full">
            <Text fontWeight="bold" fontSize="sm">
              {run.model_id}
            </Text>
            <Badge colorScheme={getStatusColor(run.status)}>
              {run.status}
            </Badge>
          </HStack>
          <Text fontSize="xs" color="gray.500">
            Started: {new Date(run.created_at).toLocaleDateString()}
          </Text>
          {run.status === 'running' && (
            <Progress size="sm" isIndeterminate colorScheme="blue" w="full" />
          )}
          <Button
            as={RouterLink}
            to={`/training/runs/${run.run_id}`}
            size="xs"
            leftIcon={<ViewIcon />}
            variant="outline"
          >
            View Details
          </Button>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default function Dashboard() {
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const cardBg = useColorModeValue('white', 'gray.800');

  // Mock data - replace with actual API calls
  const { data: stats } = useQuery('dashboard-stats', async () => {
    // In production, this would be an API call
    return {
      totalRuns: 24,
      activeRuns: 3,
      completedRuns: 18,
      successRate: 85,
    };
  });

  const { data: recentRuns } = useQuery('recent-runs', async () => {
    // In production, this would be an API call
    return [
      {
        run_id: 'run-1',
        model_id: 'unsloth/gemma-3-1b-it',
        status: 'completed',
        created_at: '2024-01-15T10:30:00Z',
      },
      {
        run_id: 'run-2',
        model_id: 'unsloth/llama-3.2-3b-instruct',
        status: 'running',
        created_at: '2024-01-15T11:00:00Z',
      },
      {
        run_id: 'run-3',
        model_id: 'unsloth/qwen2.5-4b-instruct',
        status: 'failed',
        created_at: '2024-01-15T09:15:00Z',
      },
    ];
  });

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg" mb={2}>
            Welcome to Train-Your-Own-LLM Platform
          </Heading>
          <Text color="gray.600">
            Production-grade platform for fine-tuning Large Language Models using Unsloth GRPO
          </Text>
        </Box>

        {/* Stats */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
          <StatCard
            label="Total Training Runs"
            value={stats?.totalRuns || 0}
            helpText="All time"
            arrow="increase"
            color="blue.500"
          />
          <StatCard
            label="Active Runs"
            value={stats?.activeRuns || 0}
            helpText="Currently running"
            arrow="increase"
            color="green.500"
          />
          <StatCard
            label="Completed Runs"
            value={stats?.completedRuns || 0}
            helpText="Successfully finished"
            arrow="increase"
            color="purple.500"
          />
          <StatCard
            label="Success Rate"
            value={`${stats?.successRate || 0}%`}
            helpText="Last 30 days"
            arrow="increase"
            color="orange.500"
          />
        </SimpleGrid>

        {/* Quick Actions */}
        <Box>
          <Heading size="md" mb={4}>
            Quick Actions
          </Heading>
          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
            <QuickActionCard
              title="Start Training"
              description="Begin a new GRPO training run with your chosen model and dataset"
              icon={<AddIcon />}
              link="/training"
              color="blue"
            />
            <QuickActionCard
              title="Browse Models"
              description="Explore available models from Hugging Face Hub"
              icon={<ViewIcon />}
              link="/models"
              color="green"
            />
            <QuickActionCard
              title="Upload Dataset"
              description="Upload your custom dataset or browse existing ones"
              icon={<SettingsIcon />}
              link="/datasets"
              color="purple"
            />
          </SimpleGrid>
        </Box>

        {/* Recent Runs */}
        <Box>
          <HStack justify="space-between" mb={4}>
            <Heading size="md">Recent Training Runs</Heading>
            <Button
              as={RouterLink}
              to="/training"
              size="sm"
              variant="outline"
            >
              View All
            </Button>
          </HStack>
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
            {recentRuns?.map((run) => (
              <RecentRunCard key={run.run_id} run={run} />
            ))}
          </SimpleGrid>
        </Box>

        {/* Platform Features */}
        <Box>
          <Heading size="md" mb={4}>
            Platform Features
          </Heading>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
            <Card bg={cardBg}>
              <CardBody>
                <VStack align="start" spacing={3}>
                  <Heading size="sm">🤖 AI Agent Co-pilot</Heading>
                  <Text fontSize="sm">
                    Intelligent agent that auto-detects dataset schemas, suggests optimal hyperparameters, 
                    and flags GPU memory limits to ensure successful training runs.
                  </Text>
                </VStack>
              </CardBody>
            </Card>
            <Card bg={cardBg}>
              <CardBody>
                <VStack align="start" spacing={3}>
                  <Heading size="sm">📊 Live Monitoring</Heading>
                  <Text fontSize="sm">
                    Real-time training metrics, reward charts, and GPU utilization monitoring 
                    to track your model's progress and performance.
                  </Text>
                </VStack>
              </CardBody>
            </Card>
            <Card bg={cardBg}>
              <CardBody>
                <VStack align="start" spacing={3}>
                  <Heading size="sm">🚀 One-Click Deployment</Heading>
                  <Text fontSize="sm">
                    Export your trained models to Hugging Face, GGUF, Ollama, or vLLM server 
                    with just a single click.
                  </Text>
                </VStack>
              </CardBody>
            </Card>
            <Card bg={cardBg}>
              <CardBody>
                <VStack align="start" spacing={3}>
                  <Heading size="sm">🔒 Enterprise Security</Heading>
                  <Text fontSize="sm">
                    Role-based access control, audit logging, and secure sandboxed execution 
                    for enterprise-grade security and compliance.
                  </Text>
                </VStack>
              </CardBody>
            </Card>
          </SimpleGrid>
        </Box>
      </VStack>
    </Container>
  );
}
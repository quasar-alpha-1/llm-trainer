import React from 'react';
import {
  Box,
  Flex,
  Text,
  Button,
  Stack,
  Link,
  useColorModeValue,
  useDisclosure,
  IconButton,
  HStack,
  VStack,
  CloseButton,
} from '@chakra-ui/react';
import { HamburgerIcon, CloseIcon } from '@chakra-ui/icons';
import { Link as RouterLink, useLocation } from 'react-router-dom';

const NavLink = ({ children, to }) => {
  const location = useLocation();
  const isActive = location.pathname === to;
  
  return (
    <Link
      as={RouterLink}
      px={2}
      py={1}
      rounded={'md'}
      _hover={{
        textDecoration: 'none',
        bg: useColorModeValue('gray.200', 'gray.700'),
      }}
      bg={isActive ? useColorModeValue('blue.100', 'blue.900') : 'transparent'}
      color={isActive ? useColorModeValue('blue.800', 'blue.200') : 'inherit'}
      to={to}
    >
      {children}
    </Link>
  );
};

export default function Navbar() {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const bg = useColorModeValue('white', 'gray.800');
  const color = useColorModeValue('gray.600', 'gray.200');

  return (
    <>
      <Box bg={bg} px={4} boxShadow={'sm'} position="fixed" top={0} left={0} right={0} zIndex={1000}>
        <Flex h={16} alignItems={'center'} justifyContent={'space-between'}>
          <IconButton
            size={'md'}
            icon={isOpen ? <CloseIcon /> : <HamburgerIcon />}
            aria-label={'Open Menu'}
            display={{ md: 'none' }}
            onClick={isOpen ? onClose : onOpen}
          />

          <HStack spacing={8} alignItems={'center'}>
            <Box>
              <Text fontSize="lg" fontWeight="bold" color={useColorModeValue('blue.600', 'blue.400')}>
                🚀 Train-Your-Own-LLM
              </Text>
            </Box>
            <HStack as={'nav'} spacing={4} display={{ base: 'none', md: 'flex' }}>
              <NavLink to="/">Dashboard</NavLink>
              <NavLink to="/models">Model Hub</NavLink>
              <NavLink to="/training">Training Studio</NavLink>
              <NavLink to="/datasets">Dataset Studio</NavLink>
            </HStack>
          </HStack>

          <Flex alignItems={'center'}>
            <Stack
              flex={{ base: 1, md: 0 }}
              justify={'flex-end'}
              direction={'row'}
              spacing={6}>
              <Button
                as={'a'}
                fontSize={'sm'}
                fontWeight={400}
                variant={'link'}
                href={'#'}>
                Sign In
              </Button>
              <Button
                display={{ base: 'none', md: 'inline-flex' }}
                fontSize={'sm'}
                fontWeight={600}
                color={'white'}
                bg={'blue.400'}
                href={'#'}
                _hover={{
                  bg: 'blue.300',
                }}>
                Sign Up
              </Button>
            </Stack>
          </Flex>
        </Flex>

        {isOpen ? (
          <Box pb={4} display={{ md: 'none' }}>
            <Stack as={'nav'} spacing={4}>
              <NavLink to="/">Dashboard</NavLink>
              <NavLink to="/models">Model Hub</NavLink>
              <NavLink to="/training">Training Studio</NavLink>
              <NavLink to="/datasets">Dataset Studio</NavLink>
            </Stack>
          </Box>
        ) : null}
      </Box>
    </>
  );
}
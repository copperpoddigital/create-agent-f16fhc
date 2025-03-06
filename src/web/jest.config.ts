import type { Config } from '@jest/types';

// Jest configuration for the Freight Price Movement Agent web frontend
const config: Config.InitialOptions = {
  // Use the TypeScript preset for Jest
  preset: 'ts-jest',
  
  // Use jsdom to simulate a browser environment for DOM testing
  testEnvironment: 'jsdom',
  
  // Set up files to run after the Jest environment is set up
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  
  // Define where Jest should look for test files
  roots: ['<rootDir>/src', '<rootDir>/tests'],
  
  // Patterns to detect test files
  testMatch: [
    '**/__tests__/**/*.+(ts|tsx|js)',
    '**/?(*.)+(spec|test).+(ts|tsx|js)'
  ],
  
  // Configure transformers for different file types
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest',
    '^.+\\.(js|jsx)$': 'babel-jest',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
  },
  
  // Module name mapper for path aliases and non-JS modules
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|webp|svg)$': '<rootDir>/tests/mocks/fileMock.js'
  },
  
  // Files to include in coverage reporting
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.tsx',
    '!src/reportWebVitals.ts'
  ],
  
  // Coverage thresholds to enforce
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 85,
      statements: 85
    }
  },
  
  // Plugins for watch mode
  watchPlugins: [
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname'
  ],
  
  // Reset mocks before each test
  resetMocks: true,
  
  // Timeout for each test (in milliseconds)
  testTimeout: 10000,
  
  // Enable verbose output
  verbose: true,
  
  // TypeScript-specific settings
  globals: {
    'ts-jest': {
      tsconfig: '<rootDir>/tsconfig.json',
      isolatedModules: true
    }
  }
};

export default config;
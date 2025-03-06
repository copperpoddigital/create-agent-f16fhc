module.exports = {
  root: true,
  parser: '@typescript-eslint/parser', // ESLint parser for TypeScript v5.59.0
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
    project: './tsconfig.json',
  },
  env: {
    browser: true,
    node: true,
    es6: true,
    jest: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended', 
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'plugin:jsx-a11y/recommended',
    'plugin:import/errors',
    'plugin:import/warnings',
    'plugin:import/typescript',
    'prettier', // Make sure this is last to override other configs
  ],
  plugins: [
    '@typescript-eslint', // ESLint plugin for TypeScript v5.59.0
    'react', // React specific linting rules v7.32.2
    'react-hooks', // React hooks linting rules v4.6.0
    'jsx-a11y', // Accessibility linting rules for JSX v6.7.1
    'import', // Import/export syntax linting v2.27.5
  ],
  settings: {
    react: {
      version: 'detect', // Auto-detect React version
    },
    'import/resolver': {
      typescript: {
        alwaysTryTypes: true,
        project: './tsconfig.json',
      },
    },
  },
  rules: {
    // General rules
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    
    // TypeScript rules
    'no-unused-vars': 'off', // Disable base rule
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-explicit-any': 'warn',
    
    // React rules
    'react/prop-types': 'off', // Using TypeScript for props validation
    'react/react-in-jsx-scope': 'off', // Not needed with newer React versions
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',
    
    // Import rules
    'import/order': [
      'error',
      {
        groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
        'newlines-between': 'always',
        alphabetize: {
          order: 'asc',
          caseInsensitive: true,
        },
      },
    ],
  },
  overrides: [
    {
      // Less strict rules for test files
      files: ['**/*.test.ts', '**/*.test.tsx', '**/*.spec.ts', '**/*.spec.tsx'],
      env: {
        jest: true,
      },
      rules: {
        '@typescript-eslint/no-explicit-any': 'off', // Allow 'any' in tests for flexibility
      },
    },
  ],
};
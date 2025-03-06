/**
 * Babel configuration file for the Freight Price Movement Agent web frontend.
 * This config enables modern JavaScript features, React JSX support, and TypeScript.
 * 
 * @babel/core: ^7.21.4
 * @babel/preset-env: ^7.21.4
 * @babel/preset-react: ^7.18.6
 * @babel/preset-typescript: ^7.21.4
 * @babel/plugin-transform-runtime: ^7.21.4
 */

module.exports = {
  presets: [
    [
      '@babel/preset-env',
      {
        // Target browsers with >0.2% market share, excluding dead browsers and Opera Mini
        targets: {
          browsers: ['>0.2%', 'not dead', 'not op_mini all']
        },
        // Add polyfills based on actual usage
        useBuiltIns: 'usage',
        corejs: 3
      }
    ],
    // React preset with automatic runtime (new JSX transform)
    ['@babel/preset-react', { runtime: 'automatic' }],
    // TypeScript preset with support for TSX files
    ['@babel/preset-typescript', { isTSX: true, allExtensions: true }]
  ],
  plugins: [
    // Transform runtime for helpers and built-ins
    ['@babel/plugin-transform-runtime', { regenerator: true }]
  ],
  env: {
    // Jest testing environment configuration
    test: {
      presets: [
        ['@babel/preset-env', { targets: { node: 'current' } }]
      ]
    },
    // Production build optimizations
    production: {
      // Note: Requires installing the 'babel-plugin-transform-react-remove-prop-types' package
      plugins: ['transform-react-remove-prop-types']
    }
  }
};
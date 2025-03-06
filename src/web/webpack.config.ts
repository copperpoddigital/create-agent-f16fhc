import path from 'path'; // v18.16.0
import { Configuration } from 'webpack'; // v5.88.2
import HtmlWebpackPlugin from 'html-webpack-plugin'; // v5.5.3
import MiniCssExtractPlugin from 'mini-css-extract-plugin'; // v2.7.6
import TerserPlugin from 'terser-webpack-plugin'; // v5.3.9
import CssMinimizerPlugin from 'css-minimizer-webpack-plugin'; // v5.0.1
import ForkTsCheckerWebpackPlugin from 'fork-ts-checker-webpack-plugin'; // v8.0.0
import Dotenv from 'dotenv-webpack'; // v8.0.1

/**
 * Webpack configuration function that generates the configuration based on the environment
 * This serves as a fallback build system, while Vite is the primary build tool
 */
const webpackConfig = (env: any, argv: any): Configuration => {
  const isProduction = process.env.NODE_ENV === 'production';
  
  return {
    // Set mode based on environment
    mode: isProduction ? 'production' : 'development',
    
    // Main entry point for the application
    entry: './src/index.tsx',
    
    // Output configuration
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: 'js/[name].[contenthash:8].js',
      chunkFilename: 'js/[name].[contenthash:8].chunk.js',
      publicPath: '/',
    },
    
    // Module rules for different file types
    module: {
      rules: [
        // TypeScript and TSX files
        {
          test: /\.(ts|tsx)$/,
          exclude: /node_modules/,
          use: [
            {
              loader: 'ts-loader',
              options: {
                transpileOnly: true, // Speed up compilation, type checking is done by ForkTsCheckerWebpackPlugin
              },
            },
          ],
        },
        // CSS files
        {
          test: /\.css$/,
          use: [
            MiniCssExtractPlugin.loader,
            'css-loader',
            'postcss-loader',
          ],
        },
        // Image files
        {
          test: /\.(png|jpg|jpeg|gif)$/i,
          type: 'asset/resource',
          generator: {
            filename: 'images/[name].[hash:8][ext]',
          },
        },
        // SVG files - allow both component and URL imports
        {
          test: /\.svg$/,
          use: ['@svgr/webpack', 'url-loader'],
        },
        // Font files
        {
          test: /\.(woff|woff2|eot|ttf|otf)$/i,
          type: 'asset/resource',
          generator: {
            filename: 'fonts/[name].[hash:8][ext]',
          },
        },
      ],
    },
    
    // Module resolution configuration
    resolve: {
      extensions: ['.tsx', '.ts', '.js', '.jsx', '.json'],
      alias: {
        '@': path.resolve(__dirname, 'src'), // Allow imports using @ to point to src directory
      },
    },
    
    // Plugins configuration
    plugins: [
      // Generate HTML file that includes all webpack bundles
      new HtmlWebpackPlugin({
        template: './public/index.html',
        favicon: './public/favicon.ico',
      }),
      
      // Extract CSS into separate files
      new MiniCssExtractPlugin({
        filename: 'css/[name].[contenthash:8].css',
        chunkFilename: 'css/[name].[contenthash:8].chunk.css',
      }),
      
      // Run TypeScript type checking in a separate process
      new ForkTsCheckerWebpackPlugin({
        typescript: {
          configFile: './tsconfig.json',
        },
      }),
      
      // Load environment variables from .env files
      new Dotenv({
        path: `./.env.${process.env.NODE_ENV}`,
      }),
    ],
    
    // Optimization configuration
    optimization: {
      minimizer: [
        // Minify JavaScript
        new TerserPlugin({
          terserOptions: {
            compress: {
              drop_console: true, // Remove console.log in production
            },
          },
        }),
        // Minify CSS
        new CssMinimizerPlugin(),
      ],
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          // Group vendor modules into separate chunks
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
          // Create separate chunk for chart libraries
          charts: {
            test: /[\\/]node_modules[\\/](chart\.js|react-chartjs-2)[\\/]/,
            name: 'charts',
            chunks: 'all',
          },
        },
      },
      runtimeChunk: 'single', // Create a single runtime chunk
    },
    
    // Development server configuration
    devServer: {
      historyApiFallback: true, // Support for React Router
      port: 3000,
      open: true, // Open browser when server starts
      hot: true, // Enable hot module replacement
      proxy: {
        '/api': {
          target: 'http://localhost:8000', // Proxy API requests to backend
          changeOrigin: true,
          secure: false,
        },
      },
    },
    
    // Source map configuration
    devtool: isProduction ? 'source-map' : 'eval-source-map',
    
    // Stats configuration to reduce output verbosity
    stats: {
      modules: false,
      children: false,
      chunks: false,
      chunkModules: false,
    },
    
    // Performance hints configuration
    performance: {
      hints: isProduction ? 'warning' : false,
      maxAssetSize: 512000, // 500KB
      maxEntrypointSize: 512000, // 500KB
    },
  };
};

export default webpackConfig;
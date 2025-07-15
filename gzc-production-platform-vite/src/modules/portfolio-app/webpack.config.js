const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { ModuleFederationPlugin } = require('webpack').container;
const deps = require('../../package.json').dependencies;

module.exports = {
  entry: './index.tsx',
  mode: 'development',
  
  devServer: {
    port: 3201,
    historyApiFallback: true,
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  },

  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].[contenthash].js',
    clean: true,
    publicPath: 'auto',
  },

  resolve: {
    extensions: ['.tsx', '.ts', '.js', '.jsx'],
    alias: {
      '@': path.resolve(__dirname, '../..'),
      '@gzc/ui': path.resolve(__dirname, '../../shared/gzc-ui'),
    },
  },

  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [
              '@babel/preset-env',
              ['@babel/preset-react', { runtime: 'automatic' }],
              '@babel/preset-typescript',
            ],
          },
        },
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader', 'postcss-loader'],
      },
    ],
  },

  plugins: [
    new HtmlWebpackPlugin({
      template: path.resolve(__dirname, '../../index.html'),
      title: 'Portfolio App',
    }),
    
    new ModuleFederationPlugin({
      name: 'gzc_portfolio_app',
      filename: 'remoteEntry.js',
      exposes: {
        './PortfolioApp': './App',
        './PortfolioTable': './components/PortfolioTable',
        './BlotterTable': './components/BlotterTable',
      },
      shared: {
        react: { singleton: true, requiredVersion: deps.react, eager: true },
        'react-dom': { singleton: true, requiredVersion: deps['react-dom'], eager: true },
        '@azure/msal-browser': { singleton: true, requiredVersion: deps['@azure/msal-browser'] },
        '@azure/msal-react': { singleton: true, requiredVersion: deps['@azure/msal-react'] },
        '@tanstack/react-query': { singleton: true, eager: false },
        '@tanstack/react-table': { singleton: true, eager: false },
        'alova': { singleton: true, requiredVersion: deps.alova },
        '@gzc/ui': { singleton: true, requiredVersion: '1.0.0' },
      },
    }),
  ],
};
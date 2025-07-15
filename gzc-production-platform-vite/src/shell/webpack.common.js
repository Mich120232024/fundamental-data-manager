//gzc-main-shell\webpack.common.js
const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const ModuleFederationPlugin = require("webpack/lib/container/ModuleFederationPlugin");
const dotenv = require("dotenv");
const fs = require("fs");
const webpack = require("webpack");
// Load environment variables
const envFile = path.resolve(__dirname, "./.env");
const env = dotenv.parse(fs.readFileSync(envFile));
const envKeys = Object.keys(env).reduce((prev, next) => {
    prev[`process.env.${next}`] = JSON.stringify(env[next]);
    return prev;
}, {});
const deps = require("./package.json").dependencies; // ADDED
const gzcContextPath = (file) => `@/context/${file}`;
const gzcHookPath = (file) => `@/hooks/${file}`;

module.exports = {
    entry: "./src/index.tsx",
    output: {
        publicPath: "auto",
        path: path.resolve(__dirname, "dist"),
        filename: "[name].[contenthash].js",
        clean: true,
    },
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "src"),
        },
        extensions: [".tsx", ".ts", ".js"],
    },
    module: {
        rules: [
            {
                test: /\.(ts|tsx|js|jsx)$/,
                exclude: /node_modules/,
                use: "babel-loader",
            },
            {
                test: /\.css$/i,
                use: [
                    MiniCssExtractPlugin.loader,
                    "css-loader",
                    "postcss-loader",
                ],
            },
        ],
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: "./public/index.html",
        }),
        new MiniCssExtractPlugin(),
        new webpack.DefinePlugin({
            ...envKeys,
            "process.env.SHELL_CONTEXT": JSON.stringify(true),
        }), // ensures process.env is available in bundled code
        new ModuleFederationPlugin({
            name: "gzc_main_shell",
            filename: "remoteEntry.js",
            remotes: {
                gzc_portfolio_app:
                    "gzc_portfolio_app@http://localhost:3001/remoteEntry.js",
            },
            shared: {
                react: {
                    singleton: true,
                    requiredVersion: deps.react, // CHANGED
                },
                "react-dom": {
                    singleton: true,
                    requiredVersion: deps["react-dom"], // CHANGED
                },
                "@gzc/ui": {
                    singleton: true,
                    requiredVersion: deps["@gzc/ui"], // CHANGED
                },
            },
        }),
    ],
};

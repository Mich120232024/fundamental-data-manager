const { merge } = require("webpack-merge");
const common = require("./webpack.common.js");
const path = require("path");

module.exports = merge(common, {
    mode: "development",
    devtool: "eval-source-map",
    devServer: {
        static: {
            directory: path.resolve(__dirname, "dist"),
        },
        port: 3000,
        historyApiFallback: true,
        hot: true,
        allowedHosts: "all", // useful for LAN development
        headers: {
            "Access-Control-Allow-Origin": "*",
        },
    },
    output: {
        publicPath: "auto",
        filename: "[name].[contenthash].js",
        chunkFilename: "[id].[contenthash].js",
        clean: true,
        
    },
});

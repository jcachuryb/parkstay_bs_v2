var Webpack = require("webpack");
const merge = require("webpack-merge");
const common = require("./webpack.common.js");

var config = require("../config");
const HtmlWebpackPlugin = require("html-webpack-plugin");

module.exports = merge(common, {
  mode: "development",
  devtool: "inline-source-map",
  devServer: {
    static: "../dist",
    open: true,
    hot: true,
    port: config.dev.port,
  },
  plugins: [
    new HtmlWebpackPlugin({
      filename: "index.html",
      template: "index.html",
      inject: true,
    }),
    new Webpack.DefinePlugin({
      "process.env": config.dev.env,
    }),
  ],
  stats: {
    entrypoints: false,
    children: false,
    colors: true,
  },
});

require("./check-versions")();
var Webpack = require("webpack");
const merge = require("webpack-merge");

const config = require("../config");
const common = require("./webpack.common.js");

module.exports = merge(common, {
  mode: "production",
  output: {
    path: config.build.assetsRoot,
    filename: "[name].js",
    publicPath: config.build.assetsPublicPath,
  },
  optimization: {
    splitChunks: {
      cacheGroups: {
        vendor: {
          test: /node_modules/,
          name: "vendor",
          chunks: "initial",
          enforce: true,
        },
      },
    },
  },
  plugins: [
    new Webpack.DefinePlugin({
      "process.env": config.dev.env,
    }),
  ],
});

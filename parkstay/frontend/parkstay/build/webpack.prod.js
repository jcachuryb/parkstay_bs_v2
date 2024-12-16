require("./check-versions")();
const Webpack = require("webpack");
const webpackMerge = require('webpack-merge')

const { merge } = webpackMerge
const config = require("../config");
const common = require("./webpack.common.js");

module.exports = merge(common, {
  mode: "production",
  output: {
    path: config.build.assetsRoot,
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

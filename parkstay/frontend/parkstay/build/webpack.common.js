const webpack = require("webpack");
const path = require("path");
const utils = require("./utils");

const VueLoaderPlugin = require("vue-loader/lib/plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

const environment = (process.env.NODE_ENV || "development").trim();
const isDev = environment === "development";

const resolve = utils.resolveFromRoot;

module.exports = {
  entry: {
    parkstay: "./src/apps/main.js",
  },
  plugins: [
    new VueLoaderPlugin(),
    new MiniCssExtractPlugin(),
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery",
      "window.jQuery": "jquery",
    }),
  ],
  output: {
    filename: "[name].js",
    path: path.resolve(__dirname, "dist"),
  },
  devtool: isDev ? "eval-source-map" : "source-map",
  stats: {
    children: false,
    entrypoints: false,
    colors: true,
  },
  resolve: {
    extensions: [".js", ".vue", ".json"],
    modules: [resolve("src"), resolve("node_modules")],
    alias: {
      vue$: "vue/dist/vue.common.js",
      src: resolve("src"),
      assets: resolve("src/assets"),
      components: resolve("src/components"),
    },
  },
  module: {
    rules: [
      {
        test: /\.vue$/,
        loader: "vue-loader",
      },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        loader: "babel-loader",
        options: {
          presets: [["@babel/preset-env", { targets: "defaults" }]],
        },
      },
      {
        test: /\.(png|jpe?g|gif|svg)(\?.*)?$/i,
        loader: "url-loader",
        query: {
          limit: 10000,
          name: utils.assetsPath("img/[name].[ext]"),
        },
      },
      {
        test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/i,
        loader: "url-loader",
        query: {
          limit: 100000,
          name: utils.assetsPath("fonts/[name].[ext]"),
        },
      },
      {
        test: /\.css$/,
        use: isDev
          ? ["vue-style-loader", "css-loader"]
          : [
              {
                loader: MiniCssExtractPlugin.loader,
                options: {
                  esModule: false,
                },
              },
              "css-loader",
            ],
      },
    ],
  },
};

import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";
import vueDevTools from "vite-plugin-vue-devtools";
import inject from "@rollup/plugin-inject";

import path from "path";
// import eslint from 'vite-plugin-eslint2';
import svgLoader from "vite-svg-loader";
import conf from "./config";

import $ from 'jquery'

const applicationNameShort = "parkstay";
const port = process.env.PORT ? parseInt(process.env.PORT) : 9092;
const host = process.env.HOST || "0.0.0.0";

export default defineConfig(({ mode }) => {
  const environment = mode === "development" ? "dev" : "build";

  const config = conf[environment];
  const env = config.env;
  console.log(config);
  return {
    base: ``,
    define: {
      "process.env.PARKSTAY_URL": JSON.stringify(env.PARKSTAY_URL),
      "process.env.NODE_ENV": JSON.stringify(env.NODE_ENV),
    },
    root: "",
    server: {
      host: host,
      port: port,
      strictPort: true,
      open: false,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers":
          "Origin, X-Requested-With, Content-Type, Accept",
      },
      hmr: {
        protocol: "ws",
        host: "localhost",
        port: port,
      },
    },
    plugins: [
      vue(),
      vueDevTools(),
      // eslint(),
      svgLoader({
        defaultImport: "url",
      }),
      inject({
        $: 'jquery',
        jQuery: 'jquery',
      })
    ],
    resolve: {
      alias: {
        "vue": "vue/dist/vue.esm-bundler.js",
        "@": path.resolve(__dirname, "./src"),
        "@vue-utils": path.resolve(__dirname, "src/utils/vue"),
        "@common-utils": path.resolve(__dirname, "src/components/common/"),
        "@campgrounds": path.resolve(__dirname, "src/components/campgrounds/"),
      },
    },
    build: {
      manifest: "manifest.json",
      filenameHashing: false,
      commonjsOptions: { transformMixedEsModules: true },
      root: path.resolve(__dirname, "./src/apps"),
      outDir:  config.assetsRoot,      
      publicPath: config.assetsPublicPath,
      sourcemap: true,
      rollupOptions: {
        input: {
          main: path.resolve(__dirname, "src/main.js"),
        },
        output: {
          entryFileNames: "js/[name].js",
          chunkFileNames: "js/[name].js",
          assetFileNames: "[ext]/[name].[ext]",
        },
      },
      emptyOutDir: true,
    },
  };
});

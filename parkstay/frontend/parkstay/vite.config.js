import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import vueDevTools from "vite-plugin-vue-devtools";
import inject from "@rollup/plugin-inject";
import commonjs from '@rollup/plugin-commonjs';
import { babel } from '@rollup/plugin-babel';

// import resolve from '@rollup/plugin-node-resolve';
import path from "path";
// import eslint from 'vite-plugin-eslint2';
import svgLoader from "vite-svg-loader";
import conf from "./config";

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
    server: {
        host: host,
        port: port,
        strictPort: true,
        open: false,
        headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers':
                'Origin, X-Requested-With, Content-Type, Accept',
        },
        hmr: {
            protocol: 'ws',
            host: "localhost",
            port: port,
        },
    },
    plugins: [
        vue(),
        // eslint(),
        svgLoader({
            defaultImport: 'url',
        }),
    ],
    resolve: {
        alias: {
            vue: "vue/dist/vue.esm-bundler.js",
            '@': path.resolve(__dirname, './src'),
            '@vue-utils': path.resolve(__dirname, 'src/utils/vue'),
            '@common-utils': path.resolve(__dirname, 'src/components/common/'),
            '@select2': 'select2/dist/js/select2.min.js',
        },
    },
    build: {
        manifest: 'manifest.json',
        filenameHashing: false,
        commonjsOptions: { transformMixedEsModules: true },
        root: path.resolve(__dirname, './src'),
        outDir: path.resolve(
            __dirname,
            `../../static/${applicationNameShort}_vue`
        ),
        publicPath: ``,
        sourcemap: true,
        rollupOptions: {
            input: {
                main: path.resolve(__dirname, 'src/apps/main.js'),
            },
            output: {
                entryFileNames: 'js/[name].js',
                chunkFileNames: 'js/[name].js',
                assetFileNames: '[ext]/[name].[ext]',
            },
            external: ["jquery", "bootstrap", "datatables"],
        },
        emptyOutDir: true,
    },
  }
});

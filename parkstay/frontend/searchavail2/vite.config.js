import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';
import vueDevTools from 'vite-plugin-vue-devtools';
import legacy from '@vitejs/plugin-legacy';
// import eslint from 'vite-plugin-eslint2';
import svgLoader from 'vite-svg-loader';

const applicationNameShort = 'searchavail2';
const port = process.env.PORT ? parseInt(process.env.PORT) : 9093;
const host = process.env.HOST || '0.0.0.0';

export default defineConfig(({ mode }) => {
    const isProduction = mode === 'production';

    return {
        base: ``,
        // define: {
        //   "process.env.PARKSTAY_URL": process.env.PARKSTAY_API_URL || 'http://localhost:9091',
        //   "process.env.NODE_ENV": isProduction ? "production" : "development",
        // },
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
                host: 'localhost',
                port: port,
            },
        },
        plugins: [
            vueDevTools(),
            vue(),
            // eslint(),
            svgLoader({
                defaultImport: 'url',
            }),
            legacy({
                targets: ['defaults', '> 1%', 'last 2 versions', 'not ie <= 8'],
            }),
        ],
        resolve: {
            alias: {
                vue: 'vue/dist/vue.esm-bundler.js',
                '@': path.resolve(__dirname, './src'),
                '@vue-utils': path.resolve(__dirname, 'src/utils/vue'),
                '@assets': path.resolve(__dirname, 'src/assets/'),
                '@common-utils': path.resolve(
                    __dirname,
                    'src/components/common/'
                ),
                '@components': path.resolve(__dirname, 'src/components/'),
                '@utils': path.resolve(__dirname, 'src/utils/'),
                '@daterangepicker':
                    'bootstrap-daterangepicker/daterangepicker.js',
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
                    main: path.resolve(__dirname, 'src/main.js'),
                },
                output: {
                    entryFileNames: 'js/[name].js',
                    chunkFileNames: 'js/[name].js',
                    assetFileNames: '[ext]/[name].[ext]',
                },
            },
            exclude: ['jquery', 'bootstrap'],
            emptyOutDir: true,
        },
    };
});

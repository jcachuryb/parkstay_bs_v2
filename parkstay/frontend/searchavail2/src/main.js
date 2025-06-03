import "vite/modulepreload-polyfill";
import $ from '@utils/jquery-global.js';

import { createApp } from 'vue';
import router from './router';
import App from './App.vue';
import helpers from '@/utils/helpers';

import 'jquery-validation';
import 'ol/ol.css';
import 'foundation-sites';
import '@assets/styles/foundation-min.scss';
import 'awesomplete/awesomplete.css';
import * as daterangepicker from "@daterangepicker";
import "bootstrap-daterangepicker/daterangepicker.css";

// Add CSRF Token to every request
const customHeaders = new Headers({
    'X-CSRFToken': helpers.getCookie('csrftoken'),
});
const customHeadersJSON = new Headers({
    'X-CSRFToken': helpers.getCookie('csrftoken'),
    'Content-Type': 'application/json',
});
// eslint-disable-next-line no-global-assign
fetch = ((originalFetch) => {
    return (...args) => {
        if (args.length > 1) {
            if (typeof args[1].body === 'string') {
                args[1].headers = customHeadersJSON;
            } else {
                args[1].headers = customHeaders;
            }
        }
        const result = originalFetch.apply(this, args);
        return result;
    };
})(fetch);

const app = createApp(App);

app.use(router);
router.isReady().then(() => app.mount('#parkfinder'));

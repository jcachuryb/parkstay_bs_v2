import { createApp } from 'vue';
import router from './router';
import App from './App';
import helpers from '@/utils/helpers';
import VuePaginate from 'vue-paginate';

import 'jquery-validation';
import 'ol/ol.css';
import 'foundation-sites';
import './assets/styles/foundation-min.scss';
import 'awesomplete/awesomplete.css';

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

const APP_SELECTOR = '#parkfinder';

// check if app has been mounted already. This stops the warning of mounting the app twice.
const mountPoint = document.querySelector(APP_SELECTOR);
if (mountPoint && mountPoint.__vue_app__ !== undefined) {
    // https://stackoverflow.com/questions/76247680/single-page-application-how-to-unmount-app-in-vue-js-3-composition-api-when-ent
    mountPoint.__vue_app__._instance.proxy;
} else {
    const app = createApp(App);

    app.config.globalProperties.$filters = {
        pretty(val, indent = 2) {
            if (typeof val !== 'object') {
                try {
                    val = JSON.parse(val);
                } catch (err) {
                    console.warn('value is not JSON');
                    return val;
                }
            }
            return JSON.stringify(val, null, indent);
        },
    };
    app.component('paginate', VuePaginate);
    app.use(router);
    router.isReady().then(() => app.mount(APP_SELECTOR));
}

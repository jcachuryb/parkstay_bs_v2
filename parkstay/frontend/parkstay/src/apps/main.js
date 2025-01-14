// The following line loads the standalone build of Vue instead of the runtime-only build,
// so you don't have to do: import Vue from 'vue/dist/vue'
// This is done with the browser options. For the config, see package.json
import "vite/modulepreload-polyfill";
import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import { $ } from "../hooks.js";

import alert from "../components/utils/alert.vue";
import store from "./store.js";
import { routes } from "./routes.js";
import filters from "../components/utils/filters.js";
import { mapGetters } from "vuex";
import "../hooks-css.js";

const router = createRouter({
  history: createWebHistory(),

  routes: routes,
});

if (document.getElementById("menu")) {
  const menuApp = createApp({});
  menuApp.use(router);
  menuApp.mount("#menu");
}

const app = createApp({
  computed: {
    ...mapGetters(["showAlert", "alertType", "alertMessage"]),
  },
});
app.component("alert", alert);
app.use(store);
app.use(router);

app.config.globalProperties.$filters = {
  ...filters,
};

app.mount("#app");

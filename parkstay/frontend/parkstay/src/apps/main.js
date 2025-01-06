// The following line loads the standalone build of Vue instead of the runtime-only build,
// so you don't have to do: import Vue from 'vue/dist/vue'
// This is done with the browser options. For the config, see package.json
import { $ } from "../hooks.js";
import Vue from "vue";

if (process.env.NODE_ENV == "development") {
  Vue.config.devtools = true;
}
import resource from "vue-resource";
import Router from "vue-router";

import alert from "../components/utils/alert.vue";
import basePanelHeading from "../layouts/base-panel-heading.vue";

import store from "./store.js";
import { routes } from "./routes.js";
import { mapGetters } from "vuex";
import "../hooks-css.js";
Vue.use(Router);
Vue.use(resource);

global.$ = $;

const router = new Router({
  routes: routes,
  mode: "history",
});

if (document.getElementById("menu")) {
  new Vue({
    router,
  }).$mount("#menu");
}

Vue.component("basePanelHeading", basePanelHeading);

Vue.filter("formatMoney", function (n, c, d, t) {
  c = isNaN((c = Math.abs(c))) ? 2 : c;
  d = d == undefined ? "." : d;
  t = t == undefined ? "," : t;
  var s = n < 0 ? "-" : "";
  var i = String(parseInt((n = Math.abs(Number(n) || 0).toFixed(c))));
  var j = (j = i.length) > 3 ? j % 3 : 0;
  return (
    s +
    (j ? i.substr(0, j) + t : "") +
    i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) +
    (c
      ? d +
        Math.abs(n - i)
          .toFixed(c)
          .slice(2)
      : "")
  );
});

Vue.filter("formatDate", function (date) {
  if (date) {
    return "FORMATTED DATE";
  }
  return "INVALID DATE FOR FILTER";
});

const app = new Vue({
  router: router,
  store,
  components: {
    alert,
  },
  watch: {
    $route: function () {
      let vm = this;
    //   vm.$store.dispatch("updateAlert", {
    //     visible: false,
    //     type: "danger",
    //     message: "Stop",
    //   });
    },
  },
  computed: {
    ...mapGetters(["showAlert", "alertType", "alertMessage"]),
  },
}).$mount("#app");

// The following line loads the standalone build of Vue instead of the runtime-only build,
// so you don't have to do: import Vue from 'vue/dist/vue'
// This is done with the browser options. For the config, see package.json
import { $ } from '../hooks.js'
import Vue from 'vue'
if (process.env.NODE_ENV == "development") {
    Vue.config.devtools = true;
}
import resource from 'vue-resource'
import Router from 'vue-router'

import alert from '../components/utils/alert.vue'
import basePanelHeading from '../layouts/base-panel-heading.vue'

import store from './store.js'
import { routes } from './routes.js'
import { mapGetters } from 'vuex'
import '../hooks-css.js'
Vue.use(Router);
Vue.use(resource);

global.$ = $

const router = new Router({
  'routes' : routes,
  'mode': 'history'
});

if(document.getElementById('menu')) {
    new Vue({
        router,
    }).$mount('#menu');
}

Vue.component("basePanelHeading", basePanelHeading)

new Vue({
  'router':router,
  store,
  components:{
      alert
  },
  watch:{
      $route:function () {
          let vm =this;
          vm.$store.dispatch("updateAlert",{
              visible:false,
              type:"danger",
              message: ""
          });
      }
  },
  computed:{
      ...mapGetters([
          "showAlert",
          "alertType",
          "alertMessage"
      ])
  }
}).$mount('#app');

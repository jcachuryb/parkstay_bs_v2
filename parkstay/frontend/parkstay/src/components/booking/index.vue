<template id="booking_index_vue">
    <div class="row">
        <template v-if="showLoader">
            <loader :isLoading="showLoader">{{ loaderText }}...</loader>
        </template>
        <template v-else class="booking-router">
            <router-view></router-view>
        </template>
    </div>
</template>
<script setup>

import loader from '../utils/loader.vue';
import { computed } from 'vue';
import { useStore } from "../../apps/store.js";

const store = useStore()

const showLoader = computed(() => store.getters.app_loader_state)
const loaderText = computed(() => store.getters.app_loader_text)

</script>
<style></style>

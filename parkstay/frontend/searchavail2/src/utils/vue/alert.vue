<template>
    <div v-show="show" :class="{
        'alert': true,
        'alert-success': (type == 'success'),
        'alert-warning': (type == 'warning'),
        'alert-info': (type == 'info'),
        'alert-danger': (type == 'danger'),
        'top': (placement === 'top'),
        'top-right': (placement === 'top-right')
    }" transition="fade" :style="{ width: width }" role="alert">
        <button v-show="dismissable" type="button" class="close" @click="show = false">
            <span>&times;</span>
        </button>
        <slot></slot>
    </div>
</template>

<script setup>
import { watch, useRef } from 'vue'

const _timeout = useRef(null)
const props = defineProps({
    type: {
        type: String
    },
    dismissable: {
        type: Boolean,
        default: false
    },
    show: {
        type: Boolean,
        default: false,
    },
    duration: {
        type: Number,
        default: 0
    },
    width: {
        type: String
    },
    placement: {
        type: String
    }
})

watch(
    () => props.show,
    (val) => {
        if (_timeout.value) clearTimeout(_timeout.value)
        if (val && Boolean(props.duration)) {
            _timeout.value = setTimeout(() => { props.show = false }, props.duration)
        }
    }
)
</script>

<style scoped>
.fade-transition {
    transition: opacity .3s ease;
}

.fade-enter,
.fade-leave {
    height: 0;
    opacity: 0;
}

.alert.top {
    position: fixed;
    top: 30px;
    margin: 0 auto;
    left: 0;
    right: 0;
    z-index: 1050;
}

.alert.top-right {
    position: fixed;
    top: 30px;
    right: 50px;
    z-index: 1050;
}
</style>

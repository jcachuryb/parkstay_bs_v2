<template lang="html">
    <div id="select-panel">
        <div class="row" style="margin-top: 40px;">
            <div class="col-sm-6 options">
                <div class="panel panel-primary">
                    <div class="panel-heading">
                        <h3 class="panel-title">Features</h3>
                    </div>
                    <div class="panel-body" v-bind:class="{ 'empty-options': allOptionsSelected }">
                        <p v-show="allOptionsSelected">
                            All options selected
                        </p>
                        <ul class="list-group">
                            <a href="" v-show="!isDisabled" v-for="option, key in optionsRef"
                                @click.prevent="addSelected(option, key)"
                                class="list-group-item list-group-item-primary">{{ option.name }}</a>
                            <a href="" v-show="isDisabled" v-for="option, key in optionsRef" @click.prevent.stop=""
                                class="list-group-item disabled">{{ option.name }}</a>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="col-sm-6 options">
                <div class="panel panel-primary">
                    <div class="panel-heading">
                        <h3 class="panel-title">Selected Features</h3>
                    </div>
                    <div class="panel-body" v-bind:class="{ 'empty-options': !hasSelectedOptions }">
                        <p v-show="!hasSelectedOptions">
                            No options selected
                        </p>
                        <ul class="list-group">
                            <a href="" v-show="!isDisabled" v-for="option, key in selectedRef"
                                @click.prevent="removeSelected(option, key)"
                                class="list-group-item ">{{ option.name }}</a>
                            <a href="" v-show="isDisabled" v-for="option, key in selectedRef" @click.prevent.stop=""
                                class="list-group-item disabled">{{ option.name }}</a>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import $ from 'jquery'
import { computed, watch, ref } from 'vue';

const props = defineProps({
    options: {
        type: Array,
        required: true,
        default: () => []
    },
    disabled: {
        type: Boolean,
        default: false
    },
    selected: {
        type: Array,
        required: true,
        default: () => []
    }
})
const isDisabled = ref(false)
const optionsRef = ref(props.options)
const selectedRef = ref(props.selected)
const allOptionsSelected = computed(() => !(optionsRef.value.length > 0))
const hasSelectedOptions = computed(() => selectedRef.value.length > 0)

const emit = defineEmits(['onChange'])

const addSelected = function (option, key) {
    selectedRef.value.push(option);
    optionsRef.value.splice(key, 1);
    selectedRef.value.sort(function (a, b) {
        return parseInt(a.id) - parseInt(b.id)
    });
    emit('onChange', selectedRef.value)
}
const removeSelected = function (option, key) {
    optionsRef.value.push(option);
    selectedRef.value.splice(key, 1);
    optionsRef.value.sort(function (a, b) {
        return parseInt(a.id) - parseInt(b.id)
    });
    emit('onChange', selectedRef.value)
}
const enabled = function (isEnabled) {
    isDisabled.value = !isEnabled;
}
const loadSelectedFeatures = function (passed_features) {
    $.each(passed_features, function (i, cgfeature) {
        $.each(optionsRef.value, function (j, feat) {
            if (feat != null) {
                if (cgfeature.id == feat.id) {
                    optionsRef.value.splice(j, 1);
                    selectedRef.value.push(cgfeature);
                }
            }
        })
    });
}

watch(() => props.options, (value) => {
    optionsRef.value = value
})

watch(() => props.selected, (value) => {
    selectedRef.value = value
})

defineExpose({
    enabled, 
    loadSelectedFeatures
})
</script>

<style lang="css">
.options>.panel>.panel-body {
    padding: 0;
    max-height: 300px;
    min-height: 300px;
    overflow: auto;
}

.options .list-group {
    margin-bottom: 0;
}

.options .list-group-item {
    border-radius: 0;
}

.list-group-item:last-child {
    border-bottom-left-radius: 5px;
    border-bottom-right-radius: 5px;
}

.empty-options {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 300px;
    color: #ccc;
    font-size: 2em;
}
</style>

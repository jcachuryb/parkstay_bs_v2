<template id="pkCsOpen">
    <bootstrapModal title="Open campsite" :large=true @ok="addOpen()" :isModalOpen='isModalOpen'>

        <div class="modal-body">
            <form id="openCGForm" class="form-horizontal">
                <div class="row">
                    <alert v-model:show="showError" type="danger"></alert>
                    <div class="form-group">
                        <div class="col-md-2">
                            <label for="open_cg_current_closure">Current Closure: </label>
                        </div>
                        <div class="col-md-4">
                            <input id='open_cg_current_closure' v-model="current_closure" disabled type='text'
                                class="form-control" />
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label for="open_cg_range_end">Reopen on: </label>
                        </div>
                        <div class="col-md-4">
                            <div class='input-group date' id='open_cg_range_end'>
                                <input name="open_start" v-model="formdata.range_end" type='text'
                                    class="form-control" />
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                <reason type="close" name="open_reason" v-model="formdata.closure_reason"></reason>
                <div v-show="requireDetails" class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label for="open_cg_details">Details: </label>
                        </div>
                        <div class="col-md-5">
                            <textarea name="open_details" v-model="formdata.details" class="form-control"
                                id="open_cg_details"></textarea>
                        </div>
                    </div>
                </div>
            </form>
        </div>

    </bootstrapModal>
</template>

<script setup>
import bootstrapModal from '../../utils/bootstrap-modal.vue'
import reason from '../../utils/reasons.vue'
import { $, getDateTimePicker, dateUtils, helpers } from '../../../hooks.js'
import alert from '../../utils/alert.vue'
import { computed, onMounted, ref, watch } from 'vue'
const id = ref('')
const current_closure = ref('')
const formdata = ref({
    range_end: '',
    closure_reason: '',
    details: ''
})
const picker = ref('')
const errors = ref(false)
const errorString = ref('')
const form = ref(null)
const isOpen = ref(false)

const emit = defineEmits(['openCampsite'])


const showError = computed(function () {
    return errors.value;
})
const isModalOpen = computed(function () {
    return isOpen.value;
})
const requireDetails = computed(function () {
    return (formdata.value.closure_reason === 1);
})

watch(() => isOpen.value, (val) => {
    helpers.formUtils.resetFormValidation(form.value)
})

const close = function () {
    isOpen.value = false;
    formdata.value.closure_reason = ''
}
const addOpen = function () {
    if (form.value.valid()) {
        emit('openCampsite');
    }
}
const addFormValidations = function () {
    form.value.validate({
        rules: {
            open_start: "required",
            open_reason: "required",
            open_details: {
                required: {
                    depends: function (el) {
                        return requireDetails.value;
                    }
                }
            }
        },
        messages: {
            open_start: "Enter a reopening date",
            open_reason: "Select an open reason from the options",
            open_details: "Details required if Other reason is selected"
        },
        showErrors: helpers.formUtils.utilShowFormErrors
    });
}

onMounted(function () {
    const pickerElement = $('#open_cg_range_end');
    picker.value = getDateTimePicker(pickerElement, {
        useCurrent: false,
        restrictions: { minDate: dateUtils.addDays(new Date(), 1) }
    });
    pickerElement.on('change.td', function (e) {
        const date = picker.value.dates.lastPicked
        formdata.value.range_end = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
    });
    form.value = $('#openCGForm');
    addFormValidations();
})
</script>

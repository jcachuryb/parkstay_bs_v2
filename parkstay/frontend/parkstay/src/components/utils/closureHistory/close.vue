<template id="Close">
    <bootstrapModal :title="title" :large="true" @ok="addClosure()" @cancel="close()" :isModalOpen='isModalOpen'>

        <div class="modal-body">
            <form name="closeForm" class="form-horizontal">
                <div class="row">
                    <alert v-model:show="showError" type="danger">{{ errorString }}</alert>
                    <div class="form-group">
                        <div class="col-md-2">
                            <label for="open_cg_range_start">Closure start: </label>
                        </div>
                        <div class="col-md-4">
                            <div class='input-group date' :id='close_cg_range_start'>
                                <input name="closure_start" v-model="statusHistory.range_start" type='text'
                                    class="form-control" />
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label for="open_cg_range_start">Reopen on: </label>
                        </div>
                        <div class="col-md-4">
                            <div class='input-group date' :id='close_cg_range_end'>
                                <input name="closure_end" v-model="statusHistory.range_end" type='text'
                                    class="form-control" />
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                <reason type="close" v-model="statusHistory.closure_reason"></reason>
                <div v-show="requireDetails" class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label>Details: </label>
                        </div>
                        <div class="col-md-4">
                            <textarea name="closure_details" v-model="statusHistory.details" class="form-control"
                                id="close_cg_details"></textarea>
                        </div>
                    </div>
                </div>
            </form>
        </div>

    </bootstrapModal>
</template>

<script setup>
import { $, getDateTimePicker, dateUtils } from '../../../hooks.js'
import bootstrapModal from '../bootstrap-modal.vue'
import alert from '../alert.vue'
import reason from '../reasons.vue'
import { computed, onMounted, ref } from 'vue'

const props = defineProps({
    statusHistory: {
        type: Object,
        required: true,
    },
    title: {
        type: String,
        required: true
    }
})

const emits = defineEmits(['inFocus', 'submit'])

const id = ref('')
const uid = crypto.randomUUID();
const close_cg_range_start = 'close_cg_range_start' + uid
const close_cg_range_end = 'close_cg_range_end' + uid
const current_closure = ref('')
const showDetails = ref(false)
const errors = ref(false)
const errorString = ref('')
const form = ref(null);
const statusHistory = ref(props.statusHistory)
const isOpen = ref(false)
const closeStartPicker = ref(null)
const closeEndPicker = ref(null)


const showError = computed(function () {
    return errors.value;
})
const isModalOpen = computed(function () {
    return isOpen.value;
})
const closure_id = computed(function () {
    return statusHistory.value.id ? statusHistory.value.id : '';
})
const requireDetails = computed(function () {
    return statusHistory.value.closure_reason === '1';
})
const close = function () {
    errors.value = false;
    errorString.value = '';
    isOpen.value = false;
    statusHistory.value.id = '';
    statusHistory.value.range_start = '';
    statusHistory.value.range_end = '';
    statusHistory.value.status = '1';
    statusHistory.value.details = '';
    statusHistory.value.reason = '';
    statusHistory.value.closure_reason = '';

    closeEndPicker.value.clear();
    closeStartPicker.value.clear();
}
const addClosure = function () {
    if (form.value.valid()) {
        if (!closure_id.value) {
            emits('closeRange');
        } else {
            emits('updateRange');
        }
    }
}
const addFormValidations = function () {
    form.value.validate({
        rules: {
            closure_start: "required",
            closure_status: "required",
            closure_details: {
                required: {
                    depends: function (el) {
                        return requireDetails;
                    }
                }
            }
        },
        messages: {
            closure_start: "Enter a start date",
            closure_status: "Select a closure reason from the options",
            closure_details: "Details required if Other reason is selected"
        },
        showErrors: function (errorMap, errorList) {

            $.each(this.validElements(), function (index, element) {
                var $element = $(element);
                $element.attr("data-original-title", "").parents('.form-group').removeClass('has-error');
            });

            // destroy tooltips on valid elements
            $("." + this.settings.validClass).tooltip("destroy");

            // add or update tooltips
            for (var i = 0; i < errorList.length; i++) {
                var error = errorList[i];
                $(error.element)
                    .tooltip({
                        trigger: "focus"
                    })
                    .attr("data-original-title", error.message)
                    .parents('.form-group').addClass('has-error');
            }
        }
    });
}

onMounted(() => {
    statusHistory.value.status = 1;
    statusHistory.value.reason = '';

    form.value = $(document.forms.closeForm)
    const closeStartPickerElement = $('#' + close_cg_range_start)
    const closeEndPickerElement = $('#' + close_cg_range_end)
    closeStartPicker.value = getDateTimePicker(closeStartPickerElement, {
        restrictions: { minDate: new Date() }
    });
    closeEndPicker.value = getDateTimePicker(closeEndPickerElement, {
        useCurrent: false
    });
    closeStartPickerElement.on('change.td', function (e) {
        const date = closeStartPicker.value.dates.lastPicked;
        statusHistory.value.range_start = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
        if (date) {
            closeEndPicker.value.updateOptions({
                restrictions: { minDate: date }
            });
        }
    });
    closeEndPickerElement.on('change.td', function (e) {
        const date = closeEndPicker.value.dates.lastPicked;
        statusHistory.value.range_end = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
    });

    addFormValidations();

})

defineExpose({ close, closure_id, statusHistory, isOpen, errors, errorString })

</script>

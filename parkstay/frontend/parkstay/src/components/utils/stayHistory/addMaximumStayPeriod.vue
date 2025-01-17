<template id="addMaxStayCS">
    <bootstrapModal ref="modal" :title="getTitle" :large=true @ok="addMaxStay()" okText="Add"  @cancel="close()" :isModalOpen='isModalOpen'>

        <div class="modal-body">
            <form id="addMaxStayForm" class="form-horizontal">
                <div class="row">
                    <alert v-model:show="showError" type="danger">{{ errorString }}</alert>
                    <div class="form-group">
                        <div class="col-md-2">
                            <label for="stay_maximum">Maximum Stay: </label>
                        </div>
                        <div class="col-md-4">
                            <input placeholder="Default = 28" id='stay_maximum' v-model="stay.max_days" type='text'
                                class="form-control" />
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label class="form-label required" for="stay_start_picker">
                                <span class="bi bi-calendar3"></span>
                                Period Start: 
                            </label>
                        </div>
                        <div class="col-md-4">
                            <div class='input-group date' id="stay_start_picker">
                                <input name="stay_start" v-model="stay.range_start" type='text' class="form-control" />
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label class="form-label" for="stay_end_picker">
                                <span class="bi bi-calendar3"></span>
                                Period End: 
                            </label>
                        </div>
                        <div class="col-md-4">
                            <div class='input-group date' id='stay_end_picker'>
                                <input name="stay_end" v-model="stay.range_end" type='text' class="form-control" />
                            </div>
                        </div>
                    </div>
                </div>
                <reason-component type="stay" v-model="stay.reason" ref="reason" name="stay_reason" :required="true"></reason-component>
                <div v-show="requireDetails" class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label class="form-label required" for="stay_details">Details: </label>
                        </div>
                        <div class="col-md-5">
                            <textarea name="stay_details" v-model="stay.details" class="form-control"
                                id="stay_details"></textarea>
                        </div>
                    </div>
                </div>
            </form>
        </div>

    </bootstrapModal>
</template>

<script setup>
import bootstrapModal from '../../utils/bootstrap-modal.vue';
import reasonComponent from '../../utils/reasons.vue';
import { $, getDateTimePicker, dateUtils, helpers } from '../../../hooks.js';
import alert from '../../utils/alert.vue';
import { computed, onMounted, ref, watch } from 'vue';


const props = defineProps({
    campground: {
        type: Object,
        required: true
    },
    stay: {
        type: Object
    }
});

const emits = defineEmits(['addCgStayHistory', 'updateStayHistory']);

const reason = ref(null)
const modal = ref(null)
const stay = ref(props.stay)
const start_picker = ref('')
const end_picker = ref('')
const errors = ref(false)
const errorString = ref('')
const form = ref('')
const isOpen = ref(false)
const create = ref(true)
const status = ref('')

const showError = computed(function () {
    return errors.value;
})
const isModalOpen = computed(function () {
    return isOpen.value;
})
const getTitle = computed(function () {
    return create.value ? 'Add New Maximum Stay Period' : 'Edit Maximum Stay Period';
})
const requireDetails = computed(function () {
    return (stay.value.reason == 1) ? true : false;
})

watch(() => isOpen.value, (val) => {
    helpers.formUtils.resetFormValidation(form.value)
})

const close = function () {
    stay.value.max_days = '';
    stay.value.range_start = '';
    stay.value.range_end = '';
    stay.value.reason = '';
    stay.value.details = '';

    isOpen.value = false;
    errors.value = false;
    errorString.value = '';
    status.value = '';
}
const updateReason = function (id) {
    stay.value.reason = id;
}
const addMaxStay = function () {
    if ($(form.value).valid()) {
        if (!stay.value.id) {
            emits('addCgStayHistory');
        } else {
            emits('updateStayHistory');
        }
    }
}
const addFormValidations = function () {
    form.value.validate({
        rules: {
            stay_start: "required",
            stay_reason: "required",
            stay_details: {
                required: {
                    depends: function (el) {
                        return stay.value.reason == 1;
                    }
                }
            }
        },
        messages: {
            stay_start: "Enter a start date",
            stay_reason: "Select an open reason from the options",
            open_details: "Details required if Other reason is selected"
        },
        showErrors: helpers.formUtils.utilShowFormErrors
    });
}

onMounted(function () {
    if (!create.value) {
        modal.value.title = 'Edit Maximum Stay Period';
    }
    const start_picker_element = $('#stay_start_picker');
    const end_picker_element = $('#stay_end_picker');
    start_picker.value = getDateTimePicker(start_picker_element);
    end_picker.value = getDateTimePicker(end_picker_element, {
        useCurrent: false,
    });
    start_picker_element.on('change.td', function (e) {
        const date = start_picker.value.dates.lastPicked
        stay.value.range_start = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
        end_picker.value.updateOptions({
            restrictions: { minDate: date }
        })
        end_picker.value.toggle()
    });
    end_picker_element.on('change.td', function (e) {
        const date = end_picker.value.dates.lastPicked
        stay.value.range_end = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
    });
    form.value = $('#addMaxStayForm');
    addFormValidations();
})

defineExpose({
    isOpen, create, close
})
</script>

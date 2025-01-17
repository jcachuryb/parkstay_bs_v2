<template id="ParkPriceHistoryDetail">
    <bootstrapModal title="Add Park Price History" :large=true @ok="addHistory()" @cancel="close()" @close="close()"
        :isModalOpen='isModalOpen'>

        <div class="modal-body">
            <form name="priceForm" class="form-horizontal">
                <alert v-model:show="showError" type="danger">{{ errorString }}</alert>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label class="form-label required">Car : </label>
                        </div>
                        <div class="col-md-4">
                            <input name="vehicle" v-model="priceHistory.vehicle" type='number' class="form-control" />
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label class="form-label required">Concession : </label>
                        </div>
                        <div class="col-md-4">
                            <input name="concession" v-model="priceHistory.concession" type='number'
                                class="form-control" />
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label class="form-label required">Motorbike : </label>
                        </div>
                        <div class="col-md-4">
                            <input name="motorbike" v-model="priceHistory.motorbike" type='number'
                                class="form-control" />
                        </div>
                    </div>
                </div>


                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label class="form-label required">Campervan : </label>
                        </div>
                        <div class="col-md-4">
                            <input name="campervan" v-model="priceHistory.campervan" type='number'
                                class="form-control" />
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label>Caravan : </label>
                        </div>
                        <div class="col-md-4">
                            <input name="caravan" v-model="priceHistory.caravan" type='number' class="form-control" />
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label class="form-label required">Trailer : </label>
                        </div>
                        <div class="col-md-4">
                            <input name="trailer" v-model="priceHistory.trailer" type='number' class="form-control" />
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-check m-2">
                        <input name="gst" id="gst" v-model="priceHistory.gst" type='checkbox' checked class="form-check-input" />
                        <label class="form-check-label" for="gst">GST</label>
                    </div>
                </div>

                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label class="form-label required">
                                <span class="bi bi-calendar3"></span>
                                Period start: 
                            </label>
                        </div>
                        <div class="col-md-4">
                            <div class='input-group date' date>
                                <input name="period_start" v-model="priceHistory.period_start" type='text'
                                    class="form-control" />

                            </div>
                        </div>
                    </div>
                </div>
                <reason type="price" v-model="priceHistory.reason"></reason>
                <div v-show="requireDetails" class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label class="form-label required">Details: </label>
                        </div>
                        <div class="col-md-5">
                            <textarea name="details" v-model="priceHistory.details" class="form-control"></textarea>
                        </div>
                    </div>
                </div>
            </form>
        </div>

    </bootstrapModal>
</template>

<script setup>
import bootstrapModal from '../bootstrap-modal.vue'
import reason from '../reasons.vue'
import { $, getDateTimePicker, dateUtils, helpers } from '../../../hooks.js'
import alert from '../alert.vue'
import { computed, onMounted, ref, watch } from 'vue';

const props = defineProps({
    priceHistory: {
        type: Object,
        required: true,
    },
});

const id = ref('')
const title = ref('')
const current_closure = ref('')
const closeStartPicker = ref('')
const showDetails = ref(false)
const closeEndPicker = ref(null)
const priceHistory = ref(props.priceHistory)
const errors = ref(false)
const errorString = ref('')
const form = ref('')
const isOpen = ref(false)
const selected_rate = ref(null)

const emit = defineEmits(['addParkPriceHistory', 'updateParkPriceHistory'])

const showError = computed(function () {
    return errors.value;
})
const isModalOpen = computed(function () {
    return isOpen.value;
})
const closure_id = computed(function () {
    return priceHistory.value.id ? priceHistory.value.id : '';
})
const requireDetails = computed(function () {
    return priceHistory.value.reason == '1';
})

const close = function () {
    delete priceHistory.value.original;
    errors.value = false;
    selected_rate.value = '';
    priceHistory.value = {
        vehicle: '',
        concession: '',
        motorbike: '',
        campervan: '',
        caravan: '',
        trailer: '',
        gst: true,
        period_start: '',
        reason: '',
        details: ''
    }

    errorString.value = '';
    isOpen.value = false;
}
const addHistory = function () {
    if ($(form.value).valid()) {
        emit(priceHistory.value.id ? 'updateParkPriceHistory' : 'addParkPriceHistory', priceHistory.value);
    }
}
const addFormValidations = function () {
    $(form.value).validate({
        rules: {
            vehicle: "required",
            concession: "required",
            motorbike: "required",
            campervan: "required",
            trailer: "required",
            period_start: "required",
            details: {
                required: {
                    depends: function (el) {
                        return priceHistory.value.reason === 1;
                    }
                }
            }
        },
        messages: {
            vehicle: "Enter an vehicle rate",
            concession: "Enter a concession rate",
            motorbike: "Enter a motorbike rate",
            campervan: "Enter a campervan rate",
            caravan: "Enter a caravan rate",
            trailer: "Enter a trailer rate",
            period_start: "Enter a start date",
            details: "Details required if Other reason is selected"
        },
        showErrors: helpers.formUtils.utilShowFormErrors
    });
}

watch(() => isOpen.value, (val) => {
    helpers.formUtils.resetFormValidation(form.value)
})

onMounted(() => {
    form.value = document.forms.priceForm;
    const pickerElement = $(form.value.period_start).closest('.date');
    const picker = getDateTimePicker(pickerElement, {
        useCurrent: false,
        restrictions: { minDate: dateUtils.addDays(new Date(), 1) }
    });
    pickerElement.on('change.td', function (e) {
        const date = picker.dates.lastPicked
        priceHistory.value.period_start = date ? dateUtils.formatDate(date, 'yyyy-MM-dd') : '';
    });
    addFormValidations();
});

defineExpose({
    close, addHistory, showError, isOpen, closure_id, requireDetails,
    id, title, current_closure, closeStartPicker, showDetails, closeEndPicker, selected_rate
})
</script>
<style lang="css" scoped></style>

<template id="PriceHistoryDetail">
    <bootstrapModal :title="title" :large=true @ok="addHistory()" @close="close()" :isModalOpen="isModalOpen"
        @cancel="close()">

        <div class="modal-body">
            <form name="priceForm" class="form-horizontal">
                <alert v-model:show="showError" type="danger">{{ errorString }}</alert>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-6">
                            <label class="form-label">
                                Select Rate: 
                                <i class="bi bi-question-circle" data-bs-toggle="tooltip"
                                data-bs-placement="bottom"
                                data-bs-title="Select a rate to prefill the price fields otherwise use the manual entry" />
                            </label>
                        </div>
                        <div class="col-md-4">
                            <select name="rate" v-model="selected_rate" class="form-select">
                                <option value="">Manual Entry</option>
                                <option v-for="r in rates" :value="r.id">{{ r.name }}</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-6">
                            <label class="form-label required">Adult Price: </label>
                        </div>
                        <div class="col-md-4">
                            <input :readonly="selected_rate != ''" name="adult" v-model="priceHistoryRef.adult" type='text'
                                class="form-control" />
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-6">
                            <label class="form-label required">Concession Price: </label>
                        </div>
                        <div class="col-md-4">
                            <input :readonly="selected_rate != ''" name="concession" v-model="priceHistoryRef.concession"
                                type='text' class="form-control" />
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-6">
                            <label class="form-label required">Child Price: </label>
                        </div>
                        <div class="col-md-4">
                            <input :readonly="selected_rate != ''" name="child" v-model="priceHistoryRef.child" type='text'
                                class="form-control" />
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-6">
                            <label class="form-label required">Infant Price: </label>
                        </div>
                        <div class="col-md-4">
                            <input :readonly="selected_rate != ''" name="infant" v-model="priceHistoryRef.infant"
                                type='text' class="form-control" />
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-6">
                            <label class="form-label required">
                                <span class="bi bi-calendar3"></span>
                                Period start: 
                            </label>
                        </div>
                        <div class="col-md-4">
                            <div class='input-group date'>
                                <input name="period_start" v-model="priceHistoryRef.period_start" type='text'
                                    class="form-control" />
                            </div>
                        </div>
                    </div>
                </div>

                <reason type="price" name="reason" v-model="priceHistoryRef.reason" :required="true"></reason>
                <div v-show="requireDetails" class="row">
                    <div class="form-group">
                        <div class="col-md-6">
                            <label class="form-label required">Details: </label>
                        </div>
                        <div class="col-md-5">
                            <textarea name="details" v-model="priceHistoryRef.details" class="form-control"></textarea>
                        </div>
                    </div>
                </div>


                <div class="row">
                    <div class="form-group">
                        <div class="col-md-6">
                            <label>Booking Policy: {{ priceHistoryRef.booking_policy }}</label>
                        </div>
                        <div class="col-md-4">
                            <select name="rate" v-model="priceHistoryRef.booking_policy" class="form-control">
                                <option value="">Select Booking Policy</option>
                                <option v-for="p in booking_policy.dataitems" :value="p.id">{{ p.policy_name }}</option>
                            </select>
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
import { $, getDateTimePicker, dateUtils, api_endpoints, helpers, Moment } from '../../../hooks.js'
import alert from '../alert.vue'
import { computed, onMounted, ref, unref, watch } from 'vue';

const emit = defineEmits(['addPriceHistory', 'updatePriceHistory'])

const props = defineProps({
    priceHistory: {
        type: Object,
        required: true
    },
});
const id = ref('')
const selected_rate = ref('')
const title = ref('')
const rates = ref([])
const booking_policy = ref([])
const priceHistoryRef = ref({
    adult: '',
        concession: '',
        child: '',
        infant: '',
        booking_policy: '',
})
const current_closure = ref('')
const closeStartPicker = ref('')
const showDetails = ref(false)
const datePicker = ref(null)
const errors = ref(false)
const errorString = ref('')
const form = ref('')
const isOpen = ref(false)

const showError = computed(function () {
    return errors.value;
})
const isModalOpen = computed(function () {
    return isOpen.value;
})
const closure_id = computed(function () {
    return priceHistoryRef.value.id ? priceHistoryRef.value.id : '';
})
const requireDetails = computed(function () {
    return priceHistoryRef.value.reason === 1;
})

watch(() => selected_rate.value, function (value) {
    if (value != '') {
        $.each(rates.value, function (i, rate) {
            if (rate.id == value) {
                console.log("SELECTED RATE");
                console.log(rate);
                priceHistoryRef.value.rate = rate.id;
                priceHistoryRef.value.adult = rate.adult;
                priceHistoryRef.value.concession = rate.concession;
                priceHistoryRef.value.child = rate.child;
                priceHistoryRef.value.infant = rate.infant;
                console.log("RATE POLICY");
                return;
            }
        });
    }
    else {
        delete priceHistoryRef.value.rate;
        priceHistoryRef.value.adult = '';
        priceHistoryRef.value.concession = '';
        priceHistoryRef.value.child = '';
        priceHistoryRef.value.infant = '';
        priceHistoryRef.value.booking_policy = '';
    }
})

watch(() => isOpen.value, (val) => {
    if (val) {
        const { original } = props.priceHistory;
        priceHistoryRef.value = original ? unref(original) : { ...props.priceHistory }
        priceHistoryRef.value.period_start = priceHistoryRef.value.period_start ? dateUtils.formatDate(priceHistoryRef.value.period_start, 'dd/MM/yyyy') : '';
        selected_rate.value = priceHistoryRef.value.rate_id ?? '';
        if (priceHistoryRef.value.period_start) {
            datePicker.value.updateOptions({
                defaultDate: moment(priceHistoryRef.value.period_start, "DD/MM/YYYY").toDate(),
            });
        }
    } else {
        helpers.formUtils.resetFormValidation(form.value)
        resetFields()
    }
})

const close = function () {
    resetFields()
    isOpen.value = false;
}

const resetFields = () => {
    delete priceHistoryRef.value.original;
    errors.value = false;
    selected_rate.value = '';
    priceHistoryRef.value.rate_id = ''
    priceHistoryRef.value.period_start = '';
    priceHistoryRef.value.details = '';
    priceHistoryRef.value.adult = '';
    priceHistoryRef.value.concession = '';
    priceHistoryRef.value.child = '';
    priceHistoryRef.value.infant = '';
    priceHistoryRef.value.booking_policy = '';
    priceHistoryRef.value.reason = ""

    errorString.value = '';
}

const addHistory = function () {
    if ($(form.value).valid()) {
        if (priceHistoryRef.value.id || priceHistoryRef.value.original) {
            emit('updatePriceHistory', priceHistoryRef.value);
        } else {
            emit('addPriceHistory', priceHistoryRef.value);
        }
    }
}
const fetchRates = function () {

    fetch(api_endpoints.rates).then((response) => response.json()).then((data) => {
        rates.value = data;
    });
}
const fetchBookingPolicy = function () {
    console.log(api_endpoints.booking_policy);
    fetch(api_endpoints.booking_policy).then((response) => response.json()).then((data) => {
        booking_policy.value = data;
    });

}
const addFormValidations = function () {
    $(form.value).validate({
        rules: {
            adult: "required",
            concession: "required",
            child: "required",
            infant: "required",
            period_start: "required",
            reason: "required",
            details: {
                required: {
                    depends: function (el) {
                        return priceHistoryRef.value.reason === 1;
                    }
                }
            }
        },
        messages: {
            adult: "Enter an adult rate",
            concession: "Enter a concession rate",
            child: "Enter a child rate",
            infant: "Enter a infant rate",
            period_start: "Enter a start date",
            reason: "Select a reason from the list",
            details: "Details required if Other reason is selected"
        },
        showErrors: helpers.formUtils.utilShowFormErrors
    });
}


onMounted(function () {
    [...(document.querySelectorAll('[data-bs-toggle="tooltip"]') || [])].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
    form.value = document.forms.priceForm;
    const pickerElement = $(form.value.period_start);
    datePicker.value = getDateTimePicker(pickerElement, {
        useCurrent: false,
        restrictions: { minDate: dateUtils.addDays(new Date(), 1) }
    });
    pickerElement.on('change.td', function (e) {
        const date = datePicker.value.dates.lastPicked
        priceHistoryRef.value.period_start = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
    });
    addFormValidations();
    fetchBookingPolicy();
    fetchRates();
})

defineExpose({ title, isOpen, errorString, errors, selected_rate })
</script>
<style lang="css" scoped></style>

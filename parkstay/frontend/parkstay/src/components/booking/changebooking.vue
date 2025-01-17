<template lang="html">
    <div id="change-booking">
        <modal @ok="ok()" @cancel="cancel()" title="Change Booking" large :isModalOpen='isModalOpen'>
            <form class="form-horizontal" name="changebookingForm">
                <div class="row">
                    <alert v-model:show="showError" type="danger"><strong>{{ errorString }}</strong></alert>
                    <alert :show="success" type="success"><strong>{{ successString }}</strong></alert>
                    <div class="col-lg-12">
                        <div class="form-group">
                            <label class="form-label required">
                                <span class="bi bi-calendar3"></span>
                                Dates: 
                            </label>
                            <div class="col-md-4">
                                <div class="input-group arrivalPicker date">
                                    <input type="text" class="form-control" name="arrival" placeholder="DD/MM/YYYY" />
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="input-group departurePicker date">
                                    <input type="text" class="form-control" name="departure" placeholder="DD/MM/YYYY" />
                                </div>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="col-md-2 control-label pull-left" for="Campground">Campground: </label>
                            <div class="col-md-4">
                                <select class="form-control" name="campground" v-model="booking.campground">
                                    <option value="">Select Campground</option>
                                    <option v-for="campground in campgrounds" :value="campground.id">{{ campground.name }}
                                    </option>
                                </select>
                            </div>
                        </div>
                        <div class="form-group" v-show="selectedCampground">
                            <label class="col-md-2 control-label pull-left" for="Campsite">Campsite: </label>
                            <div class="col-md-4">
                                <select class="form-control" v-show="campsites.length < 1">
                                    <option selected value="">Loading...</option>
                                </select>
                                <select class="form-control" name="campsite" v-if="campsites.length > 0"
                                    v-model="booking.campsites">
                                    <option value="">Select Campsite</option>
                                    <option v-for="campsite in campsites" :value="campsite.id">{{ campsite.name }}
                                    </option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            </form>
        </modal>
    </div>
</template>

<script setup>
import modal from '../utils/bootstrap-modal.vue'
import alert from '../utils/alert.vue'
import { $, api_endpoints, helpers, getDateTimePicker, dateUtils } from "../../hooks.js"
import { computed, onMounted, ref, toRefs, watch } from 'vue';

const emit = defineEmits(['loadingCallback'])

const props = defineProps({
    booking_id: Number,
    campgrounds: {
        type: Array,
        default: () => []
    }
})

const { campgrounds } = toRefs(props)
const isModalOpen = ref(false)
const campsites = ref([])
const form = ref(null)
const booking = ref({
    campsites: []
})
const errors = ref(false)
const errorString = ref('')
const successString = ref('')
const success = ref(false)
const arrivalPicker = ref(null)
const departurePicker = ref(null)

const selectedCampground = computed(function () {
    return booking.value.campground;
})
const selectedCampsite = computed(function () {
    return booking.value.campsites;
})
const showError = computed(function () {
    return errors.value;
})

watch(() => selectedCampground, function (value) {
    if (value) {
        fetch(api_endpoints.campgroundCampsites(value)).then((response) => response.json()).then((data) => {
            campsites.value = data;
        }, (response) => {
            console.log(response);
        });
    } else {
        campsites.value = [];
    }
})

watch(() => isModalOpen.value, (val) => {
    helpers.formUtils.resetFormValidation(form.value)
})

const ok = function () {
    if ($(form.value).valid()) {
        sendData();
    }
}
const cancel = function () {
}
const close = function () {
    isModalOpen.value = false;
}
const fetchBooking = function (id) {
    fetch(api_endpoints.booking(id)).then((response) => response.json()).then((data) => {
        booking.value = data; isModalOpen.value = true;
        eventListeners();
    }, (error) => {
        console.log(error);
    });

}
const sendData = function () {
    errors.value = false;
    success.value = false;
    var booking = booking.value;

    emit('loadingCallback', {
        value: 'processing booking',
        show: true
    })
    fetch(api_endpoints.booking(booking.id), {
        method: "PUT",
        body: booking,
        headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
    }).then((response) => response.json()).then((data) => {
        emit('loadingCallback', {
            value: 'processing booking',
            show: false
        })
        successString.value = 'Booking Updated',
            success.value = true;
        //close.value();
    }).catch((error) => {
        console.log(error);
        errors.value = true;
        errorString.value = helpers.apiVueResourceError(error);
        emit('loadingCallback', {
            value: 'processing booking',
            show: false
        })
    });
}
const addFormValidations = function () {
    $(form.value).validate({
        rules: {
            arrival: "required",
            departure: "required",
            campground: "required",
            campsite: {
                required: {
                    depends: function (el) {
                        return campsites.value.length > 0;
                    }
                }
            }
        },
        messages: {
            arrival: "field is required",
            departure: "field is required",
            campground: "field is required",
            campsite: "field is required"
        },
        showErrors: helpers.formUtils.utilShowFormErrors
    });
}
const eventListeners = function () {
    const datepickerOptions = {
        display: {
            buttons: {
                clear: true,
            }
        }
    };

    const bookingArrivalDate = dateUtils.parseDate(booking.value.arrival, 'yyyy/MM/dd', new Date())
    const bookingDepartureDate = dateUtils.parseDate(booking.value.departure, 'yyyy/MM/dd', new Date())
    const arrivalPickerElement = $('.arrivalPicker');
    const departurePickerElement = $('.departurePicker');

    arrivalPicker.value = getDateTimePicker(arrivalPickerElement,
        {
            ...datepickerOptions,
            defaultDate: bookingArrivalDate,
            restrictions: {
                minDate: dateUtils.addDays(new Date(), 1)
            }
        }
    );
    departurePicker.value = getDateTimePicker(departurePickerElement,
        {
            ...datepickerOptions,
            defaultDate: bookingDepartureDate,
            restrictions: {
                minDate: dateUtils.addDays(bookingArrivalDate, 1)
            }
        }
    );

    arrivalPickerElement.on('change.td', function (e) {
        const date = arrivalPicker.dates.lastPicked
        booking.value.arrival = date ? dateUtils.formatDate(date, 'yyyy-MM-dd') : '';
        if (date) {
            departurePicker.value.updateOptions({
                restrictions: {
                    minDate: date
                }
            });
        }
    });
    departurePickerElement.on('change.td', function (e) {
        const date = departurePicker.value.dates.lastPicked
        booking.value.departure = date ? dateUtils.formatDate(date, 'yyyy-MM-dd') : '';
    });
}


onMounted(() => {
    form.value = document.forms.changebookingForm;
    addFormValidations();
})
</script>

<style lang="css"></style>

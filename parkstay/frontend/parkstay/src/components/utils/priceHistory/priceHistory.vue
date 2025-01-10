<template id="priceHistory">
    <div class="row">
        <parkPriceHistory v-if="addParkPrice" ref="historyModal" @addParkPriceHistory="addParkHistory"
            @updateParkPriceHistory="updateParkHistory" :priceHistory="parkPrice" @cancel="closeHistory()" />
        <PriceHistoryDetail v-else ref="historyModal" @addPriceHistory="addHistory"
            @updatePriceHistory="updateHistory" :priceHistory="price"></PriceHistoryDetail>
        <div class="well">
            <div class="col-sm-8">
                <h1>Price History</h1>
            </div>
            <div class="col-sm-4">
                <button v-show="showAddBtn" @click="showHistory()" class="btn btn-primary table_btn">Add Price
                    History</button>
            </div>
            <datatable ref="history_dt" :dtHeaders="dt_headers" :dtOptions="dt_options" id="ph_table"></datatable>
        </div>
        <confirmbox id="deleteHistory" :options="deleteHistoryPrompt"></confirmbox>
    </div>
</template>

<script setup>
import datatable from '../datatable.vue'
import confirmbox from '../confirmbox.vue'
import PriceHistoryDetail from './priceHistoryDetail.vue'
import parkPriceHistory from './parkPriceHistoryDetail.vue'
import {
    $,
    bus,
    Moment,
    api_endpoints,
    helpers
}
    from '../../../hooks.js'
import { onMounted } from 'vue'
import { ref } from 'vue'

const props = defineProps({
    showAddBtn: {
        type: Boolean,
        default: true
    },
    addPriceHistory: {
        type: Boolean,
        default: true
    },
    addParkPrice: {
        type: Boolean,
        default: false
    },
    level: {
        validator: function (value) {
            var levels = ['campground', 'campsite_class', 'campsite', 'park'];
            return $.inArray(value, levels) > -1;
        },
        //required: true
    },
    historyDeleteURL: {
        type: String,
        //required: true
    },
    object_id: {
        type: Number,
        required: true
    },
    dt_options: {
        type: Object,
        required: true,
        columnDefs: [
            { "defaultContent": "-", "targets": "_all" },
        ],

    },
    dt_headers: {
        type: Array,
        default:  () => ['Period Start', 'Period End', 'Adult Price', 'Concession Price', 'Child Price', 'Comment', 'Action']
    }
})

const history_dt = ref(null)
const historyModal = ref(null)

const price = ref({
    reason: ''
})
const parkPrice = ref({
    vehicle: '',
    concession: '',
    motorbike: '',
    reason: { id: 1 },
    period_start: '',
    details: '',
    booking_policy: ''
})
const deleteHistory = ref(null)
const deleteHistoryPrompt = ref({
    icon: "<i class='fa fa-exclamation-triangle fa-2x text-danger' aria-hidden='true'></i>",
    message: "Are you sure you want to Delete this Price History Record",
    buttons: [{
        text: "Delete",
        event: "delete",
        bsColor: "btn-danger",
        handler: function () {
            deleteHistoryRecord(deleteHistory.value);
            deleteHistory.value = null;
        },
        autoclose: true,
    }],
    id: 'deleteHistory'
})

const getTitle = function () {

    if (price.value.id || price.value.original) {
        return 'Update Price History';
    } else {
        $('#gst').prop('checked', true);
        return 'Add Price History';
    }
}
const showHistory = function () {
    historyModal.value.title = getTitle();
    historyModal.value.isOpen = true;
}
const closeHistory = function () {
    price.value = {
        reason: '',
        details: ''
    };
    parkPrice.value = {
        reason: '',
        details: ''
    };
    historyModal.value.isOpen = false;
}
const deleteHistoryRecord = function (data) {
    const _level = props.level
    var url = null;
    if (_level == 'park') {
        url = api_endpoints.park_entry_rate(data.rate_id);
        console.log(url);
        $.ajax({
            beforeSend: function (xhrObj) {
                xhrObj.setRequestHeader("Content-Type", "application/json");
                xhrObj.setRequestHeader("Accept", "application/json");
            },
            method: "DELETE",
            url: url,
            xhrFields: { withCredentials: true },
            headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') }
        }).done(function (msg) {
            history_dt.value.vmDataTable.ajax.reload();
        });
    } else if (_level != 'campsite') {
        url = props.historyDeleteURL;
        $.ajax({
            beforeSend: function (xhrObj) {
                xhrObj.setRequestHeader("Content-Type", "application/json");
                xhrObj.setRequestHeader("Accept", "application/json");
            },
            method: "POST",
            url: url,
            xhrFields: { withCredentials: true },
            data: JSON.stringify(data),
            headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') }
        }).done(function (msg) {
            history_dt.value.vmDataTable.ajax.reload();
        });
    }
    else {
        url = api_endpoints.campsiterate_detail(data);
        $.ajax({
            beforeSend: function (xhrObj) {
                xhrObj.setRequestHeader("Content-Type", "application/json");
                xhrObj.setRequestHeader("Accept", "application/json");
            },
            method: "DELETE",
            url: url,
            xhrFields: { withCredentials: true },
            headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') }
        }).done(function (msg) {
            history_dt.value.vmDataTable.ajax.reload();
        });
    }
}
const getAddURL = function () {
    if (props.level == 'campground') {
        return api_endpoints.addPrice(props.object_id);
    }
    else if (props.level == 'campsite') {
        return api_endpoints.campsite_rate;
    }
    else {
        return api_endpoints.addCampsiteClassPrice(props.object_id);
    }
}
const getEditURL = function () {
    if (props.level == 'campground') {
        return api_endpoints.editPrice(props.object_id);
    }
    else if (props.level == 'campsite') {
        return api_endpoints.campsiterate_detail(price.value.id);
    }
    else {
        return api_endpoints.editCampsiteClassPrice(props.object_id);
    }
}
const addHistory = function (prices) {
    if (props.level == 'campsite') {
        price.value.campsite = props.object_id;
    }
    sendData(getAddURL(), 'POST', JSON.stringify(price));
}
const updateHistory = function (prices) {
    if (props.level == 'campsite') {
        price.value.campsite = props.object_id;
        sendData(getEditURL(), 'PUT', JSON.stringify(price));
    }
    else {
        sendData(getEditURL(), 'POST', JSON.stringify(price));
    }
}
const addParkHistory = function (prices) {
    sendData(api_endpoints.park_add_price(), 'POST', JSON.stringify(prices));
}
const updateParkHistory = function (prices) {
    sendData(api_endpoints.park_entry_rate(parkPrice.value.id), 'PUT', JSON.stringify(prices));
}
const sendData = function (url, method, data) {
    console.log(data);
    $.ajax({
        beforeSend: function (xhrObj) {
            xhrObj.setRequestHeader("Content-Type", "application/json");
            xhrObj.setRequestHeader("Accept", "application/json");
        },
        url: url,
        method: method,
        xhrFields: { withCredentials: true },
        data: data,
        headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
        dataType: 'json',
        success: function (data, stat, xhr) {
            closeHistory()
            history_dt.value.vmDataTable.ajax.reload();
        },
        error: function (resp) {
            var msg = helpers.apiError(resp);
            historyModal.value.errorString = msg;
            historyModal.value.errors = true;
        }
    });

}
const addTableListeners = function () {
    history_dt.value.vmDataTable.on('click', '.editPrice', function (e) {
        e.preventDefault();
        var rate = $(this).data('rate');
        console.log("RATE editPrice");
        console.log(rate);
        console.log(api_endpoints.campsiterate_detail(rate));
        console.log(props.level);
        var bookingpolicyid = $(this).data('bookingpolicyid');
        if (props.level == 'park') {
            fetch(api_endpoints.park_entry_rate(rate)).then((response) => {
                parkPrice.value = response.body;
                historyModal.value.selected_rate = rate;
                price.value.period_start = Moment(price.value.period_start).format('YYYY-MM-DD');
                price.value.period_end != null ? price.value.period_end : '';
                price.value.gst = price.value.gst;
                price.value.bookingpolicyid = bookingpolicyid;
            }, (error) => {
                console.log(error);
            });
            showHistory();
        } else if (props.level != 'campsite') {
            var start = $(this).data('date_start');
            var end = $(this).data('date_end');
            var reason = $(this).data('reason');
            var details = $(this).data('details');
            var bookingpolicyid = $(this).data('bookingpolicyid');
            historyModal.value.selected_rate = rate;
            price.value.period_start = Moment(start).format('D/MM/YYYY');
            price.value.booking_policy = bookingpolicyid;
            price.value.original = {
                'date_start': start,
                'rate_id': rate,
                'reason': reason,
                'details': details,
                'booking_policy': bookingpolicyid
            };
            end != null ? price.value.date_end : '';
            showHistory();
        }
        else {
            $.get(api_endpoints.campsiterate_detail(rate), function (data) {
                price.value.period_start = data.date_start;
                price.value.id = data.id;
                price.value.booking_policy = bookingpolicyid;
                price.value.gst = false;
                console.log("VM PERT");
                console.log(price.value);
                historyModal.value.selected_rate = data.rate;
                showHistory();
            });
        }
    });
    history_dt.value.vmDataTable.on('click', '.deletePrice', function (e) {
        e.preventDefault();
        let btn = this;
        if (props.level != 'campsite') {
            var data = {
                'date_start': $(btn).data('date_start'),
                'rate_id': $(btn).data('rate'),
            };
            $(btn).data('date_end') != null ? data.date_end = $(btn).data('date_end') : '';
            deleteHistory.value = data;
        }
        else {
            console.log($(btn).data('rate'));
            deleteHistory.value = $(btn).data('rate');
        }
        console.log("DELETE PRICE END");
        bus.emit('showAlert', 'deleteHistory');
    });
}

defineExpose({ history_dt, showHistory, closeHistory, deleteHistoryRecord, getTitle, addHistory, updateHistory, addParkHistory, updateParkHistory, sendData, getAddURL, getEditURL, addTableListeners })

onMounted(function () {
    addTableListeners();
})
</script>

<style></style>

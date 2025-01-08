<template id="stayHistory">
    <div class="row">
        <StayHistoryDetail :stay="stay" v-model:campsite="campsite" ref="addMaxStayModal"
            @addStayHistory="addStayHistory()" @updateStayHistory="updateStayHistory()"></StayHistoryDetail>
        <div class="well">
            <alert ref="retrieveStayAlert" v-model:show="retrieve_stay.error" type="danger"
                :duration="retrieve_stay.timeout">{{ retrieve_stay.errorString }}</alert>
            <div class="col-sm-8">
                <h1>Maximum Stay History</h1>
            </div>
            <div class="col-sm-4">
                <button @click="showAddStay()" class="btn btn-primary table_btn">Add Max Stay Period</button>
            </div>
            <datatable ref="addMaxStayDT" :dtHeaders="msh_headers" :dtOptions="msh_options" id="stay_history">
            </datatable>
        </div>
        <confirmbox id="deleteStay" :options="deleteStayPrompt"></confirmbox>
    </div>
</template>

<script setup>
import datatable from '../../utils/datatable.vue'
import alert from '../../utils/alert.vue'
import confirmbox from '../../utils/confirmbox.vue'
import StayHistoryDetail from './addMaximumStayPeriod.vue'
import {
    $, 
    bus,
    api_endpoints,
    helpers
}
    from '../../../hooks.js'
import { ref, onMounted } from 'vue'


const props = defineProps({
    datatableURL: {
        type: String,
        required: true
    },
    object_id: {
        type: Number,
        required: true
    }
})
const addMaxStayModal = ref(null)
const addMaxStayDT = ref(null)

const campsite = ref({})
const stay = ref({
    reason: ''
})
const deleteStay = ref(null)
const deleteStayPrompt = ref({
    icon: "<i class='fa fa-exclamation-triangle fa-2x text-danger' aria-hidden='true'></i>",
    message: "Are you sure you want to Delete this stay Period",
    buttons: [{
        text: "Delete",
        event: "delete",
        bsColor: "btn-danger",
        handler: function () {
            deleteStayRecord(deleteStay.value);
            deleteStay.value = null;
        },
        autoclose: true,
    }],
    id: 'deleteStay'
})
const retrieve_stay = ref({
    error: false,
    timeout: 5000,
    errorString: ''
})
const msh_headers = ['ID', 'Period Start', 'Period End', 'Maximum Stay(Nights)', 'Reason', 'Comment', 'Action']
const msh_options = ref({
    responsive: true,
    processing: true,
    deferRender: true,
    language: {
        processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
    },
    order: [
        [0, 'desc']
    ],
    ajax: {
        url: api_endpoints.campsiteStayHistory(props.object_id),
        dataSrc: ''
    },
    columns: [{
        "data": "id"
    }, {
        "data": "range_start"
    }, {
        "data": "range_end"
    }, {
        "data": "max_days"
    }, {
        "data": "reason"
    }, {
        "data": "details"
    }, {
        "mRender": function (data, type, full) {
            var id = full.id;
            if (full.editable) {
                var column = "<td ><a href='#' class='editStay' data-stay_period=\"__ID__\" >Edit</a>";
                column += "<br/><a href='#' class='deleteStay' data-stay_period=\"__ID__\" >Delete</a></td>";
                return column.replace(/__ID__/g, id);
            }
            return '';
        }
    }]
})


const showAddStay = function (create) {
    create = typeof create !== 'undefined' ? create : true;
    addMaxStayModal.value.isOpen = true;
    addMaxStayModal.value.create = create;
}
const addStayHistory = function () {
    sendData(api_endpoints.campsites_stay_history, 'POST')
}
const updateStayHistory = function () {
    sendData(api_endpoints.campsites_stay_history_detail(stay.value.id), 'PUT');
}
const deleteStayRecord = function (id) {
    var url = api_endpoints.campsites_stay_history_detail(id);
    $.ajax({
        method: "DELETE",
        url: url,
        headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
    }).done(function (msg) {
        refreshMaxStayTable();
    });
}
const refreshMaxStayTable = function () {
    addMaxStayDT.value.vmDataTable.ajax.reload();
}
const fetchStay = function (id) {
    $.ajax({
        url: api_endpoints.campsites_stay_history_detail(id),
        method: 'GET',
        xhrFields: {
            withCredentials: true
        },
        dataType: 'json',
        success: function (data, stat, xhr) {
            stay.value = data;
            showAddStay(false);
        },
        error: function (resp) {
            retrieve_stay.value.error = true;
            retrieve_stay.value.errorString = 'There was a problem trying to retrive this stay period';
            setTimeout(function () {
                retrieve_stay.value.error = false;
            }, retrieve_stay.value.timeout);
        }
    });
}
const sendData = function (url, method) {
    var data = stay.value;
    if (method == 'POST') {
        data.campsite = props.object_id;
    }
    $.ajax({
        url: url,
        method: method,
        xhrFields: { withCredentials: true },
        data: data,
        headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
        dataType: 'json',
        success: function (data, stat, xhr) {
            addMaxStayModal.value.close();
            refreshMaxStayTable();
        },
        error: function (resp) {
            errors.value = true;
            errorString.value = helpers.apiError(resp);
        }
    });

}
const attachEventListenersMaxStayDT = function () {
    addMaxStayDT.value.vmDataTable.on('click', '.editStay', function (e) {
        e.preventDefault();
        var id = $(this).attr('data-stay_period');
        fetchStay(id);
    });
    addMaxStayDT.value.vmDataTable.on('click', '.deleteStay', function (e) {
        e.preventDefault();
        var id = $(this).attr('data-stay_period');
        deleteStay.value = id;
        bus.emit('showAlert', 'deleteStay');
    });
}
onMounted(function () {
    attachEventListenersMaxStayDT();
})

</script>

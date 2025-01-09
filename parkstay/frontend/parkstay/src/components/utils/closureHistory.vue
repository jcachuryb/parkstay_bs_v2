<template id="closureHistory">
    <div class="row">
        <Close ref="closeModal" @closeRange="addClosure()" @updateRange="updateClosure()" :title="getTitle"
            :statusHistory="closure"></Close>
        <div class="well">
            <div class="col-sm-8">
                <h1>Closure History</h1>
            </div>
            <div class="col-sm-4">
                <button @click="showClose()" class="btn btn-primary table_btn">Add Closure Period</button>
            </div>
            <datatable ref="closure_dt" :dtHeaders="ch_headers" :dtOptions="ch_options" id="cg_table"></datatable>
        </div>
        <confirmbox id="deleteClosure" :options="deleteClosurePrompt"></confirmbox>
    </div>
</template>

<script setup>
import datatable from './datatable.vue'
import confirmbox from './confirmbox.vue'
import Close from './closureHistory/close.vue'
import {
    $, 
    bus,
    Moment,
    api_endpoints,
    helpers
}
    from '../../hooks.js'
import { computed, onMounted, toRefs, ref } from 'vue'

const props = defineProps({
    datatableURL: {
        type: String,
        required: true
    },
    closeCampground: {
        type: Boolean,
        default: true
    },
    object_id: {
        type: Number,
        required: true
    }
})

const { datatableURL, closeCampground, object_id } = toRefs(props)

const getTitle = computed(() => {
    if (closeCampground.value) {
        return '(Temporarily) Close Campground';
    } else {
        return '(Temporarily) Close Campsite';
    }
})

const closeModal = ref(null)
const closure_dt = ref(null)
const campground = ref({})
const campsite = ref({})
const closure = ref({
    id: '',
    status: 1,
    reason: '',
    closure_reason: ''
})
const deleteClosure = ref(null)
const deleteClosurePrompt = ref({
    icon: "<i class='fa fa-exclamation-triangle fa-2x text-danger' aria-hidden='true'></i>",
    message: "Are you sure you want to Delete this closure Period",
    buttons: [{
        text: "Delete",
        event: "deleteClosure",
        bsColor: "btn-danger",
        handler: function () {
            deleteClosureRecord(deleteClosure.value);
            deleteClosure.value = null;
        },
        autoclose: true,
    }],
    id: 'deleteClosure'
})
const ch_headers = ['Closure Start', 'Reopen On', 'Closure Reason', 'Details', 'Action']
const ch_options = {
    responsive: true,
    processing: true,
    deferRender: true,
    columnDefs: [
        { "defaultContent": "-", "targets": "_all" },
    ],

    ajax: {
        url: datatableURL.value,
        dataSrc: ''
    },
    order: [],
    columns: [{
        data: 'range_start',
        mRender: function (data, type, full) {
            return Moment(data).format('DD/MM/YYYY');
        },
        orderable: false

    }, {
        data: 'range_end',
        mRender: function (data, type, full) {
            if (data) {
                return Moment(data).format('DD/MM/YYYY');
            }
            else {
                return '';
            }
        },
        orderable: false

    }, {
        mRender: function (data, type, full) {
            return full.reason ? full.reason : '';
        },
        orderable: false
    }, {
        data: 'details',
        orderable: false,
        mRender: function (data, type, full) {
            return parseInt(full.closure_reason) == 1 ? data : '';
        }
    }, {
        data: 'editable',
        mRender: function (data, type, full) {
            if (data) {
                var id = full.id;
                var column = "<td ><a href='#' class='editRange' data-range=\"__ID__\" >Edit</a><br/><a href='#' class='deleteRange' data-range=\"__ID__\" >Delete</a></td>";
                return column.replace(/__ID__/g, id);
            }
            else {
                return "";
            }
        },
        orderable: false
    }],
    language: {
        processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
    }
}

const showClose = function () {
    closeModal.value.isOpen = true;
}
const deleteClosureRecord = function (id) {
    var url = closureURL(id);
    $.ajax({
        method: "DELETE",
        url: url,
        headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') }
    }).done(function (msg) {
        closure_dt.value.vmDataTable.ajax.reload();
    });
}
const getAddURL = function () {
    if (closeCampground.value) {
        return api_endpoints.campground_booking_ranges();
    } else {
        return api_endpoints.campsite_booking_ranges();
    }
}
const closureURL = function (id) {
    if (closeCampground.value) {
        return api_endpoints.campground_status_history_detail(id);
    } else {
        return api_endpoints.campsite_status_history_detail(id);
    }
}
const editClosure = function (id) {
    $.ajax({
        url: closureURL(id),
        method: 'GET',
        xhrFields: { withCredentials: true },
        dataType: 'json',
        success: function (data, stat, xhr) {
            closure.value = data;
            showClose();
        },
        error: function (resp) {

        }
    });
}
const addClosure = function () {
    sendData(getAddURL(), 'POST');
}
const updateClosure = function () {
    sendData(closureURL(closeModal.value.closure_id), 'PUT');
}
const sendData = function (url, method) {
    var data = $.extend({}, closeModal.value.statusHistory);
    if (closeCampground.value) {
        data.campground = object_id.value;
    } else {
        data.campsite = object_id.value;
    }

    $.ajax({
        url: url,
        method: method,
        xhrFields: { withCredentials: true },
        data: data,
        headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
        dataType: 'json',
        success: function (data, stat, xhr) {
            closeModal.value.close();
            closure_dt.value.vmDataTable.ajax.reload();
        },
        error: function (resp) {
            var msg = helpers.apiError(resp);
            closeModal.value.errorString = msg;
            closeModal.value.errors = true;
        }
    });

}
const addTableListeners = function () {

    closure_dt.value.vmDataTable.on('click', '.editRange', function (e) {
        e.preventDefault();
        var id = $(this).data('range');
        editClosure(id);
    });
    closure_dt.value.vmDataTable.on('click', '.deleteRange', function (e) {
        e.preventDefault();
        var id = $(this).data('range');
        deleteClosure.value = id;
        bus.emit('showAlert', 'deleteClosure');
    });
}

onMounted(function () {
    addTableListeners();
})
</script>

<style></style>

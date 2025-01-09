<template lang="html">
    <div id="history-booking">
        <modal :showOK="false" cancelText="Close" @ok="ok()" @cancel="cancel()" title="Booking History" large :isModalOpen='isModalOpen'>
            <div class="row">
                <div class="col-lg-12">
                    <h3>Current Booking Details</h3>
                    <div class="row">
                        <div class="col-sm-3">
                            <span><strong>Confirmation #</strong> : PB{{ booking.id }}</span>
                        </div>
                        <div class="col-sm-3">
                            <span><strong>Arrival</strong> : {{ booking.arrival | formatDate }}</span>
                        </div>
                        <div class="col-sm-3">
                            <span><strong>Departure</strong> : {{ booking.departure | formatDate }}</span>
                        </div>
                        <div class="col-sm-3">
                            <span><strong>Cost</strong> : {{ booking.cost_total | formatMoney }}</span>
                        </div>
                    </div>
                    <div class="row" style="margin-top:10px;">
                        <div class="col-sm-3">
                            <span><strong>Adults</strong> : {{ booking.guests.adults }}</span>
                        </div>
                        <div class="col-sm-3">
                            <span><strong>Adults (Concession)</strong> : {{ booking.guests.concession }}</span>
                        </div>
                        <div class="col-sm-3">
                            <span><strong>Children</strong> : {{ booking.guests.children }}</span>
                        </div>
                        <div class="col-sm-3">
                            <span><strong>Infants</strong> : {{ booking.guests.infants }}</span>
                        </div>
                    </div>
                    <div class="row" style="margin-top:10px;">
                        <div class="col-sm-4">
                            <span><strong>Campground</strong> : {{ booking.campground_name }}</span>
                        </div>
                        <div class="col-sm-8">
                            <label>Camp Site (Type): {{ CampSiteType }} </label>
                        </div>
                    </div>
                    <div class="row" style="margin-top:10px;">
                        <div class="col-sm-6">
                            <h4>Vehicles</h4>
                            <div class="row" v-for="v in booking.vehicle_payment_status">
                                <div class="col-sm-4">
                                    <span><strong>Rego</strong> : {{ v.Rego }}</span>
                                </div>
                                <div class="col-sm-4">
                                    <span><strong>Type</strong> : {{ v.Type }}</span>
                                </div>
                                <div class="col-sm-4">
                                    <span><strong>Entry Fee</strong> : <i v-if="v.Fee" class="fa fa-check"
                                            style="color:green;"></i><i v-else class="fa fa-times"
                                            style="color:red;"></i></span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-12" style="margin-top:10px;">
                    <h3>Booking History Details</h3>
                    <datatable v-if="booking_id > 0" ref="booking_history_table" id="booking_history-table"
                        :dtOptions="dtOptions" :dtHeaders="dtHeaders"></datatable>
                </div>
            </div>
        </modal>
    </div>
</template>

<script setup>

import modal from '../utils/bootstrap-modal.vue'
import datatable from '../utils/datatable.vue'
import { $, helpers, Moment } from "../../hooks.js"
import { computed, nextTick, ref, toRefs, watch } from 'vue';

const props = defineProps(['booking_id']);
const { booking_id } = toRefs(props)

const booking_history_table = ref(null)
const isModalOpen = ref(false)
const booking = ref({
    guests: {},
    campground_site_type: ""
})
const firstTimeTableLoad = ref(true)
const dtHeaders = ["Change Date", "Arrival", "Departure", "Campground", "Camp Site", "Updated By", "Details"]
const dtOptions = ref({
    language: {
        processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
    },
    responsive: true,
    processing: true,
    ajax: {
        "url": `/api/booking/${booking_id.value}/history.json`,
        "dataSrc": ''
    },
    order: [],
    /*columnDefs: [
        {
            responsivePriority: 1,
            targets: 0
        },
        {
            responsivePriority: 2,
            targets: 2
        },
        {
            responsivePriority: 3,
            targets: 8
        }
    ],*/
    columns: [
        {
            data: "created",
            orderable: false,
            searchable: false,
            mRender: function (data, type, full) {
                return Moment(data).format("DD/MM/YYYY HH:mm:ss");
            }
        },
        {
            data: "arrival",
            orderable: false,
            searchable: false,
            mRender: function (data, type, full) {
                var val = Moment(data).format("DD/MM/YYYY");
                if (booking.value.arrival == data) {
                    return `<span style="color:green;">${val}</span>`;
                }
                else {
                    return `<span style="color:red;">${val}</span>`;
                }
            }
        },
        {
            data: "departure",
            orderable: false,
            searchable: false,
            mRender: function (data, type, full) {
                var val = Moment(data).format("DD/MM/YYYY");
                if (booking.value.departure == data) {
                    return `<span style="color:green;">${val}</span>`;
                }
                else {
                    return `<span style="color:red;">${val}</span>`;
                }
            }
        },
        {
            data: "campground",
            orderable: false,
            searchable: false,
            mRender: function (data, type, full) {
                if (booking.value.campground_name == data) {
                    return `<span style="color:green;">${data}</span>`;
                }
                else {
                    return `<span style="color:red;">${data}</span>`;
                }
            }
        },
        {
            data: "campsites",
            orderable: false,
            searchable: false,
            mRender: function (data, type, full) {
                var resultList = data.sort().join(',');
                var max_length = 10;
                var popover_class = (resultList.length > max_length) ? "class='name_popover'" : "";
                var name = (resultList.length > max_length) ? resultList.substring(0, max_length - 1) + '...' : resultList;
                var column = '<div ' + popover_class + 'tabindex="0" data-toggle="popover" data-placement="top" data-content="__NAME__" >' + name + '</div>';
                if (booking.value.campsite_names == resultList) {
                    return `<span style="color:green;">${column.replace('__NAME__', resultList)}</span>`;
                }
                else {
                    return `<span style="color:red;">${column.replace('__NAME__', resultList)}</span>`;
                }
            }
        },
        {
            data: "updated_by",
            orderable: false,
        },
        {
            "className": 'details-control',
            "orderable": false,
            "data": null,
            "defaultContent": ''
        },
    ]
})

defineExpose({ booking, isModalOpen })

watch(() => booking_id.value, function (value) {
    nextTick(() => {
        if (value > 0) {
            booking_history_table.value.vmDataTable.ajax.url(`/api/booking/${value}/history.json`);
            booking_history_table.value.vmDataTable.ajax.reload();
            addEventListeners();
        }
    });
})

const CampSiteType = computed(function () {
    const typeCondensed = {};
    const resultList = [];
    for (let i = 0; i < booking.value.campground_site_type.length; i++) {
        if (booking.value.campground_site_type[i].campground_type === 0) {
            resultList.push(booking.value.campground_site_type[i].name);
            continue;
        }
        if (typeCondensed[booking.value.campground_site_type[i].type] == undefined) {
            typeCondensed[booking.value.campground_site_type[i].type] = 0;
        }
        typeCondensed[booking.value.campground_site_type[i].type] += 1;
    }
    for (let index in typeCondensed) {
        let count = typeCondensed[index];
        let site_type = index.split(':', 1)[0];
        resultList.push(`${count}x ${site_type}`);
    }
    const resultString = resultList.join(", ");
    return resultString;
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
const format = function (d) {
    // `d` is the original data object for the row
    var new_vehicles = [];
    var changed_vehicles = [];
    var vehicles = '<table class="vehicle_history_data" cellpadding="10" cellspacing="40" border="0" style="padding:10px;"><tr><th>Rego</th><th>Type</th><th>Entry Fee</th></tr>';
    $.each(d.vehicles, function (i, v) {
        var entry = v.entry_fee ? '<i class="fa fa-check" style="color:green;"></i>' : '<i class="fa fa-times" style="color:red;"></i>';

        // Check if the vehicle is a new vehicle
        var found = booking.value.vehicle_payment_status.find(b => b.Rego == v.rego.toUpperCase());
        var color = (found && found.Fee == v.entry_fee && found.Rego == v.rego.toUpperCase() && v.type == found.original_type) ? 'green' : 'red';
        vehicles += `<tr style="color: ${color};">
                                <td>${v.rego}</td>
                                <td>${v.type}</td>
                                <td>${entry}</td>
                            </tr>`
    });
    vehicles += '</table>';

    // Adults
    var adults = booking.value.guests.adults == d.details.num_adult ? `<tr style='color:green;'><td>Adults:</td><td>${d.details.num_adult}</td></tr>` : `<tr style='color:red;'><td>Adults:</td><td>${d.details.num_adult}</td></tr>`;
    // Concession
    var concession = booking.value.guests.concession == d.details.num_concession ? `<tr style='color:green;'><td>Adults (Concession):</td><td>${d.details.num_concession}</td></tr>` : `<tr style='color:red;'><td>Adults (Concession):</td><td>${d.details.num_concession}</td></tr>`;
    // Children 
    var children = booking.value.guests.children == d.details.num_child ? `<tr style='color:green;'><td>Children:</td><td>${d.details.num_child}</td></tr>` : `<tr style='color:red;'><td>Children:</td><td>${d.details.num_child}</td></tr>`;
    // Infants 
    var infants = booking.value.guests.infants == d.details.num_infant ? `<tr style='color:green;'><td>Infants:</td><td>${d.details.num_infant}</td></tr>` : `<tr style='color:red;'><td>Infants:</td><td>${d.details.num_infant}</td></tr>`;
    // Invoice 
    var invoice = `<tr><td>Invoice:</td><td><a href='/ledger/payments/invoice-pdf/${d.invoice}' target='_blank' class='text-primary' style='padding-left:0;'><i style='color:red;' class='fa fa-file-pdf-o'></i>&nbsp #${d.invoice}</a></td></tr>`
    // Cost 
    var cost = parseFloat(booking.value.cost_total) == parseFloat(d.cost_total) ? `<tr style='color:green;'><td>Cost:</td><td>${d.cost_total}</td></tr>` : `<tr style='color:red;'><td>Cost:</td><td>${d.cost_total}</td></tr>`;

    return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">' +
        adults +
        concession +
        children +
        infants +
        '<tr>' +
        '<td>Vehicles:</td>' +
        `<td>${vehicles}</td>` +
        '</tr>' +
        cost +
        invoice +
        '</table>';
}

const addEventListeners = function () {
    if (firstTimeTableLoad.value) {
        firstTimeTableLoad.value = false;
        booking_history_table.value.vmDataTable.on('click', 'td.details-control', function () {
            var tr = $(this).closest('tr');
            var row = booking_history_table.value.vmDataTable.row(tr);

            if (row.child.isShown()) {
                // This row is already open - close it
                row.child.hide();
                tr.removeClass('shown');
            }
            else {
                // Open this row
                row.child(format(row.data())).show();
                tr.addClass('shown');
            }
        });
    }
    helpers.namePopover($, booking_history_table.value.vmDataTable);
}
</script>

<style lang="css">
td.details-control {
    cursor: pointer;
    position: relative;
}

.vehicle_history_data td,
.vehicle_history_data th {
    padding-right: 10px;
}

td.details-control:before {
    content: "\f055";
    /* this is your text. You can also use UTF-8 character codes as I do here */
    font-family: FontAwesome;
    position: absolute;
    top: 7px;
    left: 25%;
    color: #32aad2;
}

tr.shown td.details-control:before {
    content: "\f056";
    /* this is your text. You can also use UTF-8 character codes as I do here */
    font-family: FontAwesome;
    position: absolute;
    top: 7px;
    left: 25%;
    color: #32aad2;
}
</style>

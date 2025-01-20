<template lang="html" id="booking-dashboard">
  <div class="row">
    <div class="col-lg-12" v-show="!isLoading">
      <div class="card p-3" style="overflow: auto;">
        <div class="row">
          <div class="col-lg-12">
            <button v-if="!exportingCSV" type="button" class="btn btn-outline-secondary pull-right" id="print-btn"
              @click="print()">
              <i class="fa fa-file-excel-o" aria-hidden="true"></i> Export to CSV
            </button>
            <button v-else type="button" class="btn btn-default pull-right" disabled>
              <i class="fa fa-circle-o-notch fa-spin" aria-hidden="true"></i> Exporting to CSV
            </button>
          </div>
        </div>
        <div class="row">
          <div class="col-md-4">
            <div class="form-group">
              <label for="">Campground</label>
              <select v-show="isLoading" class="form-control">
                <option value="">Loading...</option>
              </select>
              <select ref="campgroundSelector" v-if="!isLoading" class="form-control" v-model="filterCampground"
                id="filterCampground">
                <option value="All">All</option>
                <option v-for="campground in campgrounds" :value="campground.id">{{ campground.name }}</option>
              </select>
            </div>
          </div>
          <div class="col-md-4">
            <div class="form-group">
              <label for="">Region</label>
              <select v-show="isLoading" class="form-control" name="">
                <option value="">Loading...</option>
              </select>
              <select ref="regionSelector" v-if="!isLoading" class="form-control" v-model="filterRegion"
                id="filterRegion">
                <option value="All">All</option>
                <option v-for="region in regions" :value="region.id">{{ region.name }}</option>
              </select>
            </div>
          </div>
          <div class="col-md-4">
            <div class="form-group">
              <label for="">Cancelled</label>
              <select class="form-control" v-model="filterCanceled" id="filterCanceled">
                <option value="True">Yes</option>
                <option value="False">No</option>
              </select>
            </div>
          </div>
        </div>
        <div class="row" style="margin-bottom:10px;">
          <div class="col-md-4">
            <label class="form-label">
                <span class="bi bi-calendar3"></span>
                Date from: 
            </label>
            <div class="input-group date" id="booking-date-from">
              <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterDateFrom" />
            </div>
          </div>
          <div class="col-md-4">
            <label class="form-label">
                <span class="bi bi-calendar3"></span>
                Date to: 
            </label>
            <div class="input-group date" id="booking-date-to">
              <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterDateTo" />
            </div>
          </div>
          <div class="col-md-4" v-if="filterCanceled == 'True'">
            <div class="form-group">
              <label for="">Refund Status</label>
              <select class="form-control" v-model="filterRefundStatus" id="filterRefundStatus">
                <option value="All">All</option>
                <option value="Refunded">Refunded</option>
                <option value="Partially Refunded">Partially Refunded</option>
                <option value="Not Refunded">Not Refunded</option>
              </select>
            </div>
          </div>
        </div>
        <div class="row">
          <div class="col-lg-12">
            <datatable ref="bookings_table" id="bookings-table" :dtOptions="dtOptions" :dtHeaders="dtHeaders">
            </datatable>
          </div>
        </div>
      </div>
      <changebooking-component ref="changebooking" :booking_id="selected_booking" :campgrounds="campgrounds"
        @loadingCallback="changeBookingLoading" />
      <booking-history-component ref="bookingHistory" :booking_id="selected_booking" />
    </div>
    <loader :isLoading="isLoading">{{ loading.join(' , ') }}</loader>
  </div>
</template>

<script setup>
import {
  $,
  bus,
  getDateTimePicker, dateUtils,
  api_endpoints,
  helpers,
  Moment,
  swal,
  htmlEscape
} from "../../hooks.js";
import loader from "../utils/loader.vue";
import datatable from "../utils/datatable.vue";
import changebookingComponent from "./changebooking.vue";
import bookingHistoryComponent from "./history.vue";
import { useStore } from "../../apps/store.js";
import { computed, ref, onMounted, nextTick, onBeforeMount, watch } from "vue";
import { Parser } from "@json2csv/plainjs"

const store = useStore()
const exportingCSV = ref(false)
const campgroundSelector = ref(null)
const regionSelector = ref(null)
const bookings_table = ref(null)
const changebooking = ref(null)
const bookingHistory = ref(null)

const dtOptions = ref({
  responsive: false,
  serverSide: true,
  processing: true,
  searchDelay: 800,
  ajax: {
    url: api_endpoints.bookings,
    dataSrc: "results",
    data: function (d) {
      if (filterDateFrom.value) {
        d.arrival = filterDateFrom.value;
      }
      if (filterDateTo.value) {
        d.departure = filterDateTo.value;
      }
      if (filterCampground.value != "All") {
        d.campground = filterCampground.value;
      }
      if (filterRegion.value != "All") {
        d.region = filterRegion.value;
      }
      d.canceled = filterCanceled.value;
      d.refund_status = filterRefundStatus.value;

      return d;
    }
  },
  columnDefs: [
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
  ],
  columns: [
    {
      data: "campground_name",
      orderable: false,
      searchable: false
    },
    {
      data: "campground_region",
      orderable: false,
      searchable: false
    },
    {
      mRender: function (data, type, full) {
        //var name = full.firstname +" "+full.lastname;
        var first_name = full.firstname ? full.firstname : "";
        var last_name = full.lastname ? full.lastname : "";
        var name = first_name + " " + last_name;
        var max_length = 25;
        var short_name =
          name.length > max_length
            ? name.substring(0, max_length - 1) + "..."
            : name;

        var popover =
          name.length > max_length ? 'class="name_popover"' : "";
        var contact_details = '';
        //if (full.customer_account_phone != full.customer_account_mobile || full.customer_account_phone  != full.customer_booking_phone) {
        if (full.customer_account_phone) {
          contact_details += full.customer_account_phone + "<BR>";
        }
        //}
        if (full.customer_account_mobile != full.customer_account_phone && full.customer_account_mobile != full.customer_booking_phone) {
          if (full.customer_account_mobile.length > 1) {
            contact_details += full.customer_account_mobile + "<BR>";
          }
        }
        if (full.customer_booking_phone != full.customer_account_mobile && full.customer_booking_phone != full.customer_account_phone) {
          if (full.customer_booking_phone.length > 1) {
            contact_details += full.customer_booking_phone + "<BR>";
          }
        }
        var column =
          "<td ><div " +
          popover +
          ' tabindex="0" data-toggle="popover" data-placement="top" data-content="__NAME__">' +
          short_name + "<BR>" + contact_details;
        "</div></td>";
        column.replace(/__SHNAME__/g, short_name);
        return column.replace(/__NAME__/g, name);
      },
      orderable: false,
      searchable: false
    },
    {
      data: "id",
      orderable: false,
      searchable: false,
      mRender: function (data, type, full) {
        return full.status != "Canceled"
          ? "<a href='/api/get_confirmation/" +
          full.id +
          "' target='_blank' class='text-primary'>PB" +
          data +
          "</a><br/>"
          : "PB" + full.id;
      }
    },
    {
      data: "campground_site_type",
      mRender: function (data, type, full) {
        var typeCondensed = {};
        var resultList = [];
        for (var i = 0; i < data.length; i++) {
          if (data[i].campground_type === 0) {
            resultList.push(data[i].name);
            continue;
          }
          if (typeCondensed[data[i].type] == undefined) {
            typeCondensed[data[i].type] = 0;
          }
          typeCondensed[data[i].type] += 1;
        }
        for (var index in typeCondensed) {
          var count = typeCondensed[index];
          var site_type = index.split(':', 1)[0];
          resultList.push(`${count}x ${site_type}`);
        }
        if (resultList.length == 1) {
          var max_length = 15;
          var name = (resultList[0] > max_length) ? resultList[0].substring(0, max_length - 1) : resultList[0];
          var column = '<td> <div class="name_popover" tabindex="0" data-toggle="popover" data-placement="top" data-content="__NAME__" >' + name + '</div></td>';
          return column.replace('__NAME__', resultList[0]);
        }
        else if (data.length > 1) {
          var resultString = resultList.join(", ");
          var max_length = 15;
          var name = "Multiple";
          var column = '<td><span class="name_popover" tabindex="0" data-toggle="popover" data-placement="top" data-content="__NAME__" >' + name + "</span></td>";
          return column.replace("__NAME__", resultString);
        }
        return "<td></td>";
      },
      orderable: false,
      searchable: false
    },
    {
      data: "status",
      orderable: false,
      searchable: false,
      mRender: function (data, type, full) {
        if (data === "Canceled" && full.cancellation_reason != null) {
          let val = helpers.dtPopover(full.cancellation_reason);
          return `<span>${data}</span><br/><br/>${val}`;
        }
        return data;
      },
      createdCell: helpers.dtPopoverCellFn
    },
    {
      data: "arrival",
      orderable: false,
      searchable: false,
      mRender: function (data, type, full) {
        return Moment(data).format("DD/MM/YYYY");
      }
    },
    {
      data: "departure",
      orderable: false,
      searchable: false,
      mRender: function (data, type, full) {
        return Moment(data).format("DD/MM/YYYY");
      }
    },
    {
      mRender: function (data, type, full) {
        var status = data == true ? "Open" : "Temporarily Closed";
        var booking = JSON.stringify(full);
        var invoices = "";
        var invoice =
          "/ledger-toolkit-api/invoice-pdf/" + full.invoice_reference;
        var invoice_link = full.invoice_reference
          ? "<a href='" +
          invoice +
          "' target='_blank' class='text-primary'>Invoice</a><br/>"
          : "";
        var column = "<td >";
        var ledger_ui_url = $('#ledger_ui_url').val();
        console.log(ledger_ui_url);

        if (full.invoices.length > 0) {
          column += "<a href='" + ledger_ui_url + "/ledger/payments/oracle/payments?invoice_no=" + full.invoices[0] + "'>Ledger Payments</a><br>";
          column += "<a href='/booking-history/" + full.id + "'>Booking History</a><br>";

        }
        if (full.editable) {
          var change_booking =
            "<a href='/booking/change/" +
            full.id +
            "/' class='text-primary' data-change = '" +
            htmlEscape(booking) +
            "' > Change</a><br/>";
          // column += change_booking;
        }
        var cancel_booking =
          "<a href='/booking/cancel/" + full.id + "/' class='text-primary' data-cancel='" +
          htmlEscape(booking) +
          "' > Cancel</a><br/>";
        // column += cancel_booking;

        full.has_history
          ? (column +=
            "<a href='edit/" + full.id +
            "' class='text-primary' data-history = '" +
            htmlEscape(booking) +
            "' > View History</a><br/>")
          : "";
        $.each(full.active_invoices, (i, v) => {
          invoices +=
            "<a href='/ledger-toolkit-api/invoice-pdf/" +
            v +
            "' target='_blank' class='text-primary'><i style='color:red;' class='fa fa-file-pdf-o'></i>&nbsp #" +
            v +
            "</a><br/>";
        });
        column += invoices;
        column += "</td>";
        return column.replace("__Status__", status);
      },
      orderable: false,
      searchable: false
    }
  ]
})
const dtHeaders = ref([
  "Campground",
  "Region",
  "Person",
  "Confirmation #",
  " Camp Site(Type)",
  "Status",
  "From",
  "To",
  "Action"
])
const dateFromPicker = ref(null)
const dateToPicker = ref(null)
const loading = ref([])
const selected_booking = ref(-1)
const filterCampground = ref("All")
const filterRegion = ref("All")
const filterDateFrom = ref("")
const filterDateTo = ref("")
const filterCanceled = ref("False")
const filterRefundStatus = ref("All")

watch(() => filterCampground.value, function () {
  bookings_table.value.vmDataTable.ajax.reload();
})
watch(() => filterRegion.value, function () {
  bookings_table.value.vmDataTable.ajax.reload();
})
watch(() => filterCanceled.value, function () {
  bookings_table.value.vmDataTable.ajax.reload();
})
watch(() => filterRefundStatus.value, function () {
  bookings_table.value.vmDataTable.ajax.reload();
})

const isLoading = computed(function () {
  return loading.value.length > 0;
})
const regions = computed(function() {return store.getters.regions})
const campgrounds = computed(function() {return store.getters.campgrounds})

const changeBookingLoading = function (val) {
  const { value, show } = val
  if (show) {
    loading.value.push(value);
  } else {
    loading.value.splice(value, 1);
  }
}
const fetchCampgrounds = function () {
  loading.value.push("fetching campgrounds");
  if (campgrounds.value.length == 0) {
    store.dispatch("fetchCampgrounds");
  }
  loading.value.splice("fetching campgrounds", 1);
}
const fetchRegions = function () {
  if (regions.value.length == 0) {
    store.dispatch("fetchRegions");
  }
}
const cancelBooking = function (booking) {
  fetch(api_endpoints.booking(booking.id), {
      method: "DELETE",
      headers: { "X-CSRFToken": helpers.getCookie("csrftoken") }
    }).then((response) => response.json())
    .then(
      data => {
        bookings_table.value.vmDataTable.ajax.reload();
      },
      error => {
        console.log(error);
      }
    );
}
const addEventListeners = function () {
  const datepickerOptions = {
    useCurrent: false,
    keepInvalid: true,
    display: {
      buttons: {
        clear: true,
      }
    },

  };
  const dateFromPickerElement = $("#booking-date-from")
  dateFromPicker.value = getDateTimePicker(dateFromPickerElement, datepickerOptions);
  const dateToPickerElement = $("#booking-date-to")
  dateToPicker.value = getDateTimePicker(dateToPickerElement, {
    ...datepickerOptions,
    // restrictions: {
    //   minDate: dateFromPicker.value.dates.lastPicked
    // }
  }
  );

  /* View History */
  bookings_table.value.vmDataTable.on(
    "click",
    "a[data-history]",
    function (e) {
      e.preventDefault();
      var selected_booking = JSON.parse($(this).attr("data-history"));
      selected_booking.value = selected_booking.id;
      bookingHistory.value.booking = selected_booking;
      bookingHistory.value.isModalOpen = true;
    }
  );

  /* Campground Selector*/
  $(campgroundSelector.value)
    .select2({
      theme: "bootstrap"
    })
    .on("select2:select", function (e) {
      var selected = $(e.currentTarget);
      filterCampground.value = selected.val();
    })
    .on("select2:unselect", function (e) {
      var selected = $(e.currentTarget);
      filterCampground.value = "All";
    });
  /* End Campground Selector*/

  /* Region Selector*/
  $(regionSelector.value)
    .select2({
      theme: "bootstrap"
    })
    .on("select2:select", function (e) {
      var selected = $(e.currentTarget);
      filterRegion.value = selected.val();
    })
    .on("select2:unselect", function (e) {
      var selected = $(e.currentTarget);
      filterRegion.value = "All";
    });

  dateToPickerElement.on("change.td", function (e) {
    const date = dateToPicker.value.dates.lastPicked
    filterDateTo.value = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
    bookings_table.value.vmDataTable.ajax.reload();
  })

  console.log('Date from: ' + filterDateFrom.value)

  dateFromPickerElement.on("change.td", function (e) {
    const date = dateFromPicker.value.dates.lastPicked
    console.log("dateFromPicker")
    console.log(date)
    filterDateFrom.value = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
    bookings_table.value.vmDataTable.ajax.reload();
    if (date) {
      dateToPicker.value.updateOptions({
        restrictions: {
          minDate: date
        }
      });
    }
  })

  helpers.namePopover($, bookings_table.value.vmDataTable);
  $(document).on("keydown", function (e) {
    if (
      e.ctrlKey &&
      (e.key == "p" ||
        e.charCode == 16 ||
        e.charCode == 112 ||
        e.keyCode == 80)
    ) {
      e.preventDefault();
      bus.emit("showAlert", "printBooking");
      e.stopImmediatePropagation();
    }
  });
}
const printParams = function () {
  var str = [];
  let obj = {
    arrival: filterDateFrom.value != null ? filterDateFrom.value : "",
    departure: filterDateTo.value != null ? filterDateTo.value : "",
    campground: filterCampground.value != "All" ? filterCampground.value : "",
    region: filterRegion.value != "All" ? filterRegion.value : "",
    canceled: filterCanceled.value,
    "search[value]": bookings_table.value.vmDataTable.search()
  };
  for (var p in obj)
    if (obj.hasOwnProperty(p)) {
      str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
    }
  return str.join("&");
}
const print = function () {
  exportingCSV.value = true;

  fetch(api_endpoints.bookings + "?" + printParams()).then((response) => response.json()).then(
    res => {
      var data = res.results;

      var fields = ["Created"];
      //var fields = [...dtHeaders.value];
      var fields = [...fields, ...dtHeaders.value];
      fields.splice(fields.length - 1, 1);
      fields = [
        ...fields,
        "Adults",
        "Concession",
        "Children",
        "Infants",
        "Regos",
        "Canceled",
        "Cancelation Reason",
        "Cancelation Date",
        "Canceled By"
      ];
      fields.splice(4, 0, "Email");
      fields.splice(5, 0, "Phone");
      fields.splice(9, 0, "Booking Total");
      fields.splice(10, 0, "Booking Override Price");
      fields.splice(11, 0, "Override Reason");
      fields.splice(12, 0, "Amount Paid");
      fields.splice(24, 0, "Booking Type");

      var booking_types = {
        0: "Reception booking",
        1: "Internet booking",
        2: "Black booking",
        3: "Temporary reservation"
      };

      //var data = bookings_table.value.vmDataTable.ajax.json().results;
      const bookings = [];
      $.each(data, function (i, booking) {
        var bk = {};
        $.each(fields, function (j, field) {
          switch (j) {
            case 0:
              bk[field] = Moment(booking.created).format(
                "DD/MM/YYYY HH:mm:ss"
              );
              break;
            case 1:
              bk[field] = booking.campground_name;
              break;
            case 2:
              bk[field] = booking.campground_region;
              break;//filterDateFrom.value = dateFromPicker.defaultDate
            case 3:

              bk[field] = booking.firstname + " " + booking.lastname;
              break;
            case 4:
              bk[field] = booking.email;
              break;
            case 5:
              bk[field] = booking.phone;
              break;
            case 6:
              bk[field] = booking.id;
              break;
            case 7:
              var typeCondensed = {};
              var resultList = [];
              for (var i = 0; i < booking.campground_site_type.length; i++) {
                if (booking.campground_site_type[i].campground_type === 0) {
                  resultList.push(booking.campground_site_type[i].name);
                  continue;
                }
                if (typeCondensed[booking.campground_site_type[i].type] == undefined) {
                  typeCondensed[booking.campground_site_type[i].type] = 0;
                }
                typeCondensed[booking.campground_site_type[i].type] += 1;
              }
              for (var index in typeCondensed) {
                var count = typeCondensed[index];
                var site_type = index.split(':', 1)[0];
                resultList.push(`${count}x ${site_type}`);
              }
              var resultString = resultList.join(", ");
              bk[field] = resultString;
              break;
            case 8:
              bk[field] = booking.status;
              break;
            case 9:
              bk[field] = booking.cost_total;
              break;
            case 10:
              if (booking.override_reason == null) {
                bk[field] = "";
              } else {
                bk[field] = booking.cost_total - booking.discount;
              }
              break;
            case 11:
              bk[field] = booking.override_reason;
              break;
            case 12:
              bk[field] = booking.amount_paid;
              break;
            case 13:
              bk[field] = Moment(booking.arrival).format("DD/MM/YYYY");
              break;
            case 14:
              bk[field] = Moment(booking.departure).format("DD/MM/YYYY");
              break;
            case 15:
              bk[field] = booking.guests.adults;
              break;
            case 16:
              bk[field] = booking.guests.concession;
              break;
            case 17:
              bk[field] = booking.guests.children;
              break;
            case 18:
              bk[field] = booking.guests.infants;
              break;
            case 19:
              bk[field] = booking.vehicle_payment_status
                .map(r => {
                  var val = Object.keys(r).map(k => {
                    if (k == "Fee" || k == "original_type") {
                      return "avoid";
                    }
                    if (k == "Paid") {
                      if (r[k] == "Yes") {
                        return "Status" + " : Entry Fee Paid";
                      } else if (r[k] == "No") {
                        return "Status" + " : Unpaid";
                      } else if (r[k] == "pass_required") {
                        return "Status" + " : Park Pass Required";
                      }
                    } else {
                      return k + " : " + r[k];
                    }
                  });
                  return val.filter(i => i != "avoid");
                })
                .join(" | ");
              break;
            case 20:
              bk[field] = booking.is_canceled;
              break;
            case 21:
              bk[field] = booking.cancelation_reason;
              break;
            case 22:
              bk[field] = booking.cancelation_time
                ? Moment(booking.cancelation_time).format(
                  "DD/MM/YYYY HH:mm:ss"
                )
                : "";
              break;
            case 23:
              bk[field] = booking.canceled_by;
              break;
            case 24:
              if (
                typeof booking_types[booking.booking_type] !== "undefined"
              ) {
                bk[field] = booking_types[booking.booking_type];
              } else {
                bk[field] = booking.booking_type;
              }
              break;
          }
        });
        bookings.push(bk);
      });
      const parser = new Parser({ fields: fields });
      const csv = parser.parse(bookings);

      var a = document.createElement("a"),
        file = new Blob([csv], { type: "text/csv" });
      const _filterCampground =
        filterCampground.value == "All"
          ? "All Campgrounds "
          : $("#filterCampground")[0].selectedOptions[0].text;
      const _filterRegion =
        filterCampground.value == "All"
          ? filterRegion.value == "All"
            ? "All Regions"
            : $("#filterRegion")[0].selectedOptions[0].text
          : "";
      const filterDates = filterDateFrom.value
        ? filterDateTo.value
          ? "From " + filterDateFrom.value + " To " + filterDateTo.value
          : "From " + filterDateFrom.value
        : filterDateTo.value ? " To " + filterDateTo.value : "";
      const filename =
        _filterCampground + "_" + _filterRegion + "_" + filterDates + ".csv";
      if (window.navigator.msSaveOrOpenBlob)
        // IE10+
        window.navigator.msSaveOrOpenBlob(file, filename);
      else {
        // Others
        var url = URL.createObjectURL(file);
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        setTimeout(function () {
          document.body.removeChild(a);
          window.URL.revokeObjectURL(url);
        }, 0);
      }
      exportingCSV.value = false;
    },
    error => {
      exportingCSV.value = false;
      swal({
        type: "error",
        title: "Export Error",
        text: helpers.apiVueResourceError(error)
      });
    }
  ).catch(error => {
    exportingCSV.value = false;
    console.log(error)
  } )
}

onMounted(function () {
  fetchCampgrounds();
  fetchRegions();
  addEventListeners();
})

onBeforeMount(() => {
  filterDateFrom.value = Moment().startOf('day').format('DD/MM/YYYY');
  console.log("filterDateFrom.value")
  console.log(filterDateFrom.value)
  nextTick(() => {
    bookings_table.value.vmDataTable.ajax.reload();
  });
})
</script>

<style lang="css">
.text-warning {
  color: #f0ad4e;
}

@media print {
  .col-md-3 {
    width: 25%;
    float: left;
  }

  a[href]:after {
    content: none !important;
  }

  #print-btn {
    display: none !important;
  }
}
</style>

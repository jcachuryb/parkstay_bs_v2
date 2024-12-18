import $ from "jquery";
const JqueryIn = $;
import store from "./apps/store";
import { api_endpoints } from "./apps/api.js";
import { bus } from "./components/utils/eventBus.js";
import { helpers } from "./components/utils/helpers.js";
import DataTable from "datatables.net-bs5";
import DataTableBs from "datatables.net-bs5";
import "@popperjs/core/dist/umd/popper.min.js";

import { formatDate, parse as parseDate, addDays, isWithinInterval } from "date-fns";
// import moment from "@popperjs/core";
import moment from "moment/moment.js";
import { extendMoment } from "moment-range";
// import datetimepicker from 'eonasdan-bootstrap-datetimepicker';
import { DateTime, TempusDominus } from "@eonasdan/tempus-dominus";
import validate from "jquery-validation";
import bootstrap from 'bootstrap';
import slick from "slick-carousel-browserify";
import select2 from "select2";
import awesomplete from "awesomplete";
import daterangepicker from "bootstrap-daterangepicker";
import { formValidate } from "./components/utils/validator.js";
import swal from "sweetalert2";
import htmlEscape from "html-escape";

const Moment = extendMoment(moment);

const debounce = function (func, wait, immediate) {
  // Returns a function, that, as long as it continues to be invoked, will not
  // be triggered. The function will be called after it stops being called for
  // N milliseconds. If `immediate` is passed, trigger the function on the
  // leading edge, instead of the trailing.
  let timeout;
  return function () {
    const context = this;
    const args = arguments;
    const later = function () {
      timeout = null;
      if (!immediate) func.apply(context, args);
    };
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(context, args);
  };
};

const datetimepicker = TempusDominus;

const getDateTimePicker = function (element, options = {}) {
  const defaultOptions = {
    localization: {
      format: "DD/MM/YYYY",
    },
    restrictions: {},
  };
  const opts = $.extend({}, defaultOptions, options);
    // If it's a jquery object
  return new TempusDominus(element.length ? element[0] : element, opts);
};
const dateUtils = { formatDate, parseDate, addDays, isWithinInterval };

export {
  $,
  DataTable,
  DataTableBs,
  Moment,
  datetimepicker,
  DateTime,
  getDateTimePicker,
  dateUtils,
  api_endpoints,
  helpers,
  validate,
  bus,
  slick,
  select2,
  daterangepicker,
  awesomplete,
  formValidate,
  swal,
  htmlEscape,
  store,
  debounce,
};

export default {};

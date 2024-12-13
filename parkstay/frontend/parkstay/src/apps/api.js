const baseApiUrl = process.env.PARKSTAY_URL;
console.log("baseApiUrl:", baseApiUrl);
export const api_endpoints = {
  regions: baseApiUrl + "/api/regions.json",
  parks: baseApiUrl + "/api/parks.json",
  districts: baseApiUrl + "/api/districts.json",
  park_price_history: function(id) {
    return baseApiUrl + "/api/parks/price_history.json";
  },
  park_add_price: function() {
    return baseApiUrl + "/api/parks/add_price.json";
  },
  park_current_price: function(id, arrival) {
    return (
      baseApiUrl + "/api/parks/" + id + "/current_price.json?arrival=" + arrival
    );
  },
  park_entry_rate: function(id) {
    return baseApiUrl + "/api/parkentryrate/" + id + ".json";
  },
  park: function(id) {
    return baseApiUrl + "/api/parks/" + id + ".json";
  },
  // Campgrounds
  campgrounds: baseApiUrl + "/api/campgrounds.json",
  campgrounds_datatable: baseApiUrl + "/api/campgrounds/datatable_list.json",
  bulk_close: baseApiUrl + "/api/campgrounds/bulk_close.json",
  campground: function(id) {
    return baseApiUrl + "/api/campgrounds/" + id + ".json";
  },
  campground_status_history: function(id) {
    return (
      baseApiUrl +
      "/api/campgrounds/" +
      id +
      "/status_history.json?closures=True"
    );
  },
  campground_price_history: function(id) {
    return baseApiUrl + "/api/campgrounds/" + id + "/price_history.json";
  },
  campgroundStayHistory: function(id) {
    return baseApiUrl + "/api/campgrounds/" + id + "/stay_history.json";
  },
  campgroundCurrentStayHistory: function(id, start, end) {
    return (
      baseApiUrl +
      "/api/campgrounds/" +
      id +
      "/stay_history.json?start=" +
      start +
      "&end=" +
      end
    );
  },
  campground_stay_history_detail: function(id) {
    return baseApiUrl + "/api/campground_stay_history/" + id + ".json";
  },
  available_campsite_classes: function(id, start, end) {
    return (
      baseApiUrl +
      "/api/campgrounds/" +
      id +
      "/available_campsite_classes.json?arrival=" +
      start +
      "&departure=" +
      end
    );
  },
  campground_stay_history: baseApiUrl + "/api/campground_stay_history.json",
  addPrice: function(id) {
    return baseApiUrl + "/api/campgrounds/" + id + "/addPrice.json";
  },
  editPrice: function(id) {
    return baseApiUrl + "/api/campgrounds/" + id + "/updatePrice.json";
  },
  campgroundCampsites: function(id) {
    return baseApiUrl + "/api/campgrounds/" + id + "/campsites.json";
  },
  campground_booking_ranges: function() {
    return baseApiUrl + "/api/campground_booking_ranges.json";
  },
  campground_booking_ranges_detail: function(id) {
    return baseApiUrl + "/api/campground_booking_ranges/" + id + ".json";
  },
  campground_status_history_detail: function(id) {
    return (
      baseApiUrl +
      "/api/campground_booking_ranges/" +
      id +
      ".json?original=true"
    );
  },
  delete_campground_price: function(id) {
    return baseApiUrl + "/api/campgrounds/" + id + "/deletePrice.json";
  },
  // Campsites
  campsites: baseApiUrl + "/api/campsites.json",
  campsites_stay_history: baseApiUrl + "/api/campsites_stay_history.json",
  campsites_stay_history_detail: function(id) {
    return baseApiUrl + "/api/campsites_stay_history/" + id + ".json";
  },
  campsites_price_history: function(id) {
    return baseApiUrl + "/api/campsites/" + id + "/price_history.json";
  },
  campsite_current_price: function(id, start, end) {
    return (
      baseApiUrl +
      "/api/campsites/" +
      id +
      "/current_price.json?arrival=" +
      start +
      "&departure=" +
      end
    );
  },
  campsites_current_price: function() {
    return baseApiUrl + "/api/campsites/current_price_list.json";
  },
  campsite_status_history: function(id) {
    return (
      baseApiUrl + "/api/campsites/" + id + "/status_history.json?closures=True"
    );
  },
  campsite: function(id) {
    return baseApiUrl + "/api/campsites/" + id + ".json";
  },
  campsiteStayHistory: function(id) {
    return baseApiUrl + "/api/campsites/" + id + "/stay_history.json";
  },
  bulk_close_campsites: function() {
    return baseApiUrl + "/api/campsites/bulk_close.json";
  },
  campsite_booking_ranges: function() {
    return baseApiUrl + "/api/campsite_booking_ranges.json";
  },
  campsite_booking_ranges_detail: function(id) {
    return baseApiUrl + "/api/campsite_booking_ranges/" + id + ".json";
  },
  campsite_status_history_detail: function(id) {
    return (
      baseApiUrl + "/api/campsite_booking_ranges/" + id + ".json?original=true"
    );
  },
  available_campsites: function(campground, arrival, departure) {
    return (
      baseApiUrl +
      "/api/campgrounds/" +
      campground +
      "/available_campsites.json?arrival=" +
      arrival +
      "&departure=" +
      departure
    );
  },
  available_campsites_booking: function(
    campground,
    arrival,
    departure,
    booking
  ) {
    return (
      baseApiUrl +
      "/api/campgrounds/" +
      campground +
      "/available_campsites_booking.json?arrival=" +
      arrival +
      "&departure=" +
      departure +
      "&booking=" +
      booking
    );
  },
  features: baseApiUrl + "/api/features.json",
  campsite_rate: baseApiUrl + "/api/campsite_rate.json",
  campsiterate_detail: function(id) {
    return baseApiUrl + "/api/campsite_rate/" + id + ".json";
  },
  rates: baseApiUrl + "/api/rates.json",
  booking_policy: baseApiUrl + "/api/booking_policy/",
  // campsite types
  campsite_classes: baseApiUrl + "/api/campsite_classes.json",
  campsite_classes_active:
    baseApiUrl + "/api/campsite_classes.json?active_only=true",
  campsite_class: function(id) {
    return baseApiUrl + "/api/campsite_classes/" + id + ".json";
  },
  addCampsiteClassPrice: function(id) {
    return baseApiUrl + "/api/campsite_classes/" + id + "/addPrice.json";
  },
  editCampsiteClassPrice(id) {
    return baseApiUrl + "/api/campsite_classes/" + id + "/updatePrice.json";
  },
  deleteCampsiteClassPrice(id) {
    return baseApiUrl + "/api/campsite_classes/" + id + "/deletePrice.json";
  },
  campsiteclass_price_history: function(id) {
    return baseApiUrl + "/api/campsite_classes/" + id + "/price_history.json";
  },
  closureReasons: function() {
    return baseApiUrl + "/api/closureReasons.json";
  },
  priceReasons: function() {
    return baseApiUrl + "/api/priceReasons.json";
  },
  maxStayReasons: function() {
    return baseApiUrl + "/api/maxStayReasons.json";
  },
  discountReasons: function() {
    return baseApiUrl + "/api/discountReasons.json";
  },
  bulkPricing: function() {
    return baseApiUrl + "/api/bulkPricing";
  },
  //bookings
  bookings: baseApiUrl + "/api/booking.json",
  booking: function(id) {
    return baseApiUrl + "/api/booking/" + id + ".json";
  },
  booking_refunds: baseApiUrl + "/api/reports/booking_refunds",
  //other
  countries: baseApiUrl + "/api/countries.json",
  users: baseApiUrl + "/api/users.json",
  usersLookup: function(q) {
    return encodeURI(baseApiUrl + "/api/users.json?q=" + q);
  },
  profile: baseApiUrl + "/api/profile",
  contacts: baseApiUrl + "/api/contacts.json",
};

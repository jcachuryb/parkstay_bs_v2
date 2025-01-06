import Vue from "vue";

import { api_endpoints } from "../../hooks.js";
export default {
  fetchBooking(id) {
    return new Promise((resolve, reject) => {
      fetch(api_endpoints.booking(id))
        .then((response) => {
          resolve(response);
        })
        .catch((error) => {
          reject(error);
        });
    });
  },
};

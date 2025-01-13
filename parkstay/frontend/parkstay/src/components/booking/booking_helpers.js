import { api_endpoints } from "../../hooks.js";
export default {
  fetchBooking(id) {
    return new Promise((resolve, reject) => {
      fetch(api_endpoints.booking(id))
      .then((response) => response.json())
        .then((data) => {
          resolve(data);
        })
        .catch((error) => {
          reject(error);
        });
    });
  },
};

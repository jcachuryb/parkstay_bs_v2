<template lang="html">
    <div id="change-booking">
        <modal @ok="ok()" @cancel="cancel()" title="Change Booking" large>
            <form class="form-horizontal" name="changebookingForm">
                <div class="row">
                    <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                    <alert :show="success" type="success"><strong>{{successString}}</strong></alert>
                    <div class="col-lg-12">
                        <div class="form-group">
                            <label class="col-md-2 control-label pull-left"  for="Dates">Dates: </label>
                            <div class="col-md-4">
                                <div class="input-group arrivalPicker date">
                                    <input type="text" class="form-control" name="arrival" placeholder="DD/MM/YYYY">
                                    <span class="input-group-addon">
                                        <span class="glyphicon glyphicon-calendar "></span>
                                    </span>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="input-group departurePicker date">
                                    <input type="text" class="form-control" name="departure" placeholder="DD/MM/YYYY" >
                                    <span class="input-group-addon">
                                        <span class="glyphicon glyphicon-calendar"></span>
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="col-md-2 control-label pull-left"  for="Campground">Campground: </label>
                            <div class="col-md-4">
                                <select class="form-control" name="campground" v-model="booking.campground">
                                    <option value="">Select Campground</option>
                                    <option v-for="campground in campgrounds" :value="campground.id">{{campground.name}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-group" v-show="selectedCampground">
                            <label class="col-md-2 control-label pull-left"  for="Campsite">Campsite: </label>
                            <div class="col-md-4">
                                <select class="form-control"  v-show="campsites.length < 1" >
                                    <option selected value="">Loading...</option>
                                </select>
                                <select class="form-control" name="campsite" v-if="campsites.length > 0" v-model="booking.campsites">
                                    <option value="">Select Campsite</option>
                                    <option v-for="campsite in campsites" :value="campsite.id">{{campsite.name}}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            </form>
        </modal>
    </div>
</template>

<script>
import modal from '../utils/bootstrap-modal.vue'
import alert from '../utils/alert.vue'
import { $, api_endpoints, helpers, getDateTimePicker, dateUtils, Moment} from "../../hooks.js"
export default {
    name:'change-booking',
    components:{
        modal,
        alert
    },
    props:{
            booking_id:{
                type:Number,
            },
            campgrounds:{
                type:Array,
                default:function () {
                    return [];
                }
            }
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            campsites:[],
            form:null,
            booking: {
                campsites: []
            },
            errors: false,
            errorString: '',
            successString: '',
            success:false,
            arrivalPicker:null,
            departurePicker:null
        }
    },
    computed: {
        selectedCampground: function(){
            return this.booking.campground;
        },
        selectedCampsite: function(){
            return this.booking.campsites;
        },
        showError: function() {
            var vm = this;
            return vm.errors;
        }
    },
    watch:{
            selectedCampground:function () {
                let vm =this;
                if (vm.selectedCampground) {
                    vm.$http.get(api_endpoints.campgroundCampsites(vm.selectedCampground)).then((response)=>{
                        vm.campsites = response.body;
                    },(response) => {
                        console.log(response);
                    });
                }else {
                    vm.campsites = [];
                }
            }
    },
    methods:{
        ok:function () {
            let vm =this;
            if($(vm.form).valid()){
                vm.sendData();
            }
        },
        cancel:function () {
        },
        close:function () {
            this.isModalOpen = false;
        },
        fetchBooking: function(id){
            let vm = this;
            vm.$http.get(api_endpoints.booking(id)).then((response) => {
                vm.booking = response.body; vm.isModalOpen = true;
                vm.eventListeners();
            },(error) => {
                console.log(error);
            } );

        },
        sendData:function(){
            let vm = this;
            vm.errors = false;
            vm.success= false;
            var booking = vm.booking;
            vm.$parent.loading.push('processing booking');
            vm.$http.put(api_endpoints.booking(booking.id),JSON.stringify(booking),{
                    emulateJSON:true,
                    headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                }).then((response)=>{
                    vm.$parent.loading.splice('processing booking',1);
                    vm.successString= 'Booking Updated',
                    vm.success=true;
                    //vm.close();
                },(error)=>{
                    console.log(error);
                    vm.errors = true;
                    vm.errorString = helpers.apiVueResourceError(error);
                    vm.$parent.loading.splice('processing booking',1);
                });
        },
        addFormValidations: function() {
            let vm = this;
            $(vm.form).validate({
                rules: {
                    arrival:"required",
                    departure:"required",
                    campground:"required",
                    campsite:{
                        required: {
                            depends: function(el){
                                return vm.campsites.length > 0;
                            }
                        }
                    }
                },
                messages: {
                    arrival:"field is required",
                    departure:"field is required",
                    campground:"field is required",
                    campsite:"field is required"
                },
                showErrors: function(errorMap, errorList) {

                    $.each(this.validElements(), function(index, element) {
                        var $element = $(element);
                        $element.attr("data-original-title", "").parents('.form-group').removeClass('has-error');
                    });

                    // destroy tooltips on valid elements
                    $("." + this.settings.validClass).tooltip("destroy");

                    // add or update tooltips
                    for (var i = 0; i < errorList.length; i++) {
                        var error = errorList[i];
                        $(error.element)
                            .tooltip({
                                trigger: "focus"
                            })
                            .attr("data-original-title", error.message)
                            .parents('.form-group').addClass('has-error');
                    }
                }
            });
       },
       eventListeners:function () {
           const vm = this;
           const datepickerOptions = {
               display: {
                    buttons: {
                        clear: true,
                    }
                }
           };

           const bookingArrivalDate = dateUtils.parseDate(vm.booking.arrival, 'yyyy/MM/dd', new Date())
           const bookingDepartureDate = dateUtils.parseDate(vm.booking.departure, 'yyyy/MM/dd', new Date())
           const arrivalPickerElement = $('.arrivalPicker');
           const departurePickerElement = $('.departurePicker');
           
           vm.arrivalPicker = getDateTimePicker(arrivalPickerElement,
                {...datepickerOptions,
                    defaultDate: bookingArrivalDate,
                    restrictions: {
                        minDate: dateUtils.addDays(new Date(), 1)
                }}
            );
           vm.departurePicker = getDateTimePicker(departurePickerElement, 
                {...datepickerOptions,
                    defaultDate: bookingDepartureDate, 
                    restrictions: {
                        minDate: dateUtils.addDays(bookingArrivalDate, 1)
                }}
            );

           arrivalPickerElement.on('change.td', function(e) {
            const date = arrivalPicker.dates.lastPicked
            vm.booking.arrival = date ? dateUtils.formatDate(date, 'yyyy-MM-dd') : '';
            if(date){
                vm.departurePicker.updateOptions({
                   restrictions: {
                       minDate: date
                   }
               });
            }
           });
            departurePickerElement.on('change.td', function(e){
                const date = vm.departurePicker.dates.lastPicked
                vm.booking.departure = date ? dateUtils.formatDate(date, 'yyyy-MM-dd') : '';
           });
       }
   },
   mounted:function () {
       let vm =this;
       vm.form = document.forms.changebookingForm;
       vm.addFormValidations();
   }
}
</script>

<style lang="css">
</style>

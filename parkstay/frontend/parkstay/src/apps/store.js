import { createStore } from 'vuex'

import {
    $,
    api_endpoints
} from '../hooks.js'

const store = createStore({
    state: {
        alert:{
            visible:false,
            type:"danger",
            message: "La concha"
        },
        regions:[],
        parks:[],
        districts:[],
        campgrounds:[],
        campsite_classes:[],
        show_loader: false,
        app_loader_text: ''
    },
    mutations: {
        SETALERT(state, a) {
            state.alert = a;
        },
        SETREGIONS(state, regions) {
            state.regions = regions;
        },
        SETPARKS(state, parks) {
            state.parks = parks;
        },
        SETDISTRICTS(state, districts) {
            state.districts = districts;
        },
        SETCAMPGROUNDS(state,campgrounds){
            state.campgrounds = campgrounds;
        },
        SETCAMPSITECLASSES(state,campsite_classes){
            state.campsite_classes = campsite_classes;
        },
        SET_LOADER_STATE(state,val){
            state.show_loader = val;
            !val ? state.app_loader_text = '': '';
        },
        SET_LOADER_TEXT(state,val){
            state.app_loader_text = val;
        },
    },
    actions: {
        updateAlert(context,payload) {
            context.commit('SETALERT',payload);
        },
        fetchRegions(context) {
            $.get(api_endpoints.regions,function(data){
                context.commit('SETREGIONS',data);
            });
        },
        fetchParks(context) {
            $.get(api_endpoints.parks,function(data){
                context.commit('SETPARKS',data);
            });
        },
        fetchDistricts(context) {
            $.get(api_endpoints.districts,function(data){
                context.commit('SETDISTRICTS',data);
            });
        },
        fetchCampgrounds(context){
            return new Promise((resolve,reject) => {
                fetch(api_endpoints.campgrounds).then((response) => {
                    context.commit('SETCAMPGROUNDS',response.body);
                    resolve(response.body);
                }).catch((error) => {
                    reject(error);
                });
            }).catch((error) => {
                console.log(error);
            });
        },
        fetchCampsiteClasses(context){
            $.get(api_endpoints.campsite_classes,function(data){
                context.commit('SETCAMPSITECLASSES',data);
            });
        }
    },
    getters:{
        showAlert: state => {
            return state.alert.visible;
        },
        alertType: state => {
            return state.alert.type;
        },
        alertMessage: (state) =>  {
            return state.alert.message;
        },
        regions: state => {
            return state.regions;
        },
        parks: state => {
            return state.parks;
        },
        districts: state => {
            return state.districts;
        },
        campgrounds: state => {
            return state.campgrounds;
        },
        campsite_classes: state => {
            return state.campsite_classes;
        },
        app_loader_state: (state) => {
            return state.show_loader;
        },
        app_loader_text: (state) => {
            return state.app_loader_text;
        }
    }
});

export default store;
export const useStore = () => store

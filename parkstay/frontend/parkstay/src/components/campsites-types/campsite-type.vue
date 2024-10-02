<template lang="html">
    <div id="campsite-type">
        <div class="card p-3" id="applications">

            <div id="applications-collapse" class="" role="tabpanel" aria-labelledby="applications-heading">
                <div class="panel-body">
                    <div class="col-lg-12">
                        <div class="row">
                            <form v-show="!isLoading">
                                <div class="panel panel-primary">
                                    <div class="panel-heading">
                                        <h3 class="panel-title">{{ createCampsiteType ? 'New' : 'Edit' }} Campsite Type
                                        </h3>
                                    </div>
                                    <div class="panel-body">
                                        <div class="row">
                                            <div class="col-md-6">
                                                <div class="form-group">
                                                    <label class="control-label">Name</label>
                                                    <input type="text" name="name" class="form-control"
                                                        v-model="campsite_type.name" required />
                                                </div>
                                            </div>
                                            <div class="col-md-6">
                                                <div class="form-group">
                                                    <label class="control-label">Maximum Number of Vehicles</label>
                                                    <input type="number" name="max_vehicles" class="form-control"
                                                        v-model="campsite_type.max_vehicles" required />
                                                </div>
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-6">
                                                <div class="form-group">
                                                    <label class="control-label">Minimum Number of People</label>
                                                    <input type="number" name="name" class="form-control"
                                                        v-model="campsite_type.min_people" required />
                                                </div>
                                            </div>
                                            <div class="col-md-6">
                                                <div class="form-group">
                                                    <label class="control-label">Maximum Number of People</label>
                                                    <input type="number" name="name" class="form-control"
                                                        v-model="campsite_type.max_people" required />
                                                </div>
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-6">
                                                <div class="form-group">
                                                    <div class="checkbox">
                                                        <label class="checkbox-inline">
                                                            <input type="checkbox"
                                                                v-model="campsite_type.tent" />Tent</label>
                                                    </div>
                                                    <div class="checkbox">
                                                        <label class="checkbox-inline">
                                                            <input type="checkbox"
                                                                v-model="campsite_type.campervan" />Campervan</label>
                                                    </div>
                                                    <div class="checkbox">
                                                        <label class="checkbox-inline">
                                                            <input type="checkbox"
                                                                v-model="campsite_type.caravan" />Caravan</label>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <select-panel ref="select_features" :options="features"
                                            :selected="selected_features" id="select-features"></select-panel>
                                        <editor ref="descriptionEditor" v-model="campsite_type.description"></editor>
                                        <div class="row">
                                            <div class="col-sm-12">
                                                <div class="form-group pull-right">
                                                    <button type="button" v-show="createCampsiteType"
                                                        style="margin-right:5px" @click="addCampsiteType()"
                                                        class="btn btn-primary">Create</button>
                                                    <button type="button" v-show="!createCampsiteType"
                                                        style="margin-right:5px" @click="updateCampsiteType()"
                                                        class="btn btn-primary">Update</button>
                                                    <button type="button" class="btn btn-default pull-right"
                                                        @click="goBack">Cancel</button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </form>
                            <loader :isLoading="isLoading">Saving Campsite Type Data...</loader>
                        </div>
                    </div>
                    <div class="col-lg-12" v-if="!createCampsiteType">
                        <priceHistory level="campsite_class" :showAddBtn="canAddRate" ref="price_dt"
                            :object_id="campsiteTypeId" :dt_options="ph_options"
                            :historyDeleteURL="priceHistoryDeleteURL"></priceHistory>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import {
    $,
    api_endpoints,
    helpers,
    Moment,
    bus
}
    from '../../hooks.js';
import datatable from '../utils/datatable.vue'
import editor from '../utils/editor.vue'
import select_panel from '../utils/select-panel.vue'
import loader from '../utils/loader.vue'
import priceHistory from '../utils/priceHistory/priceHistory.vue'
export default {
    name: 'campsite-type',
    components: {
        "select-panel": select_panel,
        loader,
        priceHistory,
        editor
    },
    computed: {
        campsiteTypeId: function () {
            return parseInt(this.$route.params.campsite_type_id);
        },
        canAddRate: function () {
            return this.campsite_type.can_add_rate ? this.campsite_type.can_add_rate : false;
        },
        priceHistoryDeleteURL: function () {
            return api_endpoints.deleteCampsiteClassPrice(this.campsiteTypeId);
        }
    },
    data: function () {
        let vm = this;
        return {
            isLoading: false,
            campsite_type: {},
            features: [],
            selected_features: [],
            createCampsiteType: true,
            ph_options: {
                responsive: true,
                processing: true,
                deferRender: true,
                order: [
                    [0, 'desc']
                ],
                ajax: {
                    url:this.$route.params.campsite_type_id?  api_endpoints.campsiteclass_price_history(this.$route.params.campsite_type_id) : undefined,
                    dataSrc: ''
                },
                columns: [{
                    data: 'date_start',
                    mRender: function (data, type, full) {
                        return Moment(data).format('MMMM Do, YYYY');
                    }

                }, {
                    data: 'date_end',
                    mRender: function (data, type, full) {
                        if (data) {
                            return Moment(data).add(1, 'day').format('MMMM Do, YYYY');
                        }
                        else {
                            return '';
                        }
                    }

                }, {
                    data: 'adult'
                }, {
                    data: 'concession'
                }, {
                    data: 'child'
                }, {
                    data: 'details',
                    mRender: function (data, type, full) {
                        if (data) {
                            return data;
                        }
                        return '';
                    }
                }, {
                    data: 'editable',
                    mRender: function (data, type, full) {
                        if (data) {
                            var id = full.id;
                            var column = "<td ><a href='#' class='editPrice' data-date_start=\"__START__\"  data-date_end=\"__END__\"  data-rate=\"__RATE__\" data-reason=\"__REASON__\" data-details=\"__DETAILS__\">Edit</a><br/>"
                            if (full.deletable) {
                                column += "<a href='#' class='deletePrice' data-date_start=\"__START__\"  data-date_end=\"__END__\"  data-rate=\"__RATE__\" data-reason=\"__REASON__\" data-details=\"__DETAILS__\">Delete</a></td>";
                            }
                            column = column.replace(/__START__/g, full.date_start)
                            column = column.replace(/__END__/g, full.date_end)
                            column = column.replace(/__RATE__/g, full.rate_id)
                            column = column.replace(/__REASON__/g, full.reason)
                            column = column.replace(/__DETAILS__/g, full.details)
                            return column
                        }
                        else {
                            return "";
                        }
                    }
                }],
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
            },
        }
    },
    watch: {
        selected_features: {
            handler: function () {
                let vm = this;
                this.campsite_type.features = [];
                $.each(vm.selected_features, function (i, feature) {
                    vm.campsite_type.features.push(feature.url);
                });
            },
            deep: true
        }
    },
    methods: {
        init: function () {
            let vm = this;
            vm.loadFeatures();
            if (vm.$route.params.campsite_type_id) {
                vm.createCampsiteType = false;
                vm.fetchCampsiteType();
            }
        },
        goBack: function () {
            helpers.goBack(this);
        },
        loadFeatures: function () {
            var vm = this;
            var url = api_endpoints.features;
            $.ajax({
                url: url,
                dataType: 'json',
                headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
                success: function (data, stat, xhr) {
                    vm.features = data;
                }
            });
        },
        addCampsiteType: function () {
            this.sendData(api_endpoints.campsite_classes, 'POST');
        },
        updateCampsiteType: function () {
            this.sendData(api_endpoints.campsite_class(this.campsite_type.id), 'PUT');
        },
        fetchCampsiteType: function () {
            let vm = this;
            $.ajax({
                url: api_endpoints.campsite_class(vm.$route.params.campsite_type_id),
                method: 'GET',
                xhrFields: {
                    withCredentials: true
                },
                dataType: 'json',
                headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
                success: function (data, stat, xhr) {
                    vm.campsite_type = data;
                    vm.$refs.select_features.loadSelectedFeatures(data.features);
                    vm.isLoading = false;
                },
                error: function (resp) {
                    vm.isLoading = false;
                    if (resp.status == 404) {
                        vm.$router.push({
                            name: '404'
                        });
                    }
                }
            });
        },
        travel: function (url) {
            this.$router.replace({
                name: 'campsite-type-detail',
                params: {
                    campsite_type_id: 264
                }
            }, function () {
                console.log('done');
            });
        },
        sendData: function (url, method) {
            let vm = this;
            vm.isLoading = true;
            var data = vm.campsite_type;
            $.ajax({
                beforeSend: function (xhrObj) {
                    xhrObj.setRequestHeader("Content-Type", "application/json");
                    xhrObj.setRequestHeader("Accept", "application/json");
                },
                xhrFields: {
                    withCredentials: true
                },
                url: url,
                headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
                method: method,
                data: JSON.stringify(data),
                success: function (data) {
                    if (method == 'POST') {
                        vm.$router.push({
                            name: 'campsite-type-detail',
                            params: {
                                campsite_type_id: data.id
                            }
                        }, function () {
                            vm.init();
                        });
                    }
                    else {
                        vm.campsite = data;
                        setTimeout(function () {
                            vm.isLoading = false;
                        }, 500);
                    }
                }
            })
        }
    },
    mounted: function () {
        let vm = this;
        vm.init();
    }
}

</script>

<style lang="css">
.panel-body>div.row {
    margin-top: 10px;
}
</style>

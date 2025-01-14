<template>
    <div class="container" id="userInfo">
        <div class="row">
            <div class="col-sm-12">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <h3 class="panel-title">Personal Details <small>Provide your personal details</small>
                            <a class="panelClicker" :href="'#' + pBody" data-toggle="collapse" data-parent="#userInfo"
                                expanded="true" :aria-controls="pBody">
                                <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                            </a>
                        </h3>
                    </div>
                    <div class="panel-body collapse in" :id="pBody">
                        <form class="form-horizontal" name="personal_form" method="post">
                            <div class="form-group">
                                <label for="" class="col-sm-3 control-label">Given name(s)</label>
                                <div class="col-sm-6">
                                    <input type="text" class="form-control" name="first_name" placeholder=""
                                        v-model="profile.first_name">
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="" class="col-sm-3 control-label">Surname</label>
                                <div class="col-sm-6">
                                    <input type="text" class="form-control" name="last_name" placeholder=""
                                        v-model="profile.last_name">
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="col-sm-12">
                                    <button v-if="!updatingPersonal" class="pull-right btn btn-primary"
                                        @click.prevent="updatePersonal()">Update</button>
                                    <button v-else disabled class="pull-right btn btn-primary"><i
                                            class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-12">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <h3 class="panel-title">Address Details <small>Provide your address details</small>
                            <a class="panelClicker" :href="'#' + adBody" data-toggle="collapse" expanded="false"
                                data-parent="#userInfo" :aria-controls="adBody">
                                <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                            </a>
                        </h3>
                    </div>
                    <div v-if="loading.length == 0" class="panel-body collapse" :id="adBody">
                        <form class="form-horizontal" action="index.html" method="post">
                            <div class="form-group">
                                <label for="" class="col-sm-3 control-label">Street</label>
                                <div class="col-sm-6">
                                    <input type="text" class="form-control" name="street" placeholder=""
                                        v-model="profile.residential_address.line1">
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="" class="col-sm-3 control-label">Town/Suburb</label>
                                <div class="col-sm-6">
                                    <input type="text" class="form-control" name="surburb" placeholder=""
                                        v-model="profile.residential_address.locality">
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="" class="col-sm-3 control-label">State</label>
                                <div class="col-sm-3">
                                    <input type="text" class="form-control" name="country" placeholder=""
                                        v-model="profile.residential_address.state">
                                </div>
                                <label for="" class="col-sm-1 control-label">Postcode</label>
                                <div class="col-sm-2">
                                    <input type="text" class="form-control" name="postcode" placeholder=""
                                        v-model="profile.residential_address.postcode">
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="" class="col-sm-3 control-label">Country</label>
                                <div class="col-sm-4">
                                    <select class="form-control" name="country"
                                        v-model="profile.residential_address.country">
                                        <option v-for="c in countries" :value="c.iso_3166_1_a2">{{ c.printable_name }}
                                        </option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="col-sm-12">
                                    <button v-if="!updatingAddress" class="pull-right btn btn-primary"
                                        @click.prevent="updateAddress()">Update</button>
                                    <button v-else disabled class="pull-right btn btn-primary"><i
                                            class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-12">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <i v-if="showCompletion && profile.contact_details" class="fa fa-check fa-2x pull-left"
                            style="color:green"></i>
                        <i v-else-if="showCompletion && !profile.contact_details" class="fa fa-times fa-2x pull-left"
                            style="color:red"></i>
                        <h3 class="panel-title">Contact Details <small>Provide your contact details</small>
                            <a class="panelClicker" :href="'#' + cBody" data-toggle="collapse" data-parent="#userInfo"
                                expanded="false" :aria-controls="cBody">
                                <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                            </a>
                        </h3>
                    </div>
                    <div class="panel-body collapse" :id="cBody">
                        <form class="form-horizontal" action="index.html" method="post">
                            <div class="form-group">
                                <label for="" class="col-sm-3 control-label">Phone (work)</label>
                                <div class="col-sm-6">
                                    <input type="text" class="form-control" name="phone" placeholder=""
                                        v-model="profile.phone_number">
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="" class="col-sm-3 control-label">Mobile</label>
                                <div class="col-sm-6">
                                    <input type="text" class="form-control" name="mobile" placeholder=""
                                        v-model="profile.mobile_number">
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="" class="col-sm-3 control-label">Email</label>
                                <div class="col-sm-6">
                                    <input type="email" class="form-control" name="email" placeholder=""
                                        v-model="profile.email">
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="col-sm-12">
                                    <button v-if="!updatingContact" class="pull-right btn btn-primary"
                                        @click.prevent="updateContact()">Update</button>
                                    <button v-else disabled class="pull-right btn btn-primary"><i
                                            class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { $, api_endpoints, helpers } from "../../hooks.js"

const uid = crypto.randomUUID();
const adBody = 'adBody' + uid
const pBody = 'pBody' + uid
const cBody = 'cBody' + uid
const profile = ref({
    residential_address: {}
})
const countries = ref([])
const loading = ref([])
const updatingPersonal = ref(false)
const updatingAddress = ref(false)
const updatingContact = ref(false)
const personal_form = ref(null)

const updatePersonal = function () {
    updatingPersonal.value = true;
    fetch(helpers.add_endpoint_json(api_endpoints.users, (profile.value.id + '/update_personal')), {
        method: "POST",
        body: profile.value,
        headers: {
            'X-CSRFToken': helpers.getCookie('csrftoken')
        }
    }).then((response) => response.json()).then((data) => {
        console.log(response);
        updatingPersonal.value = false;
        profile.value = data;
        if (profile.value.residential_address == null) { profile.value.residential_address = {}; }
    }, (error) => {
        console.log(error);
        updatingPersonal.value = false;
    });
}
const updateContact = function () {
    updatingContact.value = true;
    fetch(helpers.add_endpoint_json(api_endpoints.users, (profile.value.id + '/update_contact')), {
        method: 'POST',
        body: profile.value,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': helpers.getCookie('csrftoken')
        }
    }).then((response) => response.json()).then((data) => {
        console.log(response);
        updatingContact.value = false;
        profile.value = data;
        if (profile.value.residential_address == null) { profile.value.residential_address = {}; }
    }).catch((error) => {
        console.log(error);
        updatingContact.value = false;
    });
}
const updateAddress = function () {
    updatingAddress.value = true;
    fetch(helpers.add_endpoint_json(api_endpoints.users, (profile.value.id + '/update_address')), {
        method: "POST",
        body: profile.value.residential_address,
        headers: {
            'X-CSRFToken': helpers.getCookie('csrftoken')
        }
    }).then((response) => response.json()).then((data) => {
        console.log(response);
        updatingAddress.value = false;
        profile.value = data;
        if (profile.value.residential_address == null) { profile.value.residential_address = {}; }
    }).catch((error) => {
        console.log(error);
        updatingAddress.value = false;
    });
}
const fetchCountries = function () {
    loading.value.push('fetching countries');
    fetch(api_endpoints.countries).then((response) => response.json()).then((data) => {
        countries.value = data;
        loading.value.splice('fetching countries', 1);
    }, (response) => {
        console.log(response);
        loading.value.splice('fetching countries', 1);
    });
}


onMounted(function () {
    fetchCountries();
    personal_form.value = document.forms.personal_form;
    $('.panelClicker[data-toggle="collapse"]').on('click', function () {
        var chev = $(this).children()[0];
        window.setTimeout(function () {
            $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
        }, 100);
    });
    fetchUserProfileData()

})

const fetchUserProfileData = () => {
    fetch(api_endpoints.profile, {
        headers: {
            'X-CSRFToken': helpers.getCookie('csrftoken')
        },
    }).then((response) => response.json()).then((data) => {
        profile.value = data
        if (profile.value.residential_address == null) { profile.value.residential_address = {}; }
    }).catch((error) => {
        console.log(error);
    })
}

</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>

<template>
    <div class="account-billing">
        <p v-show="!form.update_billing">Your billing details: <a v-on:click="form.update_billing = true" v-show="!form.update_billing"><i class=""></i>Edit Billing Details</a></p>
        <div v-show="!form.update_billing">
            <label class="billing-label">Company name: {{ form.billing.company_name }}</label>
            <label class="billing-label">Your address: {{ form.billing.address }}</label>
            <label class="billing-label">Your postal/zip code: {{ form.billing.zipcode }}</label>
            <label class="billing-label">Your city: {{ form.billing.city }}</label>
            <label class="billing-label">Your country: {{ form.billing.country }}</label>
        </div>

        <p v-show="form.update_billing">Please enter your billing details here. <a v-on:click="form.update_billing = false" v-show="form.update_billing && billing"><i class=""></i>Cancel Update</a></p>
        <div v-show="form.update_billing">
            <input type="text" name="company" v-model="form.billing.company_name" placeholder="Company name" v-bind:class="{'error': errors.company_name}" required>
            <span class="error-explain" v-if="errors.company_name">{{ errors.company_name }}</span>

            <input type="text" name="address" v-model="form.billing.address" placeholder="Your address" v-bind:class="{'error': errors.address}" required>
            <span class="error-explain" v-if="errors.address">{{ errors.address }}</span>

            <input type="text" name="name" v-model="form.billing.zipcode" placeholder="Your postal/zip code" v-bind:class="{'error': errors.zipcode}" required>
            <span class="error-explain" v-if="errors.zipcode">{{ errors.zipcode }}</span>

            <input type="text" name="city" v-model="form.billing.city" placeholder="Your city" v-bind:class="{'error': errors.city}" required>
            <span class="error-explain" v-if="errors.city">{{ errors.city }}</span>

            <input type="text" name="country" v-model="form.billing.country" placeholder="Your country" v-bind:class="{'error': errors.country}" required>
            <span class="error-explain" v-if="errors.country">{{ errors.country }}</span>
        </div>
    </div>
</template>

<script>
    import Organization from '../../store/organization'

    export default {
        props: {errors: null},
        data () {
            return {
                billing: null,
                form: {
                    update_billing: true,
                    billing: {
                        company_name: null,
                        address: null,
                        zipcode: null,
                        city: null,
                        country: null
                    }
                }
            }
        },
        created: function () {
            this.$http.get('account/billing').then((xhr) => {
                this.billing = xhr.data
                if (this.billing) {
                    this.form.update_billing = false
                    this.form.billing = this.billing
                } else if (Organization.model) {
                    this.form.billing = Organization.model
                }
                console.log(JSON.stringify(this.form))
            })
        },
        watch: {
            form: {
                handler: function (newValue) {
                    this.$emit('form-changed', newValue)
                },
                deep: true
            }
        },
        methods: {}
    }
</script>

<style>
    .account-billing {
        margin-bottom: 30px;
    }

    .account-billing p a {
        margin-left: 20px;
        cursor: pointer;
    }

    form label.billing-label {
        margin-top: 0;
        margin-left: 5px;
        font-size: 12px;
        color: #888;
        float: inherit;
    }

    form button.cta.billing-button {
        position: relative;
        top: 17px;
        padding: 0 20px;
        width: auto;
        height: 30px;
        line-height: initial;
    }

</style>

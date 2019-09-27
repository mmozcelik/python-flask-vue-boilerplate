<template>
    <div class="credits u-pull-left margin-top-12" v-if="account.model" v-bind:class="{'credits-low': isCreditsLow()}">
        <template v-if="account.model.credits.remains == 0">
            <div class="credits-progress">
                <div style="width:100%"></div>
            </div>
            <span v-show="account.model && account.model.is_verified">No credits left</span>
            <span v-show="account.model && !account.model.is_verified" class="text-red">Please verify your account to get your free credits!</span>
        </template>
        <template v-else>
            <div class="credits-progress">
                <div v-bind:style="{'width': getPercentage() + '%'}"></div>
            </div>
            <span>Requests: {{getRequests()}}/{{account.model.credits.total}}</span>
        </template>
        <div class="credits-upgrade">
            <a v-link="{ name: 'payment-plans' }" title="You rock!" class="btn" v-show="account.model && account.model.is_verified">Get more credits</a>
        </div>
    </div>
</template>

<script>
import Account from './../../store/account'

export default {
    props: {
        showButton: {
            type: Boolean,
            default: true
        }
    },
    data () {
        return {
            account: Account
        }
    },
    methods: {
        getRequests: function () {
            if (this.account.model.credits) {
                return (this.account.model.credits.total - this.account.model.credits.remains)
            }

            return 0
        },
        getPercentage: function () {
            if (this.account.model.credits.total > 0) {
                return ((this.getRequests() / this.account.model.credits.total) * 100).toFixed(2)
            } else if (this.account.model.credits.remains === 0) {
                return 100
            } else {
                return 0
            }
        },
        isCreditsLow: function () {
            return (this.getPercentage() > 80)
        }
    }
}
</script>

<style>
    .credits {
        font-weight: normal;
        padding-left: 10px;
    }
</style>

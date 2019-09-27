<template>
    <header id="app-header">
        <span class="u-pull-left mobile-menu-button" v-on:click="$parent.toggleMenu">
            <i class="fa fa-list fa-2x"></i>
        </span>
        <credits-billing></credits-billing>
        <div>
            <router-link id="logo" class="navbar-brand" to="/mycloud">
                <img src="/static/img/logo.png"/>
            </router-link>
        </div>

        <account-dropdown class="u-pull-right"></account-dropdown>

        <div id="app-auth-header"></div>
    </header>
</template>

<script>
    import './../assets/css/header.css'
    import AccountDropdown from './auth/account-dropdown.vue'
    import CreditsBilling from './misc/credits-progress.vue'
    import Account from './../store/account'

    export default {
        components: {AccountDropdown, CreditsBilling},
        data () {
            return {
                account: Account
            }
        }
    }
</script>

<style>

</style>

<template>
    <nav id="app-navigation">
        <div class="container">
            <div class="logo">
                <img src="/static/img/logo.svg">
            </div>
            <div class="btn button-success cta" v-if="account && account.model && !account.model.plan_id">
                <i class="fa fa-angle-double-up"></i>
                Upgrade Plan
            </div>
            <div class="nav-content">
                <ul class="top">
                    <li v-bind:class="{ 'active': hasRoute('/dashboard') }">
                        <router-link to="/dashboard" active-class="active" class="row">
                            <span class="col-md-2"><i class="fa fa-line-chart"></i></span>
                            <span class="col-md-10">{{$t('menu.dashboard')}}</span>
                        </router-link>
                    </li>
                    <li class="menu">
                        <span class="col-md-10">{{$t('common.menu')}}</span>
                    </li>
                    <li v-bind:class="{ 'active': hasRoute('/reports') }">
                        <router-link to="/reports" active-class="active" class="row">
                            <span class="col-md-2"><i class="fa fa-file-text-o"></i></span>
                            <span class="col-md-10">{{$t('menu.reports')}}</span>
                        </router-link>
                    </li>
                    <li v-bind:class="{ 'active': hasRoute('/rules') }">
                        <router-link to="/rules" active-class="active" class="row">
                            <span class="col-md-2"><i class="fa fa-cubes"></i></span>
                            <span class="col-md-10">{{$t('menu.rules')}}</span>
                        </router-link>
                    </li>
                </ul>
                <ul class="bottom">
                    <li class="menu-contact" v-bind:class="{ 'active': hasRoute('/contact-us') }">
                        <a href="mailto:support@myapp.com" active-class="active">
                            <span class="col-md-2"><i class="fa fa-envelope"></i></span>
                            <span class="col-md-10">{{$t('menu.contact_us')}}</span>
                        </a>
                    </li>
                    <li v-bind:class="{ 'active': hasRoute('/settings') }">
                        <router-link to="/settings" active-class="active" class="row">
                            <span class="col-md-2"><i class="fa fa-cogs"></i></span>
                            <span class="col-md-10">{{$t('menu.settings')}}</span>
                        </router-link>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
</template>

<script>
    import './../assets/css/menu.css'
    import Account from './../store/account'

    export default {
        data () {
            return {
                account: Account
            }
        },
        methods: {
            hasRoute: function (partial) {
                return (this.$route.path.indexOf(partial) > -1)
            }
        }
    }
</script>

<style>

</style>

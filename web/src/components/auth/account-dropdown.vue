<template>
    <div class="user-dropdown margin-top-10 margin-right-12">
        <div v-if="account.model">
            <span class="u-pull-left visible-xs-block visible-sm-block visible-md-block hidden-lg margin-right-20" data-toggle="collapse" data-target="#wallet-container">
                <i class="fa fa-money fa-2x"></i>
            </span>
            <span v-on:click.stop="toggleDropdown" v-bind:class="{ 'dropdown-opened': displayed }">
                <span style="display: inline-flex">
                    <span class="hidden-xs margin-top-4 margin-right-12">{{ account.model.name ? account.model.name : account.model.email}}</span>
                    <i class="fa fa-bars fa-2x"></i>
                </span>
                <ul>
                    <li>
                        <router-link to="/settings/account">
                            <i class="fa fa-user"></i>
                            {{$t('settings.account')}}
                        </router-link>
                    </li>
                    <li><a href="javascript:;" v-on:click="logout"> <i class="fa fa-sign-out"></i> {{$t('auth.logout')}}</a></li>
                </ul>
            </span>
        </div>
    </div>
</template>

<script>
    import Account from './../../store/account'
    import {event} from '../../event.js'

    export default {
        data: function () {
            return {
                account: Account,
                displayed: false
            }
        },
        created: function () {
            document.body.addEventListener('click', this.closeDropdown)
        },
        destroyed: function () {
            document.body.removeEventListener('click', this.closeDropdown)
        },
        methods: {
            logout: function () {
                this.$http.post('internal/auth/logout').then(
                    (xhr) => {
                        window.storage.removeItem('login-email', true)
                        window.sessionStorage.clear()
                        event.emit('set-session', null)
                    },
                    (xhr) => {
                        window.storage.removeItem('login-email', true)
                        window.sessionStorage.clear()
                        event.emit('set-session', null)
                    }
                )
            },
            toggleDropdown: function () {
                this.displayed = !this.displayed
            },
            closeDropdown: function () {
                if (this.displayed) {
                    this.displayed = false
                }
            }
        }
    }
</script>

<style>
    .user-dropdown span svg {
        margin-left: 5px;
    }

    .user-dropdown li svg {
        margin-right: 5px;
    }

    .user-dropdown div.u-pull-right {
        cursor: pointer;
        padding: 11px 11px 11px 0px;
        font-size: 1em;
    }

</style>

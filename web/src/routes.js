'use strict'

import {event} from './event.js'

import authMain from './components/auth/index.vue'
import loginAuth from './components/auth/login.vue'
import lostAuth from './components/auth/lost.vue'
import lostRecoverPassword from './components/auth/recover-password.vue'
import registerAuth from './components/auth/register.vue'
import resendAuth from './components/auth/resend.vue'
import validateAuth from './components/auth/validate.vue'
import deletedAuth from './components/auth/deleted.vue'

import appMain from './components/app/index.vue'
import appDashboard from './components/app/dashboard.vue'
import appSettings from './components/settings/modal.vue'
import appSettingsAccount from './components/settings/account.vue'

import Account from './store/account'

var requireAuth = function (to, from, next) {
    if (!window.storage.getItem('session')) {
        if (to.fullPath === '/') {
            console.log('no redirect to path')
            next({path: '/auth/login'})
        } else {
            console.log('redirect to path')
            next({path: '/auth/login', query: {redirect: to.fullPath}})
        }
    } else {
        if (Account && Account.model) {
            Account.applyScreenChange()
        }
        next()
    }
}

export default {
    routes: [
        {
            path: '',
            component: appMain,
            beforeEnter: requireAuth,
            children: [{
                path: 'validate',
                name: 'validate-account',
                component: validateAuth,
                children: [{
                    path: '/token/:token',
                    component: {},
                    action: 'validate'
                }]
            }, {
                path: 'settings',
                name: 'settings',
                component: appSettings,
                beforeEnter: requireAuth,
                children: [{
                    path: 'account',
                    name: 'settings-account',
                    component: appSettingsAccount,
                    beforeEnter: requireAuth
                }]
            }, {
                path: 'dashboard',
                name: 'dashboard',
                component: appDashboard,
                beforeEnter: requireAuth
            }]
        },
        {
            path: '/auth',
            component: authMain,
            children: [{
                path: 'login',
                component: loginAuth
            }, {
                path: 'token/:token',
                name: 'auth-token',
                component: {
                    created: function () {
                        event.emit('set-session', this.$route.params.token)
                        this.$router.push('/dashboard')
                    }
                }
            }, {
                path: 'lost',
                component: lostAuth
            }, {
                path: 'recover-password',
                component: lostRecoverPassword
            }, {
                path: 'deleted',
                component: deletedAuth
            }, {
                path: 'register',
                component: registerAuth
            }, {
                path: 'resend',
                component: resendAuth
            }]
        }
    ]
}

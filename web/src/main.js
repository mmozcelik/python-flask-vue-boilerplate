import Vue from 'vue'
import VueRouter from 'vue-router'
import VueResource from 'vue-resource'
import VueSweetalert from 'vue-sweetalert'
import VueAnalytics from 'vue-analytics'
import VueClipboard from 'vue-clipboard2'
import VueAlert from '@vuejs-pt/vue-alert'
import VTooltip from 'v-tooltip'
import VueI18n from 'vue-i18n'
import Loading from './components/misc/loading'
import VueSelect from './components/misc/select2'
import App from './App.vue'
import Routes from './routes'
import {event} from './event.js'
import enTranslations from './translations/en/en.js'

import Offline from 'offline-js'
import './assets/css/offline-js.css'
import moment from 'moment'
import Tooltips from './components/misc/tooltips'

// Polyfil fixes for IE (...)
if (!('remove' in Element.prototype)) {
    Element.prototype.remove = function () {
        if (this.parentNode) {
            this.parentNode.removeChild(this)
        }
    }
}

let loadApplication = function () {
    Offline.options = {
        // Should we check the connection status immediatly on page load.
        checkOnLoad: false,

        // Should we monitor AJAX requests to help decide if we have a connection.
        interceptRequests: true,

        // Should we automatically retest periodically when the connection is down (set to false to disable).
        reconnect: {
            // How many seconds should we wait before rechecking.
            initialDelay: 3
        },

        // Should we store and attempt to remake requests which fail while the connection is down.
        requests: true,

        // Should we show a snake game while the connection is down to keep the user entertained?
        // It's not included in the normal build, you should bring in js/snake.js in addition to
        // offline.min.js.
        game: false
    }

    Vue.config.productionTip = false
    Vue.use(VueRouter)
    Vue.use(VueResource)
    Vue.use(VueSweetalert)
    Vue.use(VueClipboard)
    Vue.use(VueAlert)
    Vue.use(VTooltip)
    Vue.use(VueI18n)
    Vue.component('v-select', VueSelect)
    Vue.component('loading', Loading)
    if (window.location.hostname === 'localhost' || window.location.hostname === 'dev.myapp.comm') {
        Vue.http.options.root = 'http://' + window.location.hostname + ':5000/v1'
    } else {
        Vue.http.options.root = window.location.origin + '/v1'
    }

    Vue.http.options.emulateJSON = true

    const i18n = new VueI18n({locale: 'en', messages: {en: enTranslations}})

    const router = new VueRouter({
        // history: true,
        routes: Routes.routes
    })

    if (window.location.hostname === 'app.myapp.com') {
        Vue.use(VueAnalytics, {
            id: 'UA-???-?',
            router: router
        })
    }

    router.beforeEach(function (to, from, next) {
        // We clear the tooltips :
        Tooltips(document.body).clear()

        next()
    })

    Vue.filter('no-decimals', function (value) {
        return value !== undefined ? value.substr(0, value.length - 3) : '-'
    })

    Vue.filter('numberformat', function (value, decimal) {
        return value !== undefined ? parseFloat(value).toFixed(decimal) : '-'
    })

    Vue.filter('dateformat', function (value, format = 'YYYY/MM/DD') {
        return value !== undefined ? moment.utc(value).local().format(format) : '-'
    })

    Vue.filter('timeformat', function (value, format = 'HH:mm:ss') {
        return value !== undefined ? moment.utc(value).local().format(format) : '-'
    })

    Vue.filter('datetimeformat', function (value, format = 'YYYY/MM/DD HH:mm:ss') {
        return value !== undefined ? moment.utc(value).local().format(format) : '-'
    })

    Vue.filter('relativeTime', function (value) {
        return value !== undefined ? moment.utc(value).fromNow() : '-'
    })

    Vue.filter('difference', function (value, format = 'HH:mm:ss') {
        var prefix = (value < 0 ? '-' : '')
        value = Math.abs(value)
        var totalSeconds = parseInt(value / 1000)
        var seconds = totalSeconds % 60
        var totalMinutes = parseInt(totalSeconds / 60)
        var minutes = parseInt(totalMinutes % 60)
        var totalHour = parseInt(totalSeconds / 3600)
        var hour = parseInt(totalHour % 24)

        var result = prefix + format.replace('HH', prefixNumber(hour, 2)).replace('mm', prefixNumber(minutes, 2)).replace('ss', prefixNumber(seconds, 2))

        return result
    })

    let prefixNumber = function (value, zeroCount) {
        var prefix = ''
        for (var count = 0; count < zeroCount - (('' + value).length); count++) {
            prefix += '0'
        }
        return prefix + value
    }

    event.init()
    window.vmEvent = event
    window.vm = new Vue(Vue.util.extend({
        router: router,
        i18n: i18n
    }, App)).$mount('#app')
}
if (window.addEventListener) {
    window.addEventListener('load', loadApplication, false)
} else if (window.attachEvent) {
    window.attachEvent('onload', loadApplication)
} else {
    window.onload = loadApplication
}

window.storage = {
    setItem: function (key, value, useSession) {
        if (typeof Storage !== 'undefined') {
            try {
                if (useSession) {
                    return window.sessionStorage.setItem(key, value)
                } else {
                    return window.localStorage.setItem(key, value)
                }
            } catch (e) {
                // Pass here
            }
        }

        return null
    },
    getItem: function (key, useSession) {
        if (typeof Storage !== 'undefined') {
            try {
                if (useSession) {
                    return window.sessionStorage.getItem(key)
                } else {
                    return window.localStorage.getItem(key)
                }
            } catch (e) {
                // Pass here
            }
        }

        return null
    },
    removeItem: function (key, useSession) {
        if (typeof Storage !== 'undefined') {
            try {
                if (useSession) {
                    return window.sessionStorage.removeItem(key)
                } else {
                    return window.localStorage.removeItem(key)
                }
            } catch (e) {
                // Pass here
            }
        }

        return null
    }
}

window.DelayedUserEngage = function () {
}

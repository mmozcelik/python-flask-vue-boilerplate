<template>
    <div id="app">
        <router-view></router-view>
    </div>
</template>


<script>
    import './assets/css/skeleton.css'
    import './assets/css/body.css'

    import {event} from './event.js'
    import Account from './store/account'
    import Application from './store/application'

    import Vue from 'vue'

    export default {
        name: 'app',
        data: function () {
            return {}
        },
        created: function () {
            let session = window.storage.getItem('session')
            if (session) {
                Vue.http.options.headers = {'auth-token': session}
            }
            let self = this
            Vue.http.interceptors.push(function (request, next) {
                next((response) => {
                    window.storage.setItem('time', new Date().getTime(), true)
                    if (response.status === 401) {
                        event.emit('set-session', null, false, '/auth/login?loggedout=1&result=' + (response.data.error || ''))
                    } else if (response.status === 402 && response.data && response.data.redirect) {
                        self.$route.push(response.data.redirect)
                    }
                })
            })

            if (['auth-token', 'validate-account'].indexOf(this.$route.name) === -1 && session !== null) {
                event.emit('set-session', session)
            }

            event.on('set-session', (session, noRedirect, redirectUrl) => {
                if (session === null) {
                    if (window.storage.getItem('session') !== null) {
                        window.storage.removeItem('session')
                        redirectUrl = redirectUrl || '/auth/login?loggedout=1'
                    } else {
                        redirectUrl = redirectUrl || '/auth/login'
                    }
                    if (!noRedirect) {
                        this.$router.push(redirectUrl)
                    }
                } else {
                    window.storage.setItem('session', session)
                    Vue.http.options.headers = {'auth-token': session}

                    // Initialize environment
                    Vue.http.get('internal/account/data').then((xhr) => {
                        Account.setModel(xhr.data)

                        return xhr
                    }, (xhr) => {
                        event.emit('set-session', null)

                        return xhr
                    })

                    // if (!window.storage.getItem('session-info', true)) {
                    //     Vue.http.get('account/data').then((xhr) => {
                    //         Account.setSession(xhr.data.session)
                    //
                    //         window.storage.setItem('session-info', JSON.stringify(xhr.data))
                    //
                    //         return xhr
                    //     }, (xhr) => {
                    //         return xhr
                    //     })
                    // } else {
                    //     let data = JSON.parse(window.storage.getItem('session-info', true))
                    //     Account.setSession(data, true)
                    // }

                    // Check if the last time we fetch application data was longer than 5 mins if so refetch it
                    // if (!window.storage.getItem('application-info') || window.storage.getItem('application-info') === 'null' || window.storage.getItem('application-last-fetch') < (new Date().getTime() - 300000)) {
                    //     Vue.http.get('app/info').then((xhr) => {
                    //         Application.set(xhr.data)
                    //
                    //         window.storage.setItem('application-info', JSON.stringify(xhr.data))
                    //         window.storage.setItem('application-last-fetch', new Date().getTime())
                    //
                    //         return xhr
                    //     }, (xhr) => {
                    //         return xhr
                    //     })
                    // } else {
                    //     let data = JSON.parse(window.storage.getItem('application-info'))
                    //     Application.set(data, true)
                    // }
                }
            })
        },
        methods: {}
    }
</script>

<style>
    #app {
        width: 100%;
        height: 100%;
    }
</style>

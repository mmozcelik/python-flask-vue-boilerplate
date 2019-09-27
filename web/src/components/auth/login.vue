<template>
    <div class="login">
        <h1 v-if="! loggedOut">{{$t('auth.welcome_back')}}</h1>
        <template v-if="loggedOut">
            <h1 v-show="!logoutReason">{{$t('auth.goodbye')}}</h1>
            <h5 v-html="$t('auth.logout_successful')" v-show="!logoutReason"></h5>
            <h5 class="text-red" style="font-size: 26px;" v-html="$t('auth.' + logoutReason)" v-if="logoutReason"></h5>
        </template>
        <form v-on:submit.prevent="onSubmit" ref="loginForm">
            <i class="fas fa-user"></i>
            <input type="email" name="email" v-model="email" v-bind:placeholder="$t('auth.your_email')" required/>
            <i class="fas fa-lock"></i>
            <input type="password" name="password" v-model="password" v-bind:placeholder="$t('auth.your_password')" required/>
            <div class="non-human-panel">
                <div class="u-pull-left">
                    <img v-bind:src="'/static/resimler/botlar/bot' + randomImageId + '.png'"/>
                </div>
                <div class="u-pull-right">
                    <img src="/static/resimler/botlar/nonhuman.png"/>
                    <div ref="recaptchaEl" name="g-recaptcha" class="g-recaptcha"
                         data-sitekey="6LfBwbkUAAAAANNWvywrXTB1sM4Cet0WlXK6cNHu" required></div>
                </div>
            </div>
            <template v-if="loading">
                <div class="fakeSubmit">
                    <div class="spinner">
                        <div class="bounce1"></div>
                        <div class="bounce2"></div>
                        <div class="bounce3"></div>
                    </div>
                </div>
            </template>
            <template v-else>
                <input type="submit" v-bind:value="$t('auth.login')"/>
            </template>
        </form>

        <router-link to="/auth/lost" class="u-pull-left">{{$t('auth.lost_your_password')}}</router-link>
        <router-link to="/auth/resend" v-if="showSendVerifyLink">{{$t('auth.resend_verification_link')}}</router-link>
        <router-link to="/auth/register" class="u-pull-right">{{$t('auth.create_account')}}</router-link>
    </div>
</template>

<script>
    /* global grecaptcha */
    import Account from './../../store/account'
    import Tooltips from './../misc/tooltips'
    import {event} from '../../event.js'

    export default {
        data: function () {
            return {
                email: window.storage.getItem('login-email', true),
                password: null,
                loggedOut: false,
                logoutReason: null,
                loading: false,
                showSendVerifyLink: false,
                randomImageId: Math.floor((Math.random() * 6) + 1)
            }
        },
        created: function () {
            if (window.document.location.hash.indexOf('loggedout') >= 0) {
                this.loggedOut = true
            }

            if (this.$route.query.result) {
                switch (this.$route.query.result) {
                    case 'verification_problem':
                    case 'verification_link_expired':
                    case 'invalid_verify_link':
                        this.showSendVerifyLink = true
                    case 'already_verified':
                        this.$alert.warning({message: this.$i18n.t('auth.' + this.$route.query.result), duration: 10000000})

                        break
                    case 'verify_success':
                    case 'successfully_registered':
                        this.$alert.info({message: this.$i18n.t('auth.' + this.$route.query.result), duration: 10000000})
                        break
                    case 'no_bots':
                    case 'stop_refresh_or_reset':
                        this.logoutReason = this.$route.query.result
                        break
                    default:
                        break
                }
                this.$router.push({query: []})
            }
        },
        mounted: function () {
            if (this.isProduction()) {
                grecaptcha.render(this.$refs.recaptchaEl)
            }
        },
        methods: {
            onSubmit: function () {
                let tooltips = Tooltips(this.$refs.loginForm)
                let captchaText = null
                if (this.isProduction()) {
                    let recaptchaResponse = document.getElementsByName('g-recaptcha-response')[0]
                    captchaText = recaptchaResponse.value
                    if (captchaText.length === 0) {
                        tooltips.error({'g-recaptcha': ['Please fill recaptcha!']})
                        return
                    }
                }

                tooltips.clear()
                window.storage.setItem('login-email', this.email, true)

                this.error = null
                this.loading = true
                this.$http.post('internal/auth/login', {
                    email: this.email,
                    password: this.password,
                    captcha: captchaText
                }).then(
                    (xhr) => {
                        if (xhr.data.token) {
                            Account.setModel(xhr.data.account)
                            event.emit('set-session', xhr.data.token)

                            if (this.$route.query.redirect) {
                                this.$router.push(this.$route.query.redirect)
                            } else {
                                this.$router.push('/dashboard')
                            }
                        } else {
                            this.loading = false
                            if (this.isProduction()) {
                                grecaptcha.reset()
                            }
                            tooltips.error({'email': ['There is a problem with the login!']})
                        }
                    },
                    (response) => {
                        this.loading = false
                        if (this.isProduction()) {
                            grecaptcha.reset()
                        }
                        tooltips.error(response.data)

                        return response
                    }
                )
            },
            isProduction: function () {
                return window.location.hostname.indexOf('myapp.com') !== -1 || window.location.hostname.indexOf('elasticbeanstalk.com') !== -1
            }
        }
    }
</script>

<style>
    .fakeSubmit {
        height: 45px;
        background: #449039;
        border-radius: 3px;
        padding: 14px;
        letter-spacing: 1.5px;
        font-family: "brandon-grotesque", sans-serif;
        text-transform: uppercase;
        font-size: 11px;
        margin-bottom: 0;
    }

    .spinner {
        margin: 0 auto;
        width: 70px;
        text-align: center;
    }

    .spinner > div {
        width: 10px;
        height: 10px;
        background-color: #fff;

        border-radius: 100%;
        display: inline-block;
        -webkit-animation: sk-bouncedelay 1.4s infinite ease-in-out both;
        animation: sk-bouncedelay 1.4s infinite ease-in-out both;
    }

    .spinner .bounce1 {
        -webkit-animation-delay: -0.32s;
        animation-delay: -0.32s;
    }

    .spinner .bounce2 {
        -webkit-animation-delay: -0.16s;
        animation-delay: -0.16s;
    }

    @-webkit-keyframes sk-bouncedelay {
        0%, 80%, 100% {
            -webkit-transform: scale(0)
        }
        40% {
            -webkit-transform: scale(1.0)
        }
    }

    @keyframes sk-bouncedelay {
        0%, 80%, 100% {
            -webkit-transform: scale(0);
            transform: scale(0);
        }
        40% {
            -webkit-transform: scale(1.0);
            transform: scale(1.0);
        }
    }
</style>

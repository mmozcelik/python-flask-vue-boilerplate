<template>
    <div>
        <h1>{{$t('auth.nice_to_meet')}}</h1>

        <p v-show="ref" class="margin-top-10"><i class="fa fa-check"></i>You are using the referral link of user {{ref}}</p>
        <form v-on:submit.prevent="onSubmit">
            <i class="fa fa-user"></i>
            <input type="text" v-model="name" v-bind:placeholder="$t('auth.your_name')" required/>
            <i class="fa fa-user"></i>
            <input type="email" v-model="email" v-bind:placeholder="$t('auth.your_email')" required/>
            <i class="fa fa-lock"></i>
            <input type="password" v-model="password" v-bind:placeholder="$t('auth.your_password')" required/>
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
                <input type="submit" value="Sign up now!"/>
            </template>
        </form>

        <router-link to="/auth/login" class="u-pull-right">{{$t('auth.already_have_account')}}</router-link>
    </div>
</template>


<script>
    /* global grecaptcha */

    import Tooltips from './../misc/tooltips'

    export default {
        data: function () {
            return {
                email: null,
                password: null,
                name: null,
                loading: false,
                showTooltip: false,
                conversionId: null,
                ref: window.storage.getItem('ref', true) || this.$route.query.ref,
                randomImageId: Math.floor((Math.random() * 6) + 1)
            }
        },
        created: function () {
            if ('tap' in window) {
                window.tap('conversion', null, 0, {}, null, (conversion) => {
                    this.conversionId = conversion.id
                })
            }
        },
        mounted: function () {
            if (this.isProduction()) {
                grecaptcha.render(this.$refs.recaptchaEl)
            }
        },
        methods: {
            mouseOver: function () {
                this.showTooltip = true
            },
            mouseOut: function () {
                this.showTooltip = false
            },
            onSubmit: function () {
                let tooltips = Tooltips(document.querySelector('form'))
                tooltips.clear()
                let captchaText = null
                if (this.isProduction()) {
                    let recaptchaResponse = document.getElementsByName('g-recaptcha-response')[0]
                    captchaText = recaptchaResponse.value
                    if (captchaText.length === 0) {
                        tooltips.error({'g-recaptcha': ['Please fill recaptcha!']})
                        return
                    }
                }

                this.error = null
                this.loading = true
                let params = {
                    email: this.email,
                    password: this.password,
                    name: this.name,
                    captcha: captchaText || '-'
                }

                this.$http.post('internal/account/', params).then(
                    (xhr) => {
                        this.$router.push('/auth/login?result=successfully_registered')

                        window.sessionStorage.removeItem('ref')
                        this.loading = false
                    },
                    (response) => {
                        this.loading = false
                        tooltips.error(response.data)
                        if (this.isProduction()) {
                            grecaptcha.reset()
                        }

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

    p.em-c-explain {
        margin-top: 20px;
    }

    .em-c-back {
        width: 100%;
        text-align: center;
        display: inline-block;
        margin-top: 8px;
        border: 2px solid #e2e2e2;
        padding: 10px;
        border-radius: 3px;
    }

    .email {
        position: relative;
    }

    .email p {
        position: absolute;
        visibility: hidden;
        top: -76px;
        background: #fff;
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 3px;
        padding: 10px;
        width: 195px;
        right: -68px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        transform: translateY(6px);
        opacity: 0;
        -webkit-transition: all .25s ease-in-out;
        -moz-transition: all .25s ease-in-out;
        -o-transition: all .25s ease-in-out;
        transition: all .25s ease-in-out;
    }

    .email.tt-open p {
        visibility: visible;
        opacity: 1;
        transform: translateY(0);
    }

    .email svg {
        position: absolute;
        right: 14px;
        top: 15px;
        opacity: 0.2;
        width: 12px;
        cursor: pointer;
        -webkit-transition: all .25s ease-in-out;
        -moz-transition: all .25s ease-in-out;
        -o-transition: all .25s ease-in-out;
        transition: all .25s ease-in-out;
    }

    .email svg:hover {
        opacity: 1;
    }

    .myapp .auth-wrapper svg.fa-check {
        position: initial;
        margin-right: 4px;
        color: green;
    }
</style>

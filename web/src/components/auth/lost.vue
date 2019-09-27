<template>
    <div>
        <h1 class="lost-title">{{$t('auth.lost_it_happens')}}</h1>
        <template v-if="! sent">
            <h5 v-html="$t('auth.lost_description')"></h5>
            <form v-on:submit.prevent="submit">
                <i class="fas fa-user"></i>
                <input type="email" v-model="email" v-bind:placeholder="$t('auth.your_email')" required/>
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
                <template v-if="error">
                    <p class="error">{{error}}</p>
                </template>
                <input type="submit" v-bind:value="$t('auth.retrieve_password')"/>
            </form>
        </template>
        <template v-if="sent">
            <p class="success">{{$t('auth.reset_link_sent')}}</p>
        </template>
        <router-link to="/auth/login" class="u-center">{{$t('auth.back_to_login')}}</router-link>
    </div>
</template>

<script>
    /* global grecaptcha */
    import Tooltips from './../misc/tooltips'

    export default {
        data: function () {
            return {
                email: window.storage.getItem('login-email', true),
                sent: false,
                error: false,
                randomImageId: Math.floor((Math.random() * 6) + 1)
            }
        },
        mounted: function () {
            if (this.isProduction()) {
                grecaptcha.render(this.$refs.recaptchaEl)
            }
        },
        methods: {
            submit: function () {
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

                this.$http.post('internal/auth/lost', {
                    email: this.email,
                    captcha: captchaText
                }).then(
                    (xhr) => {
                        this.sent = true
                    },
                    (response) => {
                        tooltips.error(response.data)
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

    a.button-gmail {
        color: #fff !important;
        width: 100%;
        height: 45px;
        display: block;
        font-size: 11px !important;
        padding: 4px;
        letter-spacing: 1.5px;
    }

    h1.lost-title {
        margin-bottom: 20px !important;
    }

    .u-center {
        text-align: center;
        width: 100%;
        display: block;
    }

</style>

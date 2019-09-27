<template>
    <div>
        <h1>{{$t('auth.resend_verification_link')}}</h1>

        <form v-on:submit.prevent="onSubmit">
            <div class="email" v-bind:class="{'tt-open': showTooltip}">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50" width="15" height="15" v-on:mouseover="mouseOver" v-on:mouseout="mouseOut">
                    <path d="M25,0A25,25,0,1,0,50,25,25,25,0,0,0,25,0Zm-.58,8.2A4.37,4.37,0,1,1,20,12.57,4.37,4.37,0,0,1,24.42,8.2Zm7.84,31h-14v-1a18.36,18.36,0,0,0,2-.44,3.07,3.07,0,0,0,1-.51,2.11,2.11,0,0,0,.64-1,7.12,7.12,0,0,0,.24-2.12v-9c0-.88,0-1.58-.07-2.12a2.16,2.16,0,0,0-.5-1.29A2.62,2.62,0,0,0,20.23,21a16.59,16.59,0,0,0-2.49-.4V19.54l8.33-.19h2.18V34.06a7.19,7.19,0,0,0,.29,2.46,2,2,0,0,0,1.09,1,11,11,0,0,0,2.63.63v1Z"/>
                </svg>
                <input type="email" v-model="email" v-bind:placeholder="$t('auth.your_email')" required/>
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
                <input type="submit" value="Resend now!"/>
            </template>
        </form>

        <router-link to="/auth/login" class="u-pull-left">{{$t('auth.back_to_login')}}</router-link>
        <router-link to="/auth/register" class="u-pull-right">{{$t('auth.create_account')}}</router-link>
    </div>
</template>


<script>
    import Tooltips from './../misc/tooltips'

    export default {
        data: function () {
            return {
                email: null,
                loading: false,
                showTooltip: false
            }
        },
        created: function () {
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

                this.error = null
                this.loading = true
                let params = {
                    email: this.email
                }

                this.$http.post('internal/auth/resend', params).then(
                    (xhr) => {
                        this.$alert.info({message: this.$i18n.t('auth.successfully_resend')})
                        this.loading = false
                    },
                    (response) => {
                        this.loading = false
                        tooltips.error(response.data)

                        return response
                    }
                )
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
</style>

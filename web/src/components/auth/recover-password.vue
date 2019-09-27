<template>
    <div>
        <h1 class="lost-title">{{$t('auth.lets_recovery')}}</h1>
        <template v-if="!sent">
            <form v-on:submit.prevent="submit">
                <i class="fas fa-lock"></i>
                <input type="password" v-model="request.password" v-bind:placeholder="$t('auth.your_password')" required/>
                <i class="fas fa-lock"></i>
                <input type="password" v-model="request.repassword" v-bind:placeholder="$t('auth.your_repassword')" required/>
                <input type="submit" v-bind:value="$t('auth.change_password')"/>
            </form>
        </template>
        <template v-if="sent">
            <p class="success">{{$t('auth.resetted_password')}}</p>
        </template>
        <router-link to="/auth/login" class="u-center">{{$t('auth.back_to_login')}}</router-link>
    </div>
</template>

<script>
    import Tooltips from './../misc/tooltips'

    export default {
        data: function () {
            return {
                request: {
                    password: null,
                    repassword: null
                },
                sent: false
            }
        },
        methods: {
            submit: function () {
                let tooltips = Tooltips(document.querySelector('form'))
                tooltips.clear()

                this.request.authKey = this.$route.query['ze']
                this.$http.post('internal/auth/recover', this.request).then(
                    (xhr) => {
                        this.sent = true
                    },
                    (response) => {
                        tooltips.error(response.data)
                    }
                )
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

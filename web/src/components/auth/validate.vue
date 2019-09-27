<template>
    <div>
        <h1 class="lost-title">Uh Oh..</h1>
        <p class="error">We were not able to validate your email, the token has expired.</p>
        <p class="error">Maybe you already validated it? If not, contact us and we'll see what we can do!</p>
    </div>
</template>

<script>
export default {
    data () {
        return {
            hasError: false
        }
    },
    init: function () {
        if (window.storage.getItem('session') !== null) {
            window.storage.removeItem('session')
        }
    },
    mounted: function () {
        this.$http.post('internal/account/email/validate', {'token': this.$route.params.token}).then(
            (xhr) => {
                window.storage.setItem('email-validated', true, true)
                window.DelayedUserEngage('userengage', 'event.validated-email')
                if (window.fbq) {
                    window.fbq('track', 'CompleteRegistration')
                }
                this.$router.push('/auth/login')
            },
            (xhr) => {
                this.hasError = true
            }
        )
    }
}
</script>

<style>
h1.lost-title {
    margin-bottom:20px!important;
}

.u-center {
    text-align:center;
    width:100%;
    display:block;
}
</style>

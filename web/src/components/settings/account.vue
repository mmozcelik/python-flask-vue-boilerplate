<template>
    <div class="settings-modal">
        <h3>Account settings</h3>
        <form v-on:submit.prevent="update" ref="form">
            <div>
                <label>{{$t('settings.email')}}</label>
                <input type="text" v-model="account.email" disabled/>
            </div>
            <div>
                <label>{{$t('settings.old_password')}}</label>
                <input type="password" name="oldPassword" v-bind:placeholder="$t('settings.old_password_placeholder')" v-model="oldPassword" v-on:keyup="resetBtnState"/>
            </div>
            <div>
                <label>{{$t('settings.password')}}</label>
                <input type="password" name="password" pattern='.{8,64}' maxlength="64" v-bind:placeholder="$t('settings.password_placeholder')" v-model="password" v-on:keyup="resetBtnState"/>
            </div>
            <div>
                <label>{{$t('settings.repassword')}}</label>
                <input type="password" name="repassword" pattern='.{8,64}' maxlength="64" v-bind:placeholder="$t('settings.repassword_placeholder')" v-model="repassword" v-on:keyup="resetBtnState"/>
            </div>
            <div class="button-container">
                <span style="margin-top: 5px">
                    <input type="submit" v-bind:value="$t('settings.update')" class="btn" v-if="!saved"/>
                    <input type="button" v-bind:value="$t('settings.saved')" class="btn" disabled v-if="saved">
                </span>
            </div>
        </form>
    </div>
</template>

<script>
    import Account from './../../store/account'
    import Tooltips from './../misc/tooltips'
    import {event} from './../../event.js'

    export default {
        components: {},
        data: function () {
            return {
                saved: false,
                confirmDeleteAccount: false,
                invalidPassword: false,
                password: '',
                repassword: '',
                oldPassword: '',
                account: {email: null, freezed: false, deleted: false}
            }
        },
        created: function () {
            if (!Account.model) {
                this.$watch(() => Account.model, (model) => {
                    this.account.email = model.email
                })
                this.$watch(() => Account.session, (session) => {
                    this.account.freezed = session.freezed
                    this.account.deleted = session.deleted
                })
            } else {
                this.account.email = Account.model.email
                this.account.freezed = Account.session.freezed
                this.account.deleted = Account.session.deleted
            }
        },
        methods: {
            update: function () {
                this.saved = true
                let form = Tooltips(this.$refs.form)
                form.clear()

                if (!this.oldPassword || this.oldPassword.length === 0) {
                    form.error({oldPassword: [this.$i18n.t('settings.old_password_empty')]})
                    return
                } else if (!this.password || this.password.length === 0) {
                    form.error({password: [this.$i18n.t('settings.new_password_empty')]})
                    return
                } else if (this.password !== this.repassword) {
                    form.error({password: [this.$i18n.t('settings.passwords_dont_match')]})
                    return
                }

                this.$http.post('account/password', {oldPassword: this.oldPassword, newPassword: this.password}).then(
                    (xhr) => {
                        this.$alert.info({message: this.$i18n.t('settings.successfully_updated')})
                    },
                    (xhr) => {
                        this.saved = false
                        form.error({btgAddress: [this.$i18n.t('settings.' + xhr.data.error)]})
                    }
                )
            },
            resetBtnState: function () {
                this.saved = false
            }
        }
    }
</script>
<style>
    .modal .settings-modal form > div.button-container {
        margin-top: 8px;
        border: none;
    }

    .modal .settings-modal .btn {
        margin-left: 15px;
        margin-top: 0px;
    }
</style>

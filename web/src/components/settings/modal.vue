<template>
    <div class="modal modal-settings modal-visible" tabindex="-1" role="dialog">
        <div class="modal-dialog is-visible">
            <div class="modal-content">
                <div class="modal-header">
                    <span class="close" aria-hidden="true" data-dismiss="modal" aria-label="Close" v-on:click="close">×</span>
                    <ul class="nav nav-tabs">
                        <router-link to="/settings/account" tag="li" role="presentation" active-class="active">
                            <a>
                                <i class="fa fa-user fa-2x"></i>
                                <div>{{$t('settings.account')}}</div>
                            </a>
                        </router-link>
                    </ul>
                </div>
                <div class="modal-body">
                    <div class="tab-content">
                        <router-view></router-view>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import './../../assets/css/modal.css'
import Modal from '../misc/modal.mixin'

export default {
    data () {
        return {
            previousUrl: '/dashboard'
        }
    },
    mixins: [Modal],
    route: {
        activate: function (transition) {
            if (transition.from && transition.from.path && transition.from.path.indexOf('settings') === -1) {
                this.previousUrl = transition.from.path
            }

            transition.next()
        }
    },
    events: {
        modalClose: function () {
            this.close()
        }
    }
}
</script>

<style>
    .modal-settings .modal-header ul li.active a {
        background:#fff;
    }
    .modal-settings .modal-header ul li a:hover {
        background:#fff;
    }

     .modal-settings .modal-header ul li.active a:after,  .modal-settings .modal-header ul li.active a:before {
    	left: 100%;
    	top: 50%;
    	border: solid transparent;
    	content: " ";
    	height: 0;
    	width: 0;
    	position: absolute;
    	pointer-events: none;
    }

     .modal-settings .modal-header ul li.active a:after {
    	border-color: rgba(255, 255, 255, 0);
    	border-left-color: #fff;
    	border-width: 7px;
    	margin-top: -7px;
    }
     .modal-settings .modal-header ul li.active a:before {
    	border-color: rgba(226, 223, 220, 0);
    	border-left-color: #E2DFDC;
    	border-width: 8px;
    	margin-top: -8px;
    }

    .modal-settings .modal-header ul li a:first-child {
        border-radius:5px 0 0 0;
    }
    .modal-settings .modal-content {
        height:100%;
    }

    .modal-settings .modal-body .tab-content h3 {
        font-size: 25px;
        margin-bottom: 5px;
        color: #A09D99;
    }
    .modal-settings .modal-body .tab-content h5 {
        font-size: 15px;
        margin-bottom: 10px;
        color: #A09D99;
    }
    .modal-settings .modal-body .tab-content form > div {
        border-bottom: 1px solid #EAEAEA;
        height: 44px
    }
    .modal-settings .modal-body .btn {
        background: #449039;
        color: #fff;
        border-radius: 3px;
        font-size: 12px;
        width: auto;
        padding: 0 20px;
        height: 37px;
        margin: 20px 0 0 0;
        float: left;
    }
</style>

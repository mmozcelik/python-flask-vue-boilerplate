<template>
    <div class="app-auth">
        <div class="device-xs visible-xs"></div>
        <div class="device-sm visible-sm"></div>
        <div class="device-md visible-md"></div>
        <div class="device-lg visible-lg"></div>

        <div class="print-logo hidden print-visible"><img alt="myapp.com" width="250" src="/static/img/logo.svg"></div>

        <nav class="navbar navbar-static-top navbar-inverse">
            <div class="container">
                <div class="navbar-header">
                    <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#top-navbar-collapse">
                        <span class="sr-only">Toggle Navigation</span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </button>
                    <a class="navbar-brand" href="/">
                        <img src="/static/img/logo.svg" width="100px"/>
                    </a>
                </div>
                <div class="collapse navbar-collapse" id="top-navbar-collapse">
                    <ul class="nav navbar-nav navbar-right cc-nav">
                        <li class="margin-right-12">
                            <div class="margin-top-10"><a href="/app/#/auth/register" class="navbar-btn btn btn-transparent btn-sm margin-left-12">Register</a></div>
                        </li>
                        <li class="margin-right-12">
                            <a href="/app/#/auth/login" class="navbar-link">
                                <small>Sign In</small>
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>

        <vue-alert></vue-alert>
        <div class="auth-wrapper">
            <div class="auth-container">
                <img src="/static/img/logo.svg" class="logo hidden-xs" width="400px"/>
                <router-view></router-view>
            </div>
        </div>

        <footer>
            <div class="container">
                <div class="row">
                    <div class="col-md-offset-2 col-md-8 col-sm-offset-1 col-sm-10">
                        <div class="row">
                            <div class="col-xs-6 col-sm-4 footer-col">
                                <p><a href="/">Home</a></p>
                                <p><a href="/app/#/auth/register">Register</a></p>
                                <p><a href="//myapp.com/faq">FAQ</a></p>
                            </div>
                            <div class="col-sm-4 footer-col">
                                <p><a href="//myapp.com/terms">Terms &amp; Conditions</a></p>
                                <p><a href="//myapp.com/privacy">Privacy Policy</a></p>
                            </div>
                        </div>
                    </div>
                </div>
                <p class="margin-top-15 copy text-center">
                    <small>© 2019 myapp.com by Myapp LLC. All rights reserved.</small>
                </p>
            </div>
        </footer>
    </div>
</template>


<script>
    import '../../assets/css/login.css'
    import '../../../static/css/landing-page/layout.css'

    export default {

    }
</script>

<style>
    .left-panel,
    .right-panel {
        position: absolute;
        top: 25%;
        margin: 0px 40px;
    }

    .right-panel {
        right: 0px;
    }

    @media (max-width: 1200px) {
        .left-panel,
        .right-panel {
            display: none;
        }
    }
</style>

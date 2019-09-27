<template>
    <div class="loading" v-show="show">
        <i class="fa fa-spinner fa-spin fa-fw fa-2x"></i> <span>{{$t('common.loading')}}</span>
    </div>
</template>

<script>
    export default {
        props: {show: {}},
        data: function () {
            return {}
        },
        created: function () {
        },
        methods: {}
    }
</script>

<style>
    .loading {
        text-align: center;
    }

    .loading span {
        font-size: 16px !important;
        display: inherit;
    }
</style>

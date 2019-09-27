<template>
    <div>
        <h1 class="lost-title">{{$t('auth.account_deleted')}}</h1>
        <p class="error">{{$t('auth.account_deleted_successfully')}}</p>
        <p class="error">{{$t('auth.account_deleted_sorry_to_go')}}</p>
    </div>
</template>

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

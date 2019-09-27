<template>
    <input type="text"/>
</template>

<script>
    /* global $ */
    export default {
        props: {
            'options': {},
            'value': {},
            'templateSelection': {default: null}
        },
        mounted: function () {
            var vm = this
            $(this.$el)
            // init select2
                .select2({data: this.options, formatResult: this.templateSelection, formatSelection: this.templateSelection})
                .val(this.value)
                .trigger('change')
                // emit event on change.
                .on('change', function () {
                    vm.$emit('input', this.value)
                })
        },
        watch: {
            value: function (value) {
                // update value
                $(this.$el).val(value)
            },
            options: function (options) {
                // update options
                $(this.$el).empty().select2({data: options})
            }
        },
        destroyed: function () {
            $(this.$el).off().select2('destroy')
        }
    }
</script>

<style>

</style>

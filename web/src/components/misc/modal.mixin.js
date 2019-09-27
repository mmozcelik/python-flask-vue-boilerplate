import './../../assets/css/modal.css'

export default {
    data () {
        return {
            visible: false
        }
    },
    ready: function () {
        setTimeout(() => {
            this.visible = true
        }, 0)

        document.onkeydown = (event) => {
            if (event.keyCode === 27 && this.visible) {
                this.close()
            }
        }
    },
    methods: {
        close: function () {
            this.visible = false
            if (this.previousUrl) {
                this.$router.push({path: this.previousUrl})
            }
            setTimeout(() => {
                this.$destroy(true)
            }, 300)
        }
    }
}

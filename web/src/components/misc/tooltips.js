import Popper from 'popper.js/build/popper'
import '../../assets/css/popper.css'

export default function (el, mode) {
    if (!mode) {
        mode = 'top'
    }

    function clear () {
        let items = searchItems('>.popper')
        for (let i = 0; i < items.length; i++) {
            items[i]._popper.destroy()
        }
    }

    function searchItems (query) {
        let items = null
        if (document.body.id) {
            items = document.body.querySelectorAll('#' + document.body.id + query)
        } else {
            let currentId = 'id-' + new Date().getTime()
            document.body.id = currentId
            items = document.body.querySelectorAll('#' + document.body.id + query)
            document.body.id = null
        }

        return items
    }

    function error (errors, element) {
        for (let key in errors) {
            if (!element) { // Not given by the user
                element = el.querySelector('[name="' + key + '"]')
                if (element === null) { // Not found, we get the first available
                    element = el.querySelectorAll('input,select,textarea')[0]
                }

                // Still nothing, so we quit
                if (element === null) continue
            }

            let items = searchItems('>.popper[data-key="' + key + '"]')
            if (items.length > 0) {
                for (let i = 0; i < items.length; i++) {
                    items[i]._popper.destroy()
                }
            }

            let item = new Popper(element, {
                parent: document.body,
                content: errors[key][0],
                attributes: ['data-key:' + key]
            }, {placement: mode, removeOnDestroy: true})

            item._popper._popper = item
        }
    }

    return {
        clear: clear,
        error: error
    }
}

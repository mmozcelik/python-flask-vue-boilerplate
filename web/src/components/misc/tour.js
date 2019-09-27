/* global Tour */

let MyappTour = {
    started: false,
    startTour: function (account, elementScope) {
        if (account.model && account.model.tourActive && !MyappTour.started) {
            MyappTour.started = true
            let startPath = elementScope.$route.path
            let tour = new Tour({
                backdrop: true,
                orphan: true,
                delay: 50,
                steps: [{
                    element: '#logo',
                    title: 'Ohh, Welcome to Myapp',
                    content: 'Let me show some of the features of Myapp in this tour, this will ease your usage of the site. If you have any detailed questions please visit our FAQ first, and FAQ does not help you, please feel free to contact us on our Facebook page.',
                    onNext: function () {
                        if (elementScope.$route.path.indexOf('mycloud') === -1) {
                            elementScope.$router.push('/mycloud')
                        }
                    }
                }],
                onEnd: function (tour) {
                    elementScope.$http.post('account/end-tour').then(
                        (xhr) => {
                            account.model.tourActive = false
                        },
                        (xhr) => {
                            return xhr
                        }
                    )
                }
            })

            tour.init()
            tour.start()
        }
    }
}

export default MyappTour

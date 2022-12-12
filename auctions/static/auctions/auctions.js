document.addEventListener('DOMContentLoaded', function() {

    update_counters();
    //setInterval(update_counters, 5000);

    if (document.querySelector('.toggle_watchlist') != undefined) {

        document.querySelectorAll('.toggle_watchlist').forEach(button => {

            const listing_id = button.dataset.listing_id;

            fetch(`/api/watching?listing_id=${listing_id}`)
            .then(response => response.json())
            .then(data => {
                update_button_display(button, data.on_watchlist);
            })
            .catch(error => {
                console.log("*** api/watching error **", error);
            })

            button.onclick = function() {

                const listing_id = this.dataset.listing_id;
                console.log(`Toggle watchlist for listing id=${listing_id}`);
                fetch(`/api/toggle?listing_id=${listing_id}`)
                .then(response => response.json())
                .then(data => {
                    update_button_display(this, data.on_watchlist);
                    update_innerHTML('#mw', data['my_watches'])
                })
                .catch(error => {
                    console.log("*** api/toggle error **", error);
                })
            }
        })
    }
});

function update_button_display(button, watching) {
    console.log(`update_button-dispay: ${button} ${watching}`);
    let filename = button.src;
    if (watching) {
        filename = filename.replace("hollow","filled");
    } else {
        filename = filename.replace("filled","hollow");
    }
    button.src = filename;
}

function update_counters() {
    fetch("/api/counters")
    .then(response => response.json())
    .then(data => {
        update_innerHTML('#al', data['active_listings'])
        update_innerHTML('#ml', data['my_listings'])
        update_innerHTML('#mw', data['my_watches'])
    })
    .catch(error => {
        console.log('**** api/counters error **', error);
    });
}

function update_innerHTML(element_id, value) {
    if (document.querySelector(element_id) != undefined) {
        document.querySelector(element_id).innerHTML = value;
    }
}
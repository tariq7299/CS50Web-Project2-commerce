//  This javascript file belong to listing_page.html


// This function will extract the csrf_token from the cookie, so to resend it back with the AJAX POST request
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}



document.addEventListener('DOMContentLoaded', function() {

    const csrftoken = getCookie('csrftoken')
    
    // The unpcoming code is the mechanism behind the "add to watchlist" button
    // It will send a post request to backend to add the listing/product to current user watchlist
    let watchlistButton = document.getElementById('watchlist-button');

    // This will check first if the watchlist button exists in html first
    // As I have removed it in case the current user who actually created the listing visited his own listing page
    // So logicly he won't need to add it to a watchlist
    if (watchlistButton != null) {
        watchlistButton.addEventListener('click', function() {
            let listingId = this.getAttribute('data-listing-id');
            const request = new Request(
                'watchlist',
                {
                    method: 'POST',
                    headers: {'X-CSRFToken': csrftoken},
                    mode: 'same-origin', 
                    body: JSON.stringify({  
                        'listing_id': listingId,
                    }),
                }
            );
            fetch(request)
                .then(response => response.json())  
                .then(data => {

                    // This if statement will tell be that he was trying to add the listing to watchlist
                    if (data.status === 'added') {
                        this.className = "added-to-watchlist";
                        this.textContent = "Added to watchlist";
                    }
                    // This if statement will tell be that he was trying to remove the listing from watchlist
                    else if (data.status === 'removed') {
                        // This will apply a custom styling for an deactivated watchlist button
                        this.className = "not-added-to-watchlist";  
                        this.textContent = "Add to watchlist"
                    } else {
                        console.log(data.error_message)
                        console.log('Error!');
                    }
                })
                .catch(error => {
                    console.log('Request failed', error);
                });
        });
    }

});


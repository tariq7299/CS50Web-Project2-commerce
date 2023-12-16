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
    
    let watchlistButton = document.getElementById('watchlist-button');
    watchlistButton.addEventListener('click', function() {
        let listingId = this.getAttribute('data-listing-id');
        const request = new Request(
            'add-to-watchlist',
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
                if (data.status === 'added') {
                    this.className = "added-to-watchlist";
                    this.textContent = "Added to watchlist";
                }
                else if (data.status === 'removed') {
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
    
});


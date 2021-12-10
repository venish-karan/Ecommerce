var updateBtns = document.getElementsByClassName('update-cart')

for(i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function() {
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('prouctId:', productId, 'Action:', action);

        console.log('USER:', user);
        if(user === 'AnonymousUser') {
            console.log('User is not authenticated');
        } else {
            updateUserOrder(productId, action);
        }
    }); 
}

function updateUserOrder(productId, action) {
    console.log('User is authenticate, sening data...');

    // send the data to this url
    var url = '/update_item/'

    // to send our post
    fetch(url, {
        // what kinda data we want to send to the backend
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'productId':productId, 'action': action})
    }) 
    // after we send the data using fetch we need a response or (promise) that data has been sent to the backend successfully.
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            console.log('Data:', data);
            location.reload();
        });
}
document.addEventListener('DOMContentLoaded', function () {
    const detailButton = document.querySelector('.update-cart-detail');

    if (detailButton) {
        detailButton.addEventListener('click', function () {
            const productId = this.dataset.product;
            const action = this.dataset.action;
            const quantity = parseInt(document.getElementById('quantity').value) || 1;

            const selectedSize = document.querySelector('input[name="size"]:checked');
            if (!selectedSize) {
                alert("Vui lòng chọn size trước khi thêm vào giỏ hàng.");
                return;
            }

            const size = selectedSize.value;
            
            const selectedColor = document.querySelector('input[name="color' + productId + '"]:checked');
            if (!selectedColor) {
                alert("Vui lòng chọn màu trước khi thêm vào giỏ hàng.");
                return;
            }
            const colorId = selectedColor.value;

            fetch('/update_item/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    productId: productId,
                    size: size,
                    color: colorId,
                    qty: quantity,
                    action: action
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Thêm vào giỏ hàng thành công:', data);
                // Ví dụ cập nhật giỏ: document.getElementById('cart-count').innerText = data.cartItems;
                alert("Đã thêm vào giỏ hàng!");
            });
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

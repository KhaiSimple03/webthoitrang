document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.update-cart');

    buttons.forEach(button => {
        button.addEventListener('click', function () {
            const productId = this.dataset.product;
            const action = this.dataset.action || 'add';
            const area = this.dataset.area;
            const modal = this.closest('.modal');
            // const modal = document.querySelector(`#sizeModal_${area}${productId}`);
            console.log(modal);

          
            const selectedSize = modal.querySelector(`input[name="size${productId}"]:checked`);
            if (!selectedSize) {
                alert("Vui lòng chọn size.");
                return;
            }
            const size = selectedSize.value;

      
            const selectedColor = modal.querySelector(`input[name="color${productId}"]:checked`);
            if (!selectedColor) {
                alert("Vui lòng chọn màu.");
                return;
            }
            const colorId = selectedColor.value;
           

           
            const quantityInput = document.getElementById(`qtyInput${productId}`);
            const qty = quantityInput ? parseInt(quantityInput.value) : 1;

           
            console.log('productId:', productId);
            console.log('action:', action);
            console.log('size:', size);
            console.log('color:', colorId);
            console.log('qty:', qty);

            
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
                    qty: qty,
                    action: action
                })
            })
            .then(res => res.json())
            .then(data => {
                console.log('Đã thêm vào giỏ:', data);
                alert("Thêm sản phẩm vào giỏ hàng thành công!");
            })
            .catch(err => {
                console.error('Lỗi khi thêm sản phẩm:', err);
                alert('Hãy đăng nhập để thêm vào giỏ hàng.');
            });
        });
    });

    // Hàm lấy CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});



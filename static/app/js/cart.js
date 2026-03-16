document.addEventListener('DOMContentLoaded', function () {

    
    document.querySelectorAll('.chg-quantity').forEach(button => {
        button.addEventListener('click', function () {
            const productId = this.dataset.product;
            const sizeId = this.dataset.size;
            const action = this.dataset.action;
            const colorId = this.dataset.color;

            const row = this.closest('tr');
            const input = row.querySelector('input[name^="quantity_"]');
            let currentQty = parseInt(input.value) || 1;

            fetch(`/api/check-stock/?product_id=${productId}&size_id=${sizeId}&color_id=${colorId}`)
                .then(res => res.json())
                .then(data => {
                    const maxStock = data.stock;

                    let newQty = currentQty;

                    if (action === 'add') {
                        if (currentQty >= maxStock) {
                            alert("Không thể vượt quá số lượng tồn kho!");
                            return;
                        }
                        newQty += 1;
                    } else if (action === 'remove') {
                        if (currentQty > 1) {
                            newQty -= 1;
                        }
                    }

                    // Gửi cập nhật nếu thay đổi
                    if (newQty !== currentQty) {

                        fetch('/update_item/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCookie('csrftoken')
                            },
                            body: JSON.stringify({
                                productId: productId,
                                size: sizeId,
                                color: colorId,
                                qty: newQty,
                                action: 'set'
                            })
                        })
                        .then(res => res.json())
                        .then(data => {
                            input.value = newQty; // update UI
                            updateCartBadge(data.cartItems);
                        });
                    }
                });
        });
    });

    // Xử lý người dùng sửa trực tiếp input
    document.querySelectorAll('input[name^="quantity_"]').forEach(input => {
        input.addEventListener('change', function () {
            const newQty = parseInt(this.value);
            if (isNaN(newQty) || newQty < 1) {
                alert('Số lượng không hợp lệ');
                this.value = 1;
                return;
            }

            const row = this.closest('tr');
            const productId = row.querySelector('.chg-quantity').dataset.product;
            const sizeId = row.querySelector('.chg-quantity').dataset.size;
            const colorId = row.querySelector('.chg-quantity').dataset.color;
          

            fetch(`/api/check-stock/?product_id=${productId}&size_id=${sizeId}&color_id=${colorId}`)
                .then(res => res.json())
                .then(data => {
                    const maxStock = data.stock;
                    if (newQty > maxStock) {
                        alert(`Chỉ còn ${maxStock} sản phẩm trong kho.`);
                        this.value = maxStock;
                        return;
                    }

                    fetch('/update_item/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({
                            productId: productId,
                            size: sizeId,
                            color: colorId,
                            qty: newQty,
                            action: 'set'
                        })
                    })
                    .then(res => res.json())
                    .then(data => {
                        updateCartBadge(data.cartItems); 
                       
                    });
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


function updateCartBadge(count) {
    const badge = document.querySelector('.nav-link .badge');
    if (badge) {
        badge.textContent = count;
    }
}




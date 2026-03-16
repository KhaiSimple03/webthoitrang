document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".remove-from-cart").forEach(button => {
        button.addEventListener("click", function () {
            const productId = this.dataset.product;
            const size = this.dataset.size;
            const colorId = this.dataset.color;

            fetch("/update_item/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    productId: productId,
                    action: "delete",
                    size: size,
                    color:colorId,
                }),
            })
            .then(response => response.json())
            .then(data => {
                // Reload trang sau khi xóa
                location.reload();
            });
        });
    });
});
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

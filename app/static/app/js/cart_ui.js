function updateCart() {
	let totalQuantity = 0;
	let totalPrice = 0;

	document.querySelectorAll('#cartItems tr').forEach(row => {
		const checkbox = row.querySelector('.itemCheckbox');
		if (checkbox && checkbox.checked) {
			const quantityInput = row.querySelector('input[name^="quantity_"]');
			if (!quantityInput) return;
			const quantity = parseInt(quantityInput.value);
			const priceText = row.querySelector('td:nth-child(6)').innerText;
			const price = parseFloat(priceText.replace(/[^0-9.-]+/g, ""));
			if (!isNaN(quantity) && !isNaN(price)) {
				totalQuantity += quantity;
				totalPrice += price * quantity;
			}
		}
	});

	document.getElementById('totalQuantity').innerText = totalQuantity;
	document.getElementById('totalPrice').innerText = totalPrice.toLocaleString('vi-VN') + 'đ';
}

document.addEventListener('DOMContentLoaded', function () {
	document.querySelectorAll('.itemCheckbox').forEach(checkbox => {
		checkbox.addEventListener('change', updateCart);
	});

	document.querySelectorAll('input[name^="quantity_"]').forEach(input => {
		input.addEventListener('input', updateCart);
	});

	const selectAll = document.getElementById('selectAll');
	if (selectAll) {
		selectAll.addEventListener('change', function (e) {
			const isChecked = e.target.checked;
			document.querySelectorAll('.itemCheckbox').forEach(cb => cb.checked = isChecked);
			updateCart();
		});
	}

	updateCart();
});

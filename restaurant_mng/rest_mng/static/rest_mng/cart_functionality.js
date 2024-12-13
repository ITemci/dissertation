
        // Initialize cart if not already in sessionStorage
        if (!sessionStorage.getItem('cart')) {
            sessionStorage.setItem('cart', JSON.stringify({}));
        }

        // Add item to cart
        function addToCart(productId, productName, productPrice) {
            const quantity = parseInt(document.getElementById(`quantity_${productId}`).value, 10);

            // Get the current cart
            let cart = JSON.parse(sessionStorage.getItem('cart'));

            // Update cart
            if (cart[productId]) {
                cart[productId].quantity += quantity; // Increment quantity
            } else {
                cart[productId] = {
                    name: productName,
                    price: productPrice,
                    quantity: quantity
                };
            }

            // Save updated cart to sessionStorage
            sessionStorage.setItem('cart', JSON.stringify(cart));

            // Update cart UI
            updateCartUI();
        }

        // Display cart items
        function updateCartUI() {
            const cart = JSON.parse(sessionStorage.getItem('cart')|| '{}');
            const cartItems = document.getElementById('cart-items');
            const checkoutButton = document.getElementById('checkout-button');
            const emptyCartMessage = document.getElementById('empty-cart-message');

            cartItems.innerHTML = '';

            if (Object.keys(cart).length === 0) {
                // Cart is empty
                checkoutButton.style.display = 'none'; // Hide checkout button
                emptyCartMessage.style.display = 'block'; // Show "Cart is empty" message
            } else {
                // Cart has items
                checkoutButton.style.display = 'block'; // Show checkout button
                emptyCartMessage.style.display = 'none'; // Hide "Cart is empty" message

                for (const [productId, item] of Object.entries(cart)) {
                    const li = document.createElement('li');
                    li.textContent = `${item.name} - Quantity: ${item.quantity} - Total: £${(item.price * item.quantity).toFixed(2)}`;
                    cartItems.appendChild(li);
                }
            }
        }

        // Checkout: Send cart data to backend
        function checkout() {
            const cart = sessionStorage.getItem('cart');

            fetch('checkout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'

                },
                body: cart
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message || 'Checkout complete!');
                sessionStorage.removeItem('cart'); // Clear cart after checkout
                updateCartUI();
            })
            .catch(error => console.error('Error during checkout:', error));
        }

        // Update cart UI on page load
        document.addEventListener('DOMContentLoaded', updateCartUI);

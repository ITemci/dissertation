const cart_btn = document.getElementById('cart_btn');
const cart = document.getElementById('cart');
cart_btn.addEventListener('click', ()=>{
    cart.classList.toggle("show");
    // Scroll to the cart when it becomes visible
            if (cart.classList.contains("show")) {
                cart.scrollIntoView({ behavior: "smooth", block: "start" });
            }
});
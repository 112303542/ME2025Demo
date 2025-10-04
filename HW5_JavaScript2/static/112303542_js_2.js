const items = document.querySelectorAll(".item");
const minusBtns = document.querySelectorAll(".minus");
const plusBtns = document.querySelectorAll(".plus");
const totalCell = document.getElementById("total");
const checkoutBtn = document.getElementById("checkout");

minusBtns.forEach((btn, index) => {
  btn.addEventListener("click", () => {
    const row = btn.closest("tr");
    const qtyInput = row.querySelector(".itemnum");
    let qty = parseInt(qtyInput.value);
    if (qty > 1) qty--;
    qtyInput.value = qty;
    updateRowTotal(row);
    updateTotal();
  });
});

plusBtns.forEach((btn, index) => {
  btn.addEventListener("click", () => {
    const row = btn.closest("tr");
    const qtyInput = row.querySelector(".itemnum");
    const stock = parseInt(row.querySelector(".stock").textContent);
    let qty = parseInt(qtyInput.value);
    if (qty < stock) qty++;
    qtyInput.value = qty;
    updateRowTotal(row);
    updateTotal();
  });
});
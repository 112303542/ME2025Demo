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

document.querySelectorAll(".itemnum").forEach(input => {
  input.addEventListener("blur", () => {
    const row = input.closest("tr");
    const stock = parseInt(row.querySelector(".stock").textContent);
    let qty = parseInt(input.value);

    if (isNaN(qty) || qty < 1) qty = 1;
    if (qty > stock) qty = stock;

    input.value = qty;
    updateRowTotal(row);
    updateTotal();
  });
});
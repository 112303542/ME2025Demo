const checkboxAll = document.getElementById("checkbox_all");
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
    if(qty > 1) qty--;
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
    if(qty < stock) qty++;
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

    if(isNaN(qty) || qty < 1) qty = 1;
    if(qty > stock) qty = stock;

    input.value = qty;
    updateRowTotal(row);
    updateTotal();
  });
});

function updateRowTotal(row) {
  const price = parseInt(row.querySelector(".price").textContent);
  const qty = parseInt(row.querySelector(".itemnum").value);
  const subtotalCell = row.querySelector(".total");
  subtotalCell.textContent = price * qty;
}

function updateTotal() {
  let total = 0;
  document.querySelectorAll("tbody tr").forEach(row => {
    const checkbox = row.querySelector(".item");
    if(checkbox.checked){
      total += parseInt(row.querySelector(".total").textContent);
    }
  });
  totalCell.textContent = total;
}

items.forEach(item => {
  item.addEventListener("change", updateTotal);
});

checkoutBtn.addEventListener("click", () => {
    const total = parseInt(totalCell.textContent);
    if(isNaN(total) || total <= 0){
        alert("請先選擇要購買的商品！");
        return;
    }

    let detail = "";
    document.querySelectorAll("tbody tr").forEach(row => {
        const checkbox = row.querySelector(".item");
        if(checkbox.checked){
            const name = row.children[1].textContent.trim();
            const qty = parseInt(row.querySelector(".itemnum").value);
            detail += `${name} * ${qty},\n`;
        }
    });

    showReceiptAlert(total, detail);

    document.querySelectorAll("tbody tr").forEach(row => {
        const checkbox = row.querySelector(".item");
        if(checkbox.checked){
            const stockCell = row.querySelector(".stock");
            let stock = parseInt(stockCell.textContent);
            const qty = parseInt(row.querySelector(".itemnum").value);
            stock -= qty;
            if(stock < 0) stock = 0;
            stockCell.textContent = stock;

            if(stock === 0){
                row.querySelector(".itemnum").disabled = true;
                row.querySelector(".plus").disabled = true;
                row.querySelector(".minus").disabled = true;
            } 
            else row.querySelector(".itemnum").value = 1;

            checkbox.checked = false;
        }
    });
});

function showReceiptAlert(total, detail){
    if(total <= 0){
        alert("請先選擇要購買的商品！");
        return;
    }

    let message = "感謝您的購買，您的總購買的產品如下：\n\n";
    message += detail;
    message += `\n總計：$${total}元`;
    alert(message);
}
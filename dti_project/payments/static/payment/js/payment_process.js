document.addEventListener("DOMContentLoaded", () => {
    const proceedBtn = document.querySelector("button[name='proceed']");
    if (!proceedBtn) return;

    proceedBtn.addEventListener("click", () => {
        const selected = document.querySelector("input[name='payment_method']:checked");
        if (!selected) {
        alert("Please select a payment method.");
        return false;
        }

        // Optional visual feedback
        proceedBtn.disabled = true;
        proceedBtn.innerText = "Processing...";
    });
    });
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".alert-dismissible").forEach((alert) => {
    setTimeout(() => {
      const closeBtn = alert.querySelector(".btn-close");
      if (closeBtn) closeBtn.click();
    }, 6000);
  });

  const methodInputs = document.querySelectorAll('input[name="preferred_method"]');
  const methodSelect = document.getElementById("preferredMethod");
  const zakatDateStep = document.getElementById("zakatDateStep");
  const zakatDateInput = document.getElementById("zakatDateInput");

  function selectedMethod() {
    if (methodSelect) return methodSelect.value;
    const checked = document.querySelector('input[name="preferred_method"]:checked');
    return checked ? checked.value : "1";
  }

  function toggleZakatDate() {
    const show = selectedMethod() === "2";
    if (zakatDateStep) {
      zakatDateStep.style.display = show ? "block" : "none";
      if (zakatDateInput) zakatDateInput.required = show;
    }
    if (methodSelect && zakatDateInput) {
      const settingsBlock = document.getElementById("settingsZakatDate");
      if (settingsBlock) settingsBlock.style.display = show ? "block" : "none";
      zakatDateInput.required = show;
    }
  }

  methodInputs.forEach((el) => el.addEventListener("change", toggleZakatDate));
  if (methodSelect) methodSelect.addEventListener("change", toggleZakatDate);
  toggleZakatDate();
});

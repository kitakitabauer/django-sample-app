document.addEventListener("DOMContentLoaded", () => {
  const toasts = document.querySelectorAll(".toast");
  if (window.bootstrap && typeof window.bootstrap.Toast === "function") {
    toasts.forEach((toastEl) => {
      const toast = new window.bootstrap.Toast(toastEl, { delay: 4000 });
      toast.show();
    });
  }
});

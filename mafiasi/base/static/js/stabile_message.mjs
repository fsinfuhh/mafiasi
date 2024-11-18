document.addEventListener("DOMContentLoaded", () => {
  const dialog = document.getElementById("stabile-message");

  // close dialog when clicked
  const close = () => dialog.style.display = "none";
  dialog.addEventListener("click", close);

  // alternatively, also close dialog after 20 seconds
  setTimeout(close, 20 * 1000);
})

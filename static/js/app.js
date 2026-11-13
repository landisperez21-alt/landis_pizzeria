// Auto-oculta las alertas despues de unos segundos.
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".alerta").forEach(function (el) {
    setTimeout(function () {
      el.style.transition = "opacity .4s ease";
      el.style.opacity = "0";
      setTimeout(function () { el.remove(); }, 400);
    }, 4200);
  });
});

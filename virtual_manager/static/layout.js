document.addEventListener('DOMContentLoaded', function() {
  // Makes nav items active and disabled if <li> href matches part of the url
  const url_prefix = $('#index-tabs').length ? 3 : 4
  const layoutNavbar = document.getElementById('layoutNavbar')
  layoutNavbar.querySelectorAll(".nav-link").forEach((x) => {
    if (window.location.href.split('/')[url_prefix] == x.href.split('/')[url_prefix]) {
      x.classList.add('active', 'disabled')
    }
  })
})

document.addEventListener("DOMContentLoaded", function () {
  // Inicializa o toast
  const toastElement = document.getElementById('example-toast');
  const toast = new bootstrap.Toast(toastElement, {
    autohide: true, // Faz o toast desaparecer automaticamente
    delay: 5000     // Define o tempo de exibição (5 segundos)
  });

  // Exibe o toast
  toast.show();
});
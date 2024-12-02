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

// Closes messages toasts after 5 secs
document.addEventListener('DOMContentLoaded', function () {
  var toastElList = [].slice.call(document.querySelectorAll('.toast'));
  var toastList = toastElList.map(function (toastEl) {
    return new bootstrap.Toast(toastEl, { autohide: true, delay: 5000 });
  });
  toastList.forEach(toast => toast.show());
});
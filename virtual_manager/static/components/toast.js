export function toast(message='No message given', context='danger', delay=5000) {
  const toastContainer = $('#toast-container')
  const toastEl = $(`
  <div class="toast align-items-center bg-${context} border-0" style="--bs-bg-opacity: .5;" role="alert" aria-live="assertive" aria-atomic="true">
    <div class="d-flex">
      <div class="toast-body">
        ${message}
      </div>
      <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
  </div>
  `)
  toastContainer.append(toastEl)
  return new bootstrap.Toast(toastEl, { autohide: true, delay: delay }).show()
}
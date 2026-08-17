$(function () {
  let $formToSubmit = null

  $('#confirm_delete').on('show.bs.modal', function (event) {
    const $button = $(event.relatedTarget)
    $formToSubmit = $button.closest('form')

    $('#confirm-delete-news').text($button.data('news'))
    $('#confirm-delete-lang').text($button.data('lang'))
  })

  $('#confirm-delete-submit').on('click', function () {
    if ($formToSubmit) {
      $formToSubmit.submit()
    }
  })
})

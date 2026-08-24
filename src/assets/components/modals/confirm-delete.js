$(function () {
  let $formToSubmit = null

  $('#confirm_delete').on('show.bs.modal', function (event) {
    const $button = $(event.relatedTarget)
    $formToSubmit = $button.closest('form')

    const itemType = $button.data('news') !== undefined ? 'news' : 'homepage'
    $(`#confirm-delete-${itemType}`).text($button.data(itemType))
    $('#confirm-delete-lang').text($button.data('lang'))
  })

  $('#confirm-delete-submit').on('click', function () {
    if ($formToSubmit) {
      $formToSubmit.submit()
    }
  })
})

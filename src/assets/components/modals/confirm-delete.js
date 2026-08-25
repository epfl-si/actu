$(function () {
  let $formToSubmit = null

  $('#confirm_delete').on('show.bs.modal', function (event) {
    const $button = $(event.relatedTarget)
    $formToSubmit = $button.closest('form')

    const itemType = $button.data('item-type')
    const itemName = $button.data('item-name')
    if (!itemType || itemName === undefined) {
      return
    }
    $(`#confirm-delete-${itemType}`).text(itemName)
    $('#confirm-delete-lang').text($button.data('lang'))
  })

  $('#confirm-delete-submit').on('click', function () {
    if ($formToSubmit) {
      $formToSubmit.submit()
    }
  })
})

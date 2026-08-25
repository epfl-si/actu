$(function () {
  function makeLinkRow(lang) {
    const $total = $(`#id_form-TOTAL_FORMS`) // formset is shared across the page unless you give it a prefix per language
    const index = parseInt($total.val(), 10)
    $total.val(index + 1)

    return $(`
      <div class="input-group mb-2 link-row">
        <input type="url" name="form-${index}-ref" class="form-control" placeholder="https://...">
      </div>
    `)
  }

  $('.add-link-btn').on('click', function () {
    const $container = $('#' + $(this).data('target'))
    $container.append(makeLinkRow($(this).data('lang')))
  })

  // For existing rows, don't remove the DOM node (that breaks id/index alignment) —
  // instead check the DELETE checkbox and hide the row.
  $(document).on('click', '.remove-link-btn', function () {
    const $row = $(this).closest('.link-row')
    $row.find('input[type=checkbox][name$="-DELETE"]').prop('checked', true)
    $row.hide()
  })
})

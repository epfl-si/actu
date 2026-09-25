$(function () {
  function makeUrlRow (prefix, removeTitle) {
    const $total = $(`#id_${prefix}-TOTAL_FORMS`)
    const index = parseInt($total.val(), 10)
    $total.val(index + 1)

    return $(`
      <div class="input-group mb-2 ${prefix}-row">
        <input type="url" name="${prefix}-${index}-url" class="form-control" placeholder="https://...">
        <span class="float-right remove-${prefix}-btn" role="button" title="${removeTitle}">
          <svg class="icon feather" aria-hidden="true">
            <use xlink:href="#trash-2"></use>
          </svg>
        </span>
        <div class="d-none">
          <input type="checkbox" name="${prefix}-${index}-DELETE" id="id_${prefix}-${index}-DELETE">
        </div>
      </div>
    `)
  }

  $('.add-url-btn').on('click', function () {
    const $container = $('#' + $(this).data('target'))
    const prefix = $container.data('prefix')
    const removeTitle = $(this).data('remove-title')
    $container.append(makeUrlRow(prefix, removeTitle))
  })

  // For existing rows, don't remove the DOM node (that breaks id/index alignment) —
  // instead check the DELETE checkbox and hide the row.
  $(document).on('click', '.remove-url-btn', function () {
    const $row = $(this).closest('.url-row')
    $row.find('input[type=checkbox][name$="-DELETE"]').prop('checked', true)
    $row.hide()
  })
})

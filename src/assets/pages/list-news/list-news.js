document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('news-form')
  const btnFilter = document.getElementById('btnFilter')

  if (!form || !btnFilter) return

  let hasChanged = false

  if (window.$) {
    $('.select-multiple').on('change', function () {
      hasChanged = true
    })

    $(document).on('click', function (e) {
      if (hasChanged && !$(e.target).closest('.form-group').length) {
        hasChanged = false
        btnFilter.click()
      }
    })

    $('.filter-remove').on('click', function (e) {
      e.preventDefault()

      const type = $(this).data('type')
      const val = $(this).data('val')

      $('#' + type)
        .find(`option[value="${val}"]`)
        .prop('selected', false)
        .trigger('change')

      btnFilter.click()
    })
  }
})

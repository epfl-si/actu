document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('news-form')

  if (!form) return

  let hasChanged = false

  if (window.$) {
    $('.select-multiple').on('change', function () {
      hasChanged = true
    })

    $(document).on('click', function (e) {
      if (hasChanged && !$(e.target).closest('.form-group').length) {
        hasChanged = false
        form.requestSubmit()
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

      form.requestSubmit()
    })
  }
})

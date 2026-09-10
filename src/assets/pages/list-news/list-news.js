document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('news-form')
  const filtersZone = document.getElementById('collapse-1')
  const btnFilter = document.getElementById('btnFilter')

  if (!form || !filtersZone || !btnFilter) return

  let hasChanged = false

  filtersZone.addEventListener('change', () => { hasChanged = true }, true)

  filtersZone.addEventListener('focusout', function () {
    setTimeout(function () {
      if (hasChanged && !filtersZone.contains(document.activeElement)) {
        hasChanged = false
        btnFilter.click()
      }
    }, 0)
  })

  if (window.$) {
    $('.filter-remove').on('click', function (e) {
      e.preventDefault()
      const type = $(this).data('type')
      const val = $(this).data('val')
      $('#' + type).find(`option[value="${val}"]`).prop('selected', false).trigger('change')
      btnFilter.click()
    })
  }
})

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('news-form')
  if (!form) return

  let debounceTimer

  function scheduleSubmit () {
    clearTimeout(debounceTimer)

    debounceTimer = setTimeout(function () {
      form.submit()
    }, 600)
  }

  if (window.$) {
    $('.select-multiple').on('change', function(e) {
      scheduleSubmit()
    })
  }

  const searchInput = document.getElementById('text-event-keyword-filter')
  if (searchInput) {
    searchInput.addEventListener('input', scheduleSubmit)
  }
})

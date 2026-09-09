document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('news-form')

  if (form && window.$) {
    let debounceTimer
    function scheduleSubmit () {
      clearTimeout(debounceTimer)
      debounceTimer = setTimeout(function () {
        form.submit()
      }, 100)
    }
    $('.select-multiple').on('change', function () {
      scheduleSubmit()
    })
  }
})

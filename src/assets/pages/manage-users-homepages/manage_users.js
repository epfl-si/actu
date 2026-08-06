/* global $ */

document.addEventListener('DOMContentLoaded', function () {
  const searchInput = document.getElementById('ajaxSearchInput')
  const addBtn = document.getElementById('add-btn')
  const addForm = document.getElementById('addForm')
  const addSciperInput = document.getElementById('addSciper')

  const transAdd = searchInput.dataset.transAdd
  const transNoResults = searchInput.dataset.transNoResults

  const errorFeedback = document.createElement('div')
  errorFeedback.className = 'text-danger mt-1 small'
  errorFeedback.style.display = 'none'

  searchInput.parentNode.insertBefore(errorFeedback, searchInput.nextSibling)

  $(searchInput).selectize({
    valueField: 'sciper',
    labelField: 'text',
    searchField: 'text',
    maxItems: 1,
    loadThrottle: 300,
    create: false,
    placeholder: searchInput.getAttribute('placeholder'),

    load: function (query, callback) {
      addBtn.style.display = 'none'
      errorFeedback.style.display = 'none'
      errorFeedback.innerText = ''

      const selectizeInput = this.$wrapper[0].querySelector('.selectize-input')
      selectizeInput.classList.remove('border-danger')

      if (query.length < 3) return callback()

      fetch(`?q=${encodeURIComponent(query)}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      })
        .then(response => {
          if (!response.ok) {
            throw new Error(`Server error (${response.status})`)
          }
          return response.json()
        })
        .then(data => {
          if (data.results && data.results.length > 0) {
            callback(data.results)
          } else {
            callback()
          }
        })
        .catch(error => {
          let errorMessage = 'Unable to contact the server.'
          if (error.message) {
            errorMessage = error.message
          }
          errorFeedback.innerText = `AJAX Error: ${errorMessage}`
          errorFeedback.style.display = 'block'

          const selectizeInput = this.$wrapper[0].querySelector('.selectize-input')
          selectizeInput.classList.add('border-danger')

          callback()
        })
    },

    render: {
      option: function (item, escape) {
        return `<div class="list-group-item list-group-item-action border-0" style="cursor: pointer;">
                  ${escape(item.text)}
                </div>`
      },
      not_found: function (data, escape) {
        return `<div class="list-group-item border-0 text-muted" style="cursor: default;">
                  <i>${escape(transNoResults)}</i>
                </div>`
      },
    },

    onChange: function (value) {
      if (value) {
        const selectedItem = this.options[value]
        addSciperInput.value = selectedItem.sciper

        addBtn.style.display = 'block'
        addBtn.textContent = `${transAdd} ${selectedItem.text}`
      } else {
        addSciperInput.value = ''
        addBtn.style.display = 'none'
      }
    },
  })

  addBtn.addEventListener('click', function (e) {
    e.preventDefault()
    if (!addSciperInput.value) return

    addForm.submit()
  })
})

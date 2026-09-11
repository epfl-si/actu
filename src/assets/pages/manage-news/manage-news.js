document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.getElementById('toggle-news-metadata')
  const metadataBlocks = Array.from(document.querySelectorAll('.display-news-metadata'))

  if (!toggle || metadataBlocks.length === 0) {
    return
  }

  const applyMetadataVisibility = function () {
    metadataBlocks.forEach(function (block) {
      block.classList.toggle('d-none', !toggle.checked)
    })
  }

  applyMetadataVisibility()
  toggle.addEventListener('change', applyMetadataVisibility)
})

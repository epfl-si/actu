;(function () {
  if (window.__editorjsDragDropWrapped) {
    return
  }

  const OriginalEditorJS = window.EditorJS

  if (!OriginalEditorJS) {
    return
  }

  window.__editorjsDragDropWrapped = true

  window.EditorJS = function (config) {
    const originalOnReady = config.onReady

    config.onReady = function () {
      if (window.DragDrop && editor) {
        // eslint-disable-next-line no-new
        new window.DragDrop(editor)
      }

      if (originalOnReady) {
        originalOnReady.apply(this, arguments)
      }
    }

    const editor = new OriginalEditorJS(config)
    return editor
  }

  Object.setPrototypeOf(window.EditorJS, OriginalEditorJS)
  window.EditorJS.prototype = OriginalEditorJS.prototype
})()

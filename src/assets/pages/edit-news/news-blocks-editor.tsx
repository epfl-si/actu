import '@vitejs/plugin-react/preamble'
import { createRoot } from 'react-dom/client'

import type { NewsBlocksEditorProps } from '../../components/blocks-editor/NewsBlocksEditor'
import NewsBlocksEditor from '../../components/blocks-editor/NewsBlocksEditor'

const propsNode = document.getElementById('news-blocks-editor-props')
const mount = document.getElementById('news-blocks-editor-root')

if (mount && propsNode?.textContent) {
  const { newsId, language, uiLanguage, blocks, i18n } = JSON.parse(
    propsNode.textContent,
  ) as NewsBlocksEditorProps

  createRoot(mount).render(
    <NewsBlocksEditor
      newsId={newsId}
      language={language}
      uiLanguage={uiLanguage}
      blocks={blocks ?? []}
      i18n={i18n}
    />,
  )
}

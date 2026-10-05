import './news-blocks-editor.scss'

export type NewsBlocksEditorProps = {
  newsId: number | null,
  language: string,
}

const NewsBlocksEditor = ({ newsId, language }: NewsBlocksEditorProps) => (
  <div className='news-blocks-editor alert alert-info' role='status'>
    A NewsBlocksEditor React Component (newsId: {newsId ?? 'not set'}, language: {language})
  </div>
)

export default NewsBlocksEditor

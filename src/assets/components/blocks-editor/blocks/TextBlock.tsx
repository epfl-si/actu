import type { BlockData } from '../types'

const TextBlock = ({ data }: { data: BlockData }) => (
  <div
    className='block-preview-text'
    dangerouslySetInnerHTML={{ __html: data.content ?? '' }}
  />
)

export default TextBlock

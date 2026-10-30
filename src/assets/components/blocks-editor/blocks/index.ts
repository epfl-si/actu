import type { ComponentType } from 'react'
import type { BlockData, BlockType } from '../types'
import TextBlock from './TextBlock'

export const BLOCK_PREVIEWS: Record<BlockType, ComponentType<{ data: BlockData }>> = {
  text: TextBlock,
}

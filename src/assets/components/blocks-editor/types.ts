export type BlockType = 'text'

export type BlockData = Record<string, string>

export type Block = {
  id: string,
  type: BlockType,
  data: BlockData,
}

export type BlockField = {
  key: string,
  required: boolean,
}

export type BlockTypePayload = {
  type: string,
  data: BlockData,
}

export type BlockEditorI18n = {
  addBlock: string,
  moveUp: string,
  moveDown: string,
  edit: string,
  remove: string,
  reorder: string,
  save: string,
  close: string,
  editBlockTitle: string,
  blockTypes: Record<BlockType, string>,
  fieldLabels: Record<string, string>,
}

export const BLOCK_ICONS: Record<BlockType, string> = {
  text: 'align-left',
}

export const BLOCK_FIELDS: Record<BlockType, BlockField[]> = {
  text: [
    { key: 'content', required: true },
  ],
}

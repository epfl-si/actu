import { useEffect, useRef, useState } from 'react'
import Sortable from 'sortablejs'
import { BLOCK_PREVIEWS } from './blocks'
import { BLOCK_FIELDS, BLOCK_ICONS } from './types'
import type {
  Block,
  BlockData,
  BlockEditorI18n,
  BlockType,
  BlockTypePayload,
} from './types'
import './news-blocks-editor.scss'

export type NewsBlocksEditorProps = {
  newsId: number | null,
  language: string,
  uiLanguage: string,
  blocks: BlockTypePayload[],
  i18n: BlockEditorI18n,
}

type AddPosition = 'top' | 'bottom'

type TinyMceEditorInstance = {
  on: (event: string, handler: () => void) => void,
  getContent: () => string,
  destroy: () => void,
}

type TinyMceGlobal = {
  init: (config: Record<string, unknown>) => void,
}

const getTinyMce = (): TinyMceGlobal | undefined =>
  (window as unknown as { tinymce?: TinyMceGlobal }).tinymce

const TINYMCE_CONFIG = {
  height: 250,
  menubar: false,
  license_key: 'gpl',
  plugins: 'lists link anchor code',
  toolbar: 'bold italic underline | bullist numlist indent outdent  | subscript ' +
    'superscript | blocks | link anchor | undo redo | fullscreen | code',
}

// Language pack file names bundled with django-tinymce.
const TINYMCE_LANGUAGES: Record<string, string> = {
  fr: 'fr_FR',
  de: 'de',
  it: 'it',
}

const isBlockType = (type: string): type is BlockType => type in BLOCK_ICONS

const isKnownBlock = (
  block: BlockTypePayload,
): block is BlockTypePayload & { type: BlockType } => isBlockType(block.type)

const createBlockId = () => {
  if (typeof crypto.randomUUID === 'function') return crypto.randomUUID()
  return `block-${Date.now()}-${Math.random().toString(36).slice(2)}`
}

const toBlocks = (payload: BlockTypePayload[]): Block[] =>
  payload.filter(isKnownBlock).map(block => ({
    id: createBlockId(),
    type: block.type,
    data: block.data ?? {},
  }))

const toPayload = (blocks: Block[]): BlockTypePayload[] =>
  blocks.map(block => ({ type: block.type, data: block.data }))

const TinyMceEditor = ({
  id,
  initialValue,
  uiLanguage,
  onChange,
}: {
  id: string,
  initialValue: string,
  uiLanguage: string,
  onChange: (value: string) => void,
}) => {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null)
  const onChangeRef = useRef(onChange)

  useEffect(() => {
    onChangeRef.current = onChange
  }, [onChange])

  useEffect(() => {
    const textarea = textareaRef.current
    const tinymce = getTinyMce()
    if (!tinymce || !textarea) return undefined

    const config: Record<string, unknown> = { target: textarea, ...TINYMCE_CONFIG }
    const tinymceLanguage = TINYMCE_LANGUAGES[uiLanguage]
    if (tinymceLanguage) config.language = tinymceLanguage

    let editor: TinyMceEditorInstance | null = null
    let disposed = false
    tinymce.init({
      ...config,
      setup: (instance: unknown) => {
        const tinymceEditor = instance as TinyMceEditorInstance
        if (disposed) {
          // The aside closed before the editor finished initializing.
          tinymceEditor.destroy()
          return
        }
        editor = tinymceEditor
        tinymceEditor.on('change input undo redo', () =>
          onChangeRef.current(tinymceEditor.getContent()),
        )
      },
    })
    return () => {
      disposed = true
      editor?.destroy()
    }
  }, [uiLanguage])

  return (
    <textarea
      ref={textareaRef}
      id={id}
      className='edit-field-editor'
      defaultValue={initialValue}
    />
  )
}

const AddBlockButton = ({
  position,
  i18n,
  onSelect,
}: {
  position: AddPosition,
  i18n: BlockEditorI18n,
  onSelect: (type: BlockType, position: AddPosition) => void,
}) => {
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!open) return undefined
    const closeOnOutsideClick = (event: Event) => {
      if (rootRef.current && !rootRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', closeOnOutsideClick)
    document.addEventListener('keydown', closeOnEscape)
    return () => {
      document.removeEventListener('mousedown', closeOnOutsideClick)
      document.removeEventListener('keydown', closeOnEscape)
    }
  }, [open])

  const menuClassName =
    position === 'bottom' ? 'dropdown-menu-news dropdown-menu-news-up' : 'dropdown-menu-news'

  return (
    <div className='dropdown-anchor' ref={rootRef}>
      <button
        type='button'
        className='add-block-btn'
        aria-haspopup='menu'
        aria-expanded={open}
        onClick={() => setOpen(!open)}
      >
        <svg className='icon feather' aria-hidden='true'>
          <use xlinkHref='#plus' />
        </svg>
        {i18n.addBlock}
      </button>
      {open && (
        <div className={menuClassName} role='menu'>
          {(Object.keys(BLOCK_ICONS) as BlockType[]).map(type => (
            <button
              key={type}
              type='button'
              role='menuitem'
              className='dropdown-item-news'
              onClick={() => {
                onSelect(type, position)
                setOpen(false)
              }}
            >
              <svg className='icon feather' aria-hidden='true'>
                <use xlinkHref={`#${BLOCK_ICONS[type]}`} />
              </svg>
              {i18n.blockTypes[type]}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

type BlockCardProps = {
  block: Block,
  i18n: BlockEditorI18n,
  isEditing: boolean,
  isFirst: boolean,
  isLast: boolean,
  onEdit: () => void,
  onDelete: () => void,
  onMove: (offset: -1 | 1) => void,
}

const BlockCard = ({
  block,
  i18n,
  isEditing,
  isFirst,
  isLast,
  onEdit,
  onDelete,
  onMove,
}: BlockCardProps) => {
  const Preview = BLOCK_PREVIEWS[block.type]

  return (
    <article
      className={`dropzone-block${isEditing ? ' is-editing' : ''}`}
      data-block-id={block.id}
    >
      <header className='block-header'>
        <div className='block-title'>
          <button
            type='button'
            className='block-grip'
            aria-label={i18n.reorder}
            title={i18n.reorder}
          >
            <svg className='icon feather' aria-hidden='true'>
              <use xlinkHref='#more-vertical' />
            </svg>
          </button>
          <svg className='icon feather' aria-hidden='true'>
            <use xlinkHref={`#${BLOCK_ICONS[block.type]}`} />
          </svg>
          <span className='block-type-label'>{i18n.blockTypes[block.type]}</span>
        </div>
        <div className='block-controls'>
          <button
            type='button'
            className='icon-btn'
            aria-label={i18n.moveUp}
            disabled={isFirst}
            onClick={() => onMove(-1)}
          >
            <svg className='icon feather' aria-hidden='true'>
              <use xlinkHref='#chevron-up' />
            </svg>
          </button>
          <button
            type='button'
            className='icon-btn'
            aria-label={i18n.moveDown}
            disabled={isLast}
            onClick={() => onMove(1)}
          >
            <svg className='icon feather' aria-hidden='true'>
              <use xlinkHref='#chevron-down' />
            </svg>
          </button>
          <button type='button' className='icon-btn' aria-label={i18n.edit} onClick={onEdit}>
            <svg className='icon feather' aria-hidden='true'>
              <use xlinkHref='#edit-2' />
            </svg>
          </button>
          <button type='button' className='icon-btn' aria-label={i18n.remove} onClick={onDelete}>
            <svg className='icon feather' aria-hidden='true'>
              <use xlinkHref='#trash-2' />
            </svg>
          </button>
        </div>
      </header>
      <div className='block-separator' role='presentation' />
      <div className='block-body-preview'>
        <Preview data={block.data} />
      </div>
    </article>
  )
}

type EditAsideProps = {
  block: Block,
  i18n: BlockEditorI18n,
  uiLanguage: string,
  draft: BlockData,
  onChange: (key: string, value: string) => void,
  onSave: () => void,
  onClose: () => void,
}

const EditAside = ({
  block,
  i18n,
  uiLanguage,
  draft,
  onChange,
  onSave,
  onClose,
}: EditAsideProps) => {
  const asideRef = useRef<HTMLElement | null>(null)

  useEffect(() => {
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', closeOnEscape)
    return () => document.removeEventListener('keydown', closeOnEscape)
  }, [onClose])

  // Full-height aside between the web2018 header/breadcrumb and the footer:
  // it stops below the header and breadcrumb at the top of the page, and
  // above the footer when scrolled to the bottom.
  useEffect(() => {
    const aside = asideRef.current
    if (!aside) return undefined

    const update = () => {
      const scrollY = window.scrollY
      const header = document.querySelector('.header')
      const breadcrumb = document.querySelector('.breadcrumb-container')
      const footer = document.querySelector('.site > .mt-auto')

      let blockingTop = header instanceof HTMLElement ? header.offsetHeight : 0
      if (breadcrumb instanceof HTMLElement) {
        blockingTop = breadcrumb.getBoundingClientRect().bottom + scrollY
      }
      const footerTop =
        footer instanceof HTMLElement
          ? footer.getBoundingClientRect().top + scrollY
          : Number.POSITIVE_INFINITY

      const top = Math.max(0, blockingTop - scrollY)
      const bottom = Math.min(
        window.innerHeight,
        Math.max(top, footerTop - scrollY),
      )
      aside.style.setProperty('--nbe-aside-top', `${top}px`)
      aside.style.setProperty('--nbe-aside-bottom', `${window.innerHeight - bottom}px`)
    }
    update()
    window.addEventListener('scroll', update, { passive: true })
    window.addEventListener('resize', update)
    return () => {
      window.removeEventListener('scroll', update)
      window.removeEventListener('resize', update)
    }
  }, [])

  return (
    <aside className='edit-aside' ref={asideRef}>
      <div className='edit-aside-header'>
        <div className='edit-aside-title-row'>
          <h2 className='edit-aside-title'>
            {i18n.editBlockTitle.replace('{type}', i18n.blockTypes[block.type])}
          </h2>
          <button
            type='button'
            className='icon-btn edit-aside-close'
            aria-label={i18n.close}
            title={i18n.close}
            onClick={onClose}
          >
            <svg className='icon feather' aria-hidden='true'>
              <use xlinkHref='#x' />
            </svg>
          </button>
        </div>
        <button type='button' className='save-changes-btn' onClick={onSave}>
          {i18n.save}
        </button>
      </div>
      <div className='edit-aside-separator' role='presentation' />
      <div className='edit-aside-fields'>
        {BLOCK_FIELDS[block.type].map(field => {
          const fieldId = `block-${block.id}-field-${field.key}`
          return (
            <div className='edit-field' key={field.key}>
              <label className='edit-field-label' htmlFor={fieldId}>
                {i18n.fieldLabels[field.key]}
                {field.required && (
                  <span className='edit-field-required' aria-hidden='true'>*</span>
                )}
              </label>
              <TinyMceEditor
                id={fieldId}
                initialValue={draft[field.key] ?? ''}
                uiLanguage={uiLanguage}
                onChange={value => onChange(field.key, value)}
              />
            </div>
          )
        })}
      </div>
    </aside>
  )
}

const NewsBlocksEditor = ({
  newsId,
  language,
  uiLanguage,
  blocks: initialBlocks,
  i18n,
}: NewsBlocksEditorProps) => {
  const [blocks, setBlocks] = useState<Block[]>(() => toBlocks(initialBlocks))
  const [editingId, setEditingId] = useState<string | null>(null)
  const [draft, setDraft] = useState<BlockData | null>(null)
  const dropzoneRef = useRef<HTMLDivElement | null>(null)

  const editingBlock = blocks.find(block => block.id === editingId) ?? null

  // SortableJS drives the drag and drop: the grip is the handle and the DOM
  // move is reverted so React re-renders the new order from state.
  useEffect(() => {
    const zone = dropzoneRef.current
    if (!zone) return undefined
    const sortable = new Sortable(zone, {
      handle: '.block-grip',
      draggable: '.dropzone-block',
      animation: 150,
      forceFallback: true,
      fallbackClass: 'dropzone-block-fallback',
      chosenClass: 'dropzone-block-chosen',
      onMove: event => (
        event.related?.classList.contains('dropzone-block') ?? false
      ),
      onEnd: event => {
        // Indexes relative to the draggable blocks only, matching the
        // `blocks` state array (raw indexes would include the add buttons).
        const { oldDraggableIndex, newDraggableIndex, item, from } = event
        if (
          oldDraggableIndex === undefined ||
          newDraggableIndex === undefined ||
          oldDraggableIndex === newDraggableIndex
        ) return
        // The state id travels on the dragged element itself (the article
        // has no DOM `id` attribute).
        const draggedId = item.dataset.blockId ?? ''
        item.remove()
        const remaining = Array.from(from.querySelectorAll(':scope > .dropzone-block'))
        const reference = remaining[oldDraggableIndex]
        if (reference) {
          from.insertBefore(item, reference)
        } else if (remaining.length > 0) {
          remaining[remaining.length - 1].after(item)
        } else {
          from.appendChild(item)
        }
        // Updaters must stay idempotent: React may invoke them more than
        // once, and removing by id keeps a replayed update a no-op.
        setBlocks(previous => {
          const dragged = previous.find(block => block.id === draggedId)
          if (!dragged) return previous
          const next = previous.filter(block => block.id !== draggedId)
          next.splice(newDraggableIndex, 0, dragged)
          return next
        })
      },
    })
    return () => sortable.destroy()
  }, [])

  const addBlock = (type: BlockType, position: AddPosition) => {
    const block: Block = { id: createBlockId(), type, data: {} }
    setBlocks(previous =>
      previous.some(existing => existing.id === block.id)
        ? previous
        : position === 'top'
          ? [block, ...previous]
          : [...previous, block],
    )
  }

  const moveBlock = (blockId: string, offset: -1 | 1) => {
    setBlocks(previous => {
      const index = previous.findIndex(block => block.id === blockId)
      const target = index + offset
      if (index < 0 || target < 0 || target >= previous.length) return previous
      const next = [...previous]
      ;[next[index], next[target]] = [next[target], next[index]]
      return next
    })
  }

  const deleteBlock = (id: string) => {
    setBlocks(previous => previous.filter(block => block.id !== id))
    if (editingId === id) {
      setEditingId(null)
      setDraft(null)
    }
  }

  const openEditAside = (block: Block) => {
    setEditingId(block.id)
    setDraft(block.data)
  }

  const closeEditAside = () => {
    setEditingId(null)
    setDraft(null)
  }

  const changeDraftField = (key: string, value: string) => {
    setDraft(previous => ({ ...(previous ?? {}), [key]: value }))
  }

  // Live edits update the preview immediately; committing happens on save.
  const saveDraft = () => {
    if (editingId === null || draft === null) return
    setBlocks(previous =>
      previous.map(block => (block.id === editingId ? { ...block, data: draft } : block)),
    )
    closeEditAside()
  }

  return (
    <div className='news-blocks-editor' data-news-id={newsId ?? undefined} data-language={language}>
      <input type='hidden' name='blocks' value={JSON.stringify(toPayload(blocks))} />
      <div className='dropzone-blocs-dynamiques' ref={dropzoneRef}>
        <AddBlockButton position='top' i18n={i18n} onSelect={addBlock} />
        {blocks.map((block, index) => {
          const displayBlock =
            block.id === editingId && draft !== null ? { ...block, data: draft } : block
          return (
            <BlockCard
              key={block.id}
              block={displayBlock}
              i18n={i18n}
              isEditing={block.id === editingId}
              isFirst={index === 0}
              isLast={index === blocks.length - 1}
              onEdit={() => openEditAside(block)}
              onDelete={() => deleteBlock(block.id)}
              onMove={offset => moveBlock(block.id, offset)}
            />
          )
        })}
        {blocks.length > 0 && (
          <AddBlockButton position='bottom' i18n={i18n} onSelect={addBlock} />
        )}
      </div>
      {editingBlock && draft !== null && (
        <EditAside
          block={editingBlock}
          i18n={i18n}
          uiLanguage={uiLanguage}
          draft={draft}
          onChange={changeDraftField}
          onSave={saveDraft}
          onClose={closeEditAside}
        />
      )}
    </div>
  )
}

export default NewsBlocksEditor

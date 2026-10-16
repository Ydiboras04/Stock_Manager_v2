import { useEffect, useRef, useState, type KeyboardEvent } from 'react'
import { needsReplenishment, type Product } from './api'

export function ErrorText({ message }: { message: string }) {
  return message ? (
    <p className="flash" role="alert">
      {message}
    </p>
  ) : null
}

const STATUS_TONE: Record<string, string> = {
  SHIPPED: 'good',
  ACCEPTED: 'good',
  VALIDATED: 'good',
  ORDERED: 'good',
  REJECTED: 'bad',
  RESERVED: 'todo',
  PREPARED: 'todo',
  PENDING: 'todo',
  RECEIVED: 'todo',
}

export function Status({ value }: { value: string }) {
  return <span className={`status ${STATUS_TONE[value] ?? ''}`}>{value.replaceAll('_', ' ')}</span>
}

/** Page title plus who can act on the page, so each role knows what is theirs. */
export function PageHead({ title, who }: { title: string; who: string }) {
  return (
    <div className="page-head">
      <h2>{title}</h2>
      <span className="who">
        Actions here: <strong>{who}</strong>
      </span>
    </div>
  )
}

export function ProductCell({ products, id }: { products: Product[]; id: number }) {
  const product = products.find((p) => p.id === id)
  if (!product) return <>#{id}</>
  return (
    <>
      <span className="sku">{product.sku}</span> <span className="dim">{product.name}</span>
    </>
  )
}

const MAX_RESULTS = 8

/**
 * Search field to pick a product by SKU or name; works with long product lists.
 * Submits the chosen product id under `name` (hidden input).
 */
export function ProductPicker({ products, name = 'product_id' }: { products: Product[]; name?: string }) {
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState<Product | null>(null)
  const [open, setOpen] = useState(false)
  const [active, setActive] = useState(0)
  const input = useRef<HTMLInputElement>(null)

  const search = query.trim().toLowerCase()
  const found = products.filter((p) => `${p.sku} ${p.name}`.toLowerCase().includes(search))
  const results = found.slice(0, MAX_RESULTS)

  // The form can only be submitted once a product is chosen from the list.
  useEffect(() => {
    input.current?.setCustomValidity(selected ? '' : 'Choose a product from the list')
  }, [selected])

  // Clear the field when the form is reset (React resets forms after their action).
  useEffect(() => {
    const form = input.current?.form
    const clear = () => {
      setQuery('')
      setSelected(null)
    }
    form?.addEventListener('reset', clear)
    return () => form?.removeEventListener('reset', clear)
  }, [])

  function choose(product: Product) {
    setSelected(product)
    setQuery(`${product.sku} — ${product.name}`)
    setOpen(false)
  }

  function onKeyDown(event: KeyboardEvent) {
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault()
      const step = event.key === 'ArrowDown' ? 1 : -1
      setOpen(true)
      setActive((i) => Math.min(Math.max(i + step, 0), results.length - 1))
    } else if (event.key === 'Enter' && open && results[active]) {
      event.preventDefault()
      choose(results[active])
    } else if (event.key === 'Escape') {
      setOpen(false)
    }
  }

  return (
    <div className="picker">
      <input
        type="text"
        ref={input}
        value={query}
        placeholder="Search product (SKU or name)…"
        autoComplete="off"
        required
        onChange={(event) => {
          setQuery(event.target.value)
          setSelected(null)
          setActive(0)
          setOpen(true)
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        onKeyDown={onKeyDown}
      />
      <input type="hidden" name={name} value={selected?.id ?? ''} />
      {open && (
        <ul className="picker-list">
          {results.map((p, i) => (
            <li
              key={p.id}
              className={i === active ? 'active' : ''}
              // mousedown instead of click: runs before the input loses focus
              onMouseDown={(event) => {
                event.preventDefault()
                choose(p)
              }}
              onMouseEnter={() => setActive(i)}
            >
              <span>
                <span className="sku">{p.sku}</span> {p.name}
              </span>
              <span className={needsReplenishment(p) ? 'low-flag' : 'dim'}>
                {p.available} available
              </span>
            </li>
          ))}
          {results.length === 0 && <li className="hint">No product found</li>}
          {found.length > MAX_RESULTS && (
            <li className="hint">{found.length - MAX_RESULTS} more… keep typing to narrow down</li>
          )}
        </ul>
      )}
    </div>
  )
}

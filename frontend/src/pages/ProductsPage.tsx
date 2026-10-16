import { useState } from 'react'
import { api, needsReplenishment, run, useList, type PageProps, type Product } from '../api'
import { ErrorText, PageHead } from '../components'

export function ProductsPage({ role, onChange }: PageProps) {
  const { items: products, error, reload } = useList<Product>('/products')
  const [actionError, setActionError] = useState('')
  const [search, setSearch] = useState('')
  const [lowOnly, setLowOnly] = useState(false)

  const text = search.trim().toLowerCase()
  const shown = products.filter(
    (p) => `${p.sku} ${p.name}`.toLowerCase().includes(text) && (!lowOnly || needsReplenishment(p)),
  )

  async function create(form: FormData) {
    const body = {
      sku: form.get('sku'),
      name: form.get('name'),
      quantity: Number(form.get('quantity')),
      min_quantity: Number(form.get('min_quantity')),
    }
    setActionError(
      await run(
        () => api('/products', 'POST', body),
        () => {
          reload()
          onChange()
        },
      ),
    )
  }

  return (
    <>
      <PageHead title="Products" who="stock manager adds products" />
      {role === 'STOCK_MANAGER' && (
        <form action={create} className="panel">
          <h3>New product</h3>
          <div className="row">
            <input type="text" name="sku" placeholder="SKU" required style={{ width: '9em' }} />
            <input type="text" name="name" placeholder="Name" required style={{ flex: '1 1 200px' }} />
            <input name="quantity" type="number" min="0" placeholder="Initial qty" required />
            <input name="min_quantity" type="number" min="0" placeholder="Qmin" required />
            <button>Add product</button>
          </div>
        </form>
      )}
      <ErrorText message={error || actionError} />
      <div className="row">
        <input
          type="search"
          placeholder="Search by SKU or name…"
          aria-label="Search products"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ flex: '1 1 240px', maxWidth: 360 }}
        />
        <label className="check">
          <input type="checkbox" checked={lowOnly} onChange={(e) => setLowOnly(e.target.checked)} /> Low
          stock only
        </label>
        <span className="note">
          {shown.length} of {products.length} products
        </span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>SKU</th>
              <th>Name</th>
              <th className="num">Quantity</th>
              <th className="num">Reserved</th>
              <th className="num">Available</th>
              <th className="num">Qmin</th>
            </tr>
          </thead>
          <tbody>
            {shown.map((p) => (
              <tr key={p.id} className={needsReplenishment(p) ? 'low' : ''}>
                <td className="sku">{p.sku}</td>
                <td>
                  {p.name} {needsReplenishment(p) && <span className="low-flag">· at or below Qmin</span>}
                </td>
                <td className="num">{p.quantity}</td>
                <td className="num">{p.reserved}</td>
                <td className="num">{p.available}</td>
                <td className="num">{p.min_quantity}</td>
              </tr>
            ))}
            {shown.length === 0 && (
              <tr>
                <td colSpan={6} className="empty">
                  No product matches.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  )
}

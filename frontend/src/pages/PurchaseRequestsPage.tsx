import { useState } from 'react'
import { api, formatDate, run, useList, type PageProps, type Product, type PurchaseRequest } from '../api'
import { ErrorText, PageHead, ProductCell, ProductPicker, Status } from '../components'

export function PurchaseRequestsPage({ role, onChange }: PageProps) {
  const { items: requests, error, reload } = useList<PurchaseRequest>('/purchase-requests')
  const { items: products } = useList<Product>('/products')
  const [actionError, setActionError] = useState('')
  const canEdit = role === 'PURCHASING_MANAGER'

  const refresh = () => {
    reload()
    onChange()
  }

  async function create(form: FormData) {
    const body = { product_id: Number(form.get('product_id')), quantity: Number(form.get('quantity')) }
    setActionError(await run(() => api('/purchase-requests', 'POST', body), refresh))
  }

  async function act(id: number, step: 'validate' | 'reject') {
    setActionError(await run(() => api(`/purchase-requests/${id}/${step}`, 'POST'), refresh))
  }

  async function order(id: number, form: FormData) {
    const body = { purchase_request_id: id, supplier_name: form.get('supplier_name') }
    setActionError(await run(() => api('/supplier-orders', 'POST', body), refresh))
  }

  return (
    <>
      <PageHead title="Purchase requests" who="purchasing manager" />
      {canEdit && (
        <form action={create} className="panel">
          <h3>New purchase request</h3>
          <div className="row">
            <ProductPicker products={products} />
            <input name="quantity" type="number" min="1" placeholder="Quantity" required />
            <button>Create request</button>
          </div>
        </form>
      )}
      <ErrorText message={error || actionError} />
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th className="num">#</th>
              <th>Date</th>
              <th>Product</th>
              <th className="num">Qty</th>
              <th>Origin</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {[...requests].reverse().map((r) => (
              <tr key={r.id}>
                <td className="num">{r.id}</td>
                <td className="date">{formatDate(r.created_at)}</td>
                <td>
                  <ProductCell products={products} id={r.product_id} />
                </td>
                <td className="num">{r.quantity}</td>
                <td>{r.created_by_system ? 'System' : 'Manual'}</td>
                <td>
                  <Status value={r.status} />
                </td>
                <td className="actions">
                  {canEdit && r.status === 'PENDING' && (
                    <div className="row">
                      <button className="small" onClick={() => act(r.id, 'validate')}>
                        Validate
                      </button>
                      <button className="small danger" onClick={() => act(r.id, 'reject')}>
                        Reject
                      </button>
                    </div>
                  )}
                  {canEdit && r.status === 'VALIDATED' && (
                    <form action={(form) => order(r.id, form)} className="row">
                      <input
                        type="text"
                        name="supplier_name"
                        placeholder="Supplier"
                        required
                        style={{ width: '11em' }}
                      />
                      <button className="small">Order from supplier</button>
                    </form>
                  )}
                </td>
              </tr>
            ))}
            {requests.length === 0 && (
              <tr>
                <td colSpan={7} className="empty">
                  No purchase requests yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  )
}

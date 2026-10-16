import { useState } from 'react'
import { api, formatDate, run, useList, type CustomerOrder, type PageProps, type Product } from '../api'
import { ErrorText, PageHead, ProductCell, ProductPicker, Status } from '../components'

export function CustomerOrdersPage({ role, onChange }: PageProps) {
  const { items: orders, error, reload } = useList<CustomerOrder>('/customer-orders')
  const { items: products, reload: reloadProducts } = useList<Product>('/products')
  const [actionError, setActionError] = useState('')
  const canEdit = role === 'STOCK_MANAGER'

  const refresh = () => {
    reload()
    reloadProducts()
    onChange()
  }

  async function place(form: FormData) {
    const body = {
      product_id: Number(form.get('product_id')),
      quantity: Number(form.get('quantity')),
      customer_name: form.get('customer_name'),
    }
    setActionError(await run(() => api('/customer-orders', 'POST', body), refresh))
  }

  async function act(id: number, step: 'prepare' | 'ship') {
    setActionError(await run(() => api(`/customer-orders/${id}/${step}`, 'POST'), refresh))
  }

  return (
    <>
      <PageHead title="Customer orders" who="stock manager" />
      {canEdit && (
        <form action={place} className="panel">
          <h3>New customer order</h3>
          <div className="row">
            <ProductPicker products={products} />
            <input name="quantity" type="number" min="1" placeholder="Quantity" required />
            <input
              type="text"
              name="customer_name"
              placeholder="Customer"
              required
              style={{ flex: '1 1 180px', maxWidth: 260 }}
            />
            <button>Place order</button>
          </div>
          <p className="note">
            If the stock is too low, the order is rejected automatically, both roles are notified and the
            missing quantity goes to a purchase request.
          </p>
        </form>
      )}
      <ErrorText message={error || actionError} />
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th className="num">#</th>
              <th>Date</th>
              <th>Customer</th>
              <th>Product</th>
              <th className="num">Qty</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {[...orders].reverse().map((o) => (
              <tr key={o.id}>
                <td className="num">{o.id}</td>
                <td className="date">{formatDate(o.created_at)}</td>
                <td>{o.customer_name}</td>
                <td>
                  <ProductCell products={products} id={o.product_id} />
                </td>
                <td className="num">{o.quantity}</td>
                <td>
                  <Status value={o.status} />
                </td>
                <td className="actions">
                  {canEdit && o.status === 'RESERVED' && (
                    <button className="small" onClick={() => act(o.id, 'prepare')}>
                      Prepare parcel
                    </button>
                  )}
                  {canEdit && o.status === 'PREPARED' && (
                    <button className="small" onClick={() => act(o.id, 'ship')}>
                      Ship
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {orders.length === 0 && (
              <tr>
                <td colSpan={7} className="empty">
                  No customer orders yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  )
}

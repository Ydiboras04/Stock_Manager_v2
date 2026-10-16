import { Fragment, useState } from 'react'
import { api, formatDate, run, useList, type PageProps, type Product, type SupplierOrder } from '../api'
import { ErrorText, PageHead, ProductCell, Status } from '../components'

export function SupplierOrdersPage({ role, onChange }: PageProps) {
  const { items: orders, error, reload } = useList<SupplierOrder>('/supplier-orders')
  const { items: products } = useList<Product>('/products')
  const [actionError, setActionError] = useState('')
  // Supplier order whose non-conformity report is being written.
  const [rejectingId, setRejectingId] = useState<number | null>(null)
  const isBuyer = role === 'PURCHASING_MANAGER'
  const isStockManager = role === 'STOCK_MANAGER'

  const refresh = () => {
    reload()
    onChange()
  }

  async function act(id: number, step: string, body?: unknown) {
    const message = await run(() => api(`/supplier-orders/${id}/${step}`, 'POST', body), refresh)
    setActionError(message)
    if (!message) setRejectingId(null)
  }

  return (
    <>
      <PageHead
        title="Supplier orders"
        who="purchasing manager tracks the supplier · stock manager checks conformity"
      />
      <ErrorText message={error || actionError} />
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th className="num">#</th>
              <th>Supplier</th>
              <th>Product</th>
              <th className="num">Qty</th>
              <th>Ordered</th>
              <th>Shipped</th>
              <th>Received</th>
              <th>Status</th>
              <th>Notes</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {[...orders].reverse().map((o) => (
              <Fragment key={o.id}>
                <tr>
                  <td className="num">{o.id}</td>
                  <td>{o.supplier_name}</td>
                  <td>
                    <ProductCell products={products} id={o.product_id} />
                  </td>
                  <td className="num">{o.quantity}</td>
                  <td className="date">{formatDate(o.created_at)}</td>
                  <td className="date">{formatDate(o.shipped_at)}</td>
                  <td className="date">{formatDate(o.received_at)}</td>
                  <td>
                    <Status value={o.status} />
                  </td>
                  <td className="dim">
                    {o.accounting_validation_pending ? 'Accounting validation pending' : o.non_conformity_report}
                  </td>
                  <td className="actions">
                    {isBuyer && o.status === 'ORDERED' && (
                      <button className="small" onClick={() => act(o.id, 'ship')}>
                        Mark shipped
                      </button>
                    )}
                    {isBuyer && o.status === 'SHIPPED' && (
                      <button className="small" onClick={() => act(o.id, 'receive')}>
                        Mark received
                      </button>
                    )}
                    {isStockManager && o.status === 'RECEIVED' && rejectingId !== o.id && (
                      <div className="row">
                        <button className="small" onClick={() => act(o.id, 'accept')}>
                          Accept (conform)
                        </button>
                        <button className="small danger" onClick={() => setRejectingId(o.id)}>
                          Reject…
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
                {isStockManager && o.status === 'RECEIVED' && rejectingId === o.id && (
                  <tr className="subrow">
                    <td colSpan={10}>
                      <form
                        className="row"
                        action={(form) => act(o.id, 'reject', { report: form.get('report') })}
                      >
                        <label htmlFor={`report-${o.id}`}>Non-conformity report for delivery #{o.id}</label>
                        <input
                          type="text"
                          id={`report-${o.id}`}
                          name="report"
                          placeholder="What is wrong with the delivery?"
                          required
                          autoFocus
                          style={{ flex: '1 1 260px', maxWidth: 480 }}
                        />
                        <button className="small danger">Reject delivery</button>
                        <button type="button" className="small ghost" onClick={() => setRejectingId(null)}>
                          Cancel
                        </button>
                      </form>
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
            {orders.length === 0 && (
              <tr>
                <td colSpan={10} className="empty">
                  No supplier orders yet. Validate a purchase request, then order it from a supplier.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  )
}

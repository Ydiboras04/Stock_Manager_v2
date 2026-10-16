import { useCallback, useEffect, useState } from 'react'
import {
  login,
  needsReplenishment,
  ROLE_LABEL,
  setToken,
  useList,
  type CustomerOrder,
  type Notification,
  type Product,
  type PurchaseRequest,
  type Role,
  type Session,
  type SupplierOrder,
} from './api'
import { ErrorText } from './components'
import { CustomerOrdersPage } from './pages/CustomerOrdersPage'
import { NotificationsPage } from './pages/NotificationsPage'
import { ProductsPage } from './pages/ProductsPage'
import { PurchaseRequestsPage } from './pages/PurchaseRequestsPage'
import { SupplierOrdersPage } from './pages/SupplierOrdersPage'

const PAGES = {
  products: { label: 'Products', Page: ProductsPage },
  customerOrders: { label: 'Customer orders', Page: CustomerOrdersPage },
  purchaseRequests: { label: 'Purchase requests', Page: PurchaseRequestsPage },
  supplierOrders: { label: 'Supplier orders', Page: SupplierOrdersPage },
  notifications: { label: 'Notifications', Page: NotificationsPage },
}
type PageKey = keyof typeof PAGES

function loadSession(): Session | null {
  try {
    const session = JSON.parse(localStorage.getItem('session') ?? 'null') as Session | null
    setToken(session?.token ?? null)
    return session
  } catch {
    return null
  }
}

function LoginForm({ onLogin }: { onLogin: (session: Session) => void }) {
  const [error, setError] = useState('')

  async function submit(form: FormData) {
    try {
      onLogin(await login(String(form.get('username')), String(form.get('password'))))
    } catch (e) {
      setError((e as Error).message)
    }
  }

  return (
    <form action={submit} className="login">
      <h1>Stock Management</h1>
      <input type="text" name="username" placeholder="Username" required autoFocus />
      <input type="password" name="password" placeholder="Password" required />
      <button>Log in</button>
      <ErrorText message={error} />
    </form>
  )
}

export default function App() {
  const [session, setSession] = useState<Session | null>(loadSession)
  const [page, setPage] = useState<PageKey>('products')

  function saveSession(value: Session | null) {
    setToken(value?.token ?? null)
    if (value) localStorage.setItem('session', JSON.stringify(value))
    else localStorage.removeItem('session')
    setSession(value)
  }

  if (!session) return <LoginForm onLogin={saveSession} />
  return <Shell session={session} page={page} setPage={setPage} onLogout={() => saveSession(null)} />
}

/** Number shown on each tab: what is waiting for the current role there. */
function useTabCounts(role: Role) {
  const products = useList<Product>('/products')
  const orders = useList<CustomerOrder>('/customer-orders')
  const requests = useList<PurchaseRequest>('/purchase-requests')
  const supplierOrders = useList<SupplierOrder>('/supplier-orders')
  const notifications = useList<Notification>('/notifications')
  const isStockManager = role === 'STOCK_MANAGER'

  const counts: Record<PageKey, number> = {
    products: products.items.filter(needsReplenishment).length,
    customerOrders: isStockManager
      ? orders.items.filter((o) => o.status === 'RESERVED' || o.status === 'PREPARED').length
      : 0,
    purchaseRequests: isStockManager
      ? 0
      : requests.items.filter((r) => r.status === 'PENDING' || r.status === 'VALIDATED').length,
    supplierOrders: supplierOrders.items.filter((o) =>
      isStockManager ? o.status === 'RECEIVED' : o.status === 'ORDERED' || o.status === 'SHIPPED',
    ).length,
    notifications: notifications.items.filter((n) => !n.read).length,
  }

  const { reload: r1 } = products
  const { reload: r2 } = orders
  const { reload: r3 } = requests
  const { reload: r4 } = supplierOrders
  const { reload: r5 } = notifications
  const reload = useCallback(() => [r1, r2, r3, r4, r5].forEach((r) => r()), [r1, r2, r3, r4, r5])
  return { counts, reload }
}

const COUNT_TITLE: Record<PageKey, string> = {
  products: 'at or below Qmin',
  customerOrders: 'waiting for you',
  purchaseRequests: 'waiting for you',
  supplierOrders: 'waiting for you',
  notifications: 'unread',
}

function Shell({
  session,
  page,
  setPage,
  onLogout,
}: {
  session: Session
  page: PageKey
  setPage: (page: PageKey) => void
  onLogout: () => void
}) {
  const { counts, reload } = useTabCounts(session.role)

  // Check for changes made by the other role every 30 seconds.
  useEffect(() => {
    const timer = setInterval(reload, 30_000)
    return () => clearInterval(timer)
  }, [reload])

  const { Page } = PAGES[page]
  return (
    <>
      <header className="topbar">
        <div className="topbar-row gutter">
          <h1 className="brand">Stock Management</h1>
          <span className="user">
            <span>
              <strong>{session.username}</strong> · {ROLE_LABEL[session.role]}
            </span>
            <button className="small ghost" onClick={onLogout}>
              Log out
            </button>
          </span>
        </div>
        <nav className="tabs gutter" aria-label="Sections">
          {(Object.keys(PAGES) as PageKey[]).map((key) => (
            <button
              key={key}
              aria-current={key === page ? 'page' : undefined}
              onClick={() => {
                setPage(key)
                reload()
              }}
            >
              {PAGES[key].label}
              {counts[key] > 0 && (
                <span
                  className={key === 'notifications' ? 'count alert' : 'count'}
                  title={`${counts[key]} ${COUNT_TITLE[key]}`}
                >
                  {counts[key]}
                </span>
              )}
            </button>
          ))}
        </nav>
      </header>
      <main className="gutter">
        <Page role={session.role} onChange={reload} />
      </main>
    </>
  )
}

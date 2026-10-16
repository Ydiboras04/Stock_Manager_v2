import { useState } from 'react'
import { api, formatDate, run, useList, type Notification, type PageProps } from '../api'
import { ErrorText, PageHead } from '../components'

export function NotificationsPage({ onChange }: PageProps) {
  const { items: notifications, error, reload } = useList<Notification>('/notifications')
  const [actionError, setActionError] = useState('')
  const unread = notifications.filter((n) => !n.read)

  const refresh = () => {
    reload()
    onChange()
  }

  async function markRead(ids: number[]) {
    const calls = () => Promise.all(ids.map((id) => api(`/notifications/${id}/read`, 'POST')))
    setActionError(await run(calls, refresh))
  }

  return (
    <>
      <PageHead title="Notifications" who="each role reads its own" />
      <ErrorText message={error || actionError} />
      {unread.length > 1 && (
        <div className="row">
          <button className="small ghost" onClick={() => markRead(unread.map((n) => n.id))}>
            Mark all {unread.length} as read
          </button>
        </div>
      )}
      <div className="table-wrap">
        {notifications.map((n) => (
          <div key={n.id} className={n.read ? 'notif' : 'notif unread'}>
            <span className="when">{formatDate(n.created_at)}</span>
            <span className="msg">{n.message}</span>
            <span>
              {n.read ? (
                <span className="dim">Read</span>
              ) : (
                <button className="small ghost" onClick={() => markRead([n.id])}>
                  Mark as read
                </button>
              )}
            </span>
          </div>
        ))}
        {notifications.length === 0 && (
          <p className="empty">
            No notifications. They appear here when a customer order is rejected for lack of stock.
          </p>
        )}
      </div>
    </>
  )
}

import { useCallback, useEffect, useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export type Role = 'STOCK_MANAGER' | 'PURCHASING_MANAGER'

export interface Session {
  token: string
  role: Role
  username: string
}

export interface Product {
  id: number
  sku: string
  name: string
  quantity: number
  reserved: number
  available: number
  min_quantity: number
}

export interface CustomerOrder {
  id: number
  product_id: number
  quantity: number
  customer_name: string
  status: string
  created_at: string
}

export interface PurchaseRequest {
  id: number
  product_id: number
  quantity: number
  created_by_system: boolean
  status: string
  created_at: string
}

export interface Notification {
  id: number
  message: string
  product_id: number | null
  read: boolean
  created_at: string
}

/** Props received by every page. `onChange` lets a page tell the app something changed. */
export interface PageProps {
  role: Role
  onChange: () => void
}

export interface SupplierOrder {
  id: number
  purchase_request_id: number
  product_id: number
  quantity: number
  supplier_name: string
  status: string
  non_conformity_report: string | null
  accounting_validation_pending: boolean
  created_at: string
  shipped_at: string | null
  received_at: string | null
}

let token: string | null = null

export function setToken(value: string | null) {
  token = value
}

export async function api<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
  const response = await fetch(API_URL + path, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  if (response.status === 401) {
    // Token expired or invalid: go back to the login screen.
    localStorage.removeItem('session')
    window.location.reload()
  }
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    const detail = data?.detail
    throw new Error(typeof detail === 'string' ? detail : `Error ${response.status}`)
  }
  return data as T
}

export async function login(username: string, password: string): Promise<Session> {
  const response = await fetch(API_URL + '/auth/login', {
    method: 'POST',
    body: new URLSearchParams({ username, password }),
  })
  if (!response.ok) throw new Error('Wrong username or password')
  const data = await response.json()
  return { token: data.access_token, role: data.role, username }
}

/** Loads a list from the API and gives a function to reload it. */
export function useList<T>(path: string) {
  const [items, setItems] = useState<T[]>([])
  const [error, setError] = useState('')

  const reload = useCallback(() => {
    api<T[]>(path)
      .then((data) => {
        setItems(data)
        setError('')
      })
      .catch((e: Error) => setError(e.message))
  }, [path])

  useEffect(reload, [reload])
  return { items, error, reload }
}

/** Runs an API call, then reloads; returns the error message if any. */
export async function run(action: () => Promise<unknown>, reload: () => void): Promise<string> {
  try {
    await action()
    reload()
    return ''
  } catch (e) {
    return (e as Error).message
  }
}

export function productLabel(products: Product[], id: number) {
  const product = products.find((p) => p.id === id)
  return product ? `${product.sku} — ${product.name}` : `#${id}`
}

export function formatDate(iso: string | null) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' })
}

export const ROLE_LABEL: Record<Role, string> = {
  STOCK_MANAGER: 'stock manager',
  PURCHASING_MANAGER: 'purchasing manager',
}

export function needsReplenishment(product: Product) {
  return product.available <= product.min_quantity
}

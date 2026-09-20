import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

function App() {
  const [revenue, setRevenue] = useState([])
  const [topProducts, setTopProducts] = useState([])

  useEffect(() => {
    fetch('http://127.0.0.1:8000/analytics/revenue-by-month')
      .then((res) => res.json())
      .then((data) => {
        console.log('revenue data:', data)
        setRevenue(data)
      })

    fetch('http://127.0.0.1:8000/analytics/top-products?limit=8')
      .then((res) => res.json())
      .then((data) => {
        console.log('top products data:', data)
        setTopProducts(data)
      })
  }, [])

  return (
    <div>
      <h1>Sales Analytics</h1>

      <h2>Revenue by month</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={revenue}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="month" stroke="#6b7280" />
          <YAxis stroke="#6b7280" />
          <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
          <Line
            type="monotone"
            dataKey="revenue"
            stroke="#2563eb"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>

      <h2>Table view</h2>
      <table>
        <thead>
          <tr>
            <th>Month</th>
            <th>Revenue</th>
          </tr>
        </thead>
        <tbody>
          {revenue.map((row) => (
            <tr key={row.month}>
              <td>{row.month}</td>
              <td>${row.revenue.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Top products by revenue</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={topProducts} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis type="number" stroke="#6b7280" />
          <YAxis
            type="category"
            dataKey="product_name"
            stroke="#6b7280"
            width={150}
          />
          <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
          <Bar dataKey="revenue" fill="#2563eb" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default App

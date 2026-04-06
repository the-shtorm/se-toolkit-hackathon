import { useState } from 'react'

function App() {
  const [message, setMessage] = useState<string>('Loading...')

  useState(() => {
    fetch('/api/v1/health')
      .then((res) => res.json())
      .then((data) => {
        setMessage(`Backend Status: ${data.status}`)
      })
      .catch(() => {
        setMessage('Backend not connected')
      })
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">
          Smart Notification Manager
        </h1>
        <p className="text-gray-600 mb-2">Version 1.0.0</p>
        <div
          className={`p-4 rounded ${
            message.includes('healthy')
              ? 'bg-green-100 text-green-700'
              : 'bg-yellow-100 text-yellow-700'
          }`}
        >
          {message}
        </div>
        <p className="text-sm text-gray-500 mt-4">
          Real-time notification dashboard - Coming Soon
        </p>
      </div>
    </div>
  )
}

export default App

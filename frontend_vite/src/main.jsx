import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
// import TestApp from './TestApp'
import 'antd/dist/reset.css'
import './utils/errorHandler' // 导入全局错误处理器

console.log('主应用启动...')

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)

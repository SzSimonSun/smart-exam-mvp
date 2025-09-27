import React from 'react'
import ReactDOM from 'react-dom/client'

// 简单的测试应用
function TestApp() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>🎯 前端测试页面</h1>
      <p>如果你能看到这个页面，说明基础的React渲染是正常的。</p>
      <div style={{ background: '#f0f0f0', padding: '10px', margin: '10px 0' }}>
        <h3>测试项目：</h3>
        <ul>
          <li>✅ React 渲染</li>
          <li>✅ 基础样式</li>
          <li>✅ JavaScript 执行</li>
        </ul>
      </div>
      <button onClick={() => alert('JavaScript 正常工作！')}>
        点击测试 JavaScript
      </button>
    </div>
  )
}

console.log('🚀 测试应用启动...')

ReactDOM.createRoot(document.getElementById('root')).render(<TestApp />)
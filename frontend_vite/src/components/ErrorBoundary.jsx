import React from 'react'
import { Button, Modal, Typography } from 'antd'

const { Text } = Typography

// 错误边界组件，用于捕获React组件树中的错误
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error) {
    // 更新state以显示错误UI
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    // 捕获错误详情
    console.error('🚨 React Error Boundary捕获到错误:', error, errorInfo)
    this.setState({ error, errorInfo })

    // 检查是否是"message port closed"错误
    if (error.message && error.message.includes('message port closed')) {
      Modal.error({
        title: '连接错误',
        content: (
          <div>
            <p>检测到浏览器扩展或网络连接问题。</p>
            <p>建议操作：</p>
            <ul>
              <li>禁用浏览器扩展后重试</li>
              <li>刷新页面重新加载</li>
              <li>检查网络连接</li>
            </ul>
          </div>
        ),
        onOk: () => {
          window.location.reload()
        }
      })
    }
  }

  handleReload = () => {
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ 
          padding: '50px', 
          textAlign: 'center',
          background: '#f5f5f5',
          minHeight: '400px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center'
        }}>
          <h2 style={{ color: '#ff4d4f', marginBottom: '20px' }}>
            😔 页面出现了问题
          </h2>
          
          <div style={{ marginBottom: '30px', maxWidth: '600px' }}>
            <Text type="secondary">
              应用遇到了意外错误。这可能是由于浏览器扩展冲突、网络连接问题或其他原因导致的。
            </Text>
          </div>

          {this.state.error && (
            <div style={{ 
              marginBottom: '20px', 
              padding: '10px', 
              background: '#fff2f0', 
              border: '1px solid #ffccc7',
              borderRadius: '4px',
              maxWidth: '600px',
              textAlign: 'left'
            }}>
              <Text type="danger" code>
                {this.state.error.message}
              </Text>
            </div>
          )}

          <div>
            <Button 
              type="primary" 
              size="large"
              onClick={this.handleReload}
              style={{ marginRight: '16px' }}
            >
              刷新页面
            </Button>
            
            <Button 
              size="large"
              onClick={() => this.setState({ hasError: false, error: null, errorInfo: null })}
            >
              重试
            </Button>
          </div>

          <div style={{ marginTop: '30px' }}>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              如果问题持续存在，请尝试：<br/>
              1. 禁用浏览器扩展<br/>
              2. 清除浏览器缓存<br/>
              3. 使用无痕模式<br/>
              4. 联系技术支持
            </Text>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
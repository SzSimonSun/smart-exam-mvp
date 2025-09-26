import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider, App as AntdApp } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import { AuthProvider, useAuth } from './hooks/auth'
import Login from './pages/Login'
import ProLayout from './components/ProLayout'
import QuestionBank from './pages/QuestionBank'
import PaperBuilder from './pages/PaperBuilder'
import UploadScan from './pages/UploadScan'
import Report from './pages/Report'
import IngestReview from './pages/IngestReview'

// 受保护的路由组件
const RequireAuth = ({ children }) => {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        flexDirection: 'column'
      }}>
        <div className="ant-spin ant-spin-lg ant-spin-spinning">
          <span className="ant-spin-dot ant-spin-dot-spin">
            <i className="ant-spin-dot-item"></i>
            <i className="ant-spin-dot-item"></i>
            <i className="ant-spin-dot-item"></i>
            <i className="ant-spin-dot-item"></i>
          </span>
        </div>
        <div style={{ marginTop: 16, color: '#666' }}>正在加载用户信息...</div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return children
}

// 主应用组件（包含 ProLayout）
const MainApp = () => {
  return (
    <ProLayout>
      <Routes>
        <Route path="/" element={<Navigate to="/questions" replace />} />
        <Route path="/questions" element={<QuestionBank />} />
        <Route path="/paper" element={<PaperBuilder />} />
        <Route path="/upload" element={<UploadScan />} />
        <Route path="/report" element={<Report />} />
        <Route path="/ingest" element={<IngestReview />} />
        <Route path="*" element={<Navigate to="/questions" replace />} />
      </Routes>
    </ProLayout>
  )
}

export default function App() {
  return (
    <ConfigProvider 
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 6,
        },
        components: {
          Layout: {
            headerBg: '#fff',
            siderBg: '#fff',
          },
        },
      }}
    >
      <AntdApp>
        <AuthProvider>
          <Router
            future={{
              v7_startTransition: true,
              v7_relativeSplatPath: true
            }}
          >
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route
                path="/*"
                element={
                  <RequireAuth>
                    <MainApp />
                  </RequireAuth>
                }
              />
            </Routes>
          </Router>
        </AuthProvider>
      </AntdApp>
    </ConfigProvider>
  )
}

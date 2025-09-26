import React, { useState, useEffect } from 'react'
import { Layout, Menu, Button } from 'antd'
import { Link, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import Login from './pages/Login'
import QuestionBank from './pages/QuestionBank'
import PaperBuilder from './pages/PaperBuilder'
import UploadScan from './pages/UploadScan'
import Report from './pages/Report'
import IngestReview from './pages/IngestReview'

const { Header, Content } = Layout

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  // 检查登录状态
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      setIsAuthenticated(true)
    }
    setLoading(false)
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('token')
    setIsAuthenticated(false)
    navigate('/login')
  }

  if (loading) {
    return <div style={{display:'flex', justifyContent:'center', alignItems:'center', height:'100vh'}}>加载中...</div>
  }

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    )
  }

  return (
    <Layout style={{minHeight:'100vh'}}>
      <Header style={{display:'flex', alignItems:'center', justifyContent:'space-between'}}>
        <div style={{display:'flex', alignItems:'center'}}>
          <div style={{color:'#fff', fontWeight:700, marginRight:24}}>Smart Exam</div>
          <Menu theme="dark" mode="horizontal" selectable={false} items={[
            { key:'q', label:<Link to="/questions">题库</Link> },
            { key:'p', label:<Link to="/paper">出卷</Link> },
            { key:'u', label:<Link to="/upload">扫描上传</Link> },
            { key:'r', label:<Link to="/report">报表</Link> },
            { key:'i', label:<Link to="/ingest">拆题入库</Link> },
          ]}/>
        </div>
        <Button type="text" style={{color:'#fff'}} onClick={handleLogout}>
          退出登录
        </Button>
      </Header>
      <Content style={{padding:24}}>
        <Routes>
          <Route path="/questions" element={<QuestionBank/>} />
          <Route path="/paper" element={<PaperBuilder/>} />
          <Route path="/upload" element={<UploadScan/>} />
          <Route path="/report" element={<Report/>} />
          <Route path="/ingest" element={<IngestReview/>} />
          <Route path="*" element={<Navigate to="/questions" replace/>} />
        </Routes>
      </Content>
    </Layout>
  )
}

import React, { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import ProLayout from '@ant-design/pro-layout'
import { 
  BookOutlined, 
  FileTextOutlined, 
  CloudUploadOutlined, 
  BarChartOutlined,
  DatabaseOutlined,
  UserOutlined,
  LogoutOutlined,
  QuestionCircleOutlined,
  GithubOutlined
} from '@ant-design/icons'
import { Avatar, Dropdown, Space } from 'antd'
import { useAuth } from '../hooks/auth'

const SmartExamProLayout = ({ children }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuth()
  
  // 菜单配置
  const menuData = [
    {
      path: '/questions',
      key: '/questions',
      name: '题库管理',
      icon: <BookOutlined />,
      children: [
        {
          path: '/questions',
          key: '/questions',
          name: '题库列表',
        },
        {
          path: '/questions/upload',
          key: '/questions/upload',
          name: '试卷拆分',
        },
      ],
    },
    {
      path: '/paper',
      key: '/paper',
      name: '试卷构建',
      icon: <FileTextOutlined />,
    },
    {
      path: '/upload',
      key: '/upload',
      name: '扫描上传',
      icon: <CloudUploadOutlined />,
    },
    {
      path: '/report',
      key: '/report',
      name: '成绩报告',
      icon: <BarChartOutlined />,
    },
    {
      path: '/ingest',
      key: '/ingest',
      name: '拆题入库',
      icon: <DatabaseOutlined />,
    },
  ]

  // 用户下拉菜单
  const userDropdownMenu = {
    items: [
      {
        key: 'profile',
        icon: <UserOutlined />,
        label: '个人设置',
        onClick: () => navigate('/profile')
      },
      {
        type: 'divider',
      },
      {
        key: 'logout',
        icon: <LogoutOutlined />,
        label: '退出登录',
        onClick: logout
      }
    ]
  }

  return (
    <ProLayout
      title="智能试卷系统"
      logo={<BookOutlined style={{ fontSize: '22px', color: '#1890ff' }} />}
      layout="mix"
      splitMenus={false}
      navTheme="light"
      primaryColor="#1890ff"
      fixedHeader
      fixSiderbar
      colorWeak={false}
      siderWidth={256}
      style={{
        minHeight: '100vh',
      }}
      location={{
        pathname: location.pathname,
      }}
      route={{
        path: '/',
        routes: menuData,
      }}
      menuDataRender={() => menuData}
      // 使用 ProLayout 的默认路由处理，防止新开标签页
      onMenuHeaderClick={(e) => {
        console.log('菜单点击:', e)
        return false
      }}
      menuProps={{
        onClick: ({ key }) => {
          console.log('菜单项点击:', key)
          navigate(key)
        }
      }}
      avatarProps={{
        src: user?.avatar,
        title: user?.name || '用户',
        size: 'small',
        render: (props, dom) => {
          return (
            <Dropdown
              menu={userDropdownMenu}
              placement="bottomRight"
            >
              <Space style={{ cursor: 'pointer' }}>
                {dom}
                <span style={{ marginLeft: 8 }}>
                  {user?.name || '用户'}
                </span>
              </Space>
            </Dropdown>
          )
        },
      }}
      actionsRender={() => [
        <QuestionCircleOutlined 
          key="help" 
          style={{ color: '#666' }}
          onClick={() => window.open('/help', '_blank')}
        />,
        <GithubOutlined 
          key="github" 
          style={{ color: '#666' }}
          onClick={() => window.open('https://github.com', '_blank')}
        />
      ]}
      footerRender={() => (
        <div style={{ textAlign: 'center', color: '#999' }}>
          Smart Exam System ©2024 Created by AI Assistant
        </div>
      )}
      // 面包屑配置
      breadcrumbRender={(routers = []) => [
        {
          path: '/',
          breadcrumbName: '首页',
        },
        ...routers,
      ]}
      // 页面切换loading
      pageLoading={false}
      // 水印
      waterMarkProps={{
        content: user?.name || 'Smart Exam',
        fontSize: 16,
        gapX: 300,
        gapY: 200,
        rotate: -22,
        fontColor: 'rgba(0,0,0,0.03)'
      }}
    >
      <div style={{ minHeight: 'calc(100vh - 48px)' }}>
        {children}
      </div>
    </ProLayout>
  )
}

export default SmartExamProLayout
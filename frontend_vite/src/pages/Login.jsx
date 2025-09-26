import React, { useEffect } from 'react'
import { Card, Form, Input, Button, message, Spin } from 'antd'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/auth'

export default function Login() {
  const [form] = Form.useForm()
  const navigate = useNavigate()
  const { login, loading, user } = useAuth()

  // 如果已经登录，直接跳转
  useEffect(() => {
    if (user) {
      navigate('/questions')
    }
  }, [user, navigate])

  const onFinish = async (values) => {
    const success = await login(values.email, values.password)
    if (success) {
      navigate('/questions')
    }
  }

  const onFinishFailed = (errorInfo) => {
    console.log('Failed:', errorInfo)
  }

  return (
    <div style={{ display: 'grid', placeItems: 'center', height: '100vh', backgroundColor: '#f0f2f5' }}>
      <Card title="智能试卷系统 - 登录" style={{ width: 400, boxShadow: '0 4px 8px rgba(0,0,0,0.1)' }}>
        <Spin spinning={loading}>
          <Form
            form={form}
            name="login"
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
            autoComplete="off"
            layout="vertical"
            initialValues={{
              email: 'teacher@example.com',
              password: 'password'
            }}
          >
            <Form.Item
              label="邮箱"
              name="email"
              rules={[
                { required: true, message: '请输入邮箱!' },
                { type: 'email', message: '邮箱格式不正确!' }
              ]}
            >
              <Input placeholder="请输入邮箱" />
            </Form.Item>

            <Form.Item
              label="密码"
              name="password"
              rules={[{ required: true, message: '请输入密码!' }]}
            >
              <Input.Password placeholder="请输入密码" />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" block loading={loading}>
                登录
              </Button>
            </Form.Item>
          </Form>
        </Spin>
        
        <div style={{ marginTop: 16, padding: 12, backgroundColor: '#f6f8fa', borderRadius: 4 }}>
          <div style={{ fontSize: 12, color: '#666', marginBottom: 8 }}>📝 测试账号：</div>
          <div style={{ fontSize: 12, color: '#333' }}>
            <div>教师: teacher@example.com / password</div>
            <div>学生: student@example.com / password</div>
            <div>管理员: admin@example.com / password</div>
          </div>
        </div>
      </Card>
    </div>
  )
}

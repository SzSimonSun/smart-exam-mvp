import React, { useState } from 'react'
import { Card, Form, Input, Button, message } from 'antd'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function Login(){
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const onFinish = async (values) => {
    setLoading(true)
    try {
      const response = await axios.post('http://localhost:8000/api/auth/login', values)
      const { access_token } = response.data
      
      // 保存token到localStorage
      localStorage.setItem('token', access_token)
      
      message.success('登录成功！')
      navigate('/questions')
    } catch (error) {
      console.error('登录失败:', error)
      message.error('登录失败，请检查邮箱和密码')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{display:'grid', placeItems:'center', height:'70vh'}}>
      <Card title="登录" style={{width: 400}}>
        <Form onFinish={onFinish} style={{width:300}} initialValues={{
          email: 'teacher@example.com',
          password: 'password'
        }}>
          <Form.Item name="email" rules={[{required:true, message:'请输入邮箱'}]}>
            <Input placeholder="邮箱"/>
          </Form.Item>
          <Form.Item name="password" rules={[{required:true, message:'请输入密码'}]}>
            <Input.Password placeholder="密码"/>
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>登录</Button>
        </Form>
        <div style={{marginTop: 16, fontSize: 12, color: '#666'}}>
          测试账号: teacher@example.com / password
        </div>
      </Card>
    </div>
  )
}

import React from 'react'
import { Card, Form, Input, Button } from 'antd'

export default function Login(){
  const onFinish = (v)=>{
    console.log('login', v)
  }
  return (
    <div style={{display:'grid', placeItems:'center', height:'70vh'}}>
      <Card title="登录">
        <Form onFinish={onFinish} style={{width:300}}>
          <Form.Item name="email" rules={[{required:true, message:'请输入邮箱'}]}>
            <Input placeholder="邮箱"/>
          </Form.Item>
          <Form.Item name="password" rules={[{required:true, message:'请输入密码'}]}>
            <Input.Password placeholder="密码"/>
          </Form.Item>
          <Button type="primary" htmlType="submit" block>登录</Button>
        </Form>
      </Card>
    </div>
  )
}

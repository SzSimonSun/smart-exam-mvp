import React from 'react'
import { Card, Button, List } from 'antd'

export default function PaperBuilder(){
  const selected = [
    {id:1, stem:'下列哪个是质数？', score:2},
    {id:2, stem:'一元二次方程求根公式是？', score:5},
  ]
  return (
    <Card title="出卷器">
      <List
        dataSource={selected}
        renderItem={item=> <List.Item>{item.id}. {item.stem}（{item.score}分）</List.Item>}
      />
      <Button type="primary">导出 PDF</Button>
    </Card>
  )
}

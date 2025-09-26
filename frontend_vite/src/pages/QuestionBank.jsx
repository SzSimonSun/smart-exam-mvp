import React from 'react'
import { Table, Button, Space, Tag } from 'antd'

export default function QuestionBank(){
  const data = [
    {id:1, stem:'下列哪个是质数？', type:'single', difficulty:2, kps:['数论/质数']},
    {id:2, stem:'一元二次方程求根公式是？', type:'fill', difficulty:3, kps:['代数/一元二次方程/求根公式']},
  ]
  const columns = [
    { title:'ID', dataIndex:'id', width:80 },
    { title:'题干', dataIndex:'stem' },
    { title:'题型', dataIndex:'type', width:120 },
    { title:'难度', dataIndex:'difficulty', width:100 },
    { title:'知识点', dataIndex:'kps', render:(kps)=>kps.map(k=><Tag key={k}>{k}</Tag>) },
    { title:'操作', render:(_,r)=>(<Space><Button size="small">编辑</Button><Button size="small" type="primary">加入试卷</Button></Space>) }
  ]
  return <Table rowKey="id" columns={columns} dataSource={data}/>
}

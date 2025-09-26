import React from 'react'
import { Card, Descriptions, Table } from 'antd'

export default function Report(){
  const summary = { score: 92, correct: 23, total: 25 }
  const details = [
    {q:1, kp:'数论/质数', result:'对'},
    {q:2, kp:'代数/一元二次方程/求根公式', result:'错'},
  ]
  return (
    <Card title="答题报告">
      <Descriptions>
        <Descriptions.Item label="总分">{summary.score}</Descriptions.Item>
        <Descriptions.Item label="正确题数">{summary.correct}/{summary.total}</Descriptions.Item>
      </Descriptions>
      <Table rowKey="q" columns={[
        {title:'题号', dataIndex:'q', width:80},
        {title:'知识点', dataIndex:'kp'},
        {title:'结果', dataIndex:'result', width:100}
      ]} dataSource={details}/>
    </Card>
  )
}

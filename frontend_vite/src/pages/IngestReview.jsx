import React from 'react'
import { Card, List, Button } from 'antd'

export default function IngestReview(){
  const items = [
    {id:1, seq:1, crop:'/mock/crop1.png', kpSuggest:['代数/方程'], confidence:0.62},
    {id:2, seq:2, crop:'/mock/crop2.png', kpSuggest:['数论/质数'], confidence:0.71},
  ]
  return (
    <Card title="拆题入库审核">
      <List
        dataSource={items}
        renderItem={it=> (
          <List.Item actions={[<Button type="link">编辑</Button>, <Button type="primary">入库</Button>]}>
            <img src={it.crop} alt="" style={{width:120, height:80, objectFit:'cover', marginRight:12}}/>
            <div>候选#{it.seq}，建议KP：{it.kpSuggest.join('、')}（置信度 {Math.round(it.confidence*100)}%）</div>
          </List.Item>
        )}
      />
    </Card>
  )
}

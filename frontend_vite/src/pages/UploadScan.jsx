import React from 'react'
import { Upload, Button, message } from 'antd'
import { UploadOutlined } from '@ant-design/icons'

export default function UploadScan(){
  const props = {
    name: 'file',
    action: '/api/answer-sheets/upload',
    onChange(info){
      if (info.file.status === 'done') message.success('上传成功')
    }
  }
  return (
    <div>
      <Upload {...props}>
        <Button icon={<UploadOutlined/>}>上传扫描文件</Button>
      </Upload>
    </div>
  )
}

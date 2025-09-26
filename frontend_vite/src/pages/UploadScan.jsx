import React, { useState } from 'react'
import { Card, Form, Upload, Button, Select, Progress, Alert, List, Tag, Row, Col, message } from 'antd'
import { UploadOutlined, InboxOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons'
import { useUpload } from '../hooks/useUpload'
import { usePapers } from '../hooks/usePapers'

const { Option } = Select
const { Dragger } = Upload

export default function UploadScan() {
  const [form] = Form.useForm()
  const [selectedFiles, setSelectedFiles] = useState([])
  
  // 使用hooks
  const { uploading, progress, uploadedFiles, uploadAnswerSheet, clearUploadedFiles } = useUpload()
  const { papers } = usePapers()

  // 文件上传前的检查
  const beforeUpload = (file) => {
    const isImage = file.type.startsWith('image/')
    const isPDF = file.type === 'application/pdf'
    
    if (!isImage && !isPDF) {
      message.error('只能上传图片或PDF文件！')
      return false
    }
    
    const isLt10M = file.size / 1024 / 1024 < 10
    if (!isLt10M) {
      message.error('文件大小不能超过10MB！')
      return false
    }
    
    return false // 阻止自动上传
  }

  // 文件选择变化
  const handleFileChange = ({ fileList }) => {
    setSelectedFiles(fileList)
  }

  // 上传处理
  const handleUpload = async (values) => {
    if (selectedFiles.length === 0) {
      message.error('请选择要上传的文件')
      return
    }

    try {
      const file = selectedFiles[0].originFileObj
      await uploadAnswerSheet(file, values.paper_id, values.class_id)
      
      // 清空文件选择
      setSelectedFiles([])
      form.resetFields(['file'])
    } catch (error) {
      console.error('上传失败:', error)
    }
  }

  return (
    <Row gutter={16}>
      <Col span={16}>
        <Card title="答题卡上传">
          <Form form={form} layout="vertical" onFinish={handleUpload}>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="paper_id"
                  label="选择试卷"
                  rules={[{ required: true, message: '请选择试卷' }]}
                >
                  <Select placeholder="请选择试卷">
                    {papers.map(paper => (
                      <Option key={paper.id} value={paper.id}>
                        {paper.name}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="class_id"
                  label="选择班级"
                  rules={[{ required: true, message: '请选择班级' }]}
                >
                  <Select placeholder="请选择班级">
                    <Option value={1}>初一(1)班</Option>
                    <Option value={2}>初一(2)班</Option>
                    <Option value={3}>初二(1)班</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Form.Item name="file" label="选择文件">
              <Dragger
                beforeUpload={beforeUpload}
                onChange={handleFileChange}
                fileList={selectedFiles}
              >
                <p className="ant-upload-drag-icon">
                  <InboxOutlined />
                </p>
                <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
                <p className="ant-upload-hint">
                  支持 JPG、PNG、PDF 格式，单个文件不超过10MB
                </p>
              </Dragger>
            </Form.Item>

            {uploading && (
              <Progress percent={progress} status="active" style={{ marginBottom: 16 }} />
            )}

            <Form.Item>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={uploading}
                disabled={selectedFiles.length === 0}
              >
                上传文件
              </Button>
            </Form.Item>
          </Form>
        </Card>
      </Col>
      
      <Col span={8}>
        <Card title="上传历史" extra={
          <Button size="small" onClick={clearUploadedFiles}>清空记录</Button>
        }>
          {uploadedFiles.length > 0 ? (
            <List
              size="small"
              dataSource={uploadedFiles}
              renderItem={item => (
                <List.Item>
                  <List.Item.Meta
                    title={item.name}
                    description={
                      <Tag color={item.status === 'success' ? 'green' : 'red'}>
                        {item.status === 'success' ? '上传成功' : '上传失败'}
                      </Tag>
                    }
                  />
                </List.Item>
              )}
            />
          ) : (
            <div style={{ textAlign: 'center', padding: 20, color: '#999' }}>
              暂无上传记录
            </div>
          )}
        </Card>
      </Col>
    </Row>
  )
}

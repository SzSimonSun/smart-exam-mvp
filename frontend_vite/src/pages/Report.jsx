import React, { useState } from 'react'
import { Card, Form, Input, Button, Table, Descriptions, Tag, Row, Col, Statistic, Progress, message } from 'antd'
import { SearchOutlined, DownloadOutlined, EyeOutlined } from '@ant-design/icons'
import api from '../hooks/api'

export default function Report() {
  const [form] = Form.useForm()
  const [reportData, setReportData] = useState(null)
  const [loading, setLoading] = useState(false)

  // 获取报告
  const fetchReport = async (values) => {
    setLoading(true)
    try {
      const response = await api.get(`/api/answer-sheets/${values.sheetId}/report`)
      setReportData(response.data)
      message.success('报告获取成功！')
    } catch (error) {
      console.error('获取报告失败:', error)
      message.error('获取报告失败')
      setReportData(null)
    } finally {
      setLoading(false)
    }
  }

  // 题目结果表格列
  const columns = [
    { title: '题号', dataIndex: 'question_id', width: 80 },
    {
      title: '得分',
      dataIndex: 'score',
      width: 80,
      render: (score, record) => (
        <Tag color={record.is_correct ? 'green' : 'red'}>
          {score}分
        </Tag>
      )
    },
    {
      title: '结果',
      dataIndex: 'is_correct',
      width: 80,
      render: (isCorrect) => (
        <Tag color={isCorrect ? 'green' : 'red'}>
          {isCorrect ? '正确' : '错误'}
        </Tag>
      )
    }
  ]

  return (
    <div>
      {/* 查询区域 */}
      <Card title="学生成绩报告" style={{ marginBottom: 16 }}>
        <Form form={form} layout="inline" onFinish={fetchReport}>
          <Form.Item
            name="sheetId"
            label="答题卡ID"
            rules={[{ required: true, message: '请输入答题卡ID' }]}
          >
            <Input 
              placeholder="请输入答题卡ID" 
              style={{ width: 200 }}
            />
          </Form.Item>
          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              icon={<SearchOutlined />}
              loading={loading}
            >
              查询报告
            </Button>
          </Form.Item>
        </Form>
        
        <div style={{ marginTop: 16, padding: 12, backgroundColor: '#f6f8fa', borderRadius: 4 }}>
          <p style={{ margin: 0, fontSize: 12, color: '#666' }}>
            📝 提示：输入答题卡ID查看学生成绩报告。示例ID: 1, 2, 3
          </p>
        </div>
      </Card>

      {/* 报告内容 */}
      {reportData && (
        <Row gutter={16}>
          <Col span={16}>
            <Card title="基本信息" style={{ marginBottom: 16 }}>
              <Descriptions column={2}>
                <Descriptions.Item label="学生姓名">{reportData.student_name}</Descriptions.Item>
                <Descriptions.Item label="试卷名称">{reportData.paper_name}</Descriptions.Item>
                <Descriptions.Item label="总分">
                  <span style={{ fontSize: 18, fontWeight: 'bold', color: '#1890ff' }}>
                    {reportData.total_score}分
                  </span>
                </Descriptions.Item>
                <Descriptions.Item label="答题时间">
                  {new Date().toLocaleString()}
                </Descriptions.Item>
              </Descriptions>
            </Card>

            <Card title="题目结果" extra={
              <Button icon={<DownloadOutlined />}>导出报告</Button>
            }>
              <Table
                rowKey="question_id"
                columns={columns}
                dataSource={reportData.items}
                pagination={false}
                size="small"
              />
            </Card>
          </Col>

          <Col span={8}>
            <Card title="成绩统计" style={{ marginBottom: 16 }}>
              <Statistic
                title="总分"
                value={reportData.total_score}
                suffix="/ 100"
                valueStyle={{ color: '#1890ff' }}
              />
              <Progress 
                percent={reportData.total_score} 
                strokeColor={{ '0%': '#ff4d4f', '60%': '#faad14', '80%': '#52c41a' }}
                style={{ marginTop: 16 }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {!reportData && !loading && (
        <Card>
          <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
            请输入答题卡ID查询报告
          </div>
        </Card>
      )}
    </div>
  )
}

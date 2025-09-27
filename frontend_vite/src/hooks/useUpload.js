import { useState, useCallback } from 'react'
import { message } from 'antd'
import api from './api'

// 文件上传Hook
export const useUpload = () => {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [uploadedFiles, setUploadedFiles] = useState([])

  // 上传答题卡
  const uploadAnswerSheet = useCallback(async (file, paperId, classId, options = {}) => {
    setUploading(true)
    setProgress(0)

    const formData = new FormData()
    formData.append('file', file)

    // 添加其他选项到FormData
    Object.keys(options).forEach(key => {
      formData.append(key, options[key])
    })

    try {
      // 将paper_id和class_id作为查询参数发送
      const response = await api.post(`/api/answer-sheets/upload?paper_id=${paperId}&class_id=${classId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          setProgress(percentCompleted)
        }
      })

      message.success('答题卡上传成功！')
      
      setUploadedFiles(prev => [...prev, {
        id: response.data.sheet_id || Date.now(),
        name: file.name,
        status: 'success',
        response: response.data
      }])

      return response.data
    } catch (error) {
      console.error('上传答题卡失败:', error)
      message.error('上传答题卡失败')
      
      setUploadedFiles(prev => [...prev, {
        id: Date.now(),
        name: file.name,
        status: 'error',
        error: error.message
      }])
      
      throw error
    } finally {
      setUploading(false)
      setProgress(0)
    }
  }, [])

  // 批量上传答题卡
  const uploadMultipleAnswerSheets = useCallback(async (files, paperId, classId, options = {}) => {
    const results = []
    const totalFiles = files.length
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      try {
        const result = await uploadAnswerSheet(file, paperId, classId, options)
        results.push({ file: file.name, success: true, data: result })
        
        // 更新整体进度
        const overallProgress = Math.round(((i + 1) / totalFiles) * 100)
        setProgress(overallProgress)
        
      } catch (error) {
        results.push({ file: file.name, success: false, error: error.message })
      }
    }

    const successCount = results.filter(r => r.success).length
    const failCount = results.filter(r => !r.success).length

    if (successCount > 0) {
      message.success(`成功上传 ${successCount} 个文件`)
    }
    if (failCount > 0) {
      message.error(`${failCount} 个文件上传失败`)
    }

    return results
  }, [uploadAnswerSheet])

  // 上传试卷文件（用于拆题）
  const uploadPaperForIngest = useCallback(async (file, options = {}) => {
    setUploading(true)
    setProgress(0)

    const formData = new FormData()
    formData.append('file', file)
    
    // 添加其他选项
    Object.keys(options).forEach(key => {
      formData.append(key, options[key])
    })

    try {
      const response = await api.post('/api/ingest/sessions', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 60000, // 文件上传设置60秒超时
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          setProgress(percentCompleted)
        }
      })

      message.success('试卷文件上传成功！')
      return response.data
    } catch (error) {
      console.error('上传试卷文件失败:', error)
      message.error('上传试卷文件失败')
      throw error
    } finally {
      setUploading(false)
      setProgress(0)
    }
  }, [])

  // 获取上传进度
  const getUploadProgress = useCallback(async (uploadId) => {
    try {
      const response = await api.get(`/api/upload/progress/${uploadId}`)
      return response.data
    } catch (error) {
      console.error('获取上传进度失败:', error)
      return null
    }
  }, [])

  // 清除上传记录
  const clearUploadedFiles = useCallback(() => {
    setUploadedFiles([])
    setProgress(0)
  }, [])

  // 取消上传
  const cancelUpload = useCallback(() => {
    setUploading(false)
    setProgress(0)
    // 这里可以添加取消请求的逻辑
  }, [])

  return {
    uploading,
    progress,
    uploadedFiles,
    uploadAnswerSheet,
    uploadMultipleAnswerSheets,
    uploadPaperForIngest,
    getUploadProgress,
    clearUploadedFiles,
    cancelUpload
  }
}

// 上传状态监听Hook
export const useUploadStatus = (uploadId) => {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)

  const checkStatus = useCallback(async () => {
    if (!uploadId) return

    setLoading(true)
    try {
      const response = await api.get(`/api/upload/status/${uploadId}`)
      setStatus(response.data)
    } catch (error) {
      console.error('检查上传状态失败:', error)
    } finally {
      setLoading(false)
    }
  }, [uploadId])

  return {
    status,
    loading,
    checkStatus
  }
}
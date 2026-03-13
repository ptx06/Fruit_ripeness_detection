import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { detectionAPI } from '../services/api'

const DetectionPage = () => {
  const { user } = useAuth()
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (file) {
      setSelectedFile(file)
      setPreviewUrl(URL.createObjectURL(file))
      setResult(null)
      setError('')
    }
  }

  const handleDetect = async () => {
    if (!selectedFile) {
      setError('请选择图片文件')
      return
    }

    if (!user) {
      setError('请先登录')
      return
    }

    setLoading(true)
    setError('')

    try {
      const detectionResult = await detectionAPI.detectFruit(selectedFile)
      setResult(detectionResult)
    } catch (err) {
      setError('检测失败: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  const resetDetection = () => {
    setSelectedFile(null)
    setPreviewUrl('')
    setResult(null)
    setError('')
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">水果成熟度检测</h1>
        <p className="text-gray-600">上传水果图片，系统将自动检测水果的成熟度状态</p>
      </div>

      {!user && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <p className="text-yellow-800">
            请先登录以使用检测功能。演示账号: demo / demo
          </p>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-8">
        {/* 上传区域 */}
        <div className="card p-6">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              选择水果图片
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-400 transition-colors">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <div className="mx-auto w-12 h-12 mb-3">
                  <svg className="w-full h-full text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <span className="text-primary-600 font-medium">点击选择文件</span>
                <p className="text-xs text-gray-500 mt-1">支持 JPG, PNG 格式</p>
              </label>
            </div>
          </div>

          {previewUrl && (
            <div className="mb-4">
              <img
                src={previewUrl}
                alt="预览"
                className="max-h-64 mx-auto rounded-lg shadow-sm"
              />
            </div>
          )}

          <div className="flex space-x-3">
            <button
              onClick={handleDetect}
              disabled={!selectedFile || !user || loading}
              className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '检测中...' : '开始检测'}
            </button>
            <button
              onClick={resetDetection}
              className="btn-secondary"
            >
              重置
            </button>
          </div>
        </div>

        {/* 结果区域 */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">检测结果</h3>
          
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          {result ? (
            <div>
              <div className="mb-4">
                <img
                  src={`http://localhost:8000${result.result_image_url}`}
                  alt="检测结果"
                  className="max-h-64 mx-auto rounded-lg shadow-sm"
                />
              </div>
              
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">检测时间:</span>
                  <span className="text-gray-900">
                    {new Date(result.timestamp).toLocaleString('zh-CN')}
                  </span>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">检测数量:</span>
                  <span className="text-gray-900">{result.detections.length} 个水果</span>
                </div>
              </div>

              {result.detections.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-medium text-gray-900 mb-2">检测详情:</h4>
                  <div className="space-y-2">
                    {result.detections.map((detection, index) => (
                      <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span className="font-medium capitalize">{detection.class_name}</span>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-600">置信度:</span>
                          <span className="font-medium text-primary-600">
                            {(detection.confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <svg className="mx-auto w-12 h-12 mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p>检测结果将显示在这里</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default DetectionPage
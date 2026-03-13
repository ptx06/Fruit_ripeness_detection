import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { detectionAPI } from '../services/api'

const HistoryPage = () => {
  const { user } = useAuth()
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState(null)

  useEffect(() => {
    if (user) {
      loadHistory()
      loadStats()
    }
  }, [user])

  const loadHistory = async () => {
    try {
      const historyData = await detectionAPI.getHistory()
      setHistory(historyData)
    } catch (error) {
      console.error('加载历史失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const statsData = await detectionAPI.getStats()
      setStats(statsData)
    } catch (error) {
      console.error('加载统计失败:', error)
    }
  }

  if (!user) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="text-center py-12">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">检测历史</h1>
          <p className="text-gray-600">请先登录以查看检测历史记录</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">检测历史</h1>
        <p className="text-gray-600">查看您的水果检测历史记录</p>
      </div>

      {/* 统计信息 */}
      {stats && (
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="card p-6">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">总检测次数</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_detections}</p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">最近7天检测</p>
                <p className="text-2xl font-bold text-gray-900">{stats.recent_detections}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 历史记录列表 */}
      <div className="card">
        <div className="p-6 border-b">
          <h2 className="text-lg font-semibold text-gray-900">检测记录</h2>
        </div>

        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">加载中...</p>
          </div>
        ) : history.length === 0 ? (
          <div className="p-8 text-center">
            <svg className="mx-auto w-12 h-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="text-gray-600">暂无检测记录</p>
          </div>
        ) : (
          <div className="divide-y">
            {history.map((record) => {
              let resultData
              try {
                resultData = JSON.parse(record.result_data)
              } catch (error) {
                resultData = null
              }

              return (
                <div key={record.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      {resultData?.result_path && (
                        <img
                          src={`http://localhost:8000/results/${resultData.result_path.split('/').pop()}`}
                          alt="检测结果"
                          className="w-16 h-16 object-cover rounded-lg"
                        />
                      )}
                      <div>
                        <p className="font-medium text-gray-900">{record.filename}</p>
                        <p className="text-sm text-gray-500">
                          {new Date(record.created_at).toLocaleString('zh-CN')}
                        </p>
                        {resultData?.detections && (
                          <p className="text-sm text-gray-600 mt-1">
                            检测到 {resultData.detections.length} 个水果
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {resultData?.detections && (
                        <div className="flex flex-wrap gap-1">
                          {resultData.detections.slice(0, 3).map((detection, index) => (
                            <span
                              key={index}
                              className="px-2 py-1 text-xs font-medium bg-primary-100 text-primary-800 rounded-full capitalize"
                            >
                              {detection.class_name}
                            </span>
                          ))}
                          {resultData.detections.length > 3 && (
                            <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded-full">
                              +{resultData.detections.length - 3}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

export default HistoryPage
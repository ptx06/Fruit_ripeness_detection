import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器，自动添加token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API方法
export const detectionAPI = {
  // 检测水果
  detectFruit: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/detect', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // 获取检测历史
  getHistory: async (skip = 0, limit = 10) => {
    const response = await api.get(`/history?skip=${skip}&limit=${limit}`)
    return response.data
  },

  // 获取检测详情
  getDetectionDetails: async (historyId) => {
    const response = await api.get(`/history/${historyId}`)
    return response.data
  },

  // 获取统计信息
  getStats: async () => {
    const response = await api.get('/stats')
    return response.data
  },
}

export const authAPI = {
  // 登录
  login: async (username, password) => {
    const response = await api.post('/auth/login', { username, password })
    return response.data
  },

  // 注册
  register: async (userData) => {
    const response = await api.post('/auth/register', userData)
    return response.data
  },

  // 获取当前用户信息
  getCurrentUser: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },
}

export default api
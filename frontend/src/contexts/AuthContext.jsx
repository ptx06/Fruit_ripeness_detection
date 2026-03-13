import React, { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../services/api'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth必须在AuthProvider内使用')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // 检查本地存储的token
    const token = localStorage.getItem('token')
    if (token) {
      // 这里可以添加验证token有效性的逻辑
      setUser({ id: 'demo-user', username: '演示用户' })
    }
    setLoading(false)
  }, [])

  const login = async (username, password) => {
    try {
      // 演示用，实际应该调用后端API
      if (username === 'demo' && password === 'demo') {
        const userData = { id: 'demo-user', username: '演示用户' }
        setUser(userData)
        localStorage.setItem('token', 'demo-token')
        return { success: true }
      }
      return { success: false, error: '用户名或密码错误' }
    } catch (error) {
      return { success: false, error: '登录失败' }
    }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('token')
  }

  const value = {
    user,
    login,
    logout,
    loading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Home from './pages/Home';
import MyCertificates from './pages/MyCertificates';
import './App.css';

// 创建 React Query 客户端
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// 受保护的路由组件
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  return isAuthenticated() ? children : <Navigate to="/login" />;
};

// 公共路由组件（已登录用户重定向到首页）
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  return isAuthenticated() ? <Navigate to="/" /> : children;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <div className="App">
            <Routes>
              {/* 公共路由 */}
              <Route 
                path="/login" 
                element={
                  <PublicRoute>
                    <Login />
                  </PublicRoute>
                } 
              />
              <Route 
                path="/register" 
                element={
                  <PublicRoute>
                    <Register />
                  </PublicRoute>
                } 
              />
              
              {/* 受保护的路由 */}
              <Route 
                path="/" 
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Home />
                    </Layout>
                  </ProtectedRoute>
                } 
              />
              
              {/* 其他受保护的路由将在后续添加 */}
              <Route 
                path="/my-applications" 
                element={
                  <ProtectedRoute>
                    <Layout>
                      <div className="container mx-auto px-4 py-8">
                        <h1 className="text-2xl font-bold">我的报名</h1>
                        <p className="text-gray-600 mt-2">功能开发中...</p>
                      </div>
                    </Layout>
                  </ProtectedRoute>
                } 
              />
              
              <Route 
                path="/my-scores" 
                element={
                  <ProtectedRoute>
                    <Layout>
                      <div className="container mx-auto px-4 py-8">
                        <h1 className="text-2xl font-bold">我的成绩</h1>
                        <p className="text-gray-600 mt-2">功能开发中...</p>
                      </div>
                    </Layout>
                  </ProtectedRoute>
                } 
              />
              
              <Route 
                path="/my-certificates" 
                element={
                  <ProtectedRoute>
                    <Layout>
                      <MyCertificates />
                    </Layout>
                  </ProtectedRoute>
                } 
              />
              
              {/* 管理员路由 */}
              <Route 
                path="/admin/*" 
                element={
                  <ProtectedRoute>
                    <Layout>
                      <div className="container mx-auto px-4 py-8">
                        <h1 className="text-2xl font-bold">管理员功能</h1>
                        <p className="text-gray-600 mt-2">功能开发中...</p>
                      </div>
                    </Layout>
                  </ProtectedRoute>
                } 
              />
              
              {/* 404 页面 */}
              <Route 
                path="*" 
                element={
                  <div className="min-h-screen flex items-center justify-center">
                    <div className="text-center">
                      <h1 className="text-4xl font-bold text-gray-900">404</h1>
                      <p className="text-gray-600 mt-2">页面未找到</p>
                    </div>
                  </div>
                } 
              />
            </Routes>
          </div>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;

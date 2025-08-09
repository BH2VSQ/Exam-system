import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { examAPI } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Calendar, MapPin, Users, Search, Plus } from 'lucide-react';
import { format } from 'date-fns';
import { zhCN } from 'date-fns/locale';

const Home = () => {
  const [exams, setExams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  const { user, isAdmin } = useAuth();

  const fetchExams = async () => {
    try {
      setLoading(true);
      const params = {
        page: currentPage,
        per_page: 10,
      };
      
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      
      const response = await examAPI.getExams(params);
      setExams(response.data.exams);
      setTotalPages(response.data.pages);
      setError('');
    } catch (err) {
      setError('获取考试列表失败');
      console.error('Error fetching exams:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExams();
  }, [currentPage, statusFilter]);

  const getStatusBadge = (status) => {
    const statusMap = {
      draft: { label: '草稿', variant: 'secondary' },
      published: { label: '已发布', variant: 'default' },
      closed: { label: '已关闭', variant: 'destructive' },
    };
    
    const statusInfo = statusMap[status] || { label: status, variant: 'secondary' };
    return <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>;
  };

  const getRegistrationStatus = (exam) => {
    const now = new Date();
    const regStart = new Date(exam.registration_start);
    const regEnd = new Date(exam.registration_end);
    
    if (now < regStart) {
      return { label: '未开始', variant: 'secondary' };
    } else if (now > regEnd) {
      return { label: '已结束', variant: 'destructive' };
    } else {
      return { label: '报名中', variant: 'default' };
    }
  };

  const filteredExams = exams.filter(exam =>
    exam.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    exam.organizer?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">考试报名管理平台</h1>
          <p className="text-gray-600 mt-2">欢迎，{user?.username}！</p>
        </div>
        {isAdmin() && (
          <Button asChild>
            <Link to="/admin/exams/create">
              <Plus className="mr-2 h-4 w-4" />
              创建考试
            </Link>
          </Button>
        )}
      </div>

      {/* 搜索和筛选 */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
          <Input
            placeholder="搜索考试名称或组织者..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="选择状态" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部状态</SelectItem>
            <SelectItem value="published">已发布</SelectItem>
            <SelectItem value="draft">草稿</SelectItem>
            <SelectItem value="closed">已关闭</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* 考试列表 */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredExams.map((exam) => {
          const regStatus = getRegistrationStatus(exam);
          return (
            <Card key={exam.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <CardTitle className="text-lg">{exam.name}</CardTitle>
                  {getStatusBadge(exam.status)}
                </div>
                <CardDescription>{exam.organizer}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center text-sm text-gray-600">
                    <Calendar className="mr-2 h-4 w-4" />
                    考试时间：{format(new Date(exam.start_time), 'yyyy年MM月dd日 HH:mm', { locale: zhCN })}
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-600">
                    <MapPin className="mr-2 h-4 w-4" />
                    考试地点：{exam.location || '待定'}
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-600">
                    <Users className="mr-2 h-4 w-4" />
                    报名人数：{exam.application_count}
                    {exam.max_applicants > 0 && ` / ${exam.max_applicants}`}
                  </div>
                  
                  <div className="flex justify-between items-center pt-2">
                    <Badge variant={regStatus.variant}>{regStatus.label}</Badge>
                    <Button asChild variant="outline" size="sm">
                      <Link to={`/exams/${exam.id}`}>
                        查看详情
                      </Link>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {filteredExams.length === 0 && !loading && (
        <div className="text-center py-12">
          <p className="text-gray-500">暂无考试信息</p>
        </div>
      )}

      {/* 分页 */}
      {totalPages > 1 && (
        <div className="flex justify-center mt-8 space-x-2">
          <Button
            variant="outline"
            onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
            disabled={currentPage === 1}
          >
            上一页
          </Button>
          <span className="flex items-center px-4">
            第 {currentPage} 页，共 {totalPages} 页
          </span>
          <Button
            variant="outline"
            onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
            disabled={currentPage === totalPages}
          >
            下一页
          </Button>
        </div>
      )}
    </div>
  );
};

export default Home;


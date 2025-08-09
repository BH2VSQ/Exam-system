import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { certificateAPI } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Loader2, Award, Calendar, FileText, Download, RefreshCw, AlertTriangle } from 'lucide-react';
import { format } from 'date-fns';
import { zhCN } from 'date-fns/locale';

const MyCertificates = () => {
  const [certificates, setCertificates] = useState([]);
  const [renewalApplications, setRenewalApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showRenewalDialog, setShowRenewalDialog] = useState(false);
  const [selectedCertificate, setSelectedCertificate] = useState(null);
  const [renewalForm, setRenewalForm] = useState({
    application_type: 'renewal',
    reason: ''
  });
  
  const { user } = useAuth();

  const fetchCertificates = async () => {
    try {
      setLoading(true);
      const params = {
        page: currentPage,
        per_page: 10,
      };
      
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      
      const response = await certificateAPI.getMyCertificates(params);
      setCertificates(response.data.certificates || []);
      setTotalPages(response.data.pages || 1);
      setError('');
    } catch (err) {
      setError('获取证书列表失败');
      console.error('Error fetching certificates:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchRenewalApplications = async () => {
    try {
      const response = await certificateAPI.getRenewalApplications();
      setRenewalApplications(response.data.applications || []);
    } catch (err) {
      console.error('Error fetching renewal applications:', err);
    }
  };

  useEffect(() => {
    fetchCertificates();
    fetchRenewalApplications();
  }, [currentPage, statusFilter]);

  const getStatusBadge = (status) => {
    const statusMap = {
      active: { label: '有效', variant: 'default' },
      expired: { label: '过期', variant: 'destructive' },
      revoked: { label: '吊销', variant: 'destructive' },
      replaced: { label: '已更换', variant: 'secondary' },
    };
    
    const statusInfo = statusMap[status] || { label: status, variant: 'secondary' };
    return <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>;
  };

  const getTypeBadge = (type) => {
    const typeMap = {
      initial: { label: '初证', variant: 'default' },
      renewal: { label: '换证', variant: 'secondary' },
      replacement: { label: '补证', variant: 'outline' },
    };
    
    const typeInfo = typeMap[type] || { label: type, variant: 'secondary' };
    return <Badge variant={typeInfo.variant}>{typeInfo.label}</Badge>;
  };

  const isExpiringSoon = (expiryDate) => {
    if (!expiryDate) return false;
    const expiry = new Date(expiryDate);
    const now = new Date();
    const threeMonthsFromNow = new Date(now.getTime() + 90 * 24 * 60 * 60 * 1000);
    return expiry <= threeMonthsFromNow && expiry > now;
  };

  const handleRenewalSubmit = async (e) => {
    e.preventDefault();
    try {
      await certificateAPI.createRenewalApplication({
        original_certificate_id: selectedCertificate.id,
        ...renewalForm
      });
      
      setShowRenewalDialog(false);
      setRenewalForm({ application_type: 'renewal', reason: '' });
      setSelectedCertificate(null);
      
      // 刷新数据
      fetchRenewalApplications();
      
      alert('申请提交成功，请等待审核');
    } catch (err) {
      alert('申请提交失败：' + (err.response?.data?.error || err.message));
    }
  };

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
          <h1 className="text-3xl font-bold text-gray-900">我的证书</h1>
          <p className="text-gray-600 mt-2">管理您的考试证书和申请更替</p>
        </div>
      </div>

      {/* 筛选器 */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="选择状态" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部状态</SelectItem>
            <SelectItem value="active">有效</SelectItem>
            <SelectItem value="expired">过期</SelectItem>
            <SelectItem value="replaced">已更换</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* 证书列表 */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {certificates.map((certificate) => (
          <Card key={certificate.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <CardTitle className="text-lg flex items-center">
                  <Award className="mr-2 h-5 w-5" />
                  {certificate.exam?.name || '考试证书'}
                </CardTitle>
                <div className="flex flex-col gap-1">
                  {getStatusBadge(certificate.status)}
                  {getTypeBadge(certificate.certificate_type)}
                </div>
              </div>
              <CardDescription>
                证书编号：{certificate.certificate_number}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center text-sm text-gray-600">
                  <Calendar className="mr-2 h-4 w-4" />
                  颁发日期：{format(new Date(certificate.issue_date), 'yyyy年MM月dd日', { locale: zhCN })}
                </div>
                
                {certificate.expiry_date && (
                  <div className="flex items-center text-sm text-gray-600">
                    <Calendar className="mr-2 h-4 w-4" />
                    有效期至：{format(new Date(certificate.expiry_date), 'yyyy年MM月dd日', { locale: zhCN })}
                    {isExpiringSoon(certificate.expiry_date) && (
                      <AlertTriangle className="ml-2 h-4 w-4 text-orange-500" />
                    )}
                  </div>
                )}
                
                {certificate.original_certificate_number && (
                  <div className="flex items-center text-sm text-gray-600">
                    <FileText className="mr-2 h-4 w-4" />
                    原证书：{certificate.original_certificate_number}
                  </div>
                )}
                
                <div className="flex justify-between items-center pt-2">
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      <Download className="mr-1 h-3 w-3" />
                      下载
                    </Button>
                    
                    {(certificate.status === 'active' && (isExpiringSoon(certificate.expiry_date) || !certificate.expiry_date)) && (
                      <Dialog open={showRenewalDialog} onOpenChange={setShowRenewalDialog}>
                        <DialogTrigger asChild>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => setSelectedCertificate(certificate)}
                          >
                            <RefreshCw className="mr-1 h-3 w-3" />
                            更替
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>申请证书更替</DialogTitle>
                            <DialogDescription>
                              请选择更替类型并说明原因
                            </DialogDescription>
                          </DialogHeader>
                          <form onSubmit={handleRenewalSubmit} className="space-y-4">
                            <div>
                              <Label htmlFor="application_type">更替类型</Label>
                              <Select 
                                value={renewalForm.application_type} 
                                onValueChange={(value) => setRenewalForm({...renewalForm, application_type: value})}
                              >
                                <SelectTrigger>
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="renewal">换证（证书即将到期）</SelectItem>
                                  <SelectItem value="replacement">补证（证书丢失损坏）</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                            
                            <div>
                              <Label htmlFor="reason">申请原因</Label>
                              <Textarea
                                id="reason"
                                placeholder="请详细说明申请更替的原因..."
                                value={renewalForm.reason}
                                onChange={(e) => setRenewalForm({...renewalForm, reason: e.target.value})}
                                required
                              />
                            </div>
                            
                            <div className="flex justify-end gap-2">
                              <Button 
                                type="button" 
                                variant="outline" 
                                onClick={() => setShowRenewalDialog(false)}
                              >
                                取消
                              </Button>
                              <Button type="submit">
                                提交申请
                              </Button>
                            </div>
                          </form>
                        </DialogContent>
                      </Dialog>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {certificates.length === 0 && !loading && (
        <div className="text-center py-12">
          <Award className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <p className="text-gray-500">暂无证书信息</p>
          <p className="text-sm text-gray-400 mt-2">
            通过考试后，您的证书将显示在这里
          </p>
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

      {/* 更替申请状态 */}
      {renewalApplications.length > 0 && (
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-6">更替申请状态</h2>
          <div className="space-y-4">
            {renewalApplications.map((application) => (
              <Card key={application.id}>
                <CardContent className="pt-6">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium">
                        {application.application_type === 'renewal' ? '换证申请' : '补证申请'}
                      </p>
                      <p className="text-sm text-gray-600">
                        原证书：{application.original_certificate?.certificate_number}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">
                        申请时间：{format(new Date(application.created_at), 'yyyy年MM月dd日', { locale: zhCN })}
                      </p>
                    </div>
                    <Badge variant={
                      application.status === 'pending' ? 'secondary' :
                      application.status === 'approved' ? 'default' :
                      application.status === 'completed' ? 'default' : 'destructive'
                    }>
                      {application.status === 'pending' ? '待审核' :
                       application.status === 'approved' ? '已批准' :
                       application.status === 'completed' ? '已完成' : '已拒绝'}
                    </Badge>
                  </div>
                  
                  {application.review_comment && (
                    <div className="mt-3 p-3 bg-gray-50 rounded-md">
                      <p className="text-sm text-gray-600">
                        <strong>审核意见：</strong>{application.review_comment}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MyCertificates;


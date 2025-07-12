import React, { useState, useEffect } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminPanel = () => {
  const [hostingPlans, setHostingPlans] = useState([]);
  const [companyInfo, setCompanyInfo] = useState({});
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('plans');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authLoading, setAuthLoading] = useState(true);
  const [loginData, setLoginData] = useState({ username: '', password: '' });
  const [loginError, setLoginError] = useState('');

  // Check authentication on component mount
  useEffect(() => {
    checkAuthentication();
  }, []);

  const checkAuthentication = async () => {
    const token = localStorage.getItem('admin_token');
    if (!token) {
      setAuthLoading(false);
      return;
    }

    try {
      const response = await axios.get(`${API}/verify-token`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.valid) {
        setIsAuthenticated(true);
        await fetchData();
      } else {
        localStorage.removeItem('admin_token');
      }
    } catch (error) {
      localStorage.removeItem('admin_token');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    
    try {
      const response = await axios.post(`${API}/login`, loginData);
      const { access_token } = response.data;
      
      localStorage.setItem('admin_token', access_token);
      setIsAuthenticated(true);
      await fetchData();
      setLoginData({ username: '', password: '' });
    } catch (error) {
      setLoginError(error.response?.data?.detail || 'Login failed');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    setIsAuthenticated(false);
    setHostingPlans([]);
    setCompanyInfo({});
  };

  // Get auth token for API requests
  const getAuthHeaders = () => {
    const token = localStorage.getItem('admin_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchData();
    }
  }, [isAuthenticated]);

  const fetchData = async () => {
    if (!isAuthenticated) return;
    
    try {
      const [plansResponse, companyResponse] = await Promise.all([
        axios.get(`${API}/hosting-plans`),
        axios.get(`${API}/company-info`)
      ]);
      setHostingPlans(plansResponse.data);
      setCompanyInfo(companyResponse.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      if (error.response?.status === 401) {
        handleLogout();
      }
    } finally {
      setLoading(false);
    }
  };

  const updatePlan = async (planId, updates) => {
    try {
      await axios.put(`${API}/hosting-plans/${planId}`, updates, {
        headers: getAuthHeaders()
      });
      await fetchData();
      alert('Plan updated successfully!');
    } catch (error) {
      if (error.response?.status === 401) {
        handleLogout();
      } else {
        alert('Error updating plan: ' + error.message);
      }
    }
  };

  const updateCompanyInfo = async (updates) => {
    try {
      await axios.put(`${API}/company-info`, updates, {
        headers: getAuthHeaders()
      });
      await fetchData();
      alert('Company info updated successfully!');
    } catch (error) {
      if (error.response?.status === 401) {
        handleLogout();
      } else {
        alert('Error updating company info: ' + error.message);
      }
    }
  };

  const PlanEditor = ({ plan, onUpdate }) => {
    const [formData, setFormData] = useState(plan);

    const handleSubmit = (e) => {
      e.preventDefault();
      onUpdate(plan.id, formData);
      setSelectedPlan(null);
    };

    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <h3 className="text-xl font-bold text-white mb-4">Edit Plan: {plan.plan_name}</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-300 mb-2">Plan Name</label>
                <input
                  type="text"
                  value={formData.plan_name}
                  onChange={(e) => setFormData({...formData, plan_name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                />
              </div>
              <div>
                <label className="block text-gray-300 mb-2">Price ($)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.base_price}
                  onChange={(e) => setFormData({...formData, base_price: parseFloat(e.target.value)})}
                  className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-gray-300 mb-2">CPU Cores</label>
                <input
                  type="number"
                  value={formData.cpu_cores || ''}
                  onChange={(e) => setFormData({...formData, cpu_cores: e.target.value ? parseInt(e.target.value) : null})}
                  className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                />
              </div>
              <div>
                <label className="block text-gray-300 mb-2">Memory (GB)</label>
                <input
                  type="number"
                  value={formData.memory_gb || ''}
                  onChange={(e) => setFormData({...formData, memory_gb: e.target.value ? parseInt(e.target.value) : null})}
                  className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                />
              </div>
              <div>
                <label className="block text-gray-300 mb-2">Disk (GB)</label>
                <input
                  type="number"
                  value={formData.disk_gb || ''}
                  onChange={(e) => setFormData({...formData, disk_gb: e.target.value ? parseInt(e.target.value) : null})}
                  className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-gray-300 mb-2">Features (one per line)</label>
              <textarea
                rows={4}
                value={formData.features.join('\n')}
                onChange={(e) => setFormData({...formData, features: e.target.value.split('\n').filter(f => f.trim())})}
                className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
              />
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={formData.popular}
                onChange={(e) => setFormData({...formData, popular: e.target.checked})}
                className="mr-2"
              />
              <label className="text-gray-300">Popular Plan</label>
            </div>
            
            <div className="flex gap-4">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Update Plan
              </button>
              <button
                type="button"
                onClick={() => setSelectedPlan(null)}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  const CompanyEditor = () => {
    const [formData, setFormData] = useState(companyInfo);

    const handleSubmit = (e) => {
      e.preventDefault();
      updateCompanyInfo(formData);
    };

    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-4">Company Information</h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-300 mb-2">Company Name</label>
            <input
              type="text"
              value={formData.name || ''}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
            />
          </div>
          
          <div>
            <label className="block text-gray-300 mb-2">Tagline</label>
            <input
              type="text"
              value={formData.tagline || ''}
              onChange={(e) => setFormData({...formData, tagline: e.target.value})}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
            />
          </div>
          
          <div>
            <label className="block text-gray-300 mb-2">Description</label>
            <textarea
              rows={4}
              value={formData.description || ''}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
            />
          </div>
          
          <div>
            <label className="block text-gray-300 mb-2">Features (one per line)</label>
            <textarea
              rows={6}
              value={formData.features ? formData.features.join('\n') : ''}
              onChange={(e) => setFormData({...formData, features: e.target.value.split('\n').filter(f => f.trim())})}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
            />
          </div>
          
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Update Company Info
          </button>
        </form>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">Blue Nebula Admin Panel</h1>
        
        <div className="mb-6">
          <nav className="flex space-x-4">
            <button
              onClick={() => setActiveTab('plans')}
              className={`px-4 py-2 rounded ${activeTab === 'plans' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'}`}
            >
              Hosting Plans
            </button>
            <button
              onClick={() => setActiveTab('company')}
              className={`px-4 py-2 rounded ${activeTab === 'company' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'}`}
            >
              Company Info
            </button>
          </nav>
        </div>
        
        {activeTab === 'plans' && (
          <div>
            <h2 className="text-2xl font-bold text-white mb-6">Manage Hosting Plans</h2>
            
            <div className="grid gap-6">
              {['ssd_shared', 'hdd_shared', 'standard_vps', 'performance_vps', 'standard_gameserver', 'performance_gameserver'].map(planType => {
                const typePlans = hostingPlans.filter(p => p.plan_type === planType);
                if (typePlans.length === 0) return null;
                
                return (
                  <div key={planType} className="bg-gray-800 rounded-lg p-6">
                    <h3 className="text-xl font-bold text-white mb-4 capitalize">
                      {planType.replace('_', ' ')}
                    </h3>
                    
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {typePlans.map(plan => (
                        <div key={plan.id} className="bg-gray-700 rounded-lg p-4">
                          <div className="flex justify-between items-start mb-2">
                            <h4 className="font-bold text-white">{plan.plan_name}</h4>
                            {plan.popular && (
                              <span className="bg-blue-600 text-white px-2 py-1 rounded text-xs">Popular</span>
                            )}
                          </div>
                          
                          <div className="text-blue-400 font-bold text-lg mb-2">
                            ${plan.base_price}/mo
                          </div>
                          
                          <div className="text-gray-300 text-sm mb-4">
                            {plan.cpu_cores && <div>CPU: {plan.cpu_cores} vCPU</div>}
                            {plan.memory_gb && <div>RAM: {plan.memory_gb} GB</div>}
                            {plan.disk_gb && <div>Disk: {plan.disk_gb} GB</div>}
                          </div>
                          
                          <button
                            onClick={() => setSelectedPlan(plan)}
                            className="w-full px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                          >
                            Edit Plan
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
        
        {activeTab === 'company' && <CompanyEditor />}
        
        {selectedPlan && (
          <PlanEditor plan={selectedPlan} onUpdate={updatePlan} />
        )}
      </div>
    </div>
  );
};

export default AdminPanel;
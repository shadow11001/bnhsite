import React, { useState, useEffect } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = BACKEND_URL; // BACKEND_URL should be https://bluenebulahosting.com/api

const AdminPanel = () => {
  const [hostingPlans, setHostingPlans] = useState([]);
  const [companyInfo, setCompanyInfo] = useState({});
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('plans');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authLoading, setAuthLoading] = useState(true);
  
  // Content management states
  const [websiteContent, setWebsiteContent] = useState({});
  const [navigationItems, setNavigationItems] = useState([]);
  const [smtpSettings, setSmtpSettings] = useState({});
  const [legalContent, setLegalContent] = useState({});

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

  // Utility function to clear all browser caches
  const clearAllCaches = () => {
    try {
      // Clear localStorage
      localStorage.clear();
      // Clear sessionStorage  
      sessionStorage.clear();
      // Clear any stored data
      console.log('Browser storage cleared');
      
      // Force reload from server
      window.location.reload(true);
    } catch (error) {
      console.error('Error clearing caches:', error);
    }
  };

  const fetchData = async (forceClear = false) => {
    if (!isAuthenticated) return;
    
    try {
      setLoading(true);
      console.log('Fetching admin data...', forceClear ? '(force refresh)' : '');
      
      // Create cache-busting timestamp
      const timestamp = new Date().getTime();
      const cacheHeaders = {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Expires': '0'
      };
      
      // Fetch admin hosting plans
      try {
        const adminPlansResponse = await axios.get(`${API}/admin/hosting-plans?_t=${timestamp}`, { 
          headers: { ...getAuthHeaders(), ...cacheHeaders }
        });
        console.log('Hosting plans loaded:', adminPlansResponse.data.length, 'plans');
        setHostingPlans(adminPlansResponse.data);
      } catch (error) {
        console.error('Error loading hosting plans:', error);
      }
      
      // Fetch company info
      try {
        const companyResponse = await axios.get(`${API}/company-info?_t=${timestamp}`, {
          headers: cacheHeaders
        });
        console.log('Company info loaded:', companyResponse.data);
        setCompanyInfo(companyResponse.data);
      } catch (error) {
        console.error('Error loading company info:', error);
      }
      
      // Fetch navigation (with fallback to default)
      try {
        const navigationResponse = await axios.get(`${API}/navigation`, { headers: getAuthHeaders() });
        console.log('Navigation loaded:', navigationResponse.data);
        setNavigationItems(navigationResponse.data);
      } catch (error) {
        console.error('Error loading navigation, using default:', error);
        // Set default navigation
        setNavigationItems([
          { id: '1', label: 'Home', href: '#home', order: 1, is_external: false },
          { 
            id: '2', 
            label: 'Hosting', 
            href: '#hosting', 
            order: 2, 
            is_external: false,
            dropdown_items: [
              { label: 'Shared Hosting', href: '#hosting' },
              { label: 'VPS Hosting', href: '#vps' },
              { label: 'GameServer Hosting', href: '#gameservers' }
            ]
          },
          { id: '3', label: 'About', href: '#about', order: 3, is_external: false },
          { id: '4', label: 'Contact', href: '#contact', order: 4, is_external: false }
        ]);
      }
      
      // Fetch SMTP settings
      try {
        const smtpResponse = await axios.get(`${API}/admin/smtp-settings`, { headers: getAuthHeaders() });
        console.log('SMTP settings loaded:', smtpResponse.data);
        setSmtpSettings(smtpResponse.data);
      } catch (error) {
        console.error('Error loading SMTP settings:', error);
      }
      
      // Fetch content sections
      try {
        // Try to load all content sections separately
        const contentSections = ['hero', 'about', 'features'];
        const contentPromises = contentSections.map(async (section) => {
          try {
            const response = await axios.get(`${API}/admin/website-content`, { headers: getAuthHeaders() });
            return { section, data: response.data[section] || {} };
          } catch (err) {
            try {
              const response = await axios.get(`${API}/website-content/${section}`);
              return { section, data: response.data };
            } catch (err2) {
              console.error(`Error loading ${section} content:`, err2);
              return { section, data: {} };
            }
          }
        });
        
        const contentResults = await Promise.all(contentPromises);
        const contentObj = {};
        contentResults.forEach(result => {
          contentObj[result.section] = result.data;
        });
        
        console.log('Content loaded:', contentObj);
        setWebsiteContent(prev => ({ ...prev, ...contentObj }));
      } catch (error) {
        console.error('Error loading content:', error);
      }
      
      // Fetch legal content
      try {
        const [termsResponse, privacyResponse] = await Promise.all([
          axios.get(`${API}/content/terms`),
          axios.get(`${API}/content/privacy`)
        ]);
        console.log('Legal content loaded');
        setLegalContent({
          terms: termsResponse.data,
          privacy: privacyResponse.data
        });
        setWebsiteContent(prev => ({ 
          ...prev, 
          terms: termsResponse.data,
          privacy: privacyResponse.data
        }));
      } catch (error) {
        console.error('Error loading legal content:', error);
      }
      
    } catch (error) {
      console.error('Error fetching admin data:', error);
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
        headers: {
          ...getAuthHeaders(),
          'Cache-Control': 'no-cache'
        }
      });
      await fetchData(true); // Force refresh after update
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
      // Try different endpoints and methods
      let response;
      try {
        response = await axios.put(`${API}/admin/company-info`, updates, { headers: getAuthHeaders() });
      } catch (err) {
        if (err.response?.status === 404) {
          // Try POST method
          response = await axios.post(`${API}/admin/company-info`, updates, { headers: getAuthHeaders() });
        } else if (err.response?.status === 405) {
          // Try different endpoint
          response = await axios.put(`${API}/company`, updates, { headers: getAuthHeaders() });
        } else {
          throw err;
        }
      }
      await fetchData();
      alert('Company info updated successfully!');
    } catch (error) {
      console.error('Error updating company info:', error);
      if (error.response?.status === 401) {
        handleLogout();
      } else {
        alert('Error updating company info: ' + (error.response?.data?.detail || error.response?.data?.message || error.message));
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
          <h3 className="text-xl font-bold text-white mb-4">Edit Plan: {plan.name}</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-300 mb-2">Plan Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                />
              </div>
              <div>
                <label className="block text-gray-300 mb-2">Price ($)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.price}
                  onChange={(e) => setFormData({...formData, price: parseFloat(e.target.value)})}
                  className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-300 mb-2">CPU</label>
                <input
                  type="text"
                  value={formData.cpu || ''}
                  onChange={(e) => setFormData({...formData, cpu: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                  placeholder="e.g., 1 vCPU"
                />
              </div>
              <div>
                <label className="block text-gray-300 mb-2">RAM</label>
                <input
                  type="text"
                  value={formData.ram || ''}
                  onChange={(e) => setFormData({...formData, ram: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                  placeholder="e.g., 1 GB RAM"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-300 mb-2">Disk Space</label>
                <input
                  type="text"
                  value={formData.disk_space || ''}
                  onChange={(e) => setFormData({...formData, disk_space: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                  placeholder="e.g., 10 GB SSD"
                />
              </div>
              <div>
                <label className="block text-gray-300 mb-2">Bandwidth</label>
                <input
                  type="text"
                  value={formData.bandwidth || ''}
                  onChange={(e) => setFormData({...formData, bandwidth: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                  placeholder="e.g., Unlimited"
                />
              </div>
            </div>
            
            {/* Shared Hosting Specific Fields */}
            {(formData.type === 'shared') && (
              <div className="bg-gray-700 p-4 rounded-lg">
                <h4 className="text-lg font-semibold text-white mb-4">Shared Hosting Limits</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-gray-300 mb-2">Domains</label>
                    <input
                      type="text"
                      value={formData.websites || ''}
                      onChange={(e) => setFormData({...formData, websites: e.target.value})}
                      className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                      placeholder="e.g., 1, 5, Unlimited"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-300 mb-2">Subdomains</label>
                    <input
                      type="text"
                      value={formData.subdomains || ''}
                      onChange={(e) => setFormData({...formData, subdomains: e.target.value})}
                      className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                      placeholder="e.g., 10, Unlimited"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-300 mb-2">Parked Domains</label>
                    <input
                      type="text"
                      value={formData.parked_domains || ''}
                      onChange={(e) => setFormData({...formData, parked_domains: e.target.value})}
                      className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                      placeholder="e.g., 5, Unlimited"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-300 mb-2">Databases</label>
                    <input
                      type="text"
                      value={formData.databases || ''}
                      onChange={(e) => setFormData({...formData, databases: e.target.value})}
                      className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                      placeholder="e.g., 1, 10, Unlimited"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-300 mb-2">Email Accounts</label>
                    <input
                      type="text"
                      value={formData.email_accounts || ''}
                      onChange={(e) => setFormData({...formData, email_accounts: e.target.value})}
                      className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                      placeholder="e.g., 5, Unlimited"
                    />
                  </div>
                </div>
              </div>
            )}
            
            <div>
              <label className="block text-gray-300 mb-2">Markup Percentage</label>
              <input
                type="number"
                step="0.01"
                value={formData.markup_percentage || 0}
                onChange={(e) => setFormData({...formData, markup_percentage: parseFloat(e.target.value)})}
                className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                placeholder="e.g., 20, 40"
              />
              <p className="text-xs text-gray-400 mt-1">Markup percentage for internal pricing strategy</p>
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
            
            <div>
              <label className="block text-gray-300 mb-2">Order URL</label>
              <input
                type="url"
                value={formData.order_url || ''}
                onChange={(e) => setFormData({...formData, order_url: e.target.value})}
                className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                placeholder="https://billing.bluenebulahosting.com"
              />
              <p className="text-xs text-gray-400 mt-1">Leave empty to use default billing URL</p>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_popular}
                onChange={(e) => setFormData({...formData, is_popular: e.target.checked})}
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
    const [companyData, setCompanyData] = useState({});
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
      console.log('Company editor: companyInfo changed:', companyInfo);
      if (companyInfo && Object.keys(companyInfo).length > 0) {
        setCompanyData(companyInfo);
      }
    }, [companyInfo]);

    const updateCompanyInfo = async () => {
      setIsLoading(true);
      try {
        await axios.put(`${API}/company-info`, companyData, { headers: getAuthHeaders() });
        alert('Company information updated successfully!');
      } catch (error) {
        alert('Error updating company info: ' + error.message);
      } finally {
        setIsLoading(false);
      }
    };

    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-6">Company Information</h3>
        
        <div className="space-y-6">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-300 mb-2">Company Name</label>
              <input
                type="text"
                value={companyData.name || ''}
                onChange={(e) => setCompanyData({...companyData, name: e.target.value})}
                className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-400 focus:outline-none"
              />
            </div>
            
            <div>
              <label className="block text-gray-300 mb-2">Tagline</label>
              <input
                type="text"
                value={companyData.tagline || ''}
                onChange={(e) => setCompanyData({...companyData, tagline: e.target.value})}
                className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-400 focus:outline-none"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-gray-300 mb-2">Company Description</label>
            <textarea
              rows={4}
              value={companyData.description || ''}
              onChange={(e) => setCompanyData({...companyData, description: e.target.value})}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-400 focus:outline-none"
            />
          </div>
          
          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <label className="block text-gray-300 mb-2">Contact Email</label>
              <input
                type="email"
                value={companyData.contact_email || ''}
                onChange={(e) => setCompanyData({...companyData, contact_email: e.target.value})}
                className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-400 focus:outline-none"
              />
            </div>
            
            <div>
              <label className="block text-gray-300 mb-2">Phone</label>
              <input
                type="tel"
                value={companyData.phone || ''}
                onChange={(e) => setCompanyData({...companyData, phone: e.target.value})}
                className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-400 focus:outline-none"
              />
            </div>
            
            <div>
              <label className="block text-gray-300 mb-2">Founded Year</label>
              <input
                type="number"
                value={companyData.founded_year || ''}
                onChange={(e) => setCompanyData({...companyData, founded_year: parseInt(e.target.value)})}
                className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-400 focus:outline-none"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-gray-300 mb-2">Address</label>
            <input
              type="text"
              value={companyData.address || ''}
              onChange={(e) => setCompanyData({...companyData, address: e.target.value})}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-400 focus:outline-none"
            />
          </div>
          
          <div>
            <label className="block text-gray-300 mb-2">Key Features (one per line)</label>
            <textarea
              rows={6}
              value={companyData.features ? companyData.features.join('\n') : ''}
              onChange={(e) => setCompanyData({...companyData, features: e.target.value.split('\n').filter(f => f.trim())})}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-400 focus:outline-none"
              placeholder="Enter one feature per line..."
            />
          </div>
          
          <button
            onClick={updateCompanyInfo}
            disabled={isLoading}
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {isLoading ? 'Updating...' : 'Update Company Info'}
          </button>
        </div>
      </div>
    );
  };

  // Login Form Component
  const LoginForm = () => {
    const [localLoginData, setLocalLoginData] = useState({ username: '', password: '' });
    const [localLoginError, setLocalLoginError] = useState('');
    const [isLoggingIn, setIsLoggingIn] = useState(false);

    const handleLocalLogin = async (e) => {
      e.preventDefault();
      setLocalLoginError('');
      setIsLoggingIn(true);
      
      try {
        const response = await axios.post(`${API}/login`, localLoginData);
        const { access_token } = response.data;
        
        localStorage.setItem('admin_token', access_token);
        setIsAuthenticated(true);
        await fetchData();
        setLocalLoginData({ username: '', password: '' });
      } catch (error) {
        setLocalLoginError(error.response?.data?.detail || 'Login failed');
      } finally {
        setIsLoggingIn(false);
      }
    };

    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="bg-gray-800 rounded-lg p-8 max-w-md w-full">
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <img 
                src="/logo.png" 
                alt="Blue Nebula Hosting" 
                className="w-16 h-16 object-contain"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
              <div className="w-16 h-16 bg-gradient-to-r from-blue-400 to-purple-600 rounded-lg items-center justify-center text-white font-bold text-2xl" style={{display: 'none'}}>
                BN
              </div>
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Admin Panel</h2>
            <p className="text-gray-400">Sign in to manage your hosting</p>
          </div>
          
          <form onSubmit={handleLocalLogin} className="space-y-6">
            {localLoginError && (
              <div className="bg-red-600/20 border border-red-500 rounded-lg p-3 text-red-400 text-sm">
                {localLoginError}
              </div>
            )}
            
            <div>
              <label className="block text-gray-300 mb-2">Username</label>
              <input
                type="text"
                value={localLoginData.username}
                onChange={(e) => setLocalLoginData(prev => ({...prev, username: e.target.value}))}
                required
                disabled={isLoggingIn}
                className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-blue-400 focus:outline-none disabled:opacity-50"
                placeholder="Enter admin username"
              />
            </div>
            
            <div>
              <label className="block text-gray-300 mb-2">Password</label>
              <input
                type="password"
                value={localLoginData.password}
                onChange={(e) => setLocalLoginData(prev => ({...prev, password: e.target.value}))}
                required
                disabled={isLoggingIn}
                className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-blue-400 focus:outline-none disabled:opacity-50"
                placeholder="Enter admin password"
              />
            </div>
            
            <button
              type="submit"
              disabled={isLoggingIn}
              className="w-full py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-colors font-semibold disabled:opacity-50"
            >
              {isLoggingIn ? 'Logging in...' : 'Login'}
            </button>
            
            <div className="text-center">
              <a href="/" className="text-blue-400 hover:text-blue-300 transition-colors text-sm">
                ← Back to Website
              </a>
            </div>
          </form>
        </div>
      </div>
    );
  };

  // Website Content Editor
  const ContentEditor = () => {
    const [selectedSection, setSelectedSection] = useState('hero');
    const [allSectionContent, setAllSectionContent] = useState({
      hero: { title: '', subtitle: '', description: '', button_text: '', button_url: '' },
      features: { title: '', subtitle: '', description: '', button_text: '', button_url: '' },
      about: { title: '', subtitle: '', description: '', button_text: '', button_url: '' }
    });
    const [isLoading, setIsLoading] = useState(false);

    const sections = [
      { key: 'hero', label: 'Hero Section', description: 'Main landing page content' },
      { key: 'features', label: 'Features Section', description: 'Why choose us section' },
      { key: 'about', label: 'About Section', description: 'Company information' }
    ];

    // Load all content sections from database
    const loadAllSectionContent = async () => {
      console.log('Loading all website content from database...');
      
      // First, try to get content from the main websiteContent state
      if (websiteContent && Object.keys(websiteContent).length > 0) {
        console.log('Using existing websiteContent:', websiteContent);
        setAllSectionContent(prev => ({
          hero: websiteContent.hero || { title: '', subtitle: '', description: '', button_text: '', button_url: '' },
          features: websiteContent.features || { title: '', subtitle: '', description: '', button_text: '', button_url: '' },
          about: websiteContent.about || { title: '', subtitle: '', description: '', button_text: '', button_url: '' }
        }));
        return;
      }
      
      // Try to load from various backend endpoints
      for (const section of sections) {
        try {
          console.log(`Attempting to load ${section.key} content...`);
          let content = null;
          
          // Try multiple endpoint variations
          const endpoints = [
            `${API}/admin/content/${section.key}`,
            `${API}/content/${section.key}`,
            `${API}/admin/website-content`,
            `${API}/website-content`
          ];
          
          for (const endpoint of endpoints) {
            try {
              console.log(`Trying endpoint: ${endpoint}`);
              const response = await axios.get(endpoint, { 
                headers: { 
                  ...getAuthHeaders(),
                  'Cache-Control': 'no-cache'
                }
              });
              
              if (endpoint.includes('website-content')) {
                // If it's a bulk endpoint, extract section-specific content
                content = response.data[section.key] || null;
              } else {
                // If it's a section-specific endpoint
                content = response.data || null;
              }
              
              if (content) {
                console.log(`${section.key} content loaded from ${endpoint}:`, content);
                break;
              }
            } catch (err) {
              console.log(`Endpoint ${endpoint} failed:`, err.response?.status, err.response?.statusText);
              continue;
            }
          }
          
          // Set the content (or default if not found)
          setAllSectionContent(prev => ({
            ...prev,
            [section.key]: content || { 
              title: `Default ${section.label}`, 
              subtitle: '', 
              description: `This is the ${section.label.toLowerCase()}. Content will be loaded from database once backend endpoints are configured.`, 
              button_text: '', 
              button_url: '' 
            }
          }));
          
        } catch (error) {
          console.error(`Failed to load ${section.key} content:`, error);
          // Set informative default content
          setAllSectionContent(prev => ({
            ...prev,
            [section.key]: { 
              title: `${section.label} (Not Connected)`, 
              subtitle: '', 
              description: `Backend content endpoint for ${section.label.toLowerCase()} not available. Please configure database content storage.`, 
              button_text: '', 
              button_url: '' 
            }
          }));
        }
      }
    };

    useEffect(() => {
      loadAllSectionContent();
    }, []);

    // Get current section content
    const currentSectionContent = allSectionContent[selectedSection] || { title: '', subtitle: '', description: '', button_text: '', button_url: '' };

    // Update current section content
    const updateCurrentSectionContent = (field, value) => {
      setAllSectionContent(prev => ({
        ...prev,
        [selectedSection]: {
          ...prev[selectedSection],
          [field]: value
        }
      }));
    };

    const updateSectionContent = async () => {
      setIsLoading(true);
      console.log(`Attempting to save ${selectedSection} content to database:`, currentSectionContent);
      
      try {
        // Try multiple endpoint and method combinations
        const endpoints = [
          { url: `${API}/admin/content/${selectedSection}`, method: 'POST' },
          { url: `${API}/admin/content/${selectedSection}`, method: 'PUT' },
          { url: `${API}/content/${selectedSection}`, method: 'POST' },
          { url: `${API}/content/${selectedSection}`, method: 'PUT' },
          { url: `${API}/admin/website-content`, method: 'POST', payload: { section: selectedSection, content: currentSectionContent } },
          { url: `${API}/website-content`, method: 'POST', payload: { section: selectedSection, content: currentSectionContent } }
        ];
        
        let success = false;
        let lastError = null;
        
        for (const endpoint of endpoints) {
          try {
            console.log(`Trying ${endpoint.method} ${endpoint.url}`);
            
            const payload = endpoint.payload || currentSectionContent;
            const config = {
              headers: {
                ...getAuthHeaders(),
                'Cache-Control': 'no-cache',
                'Content-Type': 'application/json'
              }
            };
            
            let response;
            if (endpoint.method === 'POST') {
              response = await axios.post(endpoint.url, payload, config);
            } else {
              response = await axios.put(endpoint.url, payload, config);
            }
            
            console.log(`${selectedSection} content saved successfully via ${endpoint.method} ${endpoint.url}:`, response.data);
            success = true;
            break;
            
          } catch (err) {
            console.log(`${endpoint.method} ${endpoint.url} failed:`, err.response?.status, err.response?.statusText);
            lastError = err;
            continue;
          }
        }
        
        if (success) {
          alert(`✅ ${selectedSection.charAt(0).toUpperCase() + selectedSection.slice(1)} content saved to database successfully!`);
          
          // Update the main websiteContent state to keep it in sync
          setWebsiteContent(prev => ({ 
            ...prev, 
            [selectedSection]: currentSectionContent 
          }));
          
          // Force reload content to verify save
          setTimeout(() => {
            loadAllSectionContent();
          }, 1000);
        } else {
          throw lastError || new Error('All save endpoints failed');
        }
        
      } catch (error) {
        console.error(`Error saving ${selectedSection} content:`, error);
        
        // Provide helpful error message
        let errorMessage = `Failed to save ${selectedSection} content. `;
        if (error.response?.status === 404) {
          errorMessage += 'Backend content endpoints not found. Please ensure database content storage is configured.';
        } else if (error.response?.status === 405) {
          errorMessage += 'HTTP method not allowed. Backend may need endpoint configuration updates.';
        } else if (error.response?.status === 401) {
          errorMessage += 'Authentication failed. Please log in again.';
        } else {
          errorMessage += (error.response?.data?.detail || error.response?.data?.message || error.message);
        }
        
        alert(`❌ ${errorMessage}`);
        
        // For now, save to local state so user doesn't lose work
        console.log('Saving to local state as fallback...');
        setWebsiteContent(prev => ({ 
          ...prev, 
          [selectedSection]: currentSectionContent 
        }));
        
      } finally {
        setIsLoading(false);
      }
    };

    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-6">Website Content Management</h3>
        
        <div className="grid lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1">
            <h4 className="text-white font-semibold mb-4">Sections</h4>
            <div className="space-y-2">
              {sections.map(section => (
                <button
                  key={section.key}
                  onClick={() => {
                    console.log(`Switching from ${selectedSection} to ${section.key}`);
                    console.log('Current content before switch:', currentSectionContent);
                    setSelectedSection(section.key);
                  }}
                  className={`w-full text-left p-3 rounded transition-colors ${
                    selectedSection === section.key
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  <div className="font-medium">{section.label}</div>
                  <div className="text-xs opacity-75">{section.description}</div>
                  <div className="text-xs mt-1 opacity-60">
                    Content: {allSectionContent[section.key]?.title ? '✓' : '✗'}
                  </div>
                </button>
              ))}
            </div>
          </div>
          
          <div className="lg:col-span-3">
            <div className="bg-gray-700 rounded-lg p-6">
              <h4 className="text-white font-semibold mb-4">
                Edit {sections.find(s => s.key === selectedSection)?.label}
              </h4>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-300 mb-2">Title</label>
                  <input
                    type="text"
                    value={currentSectionContent.title || ''}
                    onChange={(e) => updateCurrentSectionContent('title', e.target.value)}
                    className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                  />
                </div>
                
                {selectedSection === 'hero' && (
                  <div>
                    <label className="block text-gray-300 mb-2">Subtitle</label>
                    <input
                      type="text"
                      value={currentSectionContent.subtitle || ''}
                      onChange={(e) => updateCurrentSectionContent('subtitle', e.target.value)}
                      className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                    />
                  </div>
                )}
                
                <div>
                  <label className="block text-gray-300 mb-2">Description</label>
                  <textarea
                    rows={4}
                    value={currentSectionContent.description || ''}
                    onChange={(e) => updateCurrentSectionContent('description', e.target.value)}
                    className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                  />
                </div>
                
                <button
                  onClick={updateSectionContent}
                  disabled={isLoading}
                  className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {isLoading ? 'Saving...' : 'Save to Database'}
                </button>
                
                <button
                  onClick={loadAllSectionContent}
                  className="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                >
                  🔄 Reload from Database
                </button>
              </div>
              
              {/* Debug Information */}
              <div className="mt-6 bg-gray-800 p-4 rounded-lg">
                <h5 className="text-white font-semibold mb-2">🔧 Debug Information</h5>
                <div className="text-xs text-gray-400 space-y-1">
                  <div><strong>Selected Section:</strong> {selectedSection}</div>
                  <div><strong>Content State:</strong> {JSON.stringify(currentSectionContent, null, 2)}</div>
                  <div><strong>All Sections:</strong> {Object.keys(allSectionContent).join(', ')}</div>
                  <div><strong>API Base:</strong> {API}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Navigation Editor
  const NavigationEditor = () => {
    const [navItems, setNavItems] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
      setNavItems(navigationItems);
    }, [navigationItems]);

    const addNavItem = () => {
      const newItem = {
        id: Date.now().toString(),
        label: 'New Item',
        href: '#',
        order: navItems.length + 1,
        is_external: false
      };
      setNavItems([...navItems, newItem]);
    };

    const updateNavItem = (id, updates) => {
      setNavItems(navItems.map(item => 
        item.id === id ? { ...item, ...updates } : item
      ));
    };

    const removeNavItem = (id) => {
      setNavItems(navItems.filter(item => item.id !== id));
    };

    const saveNavigation = async () => {
      setIsLoading(true);
      try {
        // Try different endpoints and methods
        let response;
        try {
          response = await axios.post(`${API}/admin/navigation`, navItems, { headers: getAuthHeaders() });
        } catch (err) {
          if (err.response?.status === 404) {
            // Try PUT method
            response = await axios.put(`${API}/admin/navigation`, navItems, { headers: getAuthHeaders() });
          } else if (err.response?.status === 405) {
            // Try different endpoint
            response = await axios.post(`${API}/navigation-menu`, navItems, { headers: getAuthHeaders() });
          } else {
            throw err;
          }
        }
        alert('Navigation updated successfully!');
        setNavigationItems(navItems);
      } catch (error) {
        console.error('Error updating navigation:', error);
        alert('Error updating navigation: ' + (error.response?.data?.detail || error.response?.data?.message || error.message));
      } finally {
        setIsLoading(false);
      }
    };

    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold text-white">Navigation Management</h3>
          <button
            onClick={addNavItem}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
          >
            Add Item
          </button>
        </div>
        
        <div className="space-y-4 mb-6">
          {navItems.map((item, index) => (
            <div key={item.id} className="bg-gray-700 rounded-lg p-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-gray-300 mb-2">Label</label>
                  <input
                    type="text"
                    value={item.label}
                    onChange={(e) => updateNavItem(item.id, { label: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500"
                  />
                </div>
                
                <div>
                  <label className="block text-gray-300 mb-2">Link</label>
                  <input
                    type="text"
                    value={item.href}
                    onChange={(e) => updateNavItem(item.id, { href: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500"
                  />
                </div>
                
                <div>
                  <label className="block text-gray-300 mb-2">Order</label>
                  <input
                    type="number"
                    value={item.order}
                    onChange={(e) => updateNavItem(item.id, { order: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500"
                  />
                </div>
                
                <div className="flex items-end">
                  <button
                    onClick={() => removeNavItem(item.id)}
                    className="px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                  >
                    Remove
                  </button>
                </div>
              </div>
              
              <div className="mt-2 flex items-center">
                <input
                  type="checkbox"
                  checked={item.is_external}
                  onChange={(e) => updateNavItem(item.id, { is_external: e.target.checked })}
                  className="mr-2"
                />
                <label className="text-gray-300 text-sm">External Link</label>
              </div>
            </div>
          ))}
        </div>
        
        <button
          onClick={saveNavigation}
          disabled={isLoading}
          className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          {isLoading ? 'Saving...' : 'Save Navigation'}
        </button>
      </div>
    );
  };

  // Legal Content Editor
  const LegalEditor = () => {
    const [selectedType, setSelectedType] = useState('terms');
    const [legalData, setLegalData] = useState({ title: '', content: '' });
    const [isLoading, setIsLoading] = useState(false);

    const loadLegalContent = async (type) => {
      try {
        console.log('Loading legal content for:', type);
        const response = await axios.get(`${API}/content/${type}`);
        console.log('Legal content loaded:', response.data);
        setLegalData(response.data);
      } catch (error) {
        console.error('Error loading legal content:', error);
      }
    };

    useEffect(() => {
      console.log('Legal editor: selectedType changed to:', selectedType);
      console.log('Current legalContent:', legalContent);
      
      if (legalContent && legalContent[selectedType]) {
        console.log('Using cached legal content for', selectedType);
        setLegalData(legalContent[selectedType]);
      } else {
        console.log('Loading fresh legal content for', selectedType);
        loadLegalContent(selectedType);
      }
    }, [selectedType, legalContent]);

    const saveLegalContent = async () => {
      setIsLoading(true);
      try {
        await axios.put(`${API}/content`, legalData, { headers: getAuthHeaders() });
        alert(`${selectedType === 'terms' ? 'Terms of Service' : 'Privacy Policy'} updated successfully!`);
      } catch (error) {
        alert('Error updating legal content: ' + error.message);
      } finally {
        setIsLoading(false);
      }
    };

    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-6">Legal Pages Management</h3>
        
        <div className="mb-6">
          <div className="flex space-x-4">
            <button
              onClick={() => setSelectedType('terms')}
              className={`px-4 py-2 rounded transition-colors ${
                selectedType === 'terms'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Terms of Service
            </button>
            <button
              onClick={() => setSelectedType('privacy')}
              className={`px-4 py-2 rounded transition-colors ${
                selectedType === 'privacy'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Privacy Policy
            </button>
          </div>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-gray-300 mb-2">Title</label>
            <input
              type="text"
              value={legalData.title || ''}
              onChange={(e) => setLegalData({...legalData, title: e.target.value})}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-400 focus:outline-none"
            />
          </div>
          
          <div>
            <label className="block text-gray-300 mb-2">Content</label>
            <textarea
              rows={20}
              value={legalData.content || ''}
              onChange={(e) => setLegalData({...legalData, content: e.target.value})}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-400 focus:outline-none font-mono text-sm"
              placeholder="Enter your legal content here. You can use basic HTML formatting."
            />
          </div>
          
          <button
            onClick={saveLegalContent}
            disabled={isLoading}
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {isLoading ? 'Saving...' : `Save ${selectedType === 'terms' ? 'Terms of Service' : 'Privacy Policy'}`}
          </button>
        </div>
      </div>
    );
  };

  // Contact & SMTP Settings
  const ContactSMTPEditor = () => {
    const [smtpData, setSmtpData] = useState({});
    const [isLoading, setIsLoading] = useState(false);
    const [testResult, setTestResult] = useState('');

    useEffect(() => {
      setSmtpData(smtpSettings);
    }, [smtpSettings]);

    const saveSMTPSettings = async () => {
      setIsLoading(true);
      try {
        await axios.put(`${API}/admin/smtp-settings`, smtpData, { headers: getAuthHeaders() });
        alert('SMTP settings updated successfully!');
        setSmtpSettings(smtpData);
      } catch (error) {
        console.error('Error updating SMTP settings:', error);
        alert('Error updating SMTP settings: ' + (error.response?.data?.detail || error.message));
      } finally {
        setIsLoading(false);
      }
    };

    const testSMTPConnection = async () => {
      setIsLoading(true);
      setTestResult('Testing...');
      try {
        const response = await axios.post(`${API}/admin/smtp-test`, smtpData, { headers: getAuthHeaders() });
        setTestResult('✅ SMTP connection successful!');
      } catch (error) {
        console.error('Error testing SMTP connection:', error);
        setTestResult('❌ SMTP connection failed: ' + (error.response?.data?.detail || error.message));
      } finally {
        setIsLoading(false);
      }
    };

    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-6">Contact Form & SMTP Settings</h3>
        
        <div className="grid lg:grid-cols-2 gap-6">
          <div>
            <h4 className="text-white font-semibold mb-4">SMTP Configuration</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-gray-300 mb-2">SMTP Host</label>
                <input
                  type="text"
                  value={smtpData.smtp_host || ''}
                  onChange={(e) => setSmtpData({...smtpData, smtp_host: e.target.value})}
                  placeholder="mail.yourdomain.com"
                  className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-gray-300 mb-2">Port</label>
                  <input
                    type="number"
                    value={smtpData.smtp_port || 587}
                    onChange={(e) => setSmtpData({...smtpData, smtp_port: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                  />
                </div>
                
                <div className="flex items-center mt-6">
                  <input
                    type="checkbox"
                    checked={smtpData.smtp_use_tls || false}
                    onChange={(e) => setSmtpData({...smtpData, smtp_use_tls: e.target.checked})}
                    className="mr-2"
                  />
                  <label className="text-gray-300">Use TLS</label>
                </div>
              </div>
              
              <div>
                <label className="block text-gray-300 mb-2">Username</label>
                <input
                  type="text"
                  value={smtpData.smtp_username || ''}
                  onChange={(e) => setSmtpData({...smtpData, smtp_username: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                />
              </div>
              
              <div>
                <label className="block text-gray-300 mb-2">Password</label>
                <input
                  type="password"
                  value={smtpData.smtp_password || ''}
                  onChange={(e) => setSmtpData({...smtpData, smtp_password: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                />
              </div>
            </div>
          </div>
          
          <div>
            <h4 className="text-white font-semibold mb-4">Email Settings</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-gray-300 mb-2">From Email</label>
                <input
                  type="email"
                  value={smtpData.from_email || ''}
                  onChange={(e) => setSmtpData({...smtpData, from_email: e.target.value})}
                  placeholder="noreply@yourdomain.com"
                  className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                />
              </div>
              
              <div>
                <label className="block text-gray-300 mb-2">From Name</label>
                <input
                  type="text"
                  value={smtpData.from_name || ''}
                  onChange={(e) => setSmtpData({...smtpData, from_name: e.target.value})}
                  placeholder="Blue Nebula Hosting"
                  className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600"
                />
              </div>
              
              <div className="bg-gray-700 rounded p-4">
                <h5 className="text-white font-medium mb-2">Test Connection</h5>
                <button
                  onClick={testSMTPConnection}
                  disabled={isLoading}
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors disabled:opacity-50 mb-2"
                >
                  Test SMTP
                </button>
                {testResult && (
                  <div className="text-sm text-gray-300 mt-2">{testResult}</div>
                )}
              </div>
            </div>
          </div>
        </div>
        
        <div className="mt-6">
          <button
            onClick={saveSMTPSettings}
            disabled={isLoading}
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {isLoading ? 'Saving...' : 'Save SMTP Settings'}
          </button>
        </div>
      </div>
    );
  };

  // Promo Code Manager
  const PromoCodeManager = () => {
    const [promoCodes, setPromoCodes] = useState([]);
    const [editingPromo, setEditingPromo] = useState(null);
    const [showForm, setShowForm] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
      loadPromoCodes();
    }, []);

    const loadPromoCodes = async () => {
      try {
        // Try admin endpoint first
        const response = await axios.get(`${API}/admin/promo-codes`, { headers: getAuthHeaders() });
        setPromoCodes(response.data);
        console.log('Admin promo codes loaded:', response.data);
      } catch (error) {
        console.error('Error loading admin promo codes:', error);
        try {
          // Fallback to public endpoint
          const response = await axios.get(`${API}/promo-codes`);
          setPromoCodes(response.data);
          console.log('Public promo codes loaded as fallback:', response.data);
        } catch (fallbackError) {
          console.error('Error loading public promo codes:', fallbackError);
        }
      }
    };

    const savePromoCode = async (promoData) => {
      setIsLoading(true);
      try {
        if (editingPromo) {
          await axios.put(`${API}/admin/promo-codes/${editingPromo.id}`, promoData, { headers: getAuthHeaders() });
        } else {
          await axios.post(`${API}/admin/promo-codes`, promoData, { headers: getAuthHeaders() });
        }
        await loadPromoCodes();
        setShowForm(false);
        setEditingPromo(null);
        alert('Promo code saved successfully!');
      } catch (error) {
        alert('Error saving promo code: ' + error.message);
      } finally {
        setIsLoading(false);
      }
    };

    const deletePromoCode = async (id) => {
      if (confirm('Are you sure you want to delete this promo code?')) {
        try {
          await axios.delete(`${API}/admin/promo-codes/${id}`, { headers: getAuthHeaders() });
          await loadPromoCodes();
          alert('Promo code deleted successfully!');
        } catch (error) {
          alert('Error deleting promo code: ' + error.message);
        }
      }
    };

    const PromoForm = () => {
      const [formData, setFormData] = useState(editingPromo || {
        code: '',
        title: '',
        description: '',
        discount_percentage: '',
        discount_amount: '',
        expiry_date: '',
        display_location: 'hero',
        button_text: 'Copy Code',
        button_url: '',
        is_active: true
      });

      const handleSubmit = (e) => {
        e.preventDefault();
        savePromoCode(formData);
      };

      return (
        <div className="bg-gray-700 rounded-lg p-6 mb-6">
          <h4 className="text-white font-semibold mb-4">
            {editingPromo ? 'Edit Promo Code' : 'Create New Promo Code'}
          </h4>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-300 mb-2">Promo Code *</label>
                <input
                  type="text"
                  value={formData.code}
                  onChange={(e) => setFormData({...formData, code: e.target.value.toUpperCase()})}
                  className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none font-mono"
                  placeholder="SAVE20"
                  required
                />
              </div>
              
              <div>
                <label className="block text-gray-300 mb-2">Title *</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                  placeholder="Special Discount"
                  required
                />
              </div>
            </div>
            
            <div>
              <label className="block text-gray-300 mb-2">Description *</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                placeholder="Get 20% off your first order"
                rows={2}
                required
              />
            </div>
            
            <div className="grid md:grid-cols-3 gap-4">
              <div>
                <label className="block text-gray-300 mb-2">Discount %</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={formData.discount_percentage}
                  onChange={(e) => setFormData({...formData, discount_percentage: parseInt(e.target.value) || ''})}
                  className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                  placeholder="20"
                />
              </div>
              
              <div>
                <label className="block text-gray-300 mb-2">Discount $</label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.discount_amount}
                  onChange={(e) => setFormData({...formData, discount_amount: parseFloat(e.target.value) || ''})}
                  className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                  placeholder="5.00"
                />
              </div>
              
              <div>
                <label className="block text-gray-300 mb-2">Expiry Date</label>
                <input
                  type="date"
                  value={formData.expiry_date ? formData.expiry_date.split('T')[0] : ''}
                  onChange={(e) => setFormData({...formData, expiry_date: e.target.value ? new Date(e.target.value).toISOString() : ''})}
                  className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                />
              </div>
            </div>
            
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-300 mb-2">Display Location</label>
                <select
                  value={formData.display_location}
                  onChange={(e) => setFormData({...formData, display_location: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                >
                  <option value="hero">Hero Section</option>
                  <option value="pricing">Pricing Section</option>
                  <option value="floating">Floating Bar (Top)</option>
                  <option value="footer">Footer</option>
                </select>
              </div>
              
              <div>
                <label className="block text-gray-300 mb-2">Button Text</label>
                <input
                  type="text"
                  value={formData.button_text}
                  onChange={(e) => setFormData({...formData, button_text: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                  placeholder="Copy Code"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-gray-300 mb-2">
                Button URL <span className="text-sm text-gray-400">(Optional - if provided, button links to URL instead of copying code)</span>
              </label>
              <input
                type="url"
                value={formData.button_url}
                onChange={(e) => setFormData({...formData, button_url: e.target.value})}
                className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                placeholder="https://billing.bluenebulahosting.com/?promo=SAVE20"
              />
              <p className="text-xs text-gray-400 mt-1">
                Leave empty for "Copy Code" functionality, or add URL to redirect users directly to billing/signup
              </p>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                className="mr-2"
              />
              <label className="text-gray-300">Active</label>
            </div>
            
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={isLoading}
                className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {isLoading ? 'Saving...' : 'Save Promo Code'}
              </button>
              
              <button
                type="button"
                onClick={() => {
                  setShowForm(false);
                  setEditingPromo(null);
                }}
                className="px-6 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      );
    };

    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold text-white">Promo Code Management</h3>
          <button
            onClick={() => setShowForm(true)}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
          >
            Add Promo Code
          </button>
        </div>
        
        {showForm && <PromoForm />}
        
        <div className="space-y-4">
          {promoCodes.map(promo => (
            <div key={promo.id} className="bg-gray-700 rounded-lg p-4">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-4 mb-2">
                    <span className="bg-blue-600 text-white px-3 py-1 rounded font-mono font-bold">
                      {promo.code}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs ${
                      promo.is_active ? 'bg-green-600 text-white' : 'bg-gray-600 text-gray-300'
                    }`}>
                      {promo.is_active ? 'Active' : 'Inactive'}
                    </span>
                    <span className="bg-purple-600 text-white px-2 py-1 rounded text-xs">
                      {promo.display_location}
                    </span>
                  </div>
                  
                  <h4 className="font-semibold text-white">{promo.title}</h4>
                  <p className="text-gray-300 text-sm">{promo.description}</p>
                  
                  <div className="flex gap-4 mt-2 text-xs text-gray-400">
                    {promo.discount_percentage && (
                      <span>{promo.discount_percentage}% off</span>
                    )}
                    {promo.discount_amount && (
                      <span>${promo.discount_amount} off</span>
                    )}
                    {promo.expiry_date && (
                      <span>Expires: {new Date(promo.expiry_date).toLocaleDateString()}</span>
                    )}
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      setEditingPromo(promo);
                      setShowForm(true);
                    }}
                    className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-sm"
                  >
                    Edit
                  </button>
                  
                  <button
                    onClick={() => deletePromoCode(promo.id)}
                    className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
          
          {promoCodes.length === 0 && (
            <div className="text-center py-8 text-gray-400">
              No promo codes created yet. Click "Add Promo Code" to get started.
            </div>
          )}
        </div>
      </div>
    );
  };

  // Site Settings
  const SiteSettings = () => {
    const [settings, setSettings] = useState({
      uptime_kuma_api_key: 'uk1_USvIQkci-6cYMA5VcOksKY7B1TzT7ul2zrvFOniq',
      uptime_kuma_url: 'https://status.bluenebulahosting.com/status/bnh',
      status_update_interval: 30,
      site_title: 'Blue Nebula Hosting',
      site_description: 'Professional hosting solutions with enterprise-grade infrastructure'
    });
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
      loadSiteSettings();
    }, []);

    const loadSiteSettings = async () => {
      try {
        // Try admin endpoint
        const response = await axios.get(`${API}/admin/site-settings`, { headers: getAuthHeaders() });
        setSettings(prev => ({ ...prev, ...response.data }));
      } catch (error) {
        console.error('Error loading site settings:', error);
        if (error.response?.status === 404) {
          // Try alternative endpoint
          try {
            const response = await axios.get(`${API}/settings`, { headers: getAuthHeaders() });
            setSettings(prev => ({ ...prev, ...response.data }));
          } catch (altError) {
            console.error('Error loading alt site settings:', altError);
          }
        }
      }
    };

    const saveSiteSettings = async () => {
      setIsLoading(true);
      try {
        // Try admin endpoint
        let response;
        try {
          response = await axios.put(`${API}/admin/site-settings`, settings, { headers: getAuthHeaders() });
        } catch (err) {
          if (err.response?.status === 404) {
            // Try alternative endpoint
            response = await axios.put(`${API}/settings`, settings, { headers: getAuthHeaders() });
          } else if (err.response?.status === 405) {
            // Try POST method
            response = await axios.post(`${API}/admin/site-settings`, settings, { headers: getAuthHeaders() });
          } else {
            throw err;
          }
        }
        alert('Site settings updated successfully! Some changes may require a server restart.');
      } catch (error) {
        console.error('Error updating site settings:', error);
        alert('Error updating site settings: ' + (error.response?.data?.detail || error.response?.data?.message || error.message));
      } finally {
        setIsLoading(false);
      }
    };

    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-6">Site Settings</h3>
        
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="bg-gray-700 rounded-lg p-4">
            <h4 className="text-white font-semibold mb-4">System Status Configuration</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-gray-300 mb-2">Uptime Kuma API Key</label>
                <input
                  type="text"
                  value={settings.uptime_kuma_api_key}
                  onChange={(e) => setSettings({...settings, uptime_kuma_api_key: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none font-mono text-sm"
                  placeholder="uk1_..."
                />
              </div>
              
              <div>
                <label className="block text-gray-300 mb-2">Status Page URL</label>
                <input
                  type="url"
                  value={settings.uptime_kuma_url}
                  onChange={(e) => setSettings({...settings, uptime_kuma_url: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                  placeholder="https://status.yourdomain.com/status/page"
                />
              </div>
              
              <div>
                <label className="block text-gray-300 mb-2">Update Interval (seconds)</label>
                <input
                  type="number"
                  min="10"
                  max="300"
                  value={settings.status_update_interval}
                  onChange={(e) => setSettings({...settings, status_update_interval: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                />
                <p className="text-xs text-gray-400 mt-1">How often to check status (10-300 seconds)</p>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-700 rounded-lg p-4">
            <h4 className="text-white font-semibold mb-4">Site Information</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-gray-300 mb-2">Site Title</label>
                <input
                  type="text"
                  value={settings.site_title}
                  onChange={(e) => setSettings({...settings, site_title: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                />
              </div>
              
              <div>
                <label className="block text-gray-300 mb-2">Site Description</label>
                <textarea
                  rows={3}
                  value={settings.site_description}
                  onChange={(e) => setSettings({...settings, site_description: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                />
              </div>
              
              <div className="bg-gray-600 rounded p-3">
                <h5 className="text-white font-medium mb-2">Logo Upload Instructions</h5>
                <div className="text-sm text-gray-300 space-y-1">
                  <p>• Upload your logo as <code className="bg-gray-800 px-1 rounded">logo.png</code> to the website root directory</p>
                  <p>• Recommended size: 64x64 pixels (square format)</p>
                  <p>• Supported formats: PNG (preferred), JPG, SVG</p>
                  <p>• Logo will appear in header and footer automatically</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="mt-6 flex space-x-4">
          <button
            onClick={saveSiteSettings}
            disabled={isLoading}
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {isLoading ? 'Saving...' : 'Save Settings'}
          </button>
          
          <button
            onClick={loadSiteSettings}
            className="px-6 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
          >
            Reset to Current
          </button>
        </div>
        
        <div className="mt-6 bg-blue-600/20 border border-blue-600 rounded-lg p-4">
          <h4 className="text-blue-300 font-semibold mb-2">💡 Pro Tips</h4>
          <ul className="text-blue-200 text-sm space-y-1">
            <li>• Test your status page URL before saving to ensure it's accessible</li>
            <li>• Lower update intervals provide more real-time status but use more resources</li>
            <li>• Changes to API keys require backend restart to take effect</li>
            <li>• Always keep a backup of your API keys in a secure location</li>
          </ul>
        </div>
      </div>
    );
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginForm />;
  }

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
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-white">Blue Nebula Admin Panel</h1>
          <div className="flex items-center gap-4">
            <a href="/" className="text-blue-400 hover:text-blue-300 transition-colors">
              ← Back to Website
            </a>
            <button
              onClick={() => {
                console.log('Force refreshing all data...');
                fetchData(true);
              }}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
              disabled={loading}
            >
              <span>🔄</span>
              {loading ? 'Refreshing...' : 'Refresh Data'}
            </button>
            <button
              onClick={clearAllCaches}
              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors flex items-center gap-2"
            >
              <span>🗑️</span>
              Clear Cache
            </button>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
        
        <div className="mb-6">
          <nav className="flex flex-wrap gap-2">
            {[
              { key: 'plans', label: 'Hosting Plans', icon: '📦' },
              { key: 'content', label: 'Website Content', icon: '📝' },
              { key: 'navigation', label: 'Navigation Menu', icon: '🧭' },
              { key: 'company', label: 'Company Info', icon: '🏢' },
              { key: 'legal', label: 'Legal Pages', icon: '📄' },
              { key: 'contact', label: 'Contact & SMTP', icon: '📧' },
              { key: 'promo', label: 'Promo Codes', icon: '🎟️' },
              { key: 'settings', label: 'Site Settings', icon: '⚙️' }
            ].map(tab => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`px-4 py-2 rounded flex items-center gap-2 transition-colors ${
                  activeTab === tab.key 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                <span>{tab.icon}</span>
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
        
        {activeTab === 'plans' && (
          <div>
            <h2 className="text-2xl font-bold text-white mb-6">Manage Hosting Plans</h2>
            
            {/* Debug info */}
            <div className="bg-gray-700 rounded p-2 mb-4 text-xs text-gray-300">
              Debug: Loaded {hostingPlans.length} hosting plans | Loading: {loading ? 'Yes' : 'No'} | Authenticated: {isAuthenticated ? 'Yes' : 'No'}
            </div>
            
            {hostingPlans.length === 0 ? (
              <div className="bg-gray-800 rounded-lg p-6 text-center">
                <div className="text-gray-400 mb-4">
                  {loading ? 'Loading hosting plans...' : 'No hosting plans found'}
                </div>
                <div className="text-sm text-gray-500">
                  {loading ? 'Please wait...' : 'Check console for errors or refresh the page'}
                </div>
              </div>
            ) : (
              <div className="grid gap-6">
                {[
                  {key: 'ssd_shared', label: 'SSD Shared', filter: (p) => p.type === 'shared' && p.sub_type === 'ssd'},
                  {key: 'hdd_shared', label: 'HDD Shared', filter: (p) => p.type === 'shared' && p.sub_type === 'hdd'},
                  {key: 'standard_vps', label: 'Standard VPS', filter: (p) => p.type === 'vps' && p.sub_type === 'standard'},
                  {key: 'performance_vps', label: 'Performance VPS', filter: (p) => p.type === 'vps' && p.sub_type === 'performance'},
                  {key: 'standard_gameserver', label: 'Standard GameServer', filter: (p) => p.type === 'gameserver' && p.sub_type === 'standard'},
                  {key: 'performance_gameserver', label: 'Performance GameServer', filter: (p) => p.type === 'gameserver' && p.sub_type === 'performance'}
                ].map(planCategory => {
                  const typePlans = hostingPlans.filter(planCategory.filter);
                  if (typePlans.length === 0) return null;
                  
                  return (
                    <div key={planCategory.key} className="bg-gray-800 rounded-lg p-6">
                      <h3 className="text-xl font-bold text-white mb-4">
                        {planCategory.label} ({typePlans.length} plans)
                      </h3>
                      
                      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {typePlans.map(plan => (
                          <div key={plan.id} className="bg-gray-700 rounded-lg p-4">
                            <div className="flex justify-between items-start mb-2">
                              <h4 className="font-bold text-white">{plan.name}</h4>
                              {plan.is_popular && (
                                <span className="bg-blue-600 text-white px-2 py-1 rounded text-xs">Popular</span>
                              )}
                            </div>
                            
                            <div className="text-blue-400 font-bold text-lg mb-2">
                              ${plan.price}/mo
                            </div>
                            
                            <div className="text-gray-300 text-sm mb-4">
                              {plan.cpu && <div>CPU: {plan.cpu}</div>}
                              {plan.ram && <div>RAM: {plan.ram}</div>}
                              {plan.disk_space && <div>Storage: {plan.disk_space}</div>}
                              {plan.bandwidth && <div>Bandwidth: {plan.bandwidth}</div>}
                              {plan.markup_percentage > 0 && (
                                <div className="text-yellow-400 text-xs mt-1">
                                  Markup: {plan.markup_percentage}%
                                </div>
                              )}
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
            )}
          </div>
        )}
        
        {activeTab === 'content' && <ContentEditor />}
        {activeTab === 'navigation' && <NavigationEditor />}
        {activeTab === 'company' && <CompanyEditor />}
        {activeTab === 'legal' && <LegalEditor />}
        {activeTab === 'contact' && <ContactSMTPEditor />}
        {activeTab === 'promo' && <PromoCodeManager />}
        {activeTab === 'settings' && <SiteSettings />}
        
        {selectedPlan && (
          <PlanEditor plan={selectedPlan} onUpdate={updatePlan} />
        )}
      </div>
    </div>
  );
};

export default AdminPanel;
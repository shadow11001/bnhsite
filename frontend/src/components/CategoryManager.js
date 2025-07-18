import React, { useState, useEffect } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = BACKEND_URL;

const CategoryManager = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [showForm, setShowForm] = useState(false);

  // Get auth token for API requests
  const getAuthHeaders = () => {
    const token = localStorage.getItem('admin_token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  };

  // Load categories from backend
  const loadCategories = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/api/admin/categories`, { 
        headers: getAuthHeaders() 
      });
      setCategories(response.data);
      console.log('Categories loaded:', response.data);
    } catch (error) {
      console.error('Error loading categories:', error);
      // Set default categories if backend doesn't support it yet
      setCategories([
        {
          id: '1',
          name: 'SSD Shared Hosting',
          type: 'shared',
          sub_type: 'ssd',
          description: 'Fast SSD-powered shared hosting',
          resource_specs: {
            cpu: { min: '1 vCPU', max: '2 vCPU', default: '1 vCPU' },
            ram: { min: '512 MB', max: '2 GB', default: '1 GB' },
            disk_space: { min: '5 GB', max: '100 GB', default: '10 GB' },
            bandwidth: { default: 'Unlimited' }
          },
          validation_rules: {
            websites: { min: 1, max: 10, default: 1 },
            databases: { min: 1, max: 10, default: 1 },
            email_accounts: { min: 5, max: 100, default: 10 }
          },
          supports_wordpress: true,
          category_fields: ['websites', 'subdomains', 'databases', 'email_accounts'],
          is_active: true,
          display_order: 1
        },
        {
          id: '2',
          name: 'Standard VPS',
          type: 'vps',
          sub_type: 'standard',
          description: 'Virtual Private Servers with dedicated resources',
          resource_specs: {
            cpu: { min: '1 vCPU', max: '8 vCPU', default: '2 vCPU' },
            ram: { min: '1 GB', max: '32 GB', default: '4 GB' },
            disk_space: { min: '20 GB', max: '500 GB', default: '50 GB' },
            bandwidth: { default: 'Unlimited' }
          },
          validation_rules: {
            root_access: { default: true },
            os_choice: { default: true }
          },
          supports_wordpress: true,
          category_fields: ['root_access', 'os_choice', 'backup_included'],
          is_active: true,
          display_order: 2
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCategories();
  }, []);

  // Save category (create or update)
  const saveCategory = async (categoryData) => {
    setLoading(true);
    try {
      if (editingCategory) {
        await axios.put(`${API}/api/admin/categories/${editingCategory.id}`, categoryData, {
          headers: getAuthHeaders()
        });
        alert('Category updated successfully!');
      } else {
        await axios.post(`${API}/api/admin/categories`, categoryData, {
          headers: getAuthHeaders()
        });
        alert('Category created successfully!');
      }
      await loadCategories();
      setShowForm(false);
      setEditingCategory(null);
    } catch (error) {
      console.error('Error saving category:', error);
      alert('Error saving category: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  // Delete category
  const deleteCategory = async (id) => {
    if (!confirm('Are you sure you want to delete this category? This cannot be undone.')) {
      return;
    }

    try {
      await axios.delete(`${API}/api/admin/categories/${id}`, {
        headers: getAuthHeaders()
      });
      alert('Category deleted successfully!');
      await loadCategories();
    } catch (error) {
      console.error('Error deleting category:', error);
      alert('Error deleting category: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Category Form Component
  const CategoryForm = () => {
    const [formData, setFormData] = useState(editingCategory || {
      name: '',
      type: 'shared',
      sub_type: 'standard',
      description: '',
      resource_specs: {
        cpu: { min: '', max: '', default: '' },
        ram: { min: '', max: '', default: '' },
        disk_space: { min: '', max: '', default: '' },
        bandwidth: { default: '' }
      },
      validation_rules: {
        websites: { min: '', max: '', default: '' },
        databases: { min: '', max: '', default: '' },
        email_accounts: { min: '', max: '', default: '' }
      },
      supports_wordpress: true,
      category_fields: [],
      is_active: true,
      display_order: categories.length + 1
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      
      // Validate required fields
      if (!formData.name.trim()) {
        alert('Category name is required');
        return;
      }

      saveCategory(formData);
    };

    const updateResourceSpec = (resource, field, value) => {
      setFormData(prev => ({
        ...prev,
        resource_specs: {
          ...prev.resource_specs,
          [resource]: {
            ...prev.resource_specs[resource],
            [field]: value
          }
        }
      }));
    };

    const updateValidationRule = (rule, field, value) => {
      setFormData(prev => ({
        ...prev,
        validation_rules: {
          ...prev.validation_rules,
          [rule]: {
            ...prev.validation_rules[rule],
            [field]: value
          }
        }
      }));
    };

    const toggleCategoryField = (field) => {
      setFormData(prev => ({
        ...prev,
        category_fields: prev.category_fields.includes(field) 
          ? prev.category_fields.filter(f => f !== field)
          : [...prev.category_fields, field]
      }));
    };

    return (
      <div className="bg-gray-700 rounded-lg p-6 mb-6">
        <h4 className="text-white font-semibold mb-4">
          {editingCategory ? 'Edit Category' : 'Create New Category'}
        </h4>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="bg-gray-600 rounded-lg p-4">
            <h5 className="text-white font-medium mb-4">Basic Information</h5>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-300 mb-2">Category Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                  placeholder="e.g., Premium SSD Hosting"
                  required
                />
              </div>
              
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-gray-300 mb-2">Type</label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData({...formData, type: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                  >
                    <option value="shared">Shared</option>
                    <option value="vps">VPS</option>
                    <option value="gameserver">GameServer</option>
                    <option value="dedicated">Dedicated</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-gray-300 mb-2">Sub-Type</label>
                  <select
                    value={formData.sub_type}
                    onChange={(e) => setFormData({...formData, sub_type: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                  >
                    <option value="standard">Standard</option>
                    <option value="ssd">SSD</option>
                    <option value="hdd">HDD</option>
                    <option value="performance">Performance</option>
                    <option value="premium">Premium</option>
                  </select>
                </div>
              </div>
            </div>
            
            <div className="mt-4">
              <label className="block text-gray-300 mb-2">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                placeholder="Brief description of this category"
                rows={2}
              />
            </div>
          </div>

          {/* Resource Specifications */}
          <div className="bg-gray-600 rounded-lg p-4">
            <h5 className="text-white font-medium mb-4">Resource Specifications</h5>
            
            {['cpu', 'ram', 'disk_space'].map(resource => (
              <div key={resource} className="mb-4">
                <label className="block text-gray-300 mb-2 capitalize">
                  {resource.replace('_', ' ')} Limits
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <input
                    type="text"
                    value={formData.resource_specs[resource]?.min || ''}
                    onChange={(e) => updateResourceSpec(resource, 'min', e.target.value)}
                    className="px-3 py-2 bg-gray-700 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                    placeholder="Min"
                  />
                  <input
                    type="text"
                    value={formData.resource_specs[resource]?.max || ''}
                    onChange={(e) => updateResourceSpec(resource, 'max', e.target.value)}
                    className="px-3 py-2 bg-gray-700 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                    placeholder="Max"
                  />
                  <input
                    type="text"
                    value={formData.resource_specs[resource]?.default || ''}
                    onChange={(e) => updateResourceSpec(resource, 'default', e.target.value)}
                    className="px-3 py-2 bg-gray-700 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                    placeholder="Default"
                  />
                </div>
              </div>
            ))}
            
            <div>
              <label className="block text-gray-300 mb-2">Default Bandwidth</label>
              <input
                type="text"
                value={formData.resource_specs.bandwidth?.default || ''}
                onChange={(e) => updateResourceSpec('bandwidth', 'default', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                placeholder="e.g., Unlimited, 1TB, 500GB"
              />
            </div>
          </div>

          {/* Validation Rules */}
          {formData.type === 'shared' && (
            <div className="bg-gray-600 rounded-lg p-4">
              <h5 className="text-white font-medium mb-4">Shared Hosting Validation Rules</h5>
              
              {['websites', 'databases', 'email_accounts'].map(rule => (
                <div key={rule} className="mb-4">
                  <label className="block text-gray-300 mb-2 capitalize">
                    {rule.replace('_', ' ')} Limits
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    <input
                      type="number"
                      value={formData.validation_rules[rule]?.min || ''}
                      onChange={(e) => updateValidationRule(rule, 'min', parseInt(e.target.value) || '')}
                      className="px-3 py-2 bg-gray-700 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                      placeholder="Min"
                    />
                    <input
                      type="number"
                      value={formData.validation_rules[rule]?.max || ''}
                      onChange={(e) => updateValidationRule(rule, 'max', parseInt(e.target.value) || '')}
                      className="px-3 py-2 bg-gray-700 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                      placeholder="Max"
                    />
                    <input
                      type="number"
                      value={formData.validation_rules[rule]?.default || ''}
                      onChange={(e) => updateValidationRule(rule, 'default', parseInt(e.target.value) || '')}
                      className="px-3 py-2 bg-gray-700 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                      placeholder="Default"
                    />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Category-Specific Fields */}
          <div className="bg-gray-600 rounded-lg p-4">
            <h5 className="text-white font-medium mb-4">Category-Specific Fields</h5>
            <p className="text-gray-300 text-sm mb-4">
              Select which fields should appear in the plan editor for this category:
            </p>
            
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {[
                'websites', 'subdomains', 'databases', 'email_accounts',
                'parked_domains', 'addon_domains', 'root_access', 'os_choice',
                'backup_included', 'ssl_certificate', 'wordpress_support'
              ].map(field => (
                <label key={field} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.category_fields.includes(field)}
                    onChange={() => toggleCategoryField(field)}
                    className="mr-2"
                  />
                  <span className="text-gray-300 text-sm capitalize">
                    {field.replace('_', ' ')}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* WordPress and Additional Options */}
          <div className="bg-gray-600 rounded-lg p-4">
            <h5 className="text-white font-medium mb-4">Additional Options</h5>
            
            <div className="grid md:grid-cols-2 gap-4">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.supports_wordpress}
                  onChange={(e) => setFormData({...formData, supports_wordpress: e.target.checked})}
                  className="mr-2"
                />
                <label className="text-gray-300">WordPress Container Support</label>
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                  className="mr-2"
                />
                <label className="text-gray-300">Active Category</label>
              </div>
            </div>
            
            <div className="mt-4">
              <label className="block text-gray-300 mb-2">Display Order</label>
              <input
                type="number"
                value={formData.display_order}
                onChange={(e) => setFormData({...formData, display_order: parseInt(e.target.value) || 1})}
                className="w-32 px-3 py-2 bg-gray-700 text-white rounded border border-gray-500 focus:border-blue-400 focus:outline-none"
                min="1"
              />
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Saving...' : (editingCategory ? 'Update Category' : 'Create Category')}
            </button>
            
            <button
              type="button"
              onClick={() => {
                setShowForm(false);
                setEditingCategory(null);
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
        <h3 className="text-xl font-bold text-white">Category Management</h3>
        <button
          onClick={() => setShowForm(true)}
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
        >
          Add Category
        </button>
      </div>
      
      {showForm && <CategoryForm />}
      
      {loading && !showForm && (
        <div className="text-center py-8 text-gray-400">
          Loading categories...
        </div>
      )}
      
      <div className="space-y-4">
        {categories.map(category => (
          <div key={category.id} className="bg-gray-700 rounded-lg p-4">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-4 mb-2">
                  <h4 className="font-semibold text-white">{category.name}</h4>
                  <span className="bg-blue-600 text-white px-2 py-1 rounded text-xs">
                    {category.type} - {category.sub_type}
                  </span>
                  <span className={`px-2 py-1 rounded text-xs ${
                    category.is_active ? 'bg-green-600 text-white' : 'bg-gray-600 text-gray-300'
                  }`}>
                    {category.is_active ? 'Active' : 'Inactive'}
                  </span>
                  {category.supports_wordpress && (
                    <span className="bg-purple-600 text-white px-2 py-1 rounded text-xs">
                      WordPress
                    </span>
                  )}
                </div>
                
                <p className="text-gray-300 text-sm mb-2">{category.description}</p>
                
                <div className="flex gap-4 text-xs text-gray-400">
                  <span>Order: {category.display_order}</span>
                  <span>Fields: {category.category_fields?.length || 0}</span>
                  {category.resource_specs?.cpu?.default && (
                    <span>CPU: {category.resource_specs.cpu.default}</span>
                  )}
                  {category.resource_specs?.ram?.default && (
                    <span>RAM: {category.resource_specs.ram.default}</span>
                  )}
                </div>
              </div>
              
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setEditingCategory(category);
                    setShowForm(true);
                  }}
                  className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-sm"
                >
                  Edit
                </button>
                
                <button
                  onClick={() => deleteCategory(category.id)}
                  className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors text-sm"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))}
        
        {categories.length === 0 && !loading && (
          <div className="text-center py-8 text-gray-400">
            No categories created yet. Click "Add Category" to get started.
          </div>
        )}
      </div>
    </div>
  );
};

export default CategoryManager;
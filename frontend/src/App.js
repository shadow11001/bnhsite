import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import AdminPanel from "./AdminPanel";

// Legal Page Component
const LegalPage = ({ type }) => {
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchContent = async () => {
      try {
        const response = await axios.get(`${API}/content/${type}`);
        setContent(response.data);
      } catch (error) {
        console.error('Error fetching content:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchContent();
  }, [type]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <Header />
      <div className="pt-20 pb-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-8 border border-gray-700">
            <h1 className="text-4xl font-bold text-white mb-8">
              {content?.title || (type === 'terms' ? 'Terms of Service' : 'Privacy Policy')}
            </h1>
            <div className="prose prose-invert max-w-none">
              <div className="text-gray-300 whitespace-pre-wrap">
                {content?.content || `${content?.title || (type === 'terms' ? 'Terms of Service' : 'Privacy Policy')} content will be updated by the administrator.`}
              </div>
            </div>
            <div className="mt-8 pt-8 border-t border-gray-700">
              <a href="/" className="text-blue-400 hover:text-blue-300 transition-colors">
                ← Back to Home
              </a>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = BACKEND_URL; // BACKEND_URL should be the base URL (e.g., http://localhost:8001)

// Promo Code Component
const PromoCodeBanner = ({ location = "hero" }) => {
  const [promoCodes, setPromoCodes] = useState([]);
  const [dismissedFloating, setDismissedFloating] = useState(false);

  useEffect(() => {
    const fetchPromoCodes = async () => {
      try {
        const timestamp = new Date().getTime();
        const response = await axios.get(`${API}/promo-codes?_t=${timestamp}`, {
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          }
        });
        const locationCodes = response.data.filter(code => 
          code.display_location === location && code.is_active
        );
        setPromoCodes(locationCodes);
      } catch (error) {
        console.error('Error fetching promo codes:', error);
      }
    };
    fetchPromoCodes();
    
    // Check if floating banner was dismissed
    if (location === 'floating') {
      const dismissed = localStorage.getItem('promo_floating_dismissed');
      setDismissedFloating(dismissed === 'true');
    }
  }, [location]);

  const copyToClipboard = (code) => {
    navigator.clipboard.writeText(code).then(() => {
      alert(`Promo code "${code}" copied to clipboard!`);
    });
  };

  const dismissFloatingBanner = () => {
    setDismissedFloating(true);
    localStorage.setItem('promo_floating_dismissed', 'true');
  };

  const handleButtonClick = (promo) => {
    if (promo.button_url) {
      // Open URL in new tab
      window.open(promo.button_url, '_blank');
    } else {
      // Copy code to clipboard
      copyToClipboard(promo.code);
    }
  };

  if (promoCodes.length === 0) return null;
  if (location === 'floating' && dismissedFloating) return null;

  return (
    <div className="space-y-4">
      {promoCodes.map(promo => (
        <div key={promo.id} className={`
          ${location === 'floating' ? 'sticky top-0 left-0 right-0 z-[9999]' : ''}
          ${location === 'hero' ? 'mb-8' : ''}
          ${location === 'pricing' ? 'mb-6' : ''}
          bg-gradient-to-r from-green-600 to-blue-600 text-white p-4 rounded-lg shadow-lg relative
          ${location === 'floating' ? 'rounded-none shadow-2xl' : ''}
        `}>
          {/* Dismiss button for floating banners */}
          {location === 'floating' && (
            <button
              onClick={dismissFloatingBanner}
              className="absolute top-2 right-2 text-white/80 hover:text-white transition-colors z-10 bg-black/20 rounded-full p-1"
              aria-label="Dismiss"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
          
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="text-center md:text-left">
              <h3 className="font-bold text-lg">{promo.title}</h3>
              <p className="text-sm opacity-90">{promo.description}</p>
              {promo.expiry_date && (
                <p className="text-xs opacity-75 mt-1">
                  Expires: {new Date(promo.expiry_date).toLocaleDateString()}
                </p>
              )}
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-center">
                <div className="bg-white/20 px-4 py-2 rounded-lg">
                  <span className="font-mono font-bold text-lg">{promo.code}</span>
                </div>
              </div>
              
              <button
                onClick={() => handleButtonClick(promo)}
                className="bg-white text-blue-600 px-6 py-2 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
              >
                {promo.button_text}
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

// System Status Component with Uptime Kuma Integration
const SystemStatus = () => {
  const [status, setStatus] = useState({ status: 'checking', text: 'Checking...' });

  useEffect(() => {
    const checkStatus = async () => {
      try {
        // Call our backend endpoint that will fetch from Uptime Kuma
        const response = await axios.get(`${API}/system-status`);
        setStatus(response.data);
      } catch (error) {
        console.error('Error fetching status:', error);
        setStatus({ status: 'unknown', text: 'Status Unknown' });
      }
    };

    checkStatus();
    // Check status every 30 seconds
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    switch (status.status) {
      case 'operational': return 'text-green-400';
      case 'degraded': return 'text-yellow-400';
      case 'down': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusIcon = () => {
    switch (status.status) {
      case 'operational': return '●';
      case 'degraded': return '◐';
      case 'down': return '●';
      default: return '○';
    }
  };

  return (
    <a 
      href="https://status.bluenebulahosting.com/status/bnh" 
      target="_blank" 
      rel="noopener noreferrer" 
      className={`${getStatusColor()} hover:text-blue-300 transition-colors flex items-center`}
    >
      <span className="mr-1">{getStatusIcon()}</span>
      Status: {status.text}
    </a>
  );
};

// Header Component
const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isHostingDropdownOpen, setIsHostingDropdownOpen] = useState(false);
  const [navigationItems, setNavigationItems] = useState([]);

  useEffect(() => {
    const fetchNavigation = async () => {
      try {
        const response = await axios.get(`${API}/navigation`);
        if (response.data && Array.isArray(response.data)) {
          // Sort by order field
          const sortedItems = response.data.sort((a, b) => (a.order || 0) - (b.order || 0));
          setNavigationItems(sortedItems);
        }
      } catch (error) {
        console.error('Error fetching navigation:', error);
        // Fallback to default navigation if API fails
        setNavigationItems([
          { id: '1', label: 'Home', href: '#home', order: 1, is_external: false },
          { id: '2', label: 'About', href: '#about', order: 2, is_external: false },
          { id: '3', label: 'Contact', href: '#contact', order: 3, is_external: false }
        ]);
      }
    };
    
    fetchNavigation();
  }, []);

  return (
    <header className="bg-gray-900/95 backdrop-blur-sm fixed w-full z-50 border-b border-blue-500/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 flex items-center justify-center">
              <img 
                src="/logo.png" 
                alt="Blue Nebula Hosting" 
                className="w-10 h-10 object-contain"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
              <div className="w-10 h-10 bg-gradient-to-r from-blue-400 to-purple-600 rounded-lg items-center justify-center text-white font-bold text-xl" style={{display: 'none'}}>
                BN
              </div>
            </div>
            <div className="text-white">
              <h1 className="font-bold text-xl">Blue Nebula Hosting</h1>
            </div>
          </div>
          
          <nav className="hidden md:flex space-x-8">
            {/* Dynamic navigation items */}
            {navigationItems.map((item) => (
              <a 
                key={item.id}
                href={item.href}
                className="text-gray-300 hover:text-blue-400 transition-colors"
                target={item.is_external ? "_blank" : undefined}
                rel={item.is_external ? "noopener noreferrer" : undefined}
              >
                {item.label}
              </a>
            ))}
            
            {/* Keep static hosting dropdown for now */}
            <div className="relative group">
              <button 
                className="text-gray-300 hover:text-blue-400 transition-colors flex items-center"
                onMouseEnter={() => setIsHostingDropdownOpen(true)}
                onMouseLeave={() => setIsHostingDropdownOpen(false)}
              >
                Hosting
                <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {isHostingDropdownOpen && (
                <div 
                  className="absolute top-full left-0 mt-2 w-48 bg-gray-800 rounded-lg shadow-lg border border-gray-700 py-2 z-50"
                  onMouseEnter={() => setIsHostingDropdownOpen(true)}
                  onMouseLeave={() => setIsHostingDropdownOpen(false)}
                >
                  <a href="#hosting" className="block px-4 py-2 text-gray-300 hover:text-blue-400 hover:bg-gray-700 transition-colors">
                    Shared Hosting
                  </a>
                  <a href="#vps" className="block px-4 py-2 text-gray-300 hover:text-blue-400 hover:bg-gray-700 transition-colors">
                    VPS Hosting
                  </a>
                  <a href="#gameservers" className="block px-4 py-2 text-gray-300 hover:text-blue-400 hover:bg-gray-700 transition-colors">
                    GameServer Hosting
                  </a>
                </div>
              )}
            </div>
            
            <SystemStatus />
          </nav>
          
          <div className="hidden md:flex space-x-4">
            <a href="https://billing.bluenebulahosting.com" target="_blank" rel="noopener noreferrer" className="px-4 py-2 text-blue-400 border border-blue-400 rounded-lg hover:bg-blue-400 hover:text-gray-900 transition-colors">
              Client Area
            </a>
            <a href="https://panel.bluenebulahosting.com" target="_blank" rel="noopener noreferrer" className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-colors">
              Game Panel
            </a>
          </div>
          
          <button 
            className="md:hidden text-gray-300"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
        
        {isMenuOpen && (
          <div className="md:hidden pb-4">
            <nav className="flex flex-col space-y-4">
              {/* Dynamic navigation items for mobile */}
              {navigationItems.map((item) => (
                <a 
                  key={`mobile-${item.id}`}
                  href={item.href}
                  className="text-gray-300 hover:text-blue-400 transition-colors"
                  target={item.is_external ? "_blank" : undefined}
                  rel={item.is_external ? "noopener noreferrer" : undefined}
                >
                  {item.label}
                </a>
              ))}
              
              {/* Keep static hosting section for mobile */}
              <div className="space-y-2">
                <div className="text-gray-400 text-sm font-semibold">Hosting</div>
                <a href="#hosting" className="text-gray-300 hover:text-blue-400 transition-colors pl-4">Shared Hosting</a>
                <a href="#vps" className="text-gray-300 hover:text-blue-400 transition-colors pl-4">VPS Hosting</a>
                <a href="#gameservers" className="text-gray-300 hover:text-blue-400 transition-colors pl-4">GameServer Hosting</a>
              </div>
              
              <SystemStatus />
              <div className="flex flex-col space-y-2 mt-4">
                <a href="https://billing.bluenebulahosting.com" target="_blank" rel="noopener noreferrer" className="px-4 py-2 text-blue-400 border border-blue-400 rounded-lg hover:bg-blue-400 hover:text-gray-900 transition-colors text-center">
                  Client Area
                </a>
                <a href="https://panel.bluenebulahosting.com" target="_blank" rel="noopener noreferrer" className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-colors text-center">
                  Game Panel
                </a>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

// Hero Section Component
const HeroSection = () => {
  const [heroContent, setHeroContent] = useState(null);
  
  useEffect(() => {
    const fetchHeroContent = async () => {
      try {
        const response = await axios.get(`${API}/content/hero`);
        setHeroContent(response.data);
      } catch (error) {
        console.error('Error fetching hero content:', error);
        // Fallback to default content if API fails
        setHeroContent({
          title: "Fast, Reliable, and Affordable",
          subtitle: "Hosting Solutions—Starting at $1/mo",
          description: "Blue Nebula Hosting provides fast, reliable, and affordable hosting solutions with 24/7 support, 99.9% uptime guarantee, and professional managed services for shared hosting, VPS, and GameServers.",
          button_text: "View Hosting Plans",
          button_url: "#hosting"
        });
      }
    };
    
    fetchHeroContent();
  }, []);

  if (!heroContent) {
    return (
      <section id="home" className="pt-20 pb-20 min-h-screen flex items-center">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="text-white">Loading...</div>
        </div>
      </section>
    );
  }

  return (
    <section id="home" className="pt-20 pb-20 min-h-screen flex items-center">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        {/* Hero Promo Banner */}
        <PromoCodeBanner location="hero" />
        
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
          {heroContent.title || "Fast, Reliable, and Affordable"}
        </h1>
        <p className="text-xl md:text-2xl text-gray-300 mb-4">
          {heroContent.subtitle || "Hosting Solutions—Starting at $1/mo"}
        </p>
        <p className="text-lg text-gray-400 mb-8 max-w-3xl mx-auto">
          {heroContent.description || "Blue Nebula Hosting provides fast, reliable, and affordable hosting solutions with 24/7 support, 99.9% uptime guarantee, and professional managed services for shared hosting, VPS, and GameServers."}
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a href={heroContent.button_url || "#hosting"} className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-colors font-semibold text-lg">
            {heroContent.button_text || "View Hosting Plans"}
          </a>
          <a href="https://billing.bluenebulahosting.com" target="_blank" rel="noopener noreferrer" className="px-8 py-4 border-2 border-blue-400 text-blue-400 rounded-lg hover:bg-blue-400 hover:text-gray-900 transition-colors font-semibold text-lg">
            Client Portal
          </a>
        </div>
      </div>
    </section>
  );
};

// Hosting Plans Component
const HostingPlans = ({ plans, title, type, description }) => {
  let filteredPlans = [];
  
  // Filter plans based on type and sub_type from database (production format)
  if (type === 'ssd_shared') {
    filteredPlans = plans.filter(plan => plan.type === 'shared' && plan.sub_type === 'ssd');
  } else if (type === 'hdd_shared') {
    filteredPlans = plans.filter(plan => plan.type === 'shared' && plan.sub_type === 'hdd');
  } else if (type === 'standard_vps') {
    filteredPlans = plans.filter(plan => plan.type === 'vps' && plan.sub_type === 'standard');
  } else if (type === 'performance_vps') {
    filteredPlans = plans.filter(plan => plan.type === 'vps' && plan.sub_type === 'performance');
  } else if (type === 'standard_gameserver') {
    filteredPlans = plans.filter(plan => plan.type === 'gameserver' && plan.sub_type === 'standard');
  } else if (type === 'performance_gameserver') {
    filteredPlans = plans.filter(plan => plan.type === 'gameserver' && plan.sub_type === 'performance');
  }
  
  if (filteredPlans.length === 0) return null;
  
  return (
    <div className="mb-20">
      <div className="text-center mb-12">
        <h3 className="text-3xl font-bold text-white mb-4">{title}</h3>
        {description && (
          <p className="text-lg text-gray-300 max-w-2xl mx-auto">{description}</p>
        )}
      </div>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 justify-items-center max-w-6xl mx-auto">
        {filteredPlans.map((plan) => (
          <div key={plan.id} className={`relative bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border ${plan.is_popular ? 'border-blue-500 ring-2 ring-blue-500/50' : 'border-gray-700'} hover:border-blue-400 transition-all w-full max-w-sm flex flex-col h-full min-h-[400px]`}>
            {plan.is_popular && (
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <span className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                  Popular
                </span>
              </div>
            )}
            
            <div className="text-center mb-6 flex-shrink-0">
              <h4 className="text-xl font-bold text-white mb-2">{plan.name}</h4>
              <div className="text-3xl font-bold text-blue-400 mb-2">
                ${plan.price}
                <span className="text-lg text-gray-400">/mo</span>
              </div>
              
              {/* Technical Specifications */}
              {(plan.cpu || plan.ram || plan.disk_space || plan.bandwidth) && (
                <div className="text-sm text-gray-400 mb-4 space-y-1">
                  {plan.cpu && <div>CPU: {plan.cpu} {plan.cpu.includes('vCPU') ? '' : (plan.type === 'shared' ? 'Core' : 'vCPU')}</div>}
                  {plan.ram && <div>RAM: {plan.ram} {plan.ram.includes('GB') ? '' : 'GB'}</div>}
                  {plan.disk_space && <div>Storage: {plan.disk_space}</div>}
                  {plan.bandwidth && <div>Bandwidth: {plan.bandwidth}</div>}
                </div>
              )}
            </div>
            
            <ul className="space-y-2 mb-8 flex-grow">
              {plan.features.map((feature, index) => (
                <li key={index} className="flex items-center text-gray-300 text-sm">
                  <svg className="w-4 h-4 text-green-400 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  {feature}
                </li>
              ))}
              
              {plan.supported_games && (
                <li className="flex items-start text-gray-300 text-sm">
                  <svg className="w-4 h-4 text-green-400 mr-2 mt-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <div>
                    <span>Supported Games:</span>
                    <div className="text-xs text-blue-300 mt-1">
                      {plan.supported_games.join(', ')}
                    </div>
                  </div>
                </li>
              )}
            </ul>
            
            <div className="mt-auto flex-shrink-0">
              <a href={plan.order_url || "https://billing.bluenebulahosting.com"} target="_blank" rel="noopener noreferrer" className={`block w-full py-3 rounded-lg font-semibold transition-all text-center ${
                plan.is_popular 
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700' 
                  : 'border border-blue-400 text-blue-400 hover:bg-blue-400 hover:text-gray-900'
              }`}>
                Order Now
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Features Section Component
const FeaturesSection = () => {
  const [featuresContent, setFeaturesContent] = useState(null);
  
  useEffect(() => {
    const fetchFeaturesContent = async () => {
      try {
        const response = await axios.get(`${API}/content/features`);
        setFeaturesContent(response.data);
      } catch (error) {
        console.error('Error fetching features content:', error);
        // Fallback to default content if API fails
        setFeaturesContent({
          title: "Why Choose Blue Nebula?",
          description: "Professional hosting solutions with enterprise-grade infrastructure and 24/7 expert support.",
          features: [
            "99.9% Uptime Guarantee",
            "24/7 Expert Technical Support", 
            "Enterprise-Grade Security",
            "Lightning-Fast SSD Storage",
            "Free SSL Certificates",
            "Daily Automated Backups",
            "DDoS Protection",
            "Easy One-Click Installations"
          ]
        });
      }
    };
    
    fetchFeaturesContent();
  }, []);

  // Default feature cards (these can be made dynamic later if needed)
  const defaultFeatures = [
    {
      title: "Shared Hosting",
      description: "Perfect for websites and blogs with HestiaCP control panel and one-click installations.",
      image: "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwyfHxzZXJ2ZXJ8ZW58MHx8fHwxNzUyMjk1Nzg3fDA&ixlib=rb-4.1.0&q=85",
      features: ["Free SSL Certificate", "Daily Backups", "99.9% Uptime", "24/7 Support"],
      link: "#hosting"
    },
    {
      title: "VPS Hosting", 
      description: "Scalable virtual private servers with full root access and managed support.",
      image: "https://images.unsplash.com/photo-1594915440248-1e419eba6611?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHwyfHxkYXRhY2VudGVyfGVufDB8fHx8MTc1MjI5NTgwMHww&ixlib=rb-4.1.0&q=85",
      features: ["Full Root Access", "Choice of OS", "DDoS Protection", "Scalable Resources"],
      link: "#vps"
    },
    {
      title: "GameServer Hosting",
      description: "High-performance game servers with Pterodactyl panel for easy management.",
      image: "https://images.unsplash.com/photo-1542751371-adc38448a05e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1NzZ8MHwxfHNlYXJjaHwxfHxnYW1pbmd8ZW58MHx8fHwxNzUyMjgwMTA1fDA&ixlib=rb-4.1.0&q=85",
      features: ["Instant Setup", "Pterodactyl Panel", "Multiple Games", "DDoS Protection"],
      link: "#gameservers"
    }
  ];

  if (!featuresContent) {
    return (
      <section className="py-20 bg-gray-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-white text-center">Loading features...</div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-20 bg-gray-900/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">
            {featuresContent.title || "Why Choose Blue Nebula?"}
          </h2>
          <p className="text-lg text-gray-300 max-w-2xl mx-auto">
            {featuresContent.description || "Professional hosting solutions with enterprise-grade infrastructure and 24/7 expert support."}
          </p>
        </div>
        
        {/* Display database features if available */}
        {featuresContent.features && featuresContent.features.length > 0 && (
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
            {featuresContent.features.map((feature, index) => (
              <div key={index} className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700 hover:border-blue-400 transition-all text-center">
                <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <span className="text-white font-bold">✓</span>
                </div>
                <h3 className="text-white font-semibold mb-2">{feature}</h3>
              </div>
            ))}
          </div>
        )}
        
        {/* Default hosting type features */}
        <div className="grid md:grid-cols-3 gap-8">
          {defaultFeatures.map((feature, index) => (
            <div key={index} className="bg-gray-800/50 backdrop-blur-sm rounded-xl overflow-hidden border border-gray-700 hover:border-blue-400 transition-all">
              <img 
                src={feature.image} 
                alt={feature.title}
                className="w-full h-48 object-cover"
              />
              <div className="p-6">
                <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                <p className="text-gray-300 mb-4">{feature.description}</p>
                <ul className="space-y-2 mb-6">
                  {feature.features.map((item, idx) => (
                    <li key={idx} className="flex items-center text-sm text-gray-300">
                      <svg className="w-4 h-4 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {item}
                    </li>
                  ))}
                </ul>
                <a href={feature.link} className="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  View Plans
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// About Section Component
const AboutSection = () => {
  const [aboutContent, setAboutContent] = useState(null);
  
  useEffect(() => {
    const fetchAboutContent = async () => {
      try {
        const response = await axios.get(`${API}/content/about`);
        setAboutContent(response.data);
      } catch (error) {
        console.error('Error fetching about content:', error);
        // Fallback to default content if API fails
        setAboutContent({
          title: "About Blue Nebula Hosting",
          description: "Blue Nebula Hosting provides fast, reliable, and affordable hosting solutions for individuals and businesses. Our managed hosting services include shared hosting, VPS, and GameServer hosting with 24/7 support. We pride ourselves on delivering enterprise-grade infrastructure with personal support, ensuring your websites and applications run smoothly while you focus on growing your business."
        });
      }
    };
    
    fetchAboutContent();
  }, []);

  if (!aboutContent) {
    return (
      <section id="about" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-white text-center">Loading about section...</div>
        </div>
      </section>
    );
  }

  return (
    <section id="about" className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-4xl font-bold text-white mb-6">
              {aboutContent.title || "About Blue Nebula Hosting"}
            </h2>
            <div className="text-lg text-gray-300 mb-6">
              {aboutContent.description ? (
                // Split description into paragraphs if it contains line breaks
                aboutContent.description.split('\n').map((paragraph, index) => (
                  paragraph.trim() && (
                    <p key={index} className={index > 0 ? "mt-4" : ""}>
                      {paragraph.trim()}
                    </p>
                  )
                ))
              ) : (
                <>
                  <p className="mb-4">
                    Blue Nebula Hosting provides fast, reliable, and affordable hosting solutions for individuals and businesses. 
                    Our managed hosting services include shared hosting, VPS, and GameServer hosting with 24/7 support.
                  </p>
                  <p>
                    We pride ourselves on delivering enterprise-grade infrastructure with personal support, ensuring your 
                    websites and applications run smoothly while you focus on growing your business.
                  </p>
                </>
              )}
            </div>
            
            <div className="grid sm:grid-cols-3 gap-6 mb-8">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-400">99.9%</div>
                <div className="text-sm text-gray-300">Uptime Guarantee</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-400">24/7</div>
                <div className="text-sm text-gray-300">Expert Support</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-400">5000+</div>
                <div className="text-sm text-gray-300">Happy Customers</div>
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <a href="https://billing.bluenebulahosting.com" target="_blank" rel="noopener noreferrer" className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-colors text-center">
                Get Started Today
              </a>
              <a href="https://status.bluenebulahosting.com/status/bnh" target="_blank" rel="noopener noreferrer" className="px-6 py-3 border border-green-400 text-green-400 rounded-lg hover:bg-green-400 hover:text-gray-900 transition-colors text-center">
                Check System Status
              </a>
            </div>
          </div>
          
          <div className="relative">
            <img 
              src="https://images.pexels.com/photos/1181354/pexels-photo-1181354.jpeg" 
              alt="Server Infrastructure"
              className="rounded-xl"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-blue-600/20 to-transparent rounded-xl"></div>
          </div>
        </div>
      </div>
    </section>
  );
};

// Contact Section Component
const ContactSection = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      await axios.post(`${API}/contact`, formData);
      alert('Message sent successfully! We\'ll get back to you soon.');
      setFormData({ name: '', email: '', subject: '', message: '' });
    } catch (error) {
      alert('Error sending message. Please try again or contact us directly.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <section id="contact" className="py-20 bg-gray-900/50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-white mb-4">Get in Touch</h2>
          <p className="text-lg text-gray-300 mb-6">
            Have questions? Our expert support team is here to help 24/7.
          </p>
          <div className="flex flex-wrap justify-center gap-4 text-sm">
            <a href="https://billing.bluenebulahosting.com" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 transition-colors">
              Submit Support Ticket
            </a>
            <span className="text-gray-500">•</span>
            <a href="https://status.bluenebulahosting.com/status/bnh" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:text-green-300 transition-colors">
              System Status
            </a>
          </div>
        </div>
        
        <form onSubmit={handleSubmit} className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-8 border border-gray-700">
          <div className="grid md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-gray-300 font-semibold mb-2">Name</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-gray-700 text-white border border-gray-600 rounded-lg focus:border-blue-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-gray-300 font-semibold mb-2">Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-gray-700 text-white border border-gray-600 rounded-lg focus:border-blue-400 focus:outline-none"
              />
            </div>
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-300 font-semibold mb-2">Subject</label>
            <input
              type="text"
              name="subject"
              value={formData.subject}
              onChange={handleChange}
              required
              className="w-full px-4 py-3 bg-gray-700 text-white border border-gray-600 rounded-lg focus:border-blue-400 focus:outline-none"
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-300 font-semibold mb-2">Message</label>
            <textarea
              name="message"
              value={formData.message}
              onChange={handleChange}
              required
              rows={6}
              className="w-full px-4 py-3 bg-gray-700 text-white border border-gray-600 rounded-lg focus:border-blue-400 focus:outline-none"
            />
          </div>
          
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all disabled:opacity-50"
          >
            {isSubmitting ? 'Sending...' : 'Send Message'}
          </button>
        </form>
      </div>
    </section>
  );
};

// Footer Component
const Footer = () => {
  return (
    <footer className="bg-gray-900 border-t border-gray-800 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 flex items-center justify-center">
                <img 
                  src="/logo.png" 
                  alt="Blue Nebula Hosting" 
                  className="w-10 h-10 object-contain"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
                <div className="w-10 h-10 bg-gradient-to-r from-blue-400 to-purple-600 rounded-lg items-center justify-center text-white font-bold text-xl" style={{display: 'none'}}>
                  BN
                </div>
              </div>
              <div className="text-white">
                <h3 className="font-bold text-lg">Blue Nebula Hosting</h3>
              </div>
            </div>
            <p className="text-gray-400">
              Professional hosting solutions with enterprise-grade infrastructure and 24/7 support.
            </p>
          </div>
          
          <div>
            <h4 className="text-white font-semibold mb-4">Services</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#hosting" className="hover:text-blue-400 transition-colors">Shared Hosting</a></li>
              <li><a href="#vps" className="hover:text-blue-400 transition-colors">VPS Hosting</a></li>
              <li><a href="#gameservers" className="hover:text-blue-400 transition-colors">GameServers</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-white font-semibold mb-4">Support</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="https://billing.bluenebulahosting.com" target="_blank" rel="noopener noreferrer" className="hover:text-blue-400 transition-colors">Client Portal</a></li>
              <li><a href="https://panel.bluenebulahosting.com" target="_blank" rel="noopener noreferrer" className="hover:text-blue-400 transition-colors">Game Panel</a></li>
              <li><a href="https://status.bluenebulahosting.com/status/bnh" target="_blank" rel="noopener noreferrer" className="hover:text-blue-400 transition-colors">System Status</a></li>
              <li><a href="#contact" className="hover:text-blue-400 transition-colors">Contact Us</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-white font-semibold mb-4">Company</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#about" className="hover:text-blue-400 transition-colors">About Us</a></li>
              <li><a href="/terms" className="hover:text-blue-400 transition-colors">Terms of Service</a></li>
              <li><a href="/privacy" className="hover:text-blue-400 transition-colors">Privacy Policy</a></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; 2025 Blue Nebula Hosting. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

// Main App Component
const Home = () => {
  const [hostingPlans, setHostingPlans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Add cache-busting to ensure fresh data
        const timestamp = new Date().getTime();
        const plansResponse = await axios.get(`${API}/hosting-plans?_t=${timestamp}`, {
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          }
        });
        setHostingPlans(plansResponse.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 relative overflow-hidden">
      {/* Floating Promo Banner - Outside of all other content */}
      <PromoCodeBanner location="floating" />
      
      {/* Animated Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-blue-900/20 to-purple-900/20"></div>
        
        {/* Starfield Animation */}
        <div className="stars absolute inset-0">
          <div className="star absolute bg-white rounded-full opacity-80 animate-pulse" style={{
            width: '2px', height: '2px', top: '20%', left: '25%',
            animationDelay: '0s', animationDuration: '3s'
          }}></div>
          <div className="star absolute bg-white rounded-full opacity-60 animate-pulse" style={{
            width: '1px', height: '1px', top: '30%', left: '80%',
            animationDelay: '1s', animationDuration: '4s'
          }}></div>
          <div className="star absolute bg-white rounded-full opacity-90 animate-pulse" style={{
            width: '2px', height: '2px', top: '60%', left: '15%',
            animationDelay: '2s', animationDuration: '2s'
          }}></div>
          <div className="star absolute bg-white rounded-full opacity-70 animate-pulse" style={{
            width: '1px', height: '1px', top: '80%', left: '70%',
            animationDelay: '0.5s', animationDuration: '3.5s'
          }}></div>
          <div className="star absolute bg-white rounded-full opacity-85 animate-pulse" style={{
            width: '2px', height: '2px', top: '40%', left: '60%',
            animationDelay: '1.5s', animationDuration: '2.5s'
          }}></div>
          <div className="star absolute bg-white rounded-full opacity-65 animate-pulse" style={{
            width: '1px', height: '1px', top: '10%', left: '40%',
            animationDelay: '2.5s', animationDuration: '4s'
          }}></div>
          <div className="star absolute bg-white rounded-full opacity-75 animate-pulse" style={{
            width: '1px', height: '1px', top: '70%', left: '90%',
            animationDelay: '0.8s', animationDuration: '3s'
          }}></div>
          <div className="star absolute bg-white rounded-full opacity-80 animate-pulse" style={{
            width: '2px', height: '2px', top: '50%', left: '10%',
            animationDelay: '1.8s', animationDuration: '2.8s'
          }}></div>
          <div className="star absolute bg-white rounded-full opacity-70 animate-pulse" style={{
            width: '1px', height: '1px', top: '90%', left: '30%',
            animationDelay: '0.3s', animationDuration: '3.8s'
          }}></div>
          <div className="star absolute bg-white rounded-full opacity-90 animate-pulse" style={{
            width: '2px', height: '2px', top: '15%', left: '75%',
            animationDelay: '2.2s', animationDuration: '2.2s'
          }}></div>
        </div>
        
        {/* Shooting Stars */}
        <div className="shooting-star absolute bg-gradient-to-r from-blue-400 to-transparent h-px opacity-70" style={{
          width: '100px', top: '25%', left: '-100px',
          animation: 'shooting 8s linear infinite',
          animationDelay: '3s'
        }}></div>
        <div className="shooting-star absolute bg-gradient-to-r from-purple-400 to-transparent h-px opacity-50" style={{
          width: '80px', top: '60%', left: '-80px',
          animation: 'shooting 12s linear infinite',
          animationDelay: '6s'
        }}></div>
      </div>

      {/* Content */}
      <div className="relative z-10">
        <Header />
        <HeroSection />
        <FeaturesSection />
        
        {/* Hosting Plans Section */}
        <section id="hosting" className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-white mb-4">Choose Your Hosting Plan</h2>
              <p className="text-lg text-gray-300">
                Professional hosting solutions tailored to your needs
              </p>
            </div>
            
            {/* Pricing Promo Banner */}
            <PromoCodeBanner location="pricing" />
            <HostingPlans 
              plans={hostingPlans} 
              title="SSD Shared Hosting" 
              type="ssd_shared"
              description="Fast SSD-powered shared hosting with premium features"
            />
            <HostingPlans 
              plans={hostingPlans} 
              title="HDD Shared Hosting" 
              type="hdd_shared"
              description="Affordable shared hosting with reliable HDD storage"
            />
          </div>
        </section>
        
        {/* VPS Section */}
        <section id="vps" className="py-20 bg-gray-900/50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-white mb-4">VPS Hosting Solutions</h2>
              <p className="text-lg text-gray-300">
                Scalable virtual private servers with full control and managed support
              </p>
            </div>
            
            <HostingPlans 
              plans={hostingPlans} 
              title="Standard VPS" 
              type="standard_vps"
              description="Reliable VPS hosting with balanced performance and pricing"
            />
            <HostingPlans 
              plans={hostingPlans} 
              title="Performance VPS" 
              type="performance_vps"
              description="High-performance VPS with premium hardware and optimizations"
            />
          </div>
        </section>
        
        {/* GameServers Section */}
        <section id="gameservers" className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-white mb-4">GameServer Hosting</h2>
              <p className="text-lg text-gray-300">
                High-performance game servers with Pterodactyl panel management
              </p>
            </div>
            
            <HostingPlans 
              plans={hostingPlans} 
              title="Standard GameServers" 
              type="standard_gameserver"
              description="Reliable game hosting with standard performance"
            />
            <HostingPlans 
              plans={hostingPlans} 
              title="Performance GameServers" 
              type="performance_gameserver"
              description="Premium game hosting with enhanced performance and priority support"
            />
          </div>
        </section>
        
        <AboutSection />
        <ContactSection />
        <Footer />
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/admin" element={<AdminPanel />} />
          <Route path="/terms" element={<LegalPage type="terms" />} />
          <Route path="/privacy" element={<LegalPage type="privacy" />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
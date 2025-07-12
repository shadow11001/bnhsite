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
const API = `${BACKEND_URL}/api`;

// Header Component
const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="bg-gray-900/95 backdrop-blur-sm fixed w-full z-50 border-b border-blue-500/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-400 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">BN</span>
            </div>
            <div className="text-white">
              <h1 className="font-bold text-xl">Blue Nebula</h1>
              <p className="text-sm text-blue-300">Hosting</p>
            </div>
          </div>
          
          <nav className="hidden md:flex space-x-8">
            <a href="#home" className="text-gray-300 hover:text-blue-400 transition-colors">Home</a>
            <a href="#hosting" className="text-gray-300 hover:text-blue-400 transition-colors">Hosting</a>
            <a href="#vps" className="text-gray-300 hover:text-blue-400 transition-colors">VPS</a>
            <a href="#gameservers" className="text-gray-300 hover:text-blue-400 transition-colors">GameServers</a>
            <a href="#about" className="text-gray-300 hover:text-blue-400 transition-colors">About</a>
            <a href="#contact" className="text-gray-300 hover:text-blue-400 transition-colors">Contact</a>
            <a href="https://status.bluenebulahosting.com/status/bnh" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:text-green-300 transition-colors">Status</a>
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
              <a href="#home" className="text-gray-300 hover:text-blue-400 transition-colors">Home</a>
              <a href="#hosting" className="text-gray-300 hover:text-blue-400 transition-colors">Hosting</a>
              <a href="#vps" className="text-gray-300 hover:text-blue-400 transition-colors">VPS</a>
              <a href="#gameservers" className="text-gray-300 hover:text-blue-400 transition-colors">GameServers</a>
              <a href="#about" className="text-gray-300 hover:text-blue-400 transition-colors">About</a>
              <a href="#contact" className="text-gray-300 hover:text-blue-400 transition-colors">Contact</a>
              <a href="https://status.bluenebulahosting.com/status/bnh" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:text-green-300 transition-colors">Status</a>
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
  return (
    <section id="home" className="relative min-h-screen flex items-center justify-center">
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: 'url(https://images.unsplash.com/photo-1462331940025-496dfbfc7564?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHwyfHxzcGFjZSUyMG5lYnVsYXxlbnwwfHx8fDE3NTIyOTU3NTR8MA&ixlib=rb-4.1.0&q=85)'
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/80 via-purple-900/60 to-black/80"></div>
      </div>
      
      <div className="relative z-10 text-center max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
          Fast, Reliable, and 
          <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent"> Affordable</span>
        </h1>
        <h2 className="text-2xl md:text-3xl text-blue-200 mb-8">
          Hosting Solutions—Starting at <span className="text-blue-400 font-bold">$1/mo</span>
        </h2>
        <p className="text-lg text-gray-300 mb-10 max-w-2xl mx-auto">
          Blue Nebula Hosting provides fast, reliable, and affordable hosting solutions with 24/7 support, 
          99.9% uptime guarantee, and professional managed services for shared hosting, VPS, and GameServers.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a href="https://billing.bluenebulahosting.com" target="_blank" rel="noopener noreferrer" className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all transform hover:scale-105">
            Get Started
          </a>
          <a href="#hosting" className="px-8 py-4 border-2 border-blue-400 text-blue-400 font-semibold rounded-lg hover:bg-blue-400 hover:text-gray-900 transition-all">
            View Plans
          </a>
        </div>
        
        {/* Quick Links */}
        <div className="mt-12 flex flex-wrap justify-center gap-4 text-sm">
          <a href="https://billing.bluenebulahosting.com" target="_blank" rel="noopener noreferrer" className="flex items-center text-gray-300 hover:text-blue-400 transition-colors">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            Client Portal
          </a>
          <a href="https://panel.bluenebulahosting.com" target="_blank" rel="noopener noreferrer" className="flex items-center text-gray-300 hover:text-blue-400 transition-colors">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l7 7-7 7z" />
            </svg>
            Game Panel
          </a>
          <a href="https://status.bluenebulahosting.com/status/bnh" target="_blank" rel="noopener noreferrer" className="flex items-center text-green-400 hover:text-green-300 transition-colors">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            System Status
          </a>
        </div>
      </div>
    </section>
  );
};

// Hosting Plans Component
const HostingPlans = ({ plans, title, type, description }) => {
  const filteredPlans = plans.filter(plan => plan.plan_type === type);
  
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
          <div key={plan.id} className={`relative bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border ${plan.popular ? 'border-blue-500 ring-2 ring-blue-500/50' : 'border-gray-700'} hover:border-blue-400 transition-all`}>
            {plan.popular && (
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <span className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                  Popular
                </span>
              </div>
            )}
            
            <div className="text-center mb-6">
              <h4 className="text-xl font-bold text-white mb-2">{plan.plan_name}</h4>
              <div className="text-3xl font-bold text-blue-400 mb-2">
                ${plan.base_price}
                <span className="text-lg text-gray-400">/mo</span>
              </div>
            </div>
            
            <ul className="space-y-2 mb-8">
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
            
            <a href="https://billing.bluenebulahosting.com" target="_blank" rel="noopener noreferrer" className={`block w-full py-3 rounded-lg font-semibold transition-all text-center ${
              plan.popular 
                ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700' 
                : 'border border-blue-400 text-blue-400 hover:bg-blue-400 hover:text-gray-900'
            }`}>
              Order Now
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};

// Features Section Component
const FeaturesSection = () => {
  const features = [
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

  return (
    <section className="py-20 bg-gray-900/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">Why Choose Blue Nebula?</h2>
          <p className="text-lg text-gray-300 max-w-2xl mx-auto">
            Professional hosting solutions with enterprise-grade infrastructure and 24/7 expert support.
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
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
  return (
    <section id="about" className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-4xl font-bold text-white mb-6">About Blue Nebula Hosting</h2>
            <p className="text-lg text-gray-300 mb-6">
              Blue Nebula Hosting provides fast, reliable, and affordable hosting solutions for individuals and businesses. 
              Our managed hosting services include shared hosting, VPS, and GameServer hosting with 24/7 support.
            </p>
            <p className="text-gray-300 mb-8">
              We pride ourselves on delivering enterprise-grade infrastructure with personal support, ensuring your 
              websites and applications run smoothly while you focus on growing your business.
            </p>
            
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
              <div className="w-10 h-10 bg-gradient-to-r from-blue-400 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">BN</span>
              </div>
              <div className="text-white">
                <h3 className="font-bold text-lg">Blue Nebula</h3>
                <p className="text-sm text-blue-300">Hosting</p>
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
        const plansResponse = await axios.get(`${API}/hosting-plans`);
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
    <div className="min-h-screen bg-gray-900">
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
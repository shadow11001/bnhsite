# Blue Nebula Hosting - Content Management Guide

## 🚀 How to Make Changes to Your Website

### **Method 1: Admin Panel (Recommended)**

Your website includes a built-in admin panel for easy content management.

#### **Accessing the Admin Panel:**
1. **Navigate to**: `https://your-website.com/admin`
2. **Features Available**:
   - ✅ Edit hosting plans (pricing, features, specifications)
   - ✅ Update company information
   - ✅ Manage plan popularity (popular badges)
   - ✅ Modify descriptions and features

#### **Managing Hosting Plans:**
1. **Click "Hosting Plans" tab**
2. **Select the plan category** (SSD Shared, VPS, GameServers, etc.)
3. **Click "Edit Plan"** on any plan card
4. **Modify**:
   - Plan name
   - Pricing
   - CPU/Memory/Disk specifications
   - Features list
   - Popular status
5. **Save changes**

#### **Updating Company Information:**
1. **Click "Company Info" tab**
2. **Edit**:
   - Company name and tagline
   - About description
   - Features list
3. **Save changes**

---

### **Method 2: Direct API Updates**

For advanced users, you can update content via API calls:

#### **Update Hosting Plan:**
```bash
curl -X PUT "https://your-backend-url/api/hosting-plans/{plan_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_name": "New Plan Name",
    "base_price": 25.00,
    "features": ["Feature 1", "Feature 2"],
    "popular": true
  }'
```

#### **Update Company Info:**
```bash
curl -X PUT "https://your-backend-url/api/company-info" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Blue Nebula Hosting",
    "tagline": "Your New Tagline",
    "description": "Updated description"
  }'
```

---

### **Method 3: Database Direct Access**

If you need to make bulk changes or have database access:

#### **MongoDB Collections:**
- **hosting_plans**: All hosting plan data
- **company_info**: Company information
- **contact_submissions**: Contact form submissions
- **website_content**: Custom content sections

#### **Example MongoDB Updates:**
```javascript
// Update a specific plan
db.hosting_plans.updateOne(
  {"plan_name": "Topaz"},
  {"$set": {"base_price": 12.00, "popular": true}}
)

// Update company description
db.company_info.updateOne(
  {},
  {"$set": {"description": "New company description"}}
)
```

---

## 🎨 Customizing Design and Styling

### **Changing Colors/Theme:**
1. **Edit**: `/app/frontend/src/App.css`
2. **Modify CSS variables**:
   ```css
   :root {
     --primary-blue: #3b82f6;     /* Main blue color */
     --primary-purple: #8b5cf6;   /* Main purple color */
     --accent-green: #10b981;     /* Success color */
   }
   ```

### **Updating Images:**
1. **Hero Background**: Replace the image URL in `/app/frontend/src/App.js`
2. **Feature Images**: Update image URLs in the FeaturesSection component
3. **About Image**: Change the image in AboutSection component

### **Adding New Sections:**
1. **Create new component** in `/app/frontend/src/App.js`
2. **Add to the main Home component**
3. **Style using Tailwind CSS classes**

---

## 📊 Adding New Hosting Plans

### **Using Admin Panel:**
Currently, the admin panel allows editing existing plans. To add new plans:

### **Using API:**
```bash
curl -X POST "https://your-backend-url/api/hosting-plans" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_type": "ssd_shared",
    "plan_name": "Platinum",
    "base_price": 25.00,
    "cpu_cores": null,
    "memory_gb": null,
    "disk_gb": 200,
    "disk_type": "SSD",
    "features": ["Unlimited Websites", "200 GB SSD", "Free SSL"],
    "popular": false,
    "markup_percentage": 0
  }'
```

### **Plan Types Available:**
- `ssd_shared` - SSD Shared Hosting
- `hdd_shared` - HDD Shared Hosting  
- `standard_vps` - Standard VPS
- `performance_vps` - Performance VPS
- `standard_gameserver` - Standard GameServers
- `performance_gameserver` - Performance GameServers

---

## 🔗 Service Integration Management

### **Your Current Integrations:**
- **Billing System**: billing.bluenebulahosting.com (Blesta)
- **Game Panel**: panel.bluenebulahosting.com (Pterodactyl)
- **Status Page**: status.bluenebulahosting.com/status/bnh (Uptime Kuma)

### **Updating Service URLs:**
If you change any service URLs, update them in `/app/frontend/src/App.js`:

```javascript
// Find and replace these URLs:
"https://billing.bluenebulahosting.com"
"https://panel.bluenebulahosting.com"  
"https://status.bluenebulahosting.com/status/bnh"
```

### **Adding New Services:**
1. **Add links in Header component**
2. **Update Footer component**
3. **Add to Hero section quick links**

---

## 🎯 Blesta Theme Integration

### **Installing the Matching Blesta Theme:**

1. **Upload theme files** to your Blesta installation:
   ```
   /blesta/views/themes/blue_nebula/
   ├── css/
   │   └── blue_nebula_theme.css
   ```

2. **Or add custom CSS** in Blesta Admin:
   - Go to Settings → System → General → Interface
   - Add the CSS from `/app/blesta-theme/blue_nebula_theme.css`

### **Theme Features:**
- ✅ Matches your website's space theme perfectly
- ✅ Same color scheme and typography
- ✅ Professional dark design
- ✅ Responsive mobile design
- ✅ Seamless user experience transition

---

## 🚀 Deployment and Updates

### **Making Changes Live:**

#### **Frontend Changes:**
1. **Edit files** in `/app/frontend/src/`
2. **Restart frontend service**: `sudo supervisorctl restart frontend`
3. **Changes appear immediately**

#### **Backend Changes:**
1. **Edit files** in `/app/backend/`
2. **Restart backend service**: `sudo supervisorctl restart backend`
3. **Database changes persist automatically**

#### **Full Restart:**
```bash
sudo supervisorctl restart all
```

### **Checking Services:**
```bash
sudo supervisorctl status
```

---

## 📞 Content Update Examples

### **Updating Pricing:**
```javascript
// Example: Change Topaz plan from $10 to $12
// In Admin Panel or via API
{
  "base_price": 12.00
}
```

### **Adding Features to a Plan:**
```javascript
// Example: Add new feature to Diamond plan
{
  "features": [
    "Unlimited Websites",
    "100 GB SSD Storage", 
    "Unlimited Bandwidth",
    "Free SSL",
    "Daily Backups",
    "Priority Support",
    "Free Migration"  // New feature
  ]
}
```

### **Changing Popular Plans:**
```javascript
// Make Venus the popular VPS plan instead of current
{
  "popular": true
}
```

### **Updating Company Description:**
```javascript
{
  "description": "Blue Nebula Hosting provides cutting-edge hosting solutions with 99.9% uptime, enterprise-grade security, and 24/7 expert support for businesses of all sizes."
}
```

---

## 🔧 Troubleshooting

### **Common Issues:**

#### **Changes Not Appearing:**
1. **Clear browser cache**
2. **Restart services**: `sudo supervisorctl restart all`
3. **Check service status**: `sudo supervisorctl status`

#### **Admin Panel Not Loading:**
1. **Check backend is running**: `sudo supervisorctl status backend`
2. **Verify API endpoints**: `curl http://localhost:8001/api/`
3. **Check browser console** for errors

#### **Database Connection Issues:**
1. **Check MongoDB is running**
2. **Verify connection string** in `/app/backend/.env`
3. **Restart backend service**

### **Getting Help:**
- Check service logs: `tail -f /var/log/supervisor/backend.*.log`
- Verify API responses: `curl http://localhost:8001/api/hosting-plans`
- Test admin panel: Navigate to `/admin` on your website

---

## 📈 Performance Optimization

### **Recommended Monitoring:**
- **Status Page**: Monitor all services via Uptime Kuma
- **Server Resources**: Monitor CPU, memory, and disk usage
- **Database Performance**: Monitor MongoDB query performance
- **Website Speed**: Use tools like GTmetrix or PageSpeed Insights

### **Regular Maintenance:**
- **Update plans and pricing** as needed
- **Keep content fresh** with new features and offers
- **Monitor competitor pricing** and adjust accordingly
- **Update company information** as business grows

---

**Blue Nebula Hosting - Professional hosting solutions with easy content management**
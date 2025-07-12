# Blue Nebula Hosting - Blesta Theme

This theme provides seamless integration between your Blue Nebula Hosting website and Blesta billing system.

## Installation Instructions

### Method 1: Direct Upload (Recommended)

1. **Access your Blesta installation directory** on your server
2. **Navigate to the themes folder**: `/path/to/blesta/views/themes/`
3. **Create a new folder** called `blue_nebula`
4. **Upload the CSS file**: Copy `blue_nebula_theme.css` to `/blesta/views/themes/blue_nebula/css/`
5. **Create the theme structure**:
   ```
   /blesta/views/themes/blue_nebula/
   ├── css/
   │   └── blue_nebula_theme.css
   ├── images/
   └── js/
   ```

### Method 2: Custom CSS Integration

If you prefer to add custom CSS without creating a full theme:

1. **Login to Blesta Admin Panel**
2. **Go to Settings → System → General → Interface**
3. **Add Custom CSS** in the "Custom CSS" field
4. **Copy and paste** the contents of `blue_nebula_theme.css`
5. **Save Changes**

## Theme Features

### ✅ **Visual Consistency**
- Matches your Blue Nebula website's space theme
- Same color scheme (blues, purples, gradients)
- Consistent typography and spacing
- Professional dark theme with nebula gradient backgrounds

### ✅ **Responsive Design**
- Works perfectly on desktop, tablet, and mobile
- Mobile-friendly navigation and forms
- Optimized for all screen sizes

### ✅ **Enhanced User Experience**
- Smooth transitions and hover effects
- Modern card-based layouts
- Improved button and form styling
- Better visual hierarchy

### ✅ **Professional Appearance**
- Clean, modern interface
- Matches enterprise hosting company standards
- Seamless transition from main website to billing portal

## Customization

### Color Variables
You can easily customize colors by modifying the CSS variables at the top of the file:

```css
:root {
    --primary-blue: #3b82f6;        /* Main blue color */
    --primary-purple: #8b5cf6;      /* Main purple color */
    --secondary-blue: #60a5fa;      /* Lighter blue */
    --accent-green: #10b981;        /* Success/active color */
    --dark-bg: #0f0f10;             /* Dark background */
    --card-bg: #1f2937;             /* Card background */
    --border-color: #374151;        /* Border color */
    --text-primary: #ffffff;        /* Primary text */
    --text-secondary: #d1d5db;      /* Secondary text */
    --text-muted: #9ca3af;          /* Muted text */
}
```

### Adding Your Logo
To add your Blue Nebula logo to the Blesta theme:

1. **Upload your logo** to `/blesta/views/themes/blue_nebula/images/logo.png`
2. **Modify the logo CSS** in the theme file:
   ```css
   .logo img, .brand img, .navbar-brand img {
       content: url('../images/logo.png') !important;
       width: 40px !important;
       height: 40px !important;
   }
   ```

## Integration with Your Services

### Automatic Links
The theme is designed to work with your existing service links:
- **Billing Portal**: billing.bluenebulahosting.com
- **Game Panel**: panel.bluenebulahosting.com  
- **Status Page**: status.bluenebulahosting.com/status/bnh

### Service Integration
- Hosting plans will automatically link to your Blesta order forms
- Client area provides easy access to services
- Game server customers can access Pterodactyl panel
- Status page integration for service monitoring

## Browser Compatibility

✅ **Supported Browsers:**
- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### Common Issues:

**Theme not applying:**
- Clear your browser cache
- Check file permissions on the theme directory
- Ensure CSS file is in correct location

**Colors not matching:**
- Verify CSS variables are correctly set
- Check for any conflicting custom CSS
- Ensure you're using the latest version

**Mobile display issues:**
- Clear mobile browser cache
- Check responsive CSS is not being overridden
- Test in different mobile browsers

## Support

For theme-related issues:
1. Check the Blesta documentation for theme installation
2. Verify file permissions and directory structure
3. Test in different browsers
4. Contact Blue Nebula support if integration issues persist

## Updates

This theme will be updated to match any changes to your main website design. Keep the theme files updated for the best visual consistency.

---

**Blue Nebula Hosting - Professional hosting solutions with seamless billing integration**
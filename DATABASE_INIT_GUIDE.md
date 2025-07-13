# Blue Nebula Hosting - Database Initialization Guide

## 🎯 Quick Database Setup

Your MongoDB database is empty and needs to be populated with hosting plans and content.

### 🚀 Method 1: Automated Script (Recommended)

Run the initialization script:

```bash
./init_db.sh
```

This will:
- ✅ Copy the initialization script to your backend container
- ✅ Run the database population script
- ✅ Add all 36 hosting plans with correct names
- ✅ Initialize website content, navigation, company info
- ✅ Create sample promo codes
- ✅ Set up Terms of Service and Privacy Policy

### 🚀 Method 2: Manual Docker Execution

If the script doesn't work, run manually:

```bash
# Copy the script to the container
docker cp init_database.py blue-nebula-backend:/app/

# Run the initialization inside the container
docker exec blue-nebula-backend python3 init_database.py

# Clean up
docker exec blue-nebula-backend rm init_database.py
```

### 🚀 Method 3: Direct Python Execution

If you have Python and the required packages locally:

```bash
# Set environment variables (adjust as needed)
export MONGO_URL="mongodb://admin:your_password@localhost:27017/blue_nebula_hosting?authSource=admin"
export DB_NAME="blue_nebula_hosting"

# Run the script
python3 init_database.py
```

### ✅ What Gets Created

After running the initialization:

**📊 Hosting Plans (36 total):**
- **SSD Shared (3):** Opal ($1), Topaz ($10), Diamond ($15)
- **HDD Shared (3):** Quartz ($1), Granite ($50), Marble ($100)
- **Standard VPS (6):** Meteor, Asteroid, Planet, Star, Cluster, Galaxy
- **Performance VPS (9):** Probe, Rover, Lander, Satellite, Station, Outpost, Base, Colony, Spaceport
- **Standard GameServers (6):** Stardust, Flare, Comet, Nova, White Dwarf, Red Giant
- **Performance GameServers (9):** Supernova, Neutron Star, Pulsar, Magnetar, Black Hole, Quasar, Nebula, Star Cluster, Cosmos

**🌐 Website Content:**
- Hero section content
- About page content
- Features section
- Navigation menu

**🏢 Company Information:**
- Company details
- Contact information
- Social media links

**⚖️ Legal Content:**
- Terms of Service
- Privacy Policy

**🎁 Sample Promo Codes:**
- WELCOME50 (50% off, floating banner)
- SAVE20 (20% off VPS, hero section)

### 🔍 Verification

After initialization, verify everything worked:

```bash
# Check if plans are loaded
curl https://bluenebulahosting.com/api/hosting-plans

# Check system status
curl https://bluenebulahosting.com/api/system-status

# Visit your website
open https://bluenebulahosting.com
```

### 🆘 Troubleshooting

**If initialization fails:**

1. **Check container status:**
   ```bash
   docker-compose ps
   ```

2. **Check backend logs:**
   ```bash
   docker-compose logs blue-nebula-backend
   ```

3. **Check MongoDB connection:**
   ```bash
   docker exec blue-nebula-backend python3 -c "
   import os
   from motor.motor_asyncio import AsyncIOMotorClient
   import asyncio
   
   async def test():
       client = AsyncIOMotorClient(os.environ['MONGO_URL'])
       try:
           await client.admin.command('ping')
           print('✅ MongoDB connection successful')
       except Exception as e:
           print(f'❌ MongoDB connection failed: {e}')
       finally:
           client.close()
   
   asyncio.run(test())
   "
   ```

4. **Reset database (if needed):**
   ```bash
   # This will delete ALL data and start fresh
   docker exec blue-nebula-mongodb mongosh --eval "
   use blue_nebula_hosting;
   db.dropDatabase();
   "
   
   # Then run initialization again
   ./init_db.sh
   ```

### 📞 Support

If you continue having issues:
1. Check that all environment variables are set correctly
2. Ensure MongoDB authentication credentials match your docker-compose.yml
3. Verify the MONGO_URL format includes authentication parameters
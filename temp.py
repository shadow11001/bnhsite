# COMMENTED OUT - Using database initialization script instead
# @api_router.post("/init-data")
# async def initialize_data():
#     """Initialize hosting plans data with exact names from pricing table"""
#     try:
#         # Clear existing data
#         await db.hosting_plans.delete_many({})
#         
#         # SSD Shared Hosting Plans (correct names from user)
#         ssd_shared_plans = [
# MongoDB Atlas Setup Guide

## Your MongoDB Connection String

You have:
```
mongodb+srv://dipendrayadav299:<db_password>@atlascluster.yy7vz.mongodb.net/?appName=AtlasCluster
```

## Step 1: Get Your Password

Replace `<db_password>` with your actual MongoDB Atlas password.

**Important**: If your password contains special characters, you MUST URL-encode them:
- `@` → `%40`
- `:` → `%3A`
- `/` → `%2F`
- `#` → `%23`
- `&` → `%26`
- `=` → `%3D`
- `+` → `%2B`

**Example**: If your password is `pass@123:word`, encode it as:
```
pass%40123%3Aword
```

## Step 2: Add Database Name

Add `/portfolio_db` before the `?` to specify your database name:

```
mongodb+srv://dipendrayadav299:YOUR_PASSWORD@atlascluster.yy7vz.mongodb.net/portfolio_db?retryWrites=true&w=majority
```

## Step 3: Configure in .env File

Create or edit `backend/.env`:

```env
# MongoDB Atlas Connection
MONGO_URI=mongodb+srv://dipendrayadav299:YOUR_ACTUAL_PASSWORD@atlascluster.yy7vz.mongodb.net/portfolio_db?retryWrites=true&w=majority

# Flask Security (generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your-generated-secret-key-here

# Frontend URL
FRONTEND_URL=http://localhost:5173

# Environment (set to 'development' for debug mode during development)
FLASK_ENV=development
```

## Step 4: Generate SECRET_KEY

Run this command to generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it as the value for `SECRET_KEY` in your `.env` file.

## Step 5: Whitelist IP Address in MongoDB Atlas

1. Go to https://cloud.mongodb.com/
2. Select your project
3. Click "Network Access" in the left sidebar
4. Click "Add IP Address"
5. For development: Add your current IP or use `0.0.0.0/0` (allows access from anywhere - less secure)
6. For production: Add only your server's IP address

## Step 6: Test Connection

```bash
cd backend
python -c "from config import Config; Config.validate(); print('✓ Configuration valid!')"
```

If successful, you'll see: `✓ Configuration valid!`

## Step 7: Start the Application

```bash
# From backend folder
python app.py
```

You should see:
```
db connected
 * Running on http://0.0.0.0:5000
```

## Common Issues

### Issue: "MONGO_URI environment variable must be set"
**Solution**: Make sure the `.env` file exists in the `backend/` folder and contains `MONGO_URI=...`

### Issue: "Authentication failed"
**Solution**: 
- Double-check your password
- Make sure special characters are URL-encoded
- Verify the username is correct: `dipendrayadav299`

### Issue: "Could not resolve host"
**Solution**: 
- Check your internet connection
- Verify the cluster address: `atlascluster.yy7vz.mongodb.net`

### Issue: "Database not found"
**Solution**: The database `portfolio_db` will be created automatically when you first run the application.

## Security Notes

1. **Never commit `.env` to git** - It contains sensitive credentials
2. **Use strong passwords** - Both for MongoDB and SECRET_KEY
3. **Restrict IP whitelist** in production - Don't use `0.0.0.0/0` in production
4. **Rotate credentials regularly** - Change passwords periodically

## Production Deployment (Render)

When deploying to Render:
1. Go to your service settings
2. Navigate to "Environment" tab
3. Add these environment variables:
   - `MONGO_URI` = your full MongoDB connection string
   - `SECRET_KEY` = a secure random string
   - `FRONTEND_URL` = your Vercel frontend URL (e.g., `https://your-app.vercel.app`)
   - `FLASK_ENV` = `production`

## Example .env File (Complete)

```env
# MongoDB
MONGO_URI=mongodb+srv://dipendrayadav299:MyP@ssw0rd%40123@atlascluster.yy7vz.mongodb.net/portfolio_db?retryWrites=true&w=majority

# Security
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6

# CORS
FRONTEND_URL=http://localhost:5173

# Environment
FLASK_ENV=development
```

## Need Help?

If you encounter issues:
1. Check MongoDB Atlas dashboard - is your cluster running?
2. Verify IP whitelist includes your current IP
3. Double-check username/password in MongoDB Atlas
4. Ensure database user has read/write permissions
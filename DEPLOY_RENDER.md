# Deploy LinkedIn Scheduler to Render

This guide will help you deploy the LinkedIn Scheduler app to Render.com.

## Prerequisites

1. A Render account (sign up at [render.com](https://render.com))
2. Your LinkedIn app credentials
3. This GitHub repository

## Step 1: Prepare Your LinkedIn App

1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Select your existing app or create a new one
3. Update the redirect URI to: `https://your-app-name.onrender.com/auth/linkedin/callback`
   (Replace `your-app-name` with your actual Render app name)
4. Make sure your app has these scopes:
   - `r_liteprofile` - Read basic profile info
   - `w_member_social` - Post on behalf of user

## Step 2: Deploy to Render

### Option A: Using GitHub (Recommended)

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/linkedin-scheduler.git
   git push -u origin main
   ```

2. **Create Web Service on Render:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `linkedin-scheduler` (or your preferred name)
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
     - **Plan**: Free (or paid for better performance)

3. **Set Environment Variables:**
   In the Render dashboard, go to Environment tab and add:
   ```
   FLASK_ENV=production
   LINKEDIN_CLIENT_ID=86sf2mwklf3bar
   LINKEDIN_CLIENT_SECRET=WPL_AP1.9r9ObArF82SufuIY.RAvHkg==
   SECRET_KEY=zRZ3r1EwP5uhHYKXlTwNZbu9UikLkjR4ahH15fG8VZw
   LINKEDIN_REDIRECT_URI=https://your-app-name.onrender.com/auth/linkedin/callback
   ```
   
   **Important**: Replace `your-app-name` with your actual Render service name!

### Option B: Using render.yaml (Infrastructure as Code)

1. **Deploy with render.yaml:**
   - The `render.yaml` file is already configured
   - Push to GitHub and connect repository
   - Render will automatically detect and deploy using the yaml config

2. **Set Environment Variables:**
   You'll still need to manually set the environment variables in the Render dashboard.

## Step 3: Set Up Database (Optional)

For production use, you might want PostgreSQL instead of SQLite:

1. **Create PostgreSQL Database:**
   - In Render dashboard: "New +" → "PostgreSQL"
   - Name: `linkedin-scheduler-db`
   - Plan: Free

2. **Connect Database:**
   - Copy the database connection string
   - Add it as `DATABASE_URL` environment variable in your web service

## Step 4: Update LinkedIn App Redirect URI

1. Go back to LinkedIn Developer Portal
2. Update your app's redirect URI to: `https://your-actual-render-url.onrender.com/auth/linkedin/callback`
3. Save changes

## Step 5: Test Your Deployment

1. Visit your Render app URL: `https://your-app-name.onrender.com`
2. Click "Connect LinkedIn Account"
3. Complete OAuth flow
4. Test creating and scheduling posts

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_ENV` | Environment mode | `production` |
| `LINKEDIN_CLIENT_ID` | LinkedIn app client ID | `86sf2mwklf3bar` |
| `LINKEDIN_CLIENT_SECRET` | LinkedIn app client secret | `WPL_AP1.9r9ObArF82SufuIY.RAvHkg==` |
| `SECRET_KEY` | Flask session secret | `your-generated-secret-key` |
| `LINKEDIN_REDIRECT_URI` | OAuth redirect URL | `https://your-app.onrender.com/auth/linkedin/callback` |
| `DATABASE_URL` | Database connection string | `postgresql://...` (optional) |

## Troubleshooting

### Common Issues:

1. **OAuth Error - Invalid Redirect URI:**
   - Make sure the redirect URI in LinkedIn app matches exactly
   - Include `https://` and the correct domain

2. **App Won't Start:**
   - Check build logs in Render dashboard
   - Ensure all environment variables are set
   - Verify requirements.txt has all dependencies

3. **Database Errors:**
   - For SQLite: It should work automatically
   - For PostgreSQL: Ensure DATABASE_URL is set correctly

4. **LinkedIn Scope Errors:**
   - Ensure your LinkedIn app has the correct scopes
   - Only use `r_liteprofile` and `w_member_social`

### Viewing Logs:

- Go to Render dashboard → Your service → Logs
- Check for startup errors or runtime issues

## Production Considerations

1. **Database**: Consider upgrading to PostgreSQL for better reliability
2. **Monitoring**: Set up monitoring and alerts in Render
3. **Backups**: Regular database backups (if using PostgreSQL)
4. **SSL**: Render provides SSL certificates automatically
5. **Custom Domain**: You can add a custom domain in Render settings

## Scaling

- **Free Plan**: Limited resources, may sleep after inactivity
- **Paid Plans**: Better performance, no sleeping, more resources
- **Workers**: Adjust gunicorn workers in Procfile based on your plan

## Security

- Never commit sensitive data to GitHub
- Use environment variables for all secrets
- Regularly rotate your SECRET_KEY
- Monitor LinkedIn API usage

---

Your LinkedIn Scheduler should now be live at `https://your-app-name.onrender.com`! 🎉

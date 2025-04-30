# Secure Submission System - Deployment Guide

This guide will help you deploy the Secure Submission System on a production server.

## Prerequisites

Before deploying, make sure you have the following:

- A hosting provider that supports Python web applications (Heroku, AWS, DigitalOcean, etc.)
- A PostgreSQL database instance
- Domain name (optional but recommended)
- SSL certificate (for HTTPS - highly recommended for security)

## Environment Variables

Set up the following environment variables on your hosting platform:

- `DATABASE_URL`: PostgreSQL connection string in the format `postgresql://username:password@host:port/database`
- `SESSION_SECRET`: A strong random string used for securing sessions (generate using a secure method)

## Deployment Steps

### Option 1: Deploying on Heroku

1. Create a Heroku account and install the Heroku CLI
2. Create a new Heroku app: `heroku create your-app-name`
3. Add the PostgreSQL add-on: `heroku addons:create heroku-postgresql:hobby-dev`
4. Set the session secret: `heroku config:set SESSION_SECRET=your_secure_random_string`
5. Push the code to Heroku: `git push heroku main`
6. Create the database tables: `heroku run python`
   ```python
   from app import app, db
   with app.app_context():
       db.create_all()
   ```
7. Open the app: `heroku open`

### Option 2: Deploying on AWS, DigitalOcean, or Other VPS

1. Set up a server with Python 3.11 or later
2. Clone the repository to your server
3. Install dependencies: `pip install -r requirements.txt`
4. Set up environment variables in your server configuration or a `.env` file
5. Set up Nginx or Apache as a reverse proxy to your Gunicorn server
6. Create and configure a systemd service file to run the application
7. Start the service: `sudo systemctl start your-app.service`
8. Enable the service to start on boot: `sudo systemctl enable your-app.service`

## Nginx Configuration Example

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/privatekey.key;
    
    # SSL configuration (recommended settings)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH';
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Systemd Service File Example

Create a file at `/etc/systemd/system/your-app.service`:

```ini
[Unit]
Description=Secure Submission System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
Environment="PATH=/path/to/your/venv/bin"
Environment="DATABASE_URL=postgresql://username:password@host:port/database"
Environment="SESSION_SECRET=your_secure_random_string"
ExecStart=/path/to/your/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 main:app

[Install]
WantedBy=multi-user.target
```

## Setting Up HTTPS

For security reasons, HTTPS is strongly recommended:

1. Obtain an SSL certificate (Let's Encrypt provides free certificates)
2. Configure your web server with the certificate
3. Ensure all traffic is redirected from HTTP to HTTPS

## Initial Setup After Deployment

1. Access your application URL
2. You will be redirected to the setup page
3. Create the initial admin user
4. Log in with the admin credentials
5. Start using the system to create users and manage submissions

## Database Backups

Set up regular database backups to prevent data loss:

1. For PostgreSQL, use `pg_dump`: `pg_dump -U username dbname > backup.sql`
2. Schedule regular backups using a cron job
3. Store backups in a secure, off-site location

## Security Considerations

1. Use strong, unique passwords for all accounts
2. Keep the server and application updated with security patches
3. Consider implementing IP restrictions for the admin interface
4. Regularly audit user accounts and permissions
5. Set up monitoring and alerting for unusual activity

## Troubleshooting

- Check application logs for errors
- Verify all environment variables are set correctly
- Ensure the database is accessible and credentials are correct
- Check file permissions for uploaded content directories
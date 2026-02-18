require('dotenv').config();
const express = require('express');
const path = require('path');
const fs = require('fs');
const nodemailer = require('nodemailer');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware to parse form data and JSON
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Debug: log SMTP config (remove after testing)
console.log('SMTP Config:', {
  host: process.env.SMTP_HOST,
  user: process.env.SMTP_USER,
  passLength: process.env.SMTP_PASS?.length
});

// Create nodemailer transporter
const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: parseInt(process.env.SMTP_PORT) || 587,
  secure: process.env.SMTP_SECURE === 'true',
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS,
  },
});

// Contact form endpoint
app.post('/api/contact', async (req, res) => {
  try {
    const { firstName, lastName, phone, email, message } = req.body;
    console.log('req.body: ', req.body);

    // Validate required fields
    if (!firstName || !lastName || !phone) {
      return res.status(400).json({
        success: false,
        message: 'Please fill in all required fields (First Name, Last Name, Phone)'
      });
    }

    // Create nicely formatted email HTML
    const emailHtml = `
      <!DOCTYPE html>
      <html>
      <head>
        <style>
          body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
          .container { max-width: 600px; margin: 0 auto; padding: 20px; }
          .header { background-color: #1a365d; color: white; padding: 20px; text-align: center; }
          .content { background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }
          .field { margin-bottom: 15px; }
          .label { font-weight: bold; color: #1a365d; }
          .value { margin-top: 5px; }
          .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>New Contact Form Submission</h1>
          </div>
          <div class="content">
            <div class="field">
              <div class="label">Name:</div>
              <div class="value">${firstName} ${lastName}</div>
            </div>
            <div class="field">
              <div class="label">Phone:</div>
              <div class="value">${phone}</div>
            </div>
            <div class="field">
              <div class="label">Email:</div>
              <div class="value">${email || 'Not provided'}</div>
            </div>
            <div class="field">
              <div class="label">Message:</div>
              <div class="value">${message || 'No message provided'}</div>
            </div>
          </div>
          <div class="footer">
            This message was sent from the Dutton Cavanaugh website contact form.
          </div>
        </div>
      </body>
      </html>
    `;

    // Plain text version
    const emailText = `
New Contact Form Submission
============================

Name: ${firstName} ${lastName}
Phone: ${phone}
Email: ${email || 'Not provided'}
Message: ${message || 'No message provided'}

---
This message was sent from the Dutton Cavanaugh website contact form.
    `;

    // Send email
    await transporter.sendMail({
      from: process.env.CONTACT_EMAIL_FROM,
      to: process.env.CONTACT_EMAIL_TO,
      subject: `New Contact Form Submission from ${firstName} ${lastName}`,
      text: emailText,
      html: emailHtml,
    });

    res.json({ success: true, message: 'Thank you! Your message has been sent successfully.' });
  } catch (error) {
    console.error('Error sending email:', error);
    res.status(500).json({
      success: false,
      message: 'Sorry, there was an error sending your message. Please try again later.'
    });
  }
});

app.use(express.static(path.join(__dirname, 'public')));

// Explicit route mappings for service pages
const routeMap = {
  '/griffin/bookkeeping': 'griffin-bookkeeping.html',
  '/griffin/business-services': 'griffin-business-services.html',
  '/griffin/tax-planning': 'griffin-tax-planning.html',
  '/griffin/taxes': 'griffin-taxes.html',
  '/griffin_accounting/about': 'griffin_accounting-about.html'
};

// Handle mapped routes
Object.keys(routeMap).forEach(route => {
  app.get(route, (req, res) => {
    res.sendFile(path.join(__dirname, 'public', routeMap[route]));
  });
});

// Fallback for other routes
app.use((req, res) => {
  const filePath = path.join(__dirname, 'public', req.path);

  if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    res.sendFile(filePath);
  } else if (fs.existsSync(filePath + '.html')) {
    res.sendFile(filePath + '.html');
  } else {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
  }
});

app.listen(PORT, () => {
  console.log(`\n🚀 Server is running!`);
  console.log(`📍 Local: http://localhost:${PORT}`);
  console.log(`📁 Serving files from: ${path.join(__dirname, 'public')}\n`);
});

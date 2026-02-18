import express from "express";
import type { Request, Response } from "express";
import serverless from "serverless-http";
import nodemailer from "nodemailer";

const api = express();

// Middleware to parse form data and JSON
api.use(express.urlencoded({ extended: true }));
api.use(express.json());

const router = Router();

router.get("/hello", (req: Request, res: Response) => res.send("Hello World!"));

// Contact form endpoint
router.post("/contact", async (req: Request, res: Response) => {
  try {
    const { firstName, lastName, phone, email, message } = req.body;

    // Validate required fields
    if (!firstName || !lastName || !phone) {
      return res.status(400).json({
        success: false,
        message: 'Please fill in all required fields (First Name, Last Name, Phone)'
      });
    }

    // Create nodemailer transporter
    const transporter = nodemailer.createTransport({
      host: process.env.SMTP_HOST,
      port: parseInt(process.env.SMTP_PORT || '587'),
      secure: process.env.SMTP_SECURE === 'true',
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS,
      },
    });

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

api.use("/api/", router);

export const handler = serverless(api);

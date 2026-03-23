# BDI Assessment App — Deployment Guide

A professional, confidential Beck Depression Inventory app built with Streamlit + Groq AI.

---

## What It Does

| Who | Experience |
|-----|-----------|
| **Client** | Fills out 21 BDI questions → clicks Submit → sees "Thank you" message only |
| **You (therapist)** | Receive a full PDF clinical report by email instantly |
| **You (admin view)** | Log in at `/?page=admin` with your password → browse & download all reports |

---

## File Structure

```
your-repo/
├── app.py                  ← Main Streamlit app
├── questions.py            ← All 21 BDI questions & answer options
├── scoring.py              ← Score calculation & severity classification
├── report_generator.py     ← Groq API call → AI clinical report
├── pdf_creator.py          ← Converts report to professional PDF
├── email_sender.py         ← Sends PDF via Gmail SMTP
├── requirements.txt        ← Python dependencies
└── .streamlit/
    └── secrets.toml        ← API keys (DO NOT push to GitHub)
```

---

## Setup Steps

### 1. GitHub — Add `.gitignore`

Create a `.gitignore` file with:
```
.streamlit/secrets.toml
reports/
__pycache__/
*.pyc
```

Push all other files to your GitHub repo.

### 2. Gmail — Create an App Password

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Security → 2-Step Verification (must be enabled)
3. App Passwords → Create a new one called "BDI App"
4. Copy the 16-character password

### 3. Streamlit Cloud — Add Secrets

In your Streamlit Cloud dashboard:
- Open your app → **Settings** → **Secrets**
- Paste the following (fill in your real values):

```toml
GROQ_API_KEY       = "gsk_..."
GMAIL_ADDRESS      = "you@gmail.com"
GMAIL_APP_PASSWORD = "xxxx xxxx xxxx xxxx"
THERAPIST_EMAIL    = "you@gmail.com"
ADMIN_PASSWORD     = "your_secure_password"
```

### 4. Deploy

Connect your GitHub repo to Streamlit Cloud and deploy.  
Main file: `app.py`

---

## Accessing the Admin Portal

Go to your app URL with `?page=admin` appended:

```
https://your-app.streamlit.app/?page=admin
```

Enter your `ADMIN_PASSWORD` to log in and download PDF reports.

---

## BDI Scoring Reference

| Score | Classification |
|-------|---------------|
| 1–10  | Normal / Minimal |
| 11–16 | Mild Mood Disturbance |
| 17–20 | Borderline Clinical Depression |
| 21–30 | Moderate Depression |
| 31–40 | Severe Depression |
| 40+   | Extreme Depression |

---

## PDF Report Contents

Each generated report includes:
- Client name, score, severity (colour-coded)
- Full 21-item response table (flagged items in red)
- AI-generated clinical narrative with:
  - Presenting profile & score interpretation
  - Cognitive / Affective / Somatic domain analysis
  - Item-level clinical observations
  - Risk considerations (suicidal ideation flagged separately)
  - Clinical formulation
  - Treatment recommendations
  - Executive summary

---

## Notes

- The client **never** sees their score or report at any point
- Suicidal ideation (item 9) is automatically flagged in the report if endorsed
- Items scoring ≥ 2 are highlighted in red in the PDF table
- Reports are saved in a `/reports` folder on the Streamlit Cloud server
- Email failures are logged silently — the client experience is unaffected

import streamlit as st
import smtplib
import requests
import datetime
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION — edit this section only
# ══════════════════════════════════════════════════════════════════════════════

GMAIL_ADDRESS   = "Wijdan.psyc@gmail.com"
GMAIL_PASSWORD  = "rias eeul lyuu stce"
THERAPIST_EMAIL = "Wijdan.psyc@gmail.com"

# ══════════════════════════════════════════════════════════════════════════════
# BDI QUESTIONS
# ══════════════════════════════════════════════════════════════════════════════

BDI_QUESTIONS = [
    {"theme": "Sadness", "options": [
        {"score": 0, "text": "I do not feel sad."},
        {"score": 1, "text": "I feel sad."},
        {"score": 2, "text": "I am sad all the time and I can't snap out of it."},
        {"score": 3, "text": "I am so sad and unhappy that I can't stand it."},
    ]},
    {"theme": "Pessimism", "options": [
        {"score": 0, "text": "I am not particularly discouraged about the future."},
        {"score": 1, "text": "I feel discouraged about the future."},
        {"score": 2, "text": "I feel I have nothing to look forward to."},
        {"score": 3, "text": "I feel the future is hopeless and that things cannot improve."},
    ]},
    {"theme": "Sense of Failure", "options": [
        {"score": 0, "text": "I do not feel like a failure."},
        {"score": 1, "text": "I feel I have failed more than the average person."},
        {"score": 2, "text": "As I look back on my life, all I can see is a lot of failures."},
        {"score": 3, "text": "I feel I am a complete failure as a person."},
    ]},
    {"theme": "Loss of Satisfaction", "options": [
        {"score": 0, "text": "I get as much satisfaction out of things as I used to."},
        {"score": 1, "text": "I don't enjoy things the way I used to."},
        {"score": 2, "text": "I don't get real satisfaction out of anything anymore."},
        {"score": 3, "text": "I am dissatisfied or bored with everything."},
    ]},
    {"theme": "Guilt", "options": [
        {"score": 0, "text": "I don't feel particularly guilty."},
        {"score": 1, "text": "I feel guilty a good part of the time."},
        {"score": 2, "text": "I feel quite guilty most of the time."},
        {"score": 3, "text": "I feel guilty all of the time."},
    ]},
    {"theme": "Sense of Punishment", "options": [
        {"score": 0, "text": "I don't feel I am being punished."},
        {"score": 1, "text": "I feel I may be punished."},
        {"score": 2, "text": "I expect to be punished."},
        {"score": 3, "text": "I feel I am being punished."},
    ]},
    {"theme": "Self-Dislike", "options": [
        {"score": 0, "text": "I don't feel disappointed in myself."},
        {"score": 1, "text": "I am disappointed in myself."},
        {"score": 2, "text": "I am disgusted with myself."},
        {"score": 3, "text": "I hate myself."},
    ]},
    {"theme": "Self-Accusation", "options": [
        {"score": 0, "text": "I don't feel I am any worse than anybody else."},
        {"score": 1, "text": "I am critical of myself for my weaknesses or mistakes."},
        {"score": 2, "text": "I blame myself all the time for my faults."},
        {"score": 3, "text": "I blame myself for everything bad that happens."},
    ]},
    {"theme": "Suicidal Ideation", "options": [
        {"score": 0, "text": "I don't have any thoughts of killing myself."},
        {"score": 1, "text": "I have thoughts of killing myself, but I would not carry them out."},
        {"score": 2, "text": "I would like to kill myself."},
        {"score": 3, "text": "I would like to kill myself if I had the chance."},
    ]},
    {"theme": "Crying", "options": [
        {"score": 0, "text": "I don't cry any more than usual."},
        {"score": 1, "text": "I cry more now than I used to."},
        {"score": 2, "text": "I cry all the time now."},
        {"score": 3, "text": "I used to be able to cry, but now I can't cry even though I want to."},
    ]},
    {"theme": "Irritability", "options": [
        {"score": 0, "text": "I am no more irritated by things than I ever was."},
        {"score": 1, "text": "I am slightly more irritated now than usual."},
        {"score": 2, "text": "I am quite annoyed or irritated a good deal of the time."},
        {"score": 3, "text": "I feel irritated all the time."},
    ]},
    {"theme": "Social Withdrawal", "options": [
        {"score": 0, "text": "I have not lost interest in other people."},
        {"score": 1, "text": "I am less interested in other people than I used to be."},
        {"score": 2, "text": "I have lost most of my interest in other people."},
        {"score": 3, "text": "I have lost all of my interest in other people."},
    ]},
    {"theme": "Indecisiveness", "options": [
        {"score": 0, "text": "I make decisions about as well as I ever could."},
        {"score": 1, "text": "I put off making decisions more than I used to."},
        {"score": 2, "text": "I have greater difficulty in making decisions than before."},
        {"score": 3, "text": "I can't make decisions at all anymore."},
    ]},
    {"theme": "Body Image", "options": [
        {"score": 0, "text": "I don't feel that I look any worse than I used to."},
        {"score": 1, "text": "I am worried that I am looking old or unattractive."},
        {"score": 2, "text": "I feel there are permanent changes in my appearance that make me look unattractive."},
        {"score": 3, "text": "I believe that I look ugly."},
    ]},
    {"theme": "Work Inhibition", "options": [
        {"score": 0, "text": "I can work about as well as before."},
        {"score": 1, "text": "It takes an extra effort to get started at doing something."},
        {"score": 2, "text": "I have to push myself very hard to do anything."},
        {"score": 3, "text": "I can't do any work at all."},
    ]},
    {"theme": "Sleep Disturbance", "options": [
        {"score": 0, "text": "I can sleep as well as usual."},
        {"score": 1, "text": "I don't sleep as well as I used to."},
        {"score": 2, "text": "I wake up 1-2 hours earlier than usual and find it hard to get back to sleep."},
        {"score": 3, "text": "I wake up several hours earlier than I used to and cannot get back to sleep."},
    ]},
    {"theme": "Fatigability", "options": [
        {"score": 0, "text": "I don't get more tired than usual."},
        {"score": 1, "text": "I get tired more easily than I used to."},
        {"score": 2, "text": "I get tired from doing almost anything."},
        {"score": 3, "text": "I am too tired to do anything."},
    ]},
    {"theme": "Appetite Loss", "options": [
        {"score": 0, "text": "My appetite is no worse than usual."},
        {"score": 1, "text": "My appetite is not as good as it used to be."},
        {"score": 2, "text": "My appetite is much worse now."},
        {"score": 3, "text": "I have no appetite at all anymore."},
    ]},
    {"theme": "Weight Loss", "options": [
        {"score": 0, "text": "I haven't lost much weight, if any, lately."},
        {"score": 1, "text": "I have lost more than five pounds."},
        {"score": 2, "text": "I have lost more than ten pounds."},
        {"score": 3, "text": "I have lost more than fifteen pounds."},
    ]},
    {"theme": "Somatic Preoccupation", "options": [
        {"score": 0, "text": "I am no more worried about my health than usual."},
        {"score": 1, "text": "I am worried about physical problems like aches, pains, or upset stomach."},
        {"score": 2, "text": "I am very worried about physical problems and it's hard to think of much else."},
        {"score": 3, "text": "I am so worried about my physical problems that I cannot think of anything else."},
    ]},
    {"theme": "Loss of Libido", "options": [
        {"score": 0, "text": "I have not noticed any recent change in my interest in sex."},
        {"score": 1, "text": "I am less interested in sex than I used to be."},
        {"score": 2, "text": "I have almost no interest in sex."},
        {"score": 3, "text": "I have lost interest in sex completely."},
    ]},
]

# ══════════════════════════════════════════════════════════════════════════════
# SCORING
# ══════════════════════════════════════════════════════════════════════════════

def calculate_score(answers):
    return sum(v["score"] for v in answers.values())

def get_severity_level(total):
    if total <= 10:
        return {"label": "Normal / Minimal",             "range": "1-10",  "color": "#4CAF50"}
    elif total <= 16:
        return {"label": "Mild Mood Disturbance",         "range": "11-16", "color": "#8BC34A"}
    elif total <= 20:
        return {"label": "Borderline Clinical Depression","range": "17-20", "color": "#FFC107"}
    elif total <= 30:
        return {"label": "Moderate Depression",           "range": "21-30", "color": "#FF9800"}
    elif total <= 40:
        return {"label": "Severe Depression",             "range": "31-40", "color": "#F44336"}
    else:
        return {"label": "Extreme Depression",            "range": "40+",   "color": "#B71C1C"}

def get_score_breakdown(answers):
    COGNITIVE = [1, 2, 3, 5, 6, 7, 8, 12, 13]
    AFFECTIVE = [0, 4, 9, 10, 11]
    SOMATIC   = [14, 15, 16, 17, 18, 19, 20]
    def sub(indices):
        return sum(answers[i]["score"] for i in indices if i in answers)
    return {
        "cognitive_score": sub(COGNITIVE),
        "affective_score": sub(AFFECTIVE),
        "somatic_score":   sub(SOMATIC),
        "flagged_items":   [answers[i]["theme"] for i in answers if answers[i]["score"] >= 2],
        "suicidal_ideation_score": answers.get(8, {}).get("score", 0),
        "item_detail": [
            {"number": i+1, "theme": answers[i]["theme"],
             "score": answers[i]["score"], "response": answers[i]["text"]}
            for i in sorted(answers.keys())
        ],
    }

# ══════════════════════════════════════════════════════════════════════════════
# GROQ REPORT GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def generate_report(client_name, total_score, severity, breakdown, answers):
    item_lines = "\n".join(
        f"  Q{item['number']} ({item['theme']}): Score {item['score']} - \"{item['response']}\""
        for item in breakdown["item_detail"]
    )
    si_note = ""
    if breakdown["suicidal_ideation_score"] >= 1:
        si_note = (
            f"\nIMPORTANT: The client endorsed suicidal ideation "
            f"at level {breakdown['suicidal_ideation_score']} on item 9. "
            f"This requires explicit risk assessment discussion in the report."
        )
    prompt = f"""You are a licensed clinical psychologist writing a confidential professional assessment report.

CLIENT: {client_name}
ASSESSMENT: Beck Depression Inventory (BDI-II)
TOTAL SCORE: {total_score} / 63
SEVERITY: {severity['label']} (Range: {severity['range']})

DOMAIN SUB-SCORES:
  Cognitive cluster: {breakdown['cognitive_score']}
  Affective cluster: {breakdown['affective_score']}
  Somatic cluster:   {breakdown['somatic_score']}

FLAGGED ITEMS (score 2 or above): {', '.join(breakdown['flagged_items']) if breakdown['flagged_items'] else 'None'}
{si_note}

ITEM-BY-ITEM RESPONSES:
{item_lines}

---
Write a full professional psychotherapy assessment report with these sections:

1. REFERRAL AND ASSESSMENT OVERVIEW
2. PRESENTING PROFILE
3. DOMAIN ANALYSIS (Cognitive / Affective / Somatic)
4. ITEM-LEVEL CLINICAL OBSERVATIONS (highlight items scoring 2 or above; address suicidal ideation separately if endorsed)
5. RISK CONSIDERATIONS
6. CLINICAL FORMULATION
7. TREATMENT RECOMMENDATIONS
8. SUMMARY

Use formal clinical language. Reference actual scores and responses. Ready to place in a clinical file."""

    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from Streamlit secrets.")

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}],
              "max_tokens": 2000, "temperature": 0.4},
        timeout=60,
    )

    if not response.ok:
        try:
            error_detail = response.json()
        except Exception:
            error_detail = response.text
        raise Exception(f"Groq API error {response.status_code}: {error_detail}")

    return response.json()["choices"][0]["message"]["content"].strip()

# ══════════════════════════════════════════════════════════════════════════════
# PDF CREATOR
# ══════════════════════════════════════════════════════════════════════════════

def create_pdf_report(path, client_name, total_score, severity, report_text, answers, timestamp):
    DARK     = colors.HexColor("#1C1917")
    WARM     = colors.HexColor("#8B7355")
    ACCENT   = colors.HexColor("#C4956A")
    LIGHT_BG = colors.HexColor("#F7F3EE")
    BORDER   = colors.HexColor("#DDD5C8")
    RED_FLAG = colors.HexColor("#B71C1C")

    def sev_color(label):
        for k, c in [("Normal","#4CAF50"),("Mild","#8BC34A"),("Borderline","#FFC107"),
                     ("Moderate","#FF9800"),("Severe","#F44336"),("Extreme","#B71C1C")]:
            if k.lower() in label.lower():
                return colors.HexColor(c)
        return ACCENT

    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=2.5*cm, rightMargin=2.5*cm,
                            topMargin=2.5*cm, bottomMargin=2.5*cm)

    title_s   = ParagraphStyle("T",  fontName="Times-Roman",      fontSize=22, textColor=DARK, alignment=TA_CENTER, spaceAfter=4)
    sub_s     = ParagraphStyle("S",  fontName="Times-Italic",      fontSize=11, textColor=WARM, alignment=TA_CENTER, spaceAfter=2)
    meta_s    = ParagraphStyle("M",  fontName="Helvetica",         fontSize=8,  textColor=WARM, alignment=TA_CENTER, spaceAfter=14)
    section_s = ParagraphStyle("Se", fontName="Helvetica-Bold",    fontSize=10, textColor=WARM, spaceBefore=14, spaceAfter=4)
    body_s    = ParagraphStyle("B",  fontName="Helvetica",         fontSize=9.5,textColor=DARK, leading=15, spaceAfter=6)
    small_s   = ParagraphStyle("Sm", fontName="Helvetica",         fontSize=8.5,textColor=WARM, leading=13)
    flag_s    = ParagraphStyle("F",  fontName="Helvetica-Bold",    fontSize=9.5,textColor=RED_FLAG, leading=14)
    footer_s  = ParagraphStyle("Ft", fontName="Helvetica-Oblique", fontSize=7.5,textColor=WARM, leading=11, alignment=TA_CENTER)

    story = []
    date_str = datetime.datetime.now().strftime("%B %d, %Y  |  %H:%M")

    story += [
        Paragraph("Beck Depression Inventory", title_s),
        Spacer(1, 0.5*cm),
        Paragraph("Clinical Assessment Report", sub_s),
        Paragraph(f"CONFIDENTIAL  -  {date_str}", meta_s),
        HRFlowable(width="100%", thickness=1, color=BORDER),
        Spacer(1, 0.4*cm),
    ]

    info_data = [
        [Paragraph("<b>Client</b>", small_s), Paragraph(client_name, body_s),
         Paragraph("<b>Total Score</b>", small_s), Paragraph(f"<b>{total_score} / 63</b>", body_s)],
        [Paragraph("<b>Assessment</b>", small_s), Paragraph("BDI-II", body_s),
         Paragraph("<b>Severity</b>", small_s),
         Paragraph(f"<b>{severity['label']}</b>",
                   ParagraphStyle("SL", fontName="Helvetica-Bold", fontSize=9.5,
                                  textColor=sev_color(severity['label'])))],
    ]
    info_t = Table(info_data, colWidths=[3*cm, 6.5*cm, 3*cm, 4.5*cm])
    info_t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),LIGHT_BG), ("BOX",(0,0),(-1,-1),0.5,BORDER),
        ("INNERGRID",(0,0),(-1,-1),0.3,BORDER),
        ("TOPPADDING",(0,0),(-1,-1),8), ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("LEFTPADDING",(0,0),(-1,-1),10),
    ]))
    story += [info_t, Spacer(1, 0.5*cm)]

    story += [
        Paragraph("ITEM RESPONSES", section_s),
        HRFlowable(width="100%", thickness=0.5, color=BORDER),
        Spacer(1, 0.2*cm),
    ]

    rows = [[Paragraph("<b>#</b>", small_s), Paragraph("<b>Domain</b>", small_s),
             Paragraph("<b>Response Selected</b>", small_s), Paragraph("<b>Score</b>", small_s)]]
    for i in sorted(answers.keys()):
        a  = answers[i]
        sv = a["score"]
        rows.append([
            Paragraph(str(i+1), small_s),
            Paragraph(a["theme"], small_s),
            Paragraph(a["text"], ParagraphStyle("RC", fontName="Helvetica", fontSize=8.5, textColor=DARK, leading=12)),
            Paragraph(f"<b>{sv}</b>", ParagraphStyle("SC", fontName="Helvetica-Bold", fontSize=9,
                      textColor=RED_FLAG if sv >= 2 else DARK, alignment=TA_CENTER)),
        ])
    tstyle = [
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#EDE9E3")),
        ("BOX",(0,0),(-1,-1),0.5,BORDER), ("INNERGRID",(0,0),(-1,-1),0.3,BORDER),
        ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),6), ("ALIGN",(3,0),(3,-1),"CENTER"),
    ]
    for row_idx, i in enumerate(sorted(answers.keys()), start=1):
        if answers[i]["score"] >= 2:
            tstyle.append(("BACKGROUND",(0,row_idx),(-1,row_idx),colors.HexColor("#FFF3F3")))
    t = Table(rows, colWidths=[1*cm, 3.5*cm, 11*cm, 1.5*cm])
    t.setStyle(TableStyle(tstyle))
    story += [t, Spacer(1, 0.5*cm)]

    story += [
        HRFlowable(width="100%", thickness=1, color=BORDER),
        Spacer(1, 0.3*cm),
        Paragraph("CLINICAL REPORT", section_s),
        HRFlowable(width="100%", thickness=0.5, color=BORDER),
        Spacer(1, 0.2*cm),
    ]
    for line in report_text.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.2*cm))
        elif line.isupper() or (line.endswith(":") and len(line) < 60):
            story.append(Paragraph(line, section_s))
        elif "suicidal" in line.lower():
            story.append(Paragraph(line, flag_s))
        else:
            story.append(Paragraph(line, body_s))

    story += [
        Spacer(1, 0.6*cm),
        HRFlowable(width="100%", thickness=0.5, color=BORDER),
        Spacer(1, 0.2*cm),
        Paragraph(
            "This report is strictly confidential and intended solely for the treating clinician. "
            "It is not to be shared with the client or any third party without explicit written consent. "
            "AI-assisted analysis should be reviewed in conjunction with clinical judgment.",
            footer_s
        ),
    ]
    doc.build(story)

# ══════════════════════════════════════════════════════════════════════════════
# EMAIL SENDER
# ══════════════════════════════════════════════════════════════════════════════

def send_report_email(pdf_path, client_name, total_score, severity, filename):
    date_str = datetime.datetime.now().strftime("%B %d, %Y at %H:%M")
    msg = MIMEMultipart("mixed")
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = THERAPIST_EMAIL
    msg["Subject"] = f"[BDI Report] {client_name} - {severity['label']} (Score: {total_score}/63) - {date_str}"

    body_html = f"""
    <html><body style="font-family:Georgia,serif;color:#1C1917;background:#F7F3EE;padding:24px;">
      <div style="max-width:560px;margin:0 auto;background:white;
                  border:1px solid #DDD5C8;border-radius:4px;padding:32px;">
        <h2 style="font-weight:300;font-size:22px;margin-bottom:4px;">Beck Depression Inventory</h2>
        <p style="color:#8B7355;font-size:12px;letter-spacing:.08em;text-transform:uppercase;margin-top:0;">
          New Assessment Submitted</p>
        <hr style="border:none;border-top:1px solid #DDD5C8;margin:20px 0;">
        <table style="width:100%;font-size:14px;border-collapse:collapse;">
          <tr><td style="padding:8px 0;color:#8B7355;width:40%;">Client</td>
              <td style="padding:8px 0;"><strong>{client_name}</strong></td></tr>
          <tr><td style="padding:8px 0;color:#8B7355;">Date and Time</td>
              <td style="padding:8px 0;">{date_str}</td></tr>
          <tr><td style="padding:8px 0;color:#8B7355;">Total Score</td>
              <td style="padding:8px 0;"><strong>{total_score} / 63</strong></td></tr>
          <tr><td style="padding:8px 0;color:#8B7355;">Severity</td>
              <td style="padding:8px 0;">
                <strong style="color:{severity['color']};">{severity['label']}</strong></td></tr>
        </table>
        <hr style="border:none;border-top:1px solid #DDD5C8;margin:20px 0;">
        <p style="font-size:13px;line-height:1.6;">Full clinical report attached as PDF.</p>
        <p style="font-size:11px;color:#8B7355;margin-top:24px;font-style:italic;">
          Confidential - intended only for the treating clinician.</p>
      </div>
    </body></html>"""

    msg.attach(MIMEText(body_html, "html"))
    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
    msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, THERAPIST_EMAIL, msg.as_string())

# ══════════════════════════════════════════════════════════════════════════════
# STREAMLIT UI
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title="Psychological Assessment", page_icon="🧠",
                   layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600&family=Jost:wght@300;400;500&display=swap');
:root{--cream:#F7F3EE;--deep:#1C1917;--warm:#8B7355;--accent:#C4956A;--border:#DDD5C8;--selected:#2D2926;}
html,body,[class*="css"]{font-family:'Jost',sans-serif;background-color:var(--cream);color:var(--deep);}
.stApp{background-color:var(--cream);}
h1,h2,h3{font-family:'Cormorant Garamond',serif;color:var(--deep);}
.assessment-header{text-align:center;padding:3rem 0 2rem 0;border-bottom:1px solid var(--border);margin-bottom:2.5rem;}
.assessment-header h1{font-size:2.6rem;font-weight:300;letter-spacing:.04em;margin-bottom:.4rem;}
.assessment-header p{color:var(--warm);font-size:.9rem;font-weight:300;letter-spacing:.08em;text-transform:uppercase;}
.question-block{background:white;border:1px solid var(--border);border-radius:4px;padding:1.8rem 2rem;margin-bottom:1.2rem;transition:border-color .2s ease;}
.question-block:hover{border-color:var(--accent);}
.question-number{font-size:.72rem;font-weight:500;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin-bottom:.5rem;}
.question-text{font-family:'Cormorant Garamond',serif;font-size:1.15rem;font-weight:400;color:var(--deep);margin-bottom:1.2rem;line-height:1.5;}
div[data-testid="stRadio"]>label{display:none;}
div[data-testid="stRadio"]>div{gap:.5rem!important;}
div[data-testid="stRadio"]>div>label{background:var(--cream)!important;border:1px solid var(--border)!important;border-radius:3px!important;padding:.65rem 1rem!important;cursor:pointer!important;transition:all .15s ease!important;font-size:.88rem!important;color:var(--deep)!important;font-family:'Jost',sans-serif!important;width:100%!important;}
div[data-testid="stRadio"]>div>label:hover{border-color:var(--accent)!important;background:#FDF9F4!important;}
.progress-bar-wrapper{background:var(--border);border-radius:2px;height:3px;margin-bottom:2rem;}
.progress-bar-fill{height:3px;border-radius:2px;background:linear-gradient(90deg,var(--warm),var(--accent));transition:width .4s ease;}
.submit-section{text-align:center;padding:2rem 0 3rem 0;}
.stButton>button{background:var(--selected)!important;color:var(--cream)!important;border:none!important;padding:.85rem 3rem!important;font-family:'Jost',sans-serif!important;font-size:.85rem!important;font-weight:400!important;letter-spacing:.12em!important;text-transform:uppercase!important;border-radius:2px!important;}
.stButton>button:hover{background:var(--warm)!important;}
.thank-you-block{text-align:center;padding:5rem 2rem;}
.thank-you-block h2{font-size:2.2rem;font-weight:300;margin-bottom:1rem;}
.thank-you-block p{color:var(--warm);font-size:.95rem;font-weight:300;max-width:380px;margin:0 auto;line-height:1.7;}
.warning-box{background:#FFF8F0;border-left:3px solid #E07B39;padding:1rem 1.2rem;border-radius:0 4px 4px 0;font-size:.88rem;color:#7A3D1A;margin:1rem 0;}
div[data-testid="stTextInput"] input{background:white!important;border:1px solid var(--border)!important;border-radius:3px!important;font-family:'Jost',sans-serif!important;color:var(--deep)!important;}
</style>
""", unsafe_allow_html=True)

page = st.query_params.get("page", "client")

if page == "admin":
    st.markdown("""
    <div class="assessment-header">
        <p>Therapist Portal</p><h1>Assessment Reports</h1>
    </div>""", unsafe_allow_html=True)

    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        pwd = st.text_input("Enter admin password", type="password", placeholder="Password")
        if st.button("Access Portal"):
            if pwd == st.secrets.get("ADMIN_PASSWORD", ""):
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    else:
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        files = sorted([f for f in os.listdir(reports_dir) if f.endswith(".pdf")], reverse=True)
        if not files:
            st.info("No reports submitted yet.")
        else:
            st.markdown(f"**{len(files)} report(s) on file**")
            for fname in files:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"📄 `{fname}`")
                with col2:
                    with open(os.path.join(reports_dir, fname), "rb") as f:
                        st.download_button("Download", data=f, file_name=fname,
                                           mime="application/pdf", key=fname)
        if st.button("Log out"):
            st.session_state.admin_authenticated = False
            st.rerun()

else:
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    if st.session_state.submitted:
        st.markdown("""
        <div class="thank-you-block">
            <h2>Thank You</h2>
            <p>Your responses have been submitted successfully.<br>
            Your clinician will be in touch with you shortly.</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="assessment-header">
            <p>Confidential Psychological Assessment</p>
            <h1>Beck Depression Inventory</h1>
        </div>""", unsafe_allow_html=True)

        st.markdown("""
        <p style="font-size:.88rem;color:#8B7355;text-align:center;margin-bottom:2rem;
                  font-weight:300;line-height:1.7;">
        Please read each statement carefully and select the response<br>
        that best describes how you have been feeling <strong>over the past two weeks</strong>.
        </p>""", unsafe_allow_html=True)

        answers = {}
        all_answered = True
        client_name = st.text_input("Your name (optional)", placeholder="First name or initials")
        st.markdown("<br>", unsafe_allow_html=True)

        for i, q in enumerate(BDI_QUESTIONS):
            st.markdown(f"""
            <div class="question-block">
                <div class="question-number">Question {i+1} of {len(BDI_QUESTIONS)}</div>
                <div class="question-text">{q['theme']}</div>
            </div>""", unsafe_allow_html=True)

            options = [opt["text"] for opt in q["options"]]
            choice = st.radio(label=f"q_{i}", options=options, index=None,
                              key=f"q_{i}", label_visibility="collapsed")
            if choice is None:
                all_answered = False
            else:
                score_val = next(opt["score"] for opt in q["options"] if opt["text"] == choice)
                answers[i] = {"score": score_val, "text": choice, "theme": q["theme"]}

        answered_count = len(answers)
        pct = int((answered_count / len(BDI_QUESTIONS)) * 100)
        st.markdown(f"""
        <div style="text-align:center;margin:1.5rem 0 .5rem 0;
                    font-size:.78rem;color:#8B7355;letter-spacing:.08em;">
            {answered_count} of {len(BDI_QUESTIONS)} answered
        </div>
        <div class="progress-bar-wrapper">
            <div class="progress-bar-fill" style="width:{pct}%"></div>
        </div>""", unsafe_allow_html=True)

        if not all_answered and answered_count > 0:
            st.markdown('<div class="warning-box">Please answer all questions before submitting.</div>',
                        unsafe_allow_html=True)

        st.markdown('<div class="submit-section">', unsafe_allow_html=True)
        submit = st.button("Submit Assessment", disabled=not all_answered)
        st.markdown('</div>', unsafe_allow_html=True)

        if submit and all_answered:
            with st.spinner("Submitting your responses..."):
                total_score = calculate_score(answers)
                severity    = get_severity_level(total_score)
                breakdown   = get_score_breakdown(answers)
                report_text = generate_report(client_name or "Anonymous", total_score,
                                              severity, breakdown, answers)
                timestamp  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_name  = (client_name or "anonymous").replace(" ", "_").lower()
                filename   = f"BDI_{safe_name}_{timestamp}.pdf"
                os.makedirs("reports", exist_ok=True)
                pdf_path   = os.path.join("reports", filename)

                create_pdf_report(pdf_path, client_name or "Anonymous", total_score,
                                  severity, report_text, answers, timestamp)
                try:
                    send_report_email(pdf_path, client_name or "Anonymous",
                                      total_score, severity, filename)
                except Exception as e:
                    st.warning(f"Report saved but email failed: {e}")

                st.session_state.submitted = True
                st.rerun()

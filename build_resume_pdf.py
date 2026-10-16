"""Render master_resume.json into a one-page PDF (Letter) with reportlab.

LibreOffice isn't available on this machine, so the skill's docx->pdf step
can't run. This draws the same content directly, matching the template's
look: Calibri-ish sans, name centred, double-rule section headings.
"""
import json
import sys

from reportlab.lib.colors import HexColor, black
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (BaseDocTemplate, Frame, HRFlowable, ListFlowable,
                                ListItem, PageTemplate, Paragraph, Spacer)

SRC = sys.argv[1]
OUT = sys.argv[2]

LINK = HexColor("#0563C1")
BODY = 7.9
NAME = 17

doc = BaseDocTemplate(
    OUT, pagesize=LETTER,
    leftMargin=0.5 * inch, rightMargin=0.5 * inch,
    topMargin=0.38 * inch, bottomMargin=0.32 * inch,
    title="Yasaswin Palukuri - Resume", author="Yasaswin Palukuri",
)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f",
              leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="p", frames=[frame])])

S = {
    "name": ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=NAME,
                           leading=NAME + 2, alignment=1, spaceAfter=3),
    "contact": ParagraphStyle("contact", fontName="Helvetica", fontSize=8.0,
                              leading=10, alignment=1, textColor=black),
    "h": ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=9.2,
                        leading=11, spaceBefore=5, spaceAfter=1),
    "sum": ParagraphStyle("sum", fontName="Helvetica", fontSize=BODY,
                          leading=BODY + 2.0, alignment=TA_JUSTIFY, spaceAfter=1),
    "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=BODY + 0.5,
                            leading=BODY + 2.4, spaceBefore=3, spaceAfter=0),
    "meta": ParagraphStyle("meta", fontName="Helvetica-Oblique", fontSize=BODY - 0.5,
                           leading=BODY + 1.8, textColor=HexColor("#444444"), spaceAfter=1),
    "b": ParagraphStyle("b", fontName="Helvetica", fontSize=BODY,
                        leading=BODY + 1.9, alignment=TA_JUSTIFY),
    "skill": ParagraphStyle("skill", fontName="Helvetica", fontSize=BODY,
                            leading=BODY + 2.0, spaceAfter=0.5),
}


def rule():
    return HRFlowable(width="100%", thickness=0.8, color=black,
                      spaceBefore=1, spaceAfter=3)


def heading(text):
    return [Paragraph(text.upper(), S["h"]), rule()]


def bullets(items):
    return ListFlowable(
        [ListItem(Paragraph(b, S["b"]), leftIndent=11, value="bulletchar")
         for b in items],
        bulletType="bullet", bulletFontSize=BODY, bulletOffsetY=0.5,
        leftIndent=11, spaceBefore=1, spaceAfter=1, start="•",
    )


d = json.load(open(SRC))
story = []

# ---- header ----
story.append(Paragraph("Yasaswin Palukuri", S["name"]))
contact = ('Toronto, ON &nbsp;|&nbsp; +1 437-433-7488 &nbsp;|&nbsp; '
           '<a href="mailto:palukuriyasaswin@gmail.com" color="#0563C1">palukuriyasaswin@gmail.com</a>'
           ' &nbsp;|&nbsp; <a href="https://www.linkedin.com/in/yasaswin-palukuri" color="#0563C1">LinkedIn</a>'
           ' &nbsp;|&nbsp; <a href="https://github.com/yasaswinpalukuri" color="#0563C1">GitHub</a>'
           ' &nbsp;|&nbsp; <a href="https://yasaswinpalukuri.github.io" color="#0563C1">Portfolio</a>')
story.append(Paragraph(contact, S["contact"]))
story.append(Spacer(1, 3))

# ---- summary ----
story += heading("Summary")
story.append(Paragraph(d["summary"], S["sum"]))

# ---- skills ----
story += heading("Skills")
for s in d["skills"]:
    story.append(Paragraph(f'<b>{s["label"]}:</b> {s["items"]}', S["skill"]))

# ---- experience (Gaddr + Verita) ----
story += heading("Experience")
story.append(Paragraph("Full-Stack Developer Intern — Gaddr", S["title"]))
story.append(Paragraph("Remote · Oct 2026 – Present", S["meta"]))
story.append(bullets([
    "Working on the AI job recommendation feature for the Gaddr Jobs platform "
    "(React, React Router, TypeScript, Better Auth, Stripe, PostgreSQL).",
    "Delivered the master prompt behind the recommendation engine; it is in validation "
    "and being refined against real results.",
]))
# Verita Network is intentionally left off the resume (portfolio only).

# ---- projects ----
sec = d["sections"][0]
story += heading(sec["heading"])
for it in sec["items"]:
    name = it["name"]
    for ln in it.get("links", []):
        name += f' &nbsp;<a href="{ln["url"]}" color="#0563C1">[{ln["label"]}]</a>'
    story.append(Paragraph(name, S["title"]))
    if it.get("meta"):
        story.append(Paragraph(it["meta"], S["meta"]))
    story.append(bullets(it["bullets"]))

# ---- additional experience ----
story += heading("Additional Experience")
story.append(Paragraph("Crew Member and Trainer — Shake Shack", S["title"]))
story.append(Paragraph("Toronto, ON · May 2024 – Sep 2026", S["meta"]))
story.append(bullets([
    "Trained 20+ new team members in cooking, customer engagement, POS and service, "
    "including new recruits at New Shack Openings, and ran the shift for two days at one; "
    "served 100+ guests per shift on average.",
]))

# ---- education + certifications ----
story += heading("Education &amp; Certifications")
for e in d["education"]:
    story.append(Paragraph(f'<b>{e["credential"]}</b> — {e["details"]}', S["skill"]))
certs = []
for c in d["certifications"]:
    txt = c["name"]
    if c.get("url"):
        txt = f'<a href="{c["url"]}" color="#0563C1">{txt}</a>'
    certs.append(f'{txt} ({c["issuer"]})')
story.append(Paragraph('<b>Certifications:</b> ' + ' &nbsp;·&nbsp; '.join(certs), S["skill"]))

doc.build(story)
print("wrote", OUT)

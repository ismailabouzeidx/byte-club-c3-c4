"""Create the two source documents from one fictional business definition."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

SUMMARY = """Byte Club Studio is a fictional small business offering practical coding help. Its mission is to make practical coding help clear, approachable, and honestly scoped for students and small organizations.

Services and published prices (USD): Python tutoring costs $25 per 60-minute individual session. Code Clinic costs $40 per 60-minute debugging and code-review session. A starter website consultation is free for 20 minutes; website implementation starts at $300 and needs a written scope and quote. No discounts, certified qualifications, exact project deadlines, or live appointment availability are published.

Python tutoring teaches concepts through guided practice. Code Clinic helps customers understand and improve their own code; it does not complete assessed work for submission. Website work is limited to small informational sites, not payment systems or complex backend applications.

Our fictional team is Lina Haddad (learning lead), Omar Nader (development lead), and Maya Saleh (customer operations). Our distinctive promise is small, clearly scoped help with explanations and written expectations. The target audience is beginner programmers and small organizations needing a simple web presence.

Sessions are online, in English or Arabic, by confirmed appointment. The contact address is hello@byteclub.example (a demonstration address). The chatbot records local customer-interest and feedback logs; it does not send email, reserve a slot, process payments, or update an external CRM. Name, email, and service needs are required to record a contact request. The attached business PDF contains the rescheduling and group-session policies.
"""

PDF_SECTIONS = [
    ("MISSION & AUDIENCE", "Practical coding help for students, beginners, and small organizations. We explain the work, set realistic limits, and help customers become more independent."),
    ("SERVICES & PRICES", "Python tutoring: USD 25 / 60 minutes, individual guided practice.<br/>Code Clinic: USD 40 / 60 minutes, debugging and code review.<br/>Starter website: free 20-minute consultation; implementation starts at USD 300, subject to written scope and quote."),
    ("OUR FICTIONAL TEAM", "Lina Haddad - learning lead. Omar Nader - development lead. Maya Saleh - customer operations. These are invented profiles for this fictional business."),
    ("WHY BYTE CLUB", "Small, clearly scoped help; understandable explanations; English or Arabic sessions; transparent published starting prices and written expectations."),
    ("POLICIES & LIMITS", "Sessions are online and require confirmed appointments. Rescheduling is free with at least 24 hours' notice. Group tutoring is limited to three learners; group pricing is not published and must be requested. No refund policy, certification, discounts, delivery deadlines, or live availability are published. Code Clinic supports understanding; we do not complete assessed work for submission. Website work covers small informational sites, not payment systems or complex backend applications."),
    ("CONTACT & AGENT SCOPE", "hello@byteclub.example is a demonstration address. The chatbot can answer from these documents, record an authorized contact request with name/email/needs, and log feedback or unknown questions. Logs are local demonstrations. A receipt does not confirm a booking, an email, a payment, or an external CRM update."),
]


def create_business_files(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "business_summary.txt").write_text(SUMMARY, encoding="utf-8")
    # The brief uses summary.txt once and business_summary.txt in its checklist.
    # Provide an identical alias to satisfy both spellings without ambiguity.
    (folder / "summary.txt").write_text(SUMMARY, encoding="utf-8")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ClubTitle", fontName="Helvetica-Bold", fontSize=32, leading=34, textColor=colors.HexColor("#171a20"), spaceAfter=8))
    styles.add(ParagraphStyle(name="ClubLabel", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=colors.HexColor("#8a5b10"), spaceBefore=13, spaceAfter=5))
    styles.add(ParagraphStyle(name="ClubBody", fontName="Helvetica", fontSize=10, leading=14, textColor=colors.HexColor("#303943")))
    doc = SimpleDocTemplate(str(folder / "about_business.pdf"), pagesize=letter,
                            leftMargin=46, rightMargin=46, topMargin=38, bottomMargin=40,
                            title="Byte Club Studio - Business profile", author="Byte Club Studio",
                            subject="Services and policies")
    story = [Paragraph("BYTE CLUB STUDIO", styles["ClubTitle"]),
             Paragraph("CODING HELP. CLEAR EXPECTATIONS.", styles["ClubLabel"]),
             Paragraph("Fictional business profile | Ismail Abou Zeid", styles["ClubBody"])]
    for title, body in PDF_SECTIONS:
        story.extend([Paragraph(title, styles["ClubLabel"]), Paragraph(body, styles["ClubBody"])])
    def footer(canvas, document):
        canvas.setStrokeColor(colors.HexColor("#e0b260"))
        canvas.line(46, 32, 566, 32)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#647080"))
        canvas.drawString(46, 20, "FICTIONAL BUSINESS | No real payments or appointments")
        canvas.drawRightString(566, 20, str(document.page))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    for assignment in ["C3", "C4"]:
        create_business_files(root / assignment / "me")

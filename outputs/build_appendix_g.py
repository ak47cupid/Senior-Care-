from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path

ROOT=Path.cwd(); PRE=ROOT/'docs'/'previews'/'all-features'; OUT=ROOT/'outputs'/'manuscript'; OUT.mkdir(parents=True,exist_ok=True)
NAVY=RGBColor(18,55,75); TEAL=RGBColor(13,123,124); MUTED=RGBColor(83,101,112)
doc=Document(); sec=doc.sections[0]
sec.page_width=Inches(8.5); sec.page_height=Inches(11)
sec.top_margin=Inches(.55); sec.bottom_margin=Inches(.55); sec.left_margin=Inches(.72); sec.right_margin=Inches(.72)
styles=doc.styles
normal=styles['Normal']; normal.font.name='Arial'; normal.font.size=Pt(9.5); normal.font.color.rgb=RGBColor(35,45,52); normal.paragraph_format.space_after=Pt(4); normal.paragraph_format.line_spacing=1.04
for name,size in [('Title',22),('Heading 1',15),('Heading 2',11)]:
 s=styles[name]; s.font.name='Arial'; s.font.size=Pt(size); s.font.color.rgb=NAVY; s.font.bold=True; s.paragraph_format.space_before=Pt(4); s.paragraph_format.space_after=Pt(5)

def para(text='',bold_prefix=None,align=None,space_after=None):
 p=doc.add_paragraph()
 if bold_prefix and text.startswith(bold_prefix): p.add_run(bold_prefix).bold=True; p.add_run(text[len(bold_prefix):])
 else:p.add_run(text)
 if align is not None:p.alignment=align
 if space_after is not None:p.paragraph_format.space_after=Pt(space_after)
 return p
def bullet(text):
 p=doc.add_paragraph(style='List Bullet'); p.paragraph_format.left_indent=Inches(.22); p.paragraph_format.first_line_indent=Inches(-.13); p.paragraph_format.space_after=Pt(2); p.add_run(text); return p
def step(n,title,text):
 p=doc.add_paragraph(); p.paragraph_format.left_indent=Inches(.24); p.paragraph_format.first_line_indent=Inches(-.24); p.paragraph_format.space_after=Pt(3)
 r=p.add_run(f'{n}. {title} '); r.bold=True; r.font.color.rgb=TEAL; p.add_run(text); return p
def h(text,level=1): doc.add_heading(text,level=level)
def fig(file,caption,width=6.85):
 path=PRE/file
 p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(2); p.paragraph_format.space_after=Pt(1)
 p.add_run().add_picture(str(path),width=Inches(width))
 c=doc.add_paragraph(); c.alignment=WD_ALIGN_PARAGRAPH.CENTER; c.paragraph_format.space_after=Pt(4)
 r=c.add_run(caption); r.italic=True; r.font.size=Pt(8.5); r.font.color.rgb=MUTED
def note(title,text):
 t=doc.add_table(rows=1,cols=1); c=t.cell(0,0); c.text=''; tcpr=c._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd'); sh.set(qn('w:fill'),'EAF5F3'); tcpr.append(sh)
 p=c.paragraphs[0]; p.paragraph_format.space_after=Pt(2); rr=p.add_run(title+' '); rr.bold=True; rr.font.color.rgb=TEAL; p.add_run(text)
 for rr in p.runs:rr.font.size=Pt(9)

def newpage():doc.add_page_break()

# Running footer
for s in doc.sections:
 p=s.footer.paragraphs[0]; p.alignment=WD_ALIGN_PARAGRAPH.CENTER
 r=p.add_run('APPENDIX G  |  BARANGAY ASSISTANCE SYSTEM USER GUIDE  |  '); r.font.name='Arial'; r.font.size=Pt(8); r.font.color.rgb=MUTED
 fld=OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),'PAGE'); p._p.append(fld)

# Page 1
p=doc.add_paragraph('APPENDIX G','Title'); p.paragraph_format.space_after=Pt(0)
p=doc.add_paragraph('USER GUIDE / MANUAL'); p.paragraph_format.space_after=Pt(7); p.runs[0].bold=True; p.runs[0].font.name='Arial'; p.runs[0].font.size=Pt(16); p.runs[0].font.color.rgb=TEAL
para('Senior Citizen Assistance System for Barangay Services',bold_prefix='Senior Citizen Assistance System')
h('1. Introduction')
para('This guide describes the current project build of the Senior Citizen Assistance System for senior citizens, barangay staff, and administrators. The project supports senior registration, application review, assistance requests, announcements, events, notifications, and reports. It has not yet been deployed for barangay use; the screenshots and steps are for a configured local demonstration environment.')
para('The system provides:')
for x in ['Online senior registration and application status tracking.','Secure review of identification and requested supporting documents.','Assistance request submission, review, scheduling, and release records.','Senior records, announcements, events, and in-system notifications.','Monthly reports, CSV export, SMS tools, audit records, and administrative settings.']: bullet(x)
h('2. Accessing the System')
step(1,'Open a browser.','Open the browser on the computer where the project is configured in XAMPP. For a local demonstration, use http://localhost/barangay-assistance-system/. There is no live barangay URL yet.')
step(2,'Choose an action.','From the landing page, select Register as a Senior to create an account or Sign in if you already have an account.')
fig('01-public-landing-page.png','Figure G.1. Public landing page and entry points.',6.65)
note('Project preview.','Screenshots use local demonstration data and are not evidence of a live deployment. A barangay URL and operational access will be available only after deployment and configuration.')

# Page 2
newpage(); h('3. Creating a Senior Citizen Account')
para('A senior citizen may register through the public form. Complete the form carefully and provide the required documents. A submitted account is marked Pending while barangay personnel review the application.')
step(1,'Open registration.','From the landing page, choose Register as a Senior.')
step(2,'Enter personal details.','Complete the location, name, birthdate, contact, household, and emergency-contact fields. Registration is for people aged 60 or older.')
step(3,'Create a password.','Enter a password with at least eight characters, then enter it again to confirm.')
step(4,'Attach the required files.','Upload a 1x1 photo (JPG, PNG, or WebP) and valid identification (JPG, PNG, or PDF). Each file can be up to 2 MB.')
step(5,'Review and submit.','Check the information and consent fields, then submit the form. Save your sign-in email and check your application status after signing in.')
fig('03-public-senior-registration.png','Figure G.2. Senior citizen registration form. Scroll through the form to complete all sections.',6.65)
note('Before you submit.','Use an email address you can access. Keep your password private. If staff request a replacement document, sign in and upload the requested file from the Application page.')

# Page 3
newpage(); h('4. Signing In and Recovering Access')
para('Use the same email address and password entered during registration. Pending and rejected applicants can sign in to check the application and respond to document requests. Only active senior accounts can use the assistance-request service.')
step(1,'Open Sign in.','Select Sign in on the landing page.')
step(2,'Enter your credentials.','Type your registered email and password, then submit the form. The system opens the dashboard available to your role.')
step(3,'Reset a forgotten password.','Choose Forgot Password on the sign-in page. Enter your registered email, enter the six-digit code sent to that email, and set a new password.')
step(4,'Check your inbox.','If the message is not visible, check Spam/Junk. A reset code expires after 10 minutes; request a new one if it expires. Email delivery must be configured in the local environment for password recovery to work.')
# two images on one row
imgs=doc.add_table(rows=1,cols=2); imgs.autofit=False
for cell,file in zip(imgs.rows[0].cells,['02-public-sign-in.png','04-public-forgot-password.png']):
 cell.width=Inches(3.35); cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
 p=cell.paragraphs[0]; p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(str(PRE/file),width=Inches(3.25))
cp=doc.add_paragraph('Figure G.3. Sign-in page.                         Figure G.4. Password recovery page.'); cp.alignment=WD_ALIGN_PARAGRAPH.CENTER; cp.paragraph_format.space_after=Pt(5); cp.runs[0].italic=True; cp.runs[0].font.size=Pt(8.5); cp.runs[0].font.color.rgb=MUTED
h('Role-based dashboard')
para('After signing in, use the navigation menu to open the pages available to your role. Senior citizens see their own profile, requests, announcements, and events. Staff and administrators see management tools based on their permissions.')
note('Sign out.','Choose Logout when finished, especially on a shared computer. Do not share verification codes or passwords with anyone.')

# Page 4
newpage(); h('5. Senior Citizen User Guide')
para('In the local demonstration, the senior dashboard summarizes account status, recent requests, notifications, and announcements. Use the side menu to update your profile, submit a request, or view community information.')
fig('24-senior-dashboard.png','Figure G.5. Senior citizen dashboard (local demonstration account).',6.65)
step(1,'Review your application.','If your account is Pending or a document needs attention, open Application to read the status and staff remarks. Upload a replacement document when requested.')
step(2,'Keep your profile current.','Open Profile to review your contact and address information. Save any permitted updates.')
step(3,'Read barangay updates.','Open Announcements or Events to see information published by barangay personnel. Open Notifications to review account updates and follow their links.')
h('Accessibility options')
para('The senior interface provides larger text controls and English/Cebuano navigation labels for key actions. Use the accessibility controls on the senior pages when needed.')
note('Privacy.','Use your own account to review only your own application, profile, and assistance history. Keep medical and identity information private.')

# Page 5
newpage(); h('6. Submitting and Tracking an Assistance Request')
para('Active senior citizens can submit requests from My Assistance Requests. The request page records status updates and, when assistance is released, the release details.')
step(1,'Open Requests.','Choose Requests in the senior navigation, then select Submit a Request.')
step(2,'Choose the request type.','Select the available assistance category that fits your situation, such as Medical/Financial Assistance, Death Assistance, or Special / Indigent Assistance.')
step(3,'Complete the form.','Describe the need and complete the financial and pension details shown for that request type. Attach the requested supporting document. Death Assistance requires a death certificate and identification.')
step(4,'Submit and track.','Submit once, then review the request status, staff remarks, and timeline on the same page. The status may change as staff review and process the request.')
step(5,'Claim assistance.','When the request is scheduled or approved, follow the barangay’s instructions. Bring a Senior Citizen ID or another valid ID when claiming assistance.')
fig('26-senior-assistance-requests.png','Figure G.6. My Assistance Requests page (demonstration screen; the current form may display additional fields by request type).',6.65)
note('Keep documents readable.','Upload clear, complete images or PDF files. If staff request a clearer or corrected document, open the request or Application page and follow the on-screen instructions.')

# Page 6
newpage(); h('7. Barangay Staff User Guide')
para('In a configured local demonstration, barangay staff use the staff dashboard to review senior records and documents, process assistance requests, post community information, send SMS messages, and prepare reports. These are project features; they are not yet available through a deployed barangay service.')
fig('17-staff-dashboard.png','Figure G.7. Barangay staff dashboard (local demonstration data).',6.65)
step(1,'Review senior records.','Open Seniors to search and review registered senior information. Handle identification and supporting documents only for authorized service purposes.')
step(2,'Process assistance requests.','Open Requests, review the request details and supporting documents, and record the decision with clear remarks. For an approved or scheduled request, record its release details when it is distributed.')
step(3,'Maintain community information.','Use Announcements to publish notices and Events to post schedules for senior citizens.')
step(4,'Send service updates.','Use Send SMS to send an authorized message to selected recipients. Check the result in SMS logs when available; delivery depends on the configured gateway and phone.')
step(5,'Prepare a report.','Open Reports, select the reporting month and year, and choose Apply. Use Download CSV to save the data or Print / Save PDF to create a print-ready copy.')
h('Registration review permissions')
para('Staff may review submitted identification and request additional or replacement documents. The Administrator makes the final registration approval or rejection decision.')
note('Record decisions clearly.','Enter accurate remarks and release information so the applicant can understand the outcome and the barangay has a traceable service record.')

# Page 7
newpage(); h('8. Administrator User Guide')
para('In the local demonstration, administrators manage system access and make final registration decisions. The administrator navigation also includes senior records, assistance requests, announcements, events, reports, SMS logs, audit logs, settings, and backup guidance. The project has not yet been deployed for operational barangay use.')
fig('05-admin-dashboard.png','Figure G.8. Administrator dashboard (local demonstration data).',6.65)
step(1,'Review registrations.','Open Registrations and filter by status. Select Review application to inspect the submitted information and identification. Resolve possible duplicate flags carefully and record the review remarks.')
step(2,'Approve or reject.','After checking the application and requirements, record the final decision. Approved accounts become Active; rejected applicants can sign in to view the status and address document requests when applicable.')
step(3,'Manage users and records.','Use Users to manage accounts and Seniors to maintain authorized senior records. Use Requests to review assistance and record releases.')
step(4,'Generate monthly reports.','Open Reports, select month and year, and apply the filter. Download CSV for analysis or use Print / Save PDF for a printable report. Reports include registration, request, distribution, beneficiary, and cash totals as available.')
step(5,'Review system activity.','Use Audit Logs and SMS Logs to inspect recorded actions and message outcomes. Settings contains system configuration controls.')
h('Backup and safe handling')
para('The Backup page provides a command reference; it does not run an automatic backup. Follow the barangay’s approved procedure to back up both the database and private uploaded documents, and periodically verify that a restore works. Do not store downloaded reports or identity documents on shared devices.')
note('Protect personal information.','Give each user only the access required for their role. Use strong unique passwords, sign out after work, and handle identity, contact, and health information according to barangay policy.')

path=OUT/'Appendix_G_User_Guide_Manual_Revised.docx'; doc.save(path); print(path)


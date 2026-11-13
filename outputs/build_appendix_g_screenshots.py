from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path.cwd(); DL=Path(r'C:\Users\Jake\Downloads'); OUT=ROOT/'outputs'/'manuscript'; AS=OUT/'appendix_g_screenshots'; AS.mkdir(parents=True,exist_ok=True)
names=['29b65533-dc06-48a5-8bfd-9f014db6ab28.jpg','ba8217c8-91b0-48ad-bdf0-8e523979b571.jpg','d4702a79-0d1f-4e00-8cef-ab09fada488d.jpg','2dcf8f2c-1ed6-41ee-8247-039d69cdf14a.jpg','8401b775-3586-45f0-8f3f-a11354c24389.jpg','89496a45-5be6-4650-a02f-9d1b6b104f42.jpg','ca3cbc2e-6bb3-495d-8605-1e8804b695b9.jpg','9c22531d-42de-445e-ac0e-1d0c7cf92995.jpg','aca83531-a537-4bdb-9f79-f54b2d7e52b5.jpg','f5d08e7e-ea83-4c0c-9259-1ac04c8e4e8a.jpg','5e91bc7c-d057-4766-844a-b90aeaa6368d.jpg','d46dd987-bf5e-46de-986b-a2ae04a00ff5.jpg','f07cdc57-57fa-4a16-aa22-fc727d80cb01.jpg','7168ace5-d4bf-4123-9a2e-90e2eeb49a6b.jpg','f264aac2-091c-4c6d-8842-beb3d2c4b94f.jpg','7a43d573-e778-45c5-8b9e-da29997f68ad.jpg','242f991f-89ee-4344-81ad-66625ae27712.jpg','feb86439-762d-4abe-bf9c-09d4ebe5a961.jpg']
# Solid masks remove demo identifiers and personal/health details from included interface previews.
redactions={
 4:[(320,217,1880,402)],
 5:[(317,310,1880,378)],
 8:[(320,190,1880,465)],
 9:[(320,174,1880,465)],
 11:[(320,456,1880,508)],
 14:[(336,163,1120,310)],
 16:[(320,220,1880,350)],
 17:[(320,168,1880,410)],
}
images={}
for i,n in enumerate(names,1):
    src=DL/n
    if not src.exists():raise FileNotFoundError(src)
    im=Image.open(src).convert('RGB'); d=ImageDraw.Draw(im)
    for rect in redactions.get(i,[]):
        d.rectangle(rect,fill='#f5f8f7')
    # Add subtle redaction label on fully concealed data rows where the mask would otherwise resemble an empty table.
    if i in [4,5,8,11,16,17]:
        y={4:233,5:332,8:300,9:190,11:472,16:275,17:195}[i]
        d.text((345,y),'DEMO RECORDS REDACTED',fill='#526772')
    p=AS/f'figure_{i:02d}.jpg'; im.save(p,quality=90,optimize=True); images[i]=p
public_files=['codex-clipboard-f2bad18f-a02c-40c4-b774-a4c391af7a01.png','codex-clipboard-8691213f-5b64-4414-a65e-390c05d3a388.png','codex-clipboard-4741f39d-dee1-4c1d-b875-a43e625aa31e.png','codex-clipboard-510aeb3a-f36a-473f-b72b-3b6dab487675.png']
for i,n in enumerate(public_files,19):
    im=Image.open(Path(r'C:\\Users\\Jake\\AppData\\Local\\Temp')/n).convert('RGB')
    p=AS/f'figure_{i:02d}.jpg';im.save(p,quality=90,optimize=True);images[i]=p

# Word setup
NAVY=RGBColor(17,58,78); TEAL=RGBColor(9,119,119); GRAY=RGBColor(87,103,111); BLACK=RGBColor(35,45,52)
doc=Document(); sec=doc.sections[0]; sec.page_width=Inches(8.5); sec.page_height=Inches(11); sec.top_margin=Inches(.55); sec.bottom_margin=Inches(.55); sec.left_margin=Inches(.68); sec.right_margin=Inches(.68)
styles=doc.styles
styles['Normal'].font.name='Arial'; styles['Normal'].font.size=Pt(9.2); styles['Normal'].font.color.rgb=BLACK; styles['Normal'].paragraph_format.space_after=Pt(3); styles['Normal'].paragraph_format.line_spacing=1.0
for name,size in [('Title',23),('Heading 1',15),('Heading 2',11)]:
 s=styles[name]; s.font.name='Arial'; s.font.size=Pt(size); s.font.bold=True; s.font.color.rgb=NAVY; s.paragraph_format.space_before=Pt(3); s.paragraph_format.space_after=Pt(4)

def H(t,l=1):return doc.add_heading(t,level=l)
def P(t='',bold=None,align=None,after=3):
 p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(after)
 if bold and t.startswith(bold):p.add_run(bold).bold=True;p.add_run(t[len(bold):])
 else:p.add_run(t)
 if align is not None:p.alignment=align
 return p
def bullet(t):
 p=doc.add_paragraph(style='List Bullet'); p.paragraph_format.left_indent=Inches(.23);p.paragraph_format.first_line_indent=Inches(-.12);p.paragraph_format.space_after=Pt(1);p.add_run(t);return p
def step(num,title,text):
 p=doc.add_paragraph();p.paragraph_format.left_indent=Inches(.22);p.paragraph_format.first_line_indent=Inches(-.22);p.paragraph_format.space_after=Pt(2)
 r=p.add_run(f'{num}. {title} ');r.bold=True;r.font.color.rgb=TEAL;p.add_run(text);return p
def newpage():doc.add_page_break()
def pic(i,caption,width=6.9):
 p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(1);p.paragraph_format.space_after=Pt(0);p.add_run().add_picture(str(images[i]),width=Inches(width))
 c=doc.add_paragraph();c.alignment=WD_ALIGN_PARAGRAPH.CENTER;c.paragraph_format.space_after=Pt(3);r=c.add_run(caption);r.italic=True;r.font.size=Pt(8);r.font.color.rgb=GRAY
def pair(items,width=3.35):
 t=doc.add_table(rows=1,cols=len(items));t.autofit=False
 for cell,(i,cap) in zip(t.rows[0].cells,items):
  cell.width=Inches(width);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
  p=cell.paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(0);p.add_run().add_picture(str(images[i]),width=Inches(width-.08))
  c=cell.add_paragraph();c.alignment=WD_ALIGN_PARAGRAPH.CENTER;c.paragraph_format.space_after=Pt(3);r=c.add_run(cap);r.italic=True;r.font.size=Pt(7.6);r.font.color.rgb=GRAY

def callout(title,text):
 t=doc.add_table(rows=1,cols=1);c=t.cell(0,0);c.text='';pr=c._tc.get_or_add_tcPr();sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'EAF4F2');pr.append(sh)
 p=c.paragraphs[0];p.paragraph_format.space_after=Pt(2);r=p.add_run(title+' ');r.bold=True;r.font.color.rgb=TEAL;p.add_run(text)
 for r in p.runs:r.font.size=Pt(8.8)
# Footer
for s in doc.sections:
 f=s.footer.paragraphs[0];f.alignment=WD_ALIGN_PARAGRAPH.CENTER;r=f.add_run('APPENDIX G  |  SENIOR ASSIST  |  ');r.font.name='Arial';r.font.size=Pt(8);r.font.color.rgb=GRAY
 fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');f._p.append(fld)

# Page 1: scope and local-only access
p=doc.add_paragraph('APPENDIX G','Title');p.paragraph_format.space_after=Pt(0)
p=doc.add_paragraph('USER GUIDE / MANUAL');p.paragraph_format.space_after=Pt(6);r=p.runs[0];r.font.name='Arial';r.font.size=Pt(16);r.font.bold=True;r.font.color.rgb=TEAL
P('Senior Assist - Barangay Tungkil',bold='Senior Assist')
H('1. Introduction')
P('This guide explains the current project build of Senior Assist for senior citizens, barangay staff, and administrators. The screenshots show the application’s local demonstration interface and its main service workflows: registration, senior records, assistance requests, community notices, SMS, and reports.')
callout('Project status.','The system has not been deployed. Use it only in the configured local demonstration environment. There is no live barangay web address yet; screenshots and sample records are demonstrations.')
H('2. Opening the local demonstration')
step(1,'Start the local environment.','The project team or authorized technician must start and configure the local XAMPP, PHP, and database services.')
step(2,'Open the system.','On that computer, open a browser and visit http://localhost/barangay-assistance-system/. This address works only when the project is installed at that local path.')
step(3,'Sign in with an assigned account.','Use the demonstration credentials provided by the project team. Do not use sample accounts with real beneficiary data.')
H('User roles')
bullet('Senior Citizen: maintains a profile, follows application progress, submits assistance requests, and reads notices and events.')
bullet('Barangay Staff: reviews submitted records and requests, records decisions, posts updates, and prepares service reports.')
bullet('Administrator: manages user access, makes final registration decisions, oversees releases, and reviews reports and system logs.')
P('The navigation menu varies by role. Use Logout when finished, especially on a shared computer.',bold='The navigation menu varies by role.')

# Page 3: Public screens and account access
newpage();H('3. Public Portal Registration and Password Recovery')
P('The public pages let a senior citizen open the registration form or sign in. The images below are earlier public-screen previews. The current project remains a local demonstration and its interface may differ.')
pair([(19,'Figure G.1. Public landing page preview.'),(20,'Figure G.2. Senior registration form preview.')],3.45)
step(1,'Start registration.','From the landing page, choose Register as a Senior. Complete the required personal, location, and contact information.')
step(2,'Attach the required files.','Upload the 1x1 photo and valid identification requested by the form. Use the listed file types and size limits.')
step(3,'Submit for review.','Review the entries and submit. The account begins in Pending status while the barangay reviews the application.')
pair([(21,'Figure G.3. Sign-in page preview.'),(22,'Figure G.4. Earlier password-recovery screen preview.')],3.45)
step(4,'Sign in or recover access.','Enter the registered email and password. For password recovery in the current project, enter the registered email, use the six-digit code sent to that email, then choose a new password.')
callout('Preview mismatch.','Figure G.4 contains an older office-only reset notice. The current project uses email-code recovery when email delivery is configured; follow the current local build, not that older notice.')

# Page 4: Senior citizen guide
newpage();H('4. Senior Citizen Guide')
P('The senior portal is intended for the applicant’s own profile and service requests. Features become available according to account status and role.')
step(1,'Create an account.','From the public landing page, choose Register as a Senior. Complete the required personal, address, contact, and emergency-contact details. Upload a 1x1 photo and a valid ID file as requested by the form.')
step(2,'Wait for review.','After submission, the application is Pending. Sign in to open Application and read the status or any document request. The Administrator records the final approval or rejection.')
step(3,'Respond to a document request.','If staff ask for a clearer or replacement file, open Application and upload the requested item. Follow the on-screen file format and size limits.')
step(4,'Submit assistance.','Once the account is Active, open Requests and choose Submit a Request. Select the assistance type, complete the details, and attach supporting documents requested by the form.')
step(5,'Track and follow up.','Return to Requests to review the status, remarks, timeline, schedule, and release details. Follow the barangay’s instructions when assistance is ready to claim.')
H('Community information and privacy')
P('Open Announcements and Events to read items published by barangay personnel. Use Notifications to follow account updates. Keep your password and verification codes private, and use your account only to view your own records.')
callout('Local demonstration only.','Account creation, email recovery, and notifications depend on the local application and its configured services. The system is not yet available as a live barangay service.')

# Page 3: Staff dashboard and review queue
newpage();H('5. Barangay Staff Guide')
P('Use the Staff dashboard to see the service queue and open common work areas. The current preview shows request totals, items awaiting review, registrations, schedules, and report access.')
pair([(7,'Figure G.5. Staff dashboard.'),(5,'Figure G.6. Senior records list; personal rows redacted.')],3.45)
H('Review registrations and senior records',2)
step(1,'Open Registrations.','Filter by status and choose Review application for a pending applicant.')
step(2,'Review the submission.','Check the application and valid identification using the authorized review page. Staff may request additional or replacement documents and explain what needs correction.')
step(3,'Open Seniors when needed.','Use the senior records list to locate an existing record. Open a record only for authorized service work and keep the information confidential.')
pic(6,'Figure G.7. Pending senior registration list; personal details redacted.',6.6)
callout('Approval permission.','Staff can review documents and support the application process. The Administrator makes the final registration approval or rejection decision.')

# Page 4: requests and community pages
newpage();H('6. Reviewing Requests and Community Updates')
P('Staff review assistance requests and keep community information current. Give applicants clear remarks so they know the next step.')
pic(14,'Figure G.8. Assistance request review; applicant and request details redacted.',6.65)
step(1,'Review the request.','Open Requests, read the request information, and inspect available supporting documents.')
step(2,'Record a decision.','Choose Approve or Reject. Enter remarks, and provide a reason when rejecting. Save the decision.')
step(3,'Record a release after approval.','When assistance is approved or scheduled and distributed, use the release form to record the item, quantity, amount, release time, recipient, and other required details. Available actions depend on the signed-in role.')
pair([(2,'Figure G.9. Announcements page.'),(3,'Figure G.10. Events page.')],3.45)
P('For an announcement, select New announcement, enter the notice, choose its audience, and save. For an event, enter the title, description, location, and date, then select Add event.')

# Page 5: staff SMS and reports
newpage();H('7. Sending Messages and Preparing Reports')
P('Staff can send service messages and prepare reports from the left navigation. SMS delivery requires the configured gateway and an available connected phone.')
pair([(1,'Figure G.11. Staff SMS log and Send SMS action.'),(11,'Figure G.12. Monthly service report; sample row redacted.')],3.45)
H('Send an SMS',2)
step(1,'Open Send SMS.','Select the Send SMS button to open the message form.')
step(2,'Choose recipients and write the message.','Review the selected recipients and message carefully before sending. Send only authorized service information.')
step(3,'Check the result.','Review the SMS status and sent time in the log. A successful system response depends on the SMS service configuration and phone connection.')
H('Prepare a monthly report',2)
step(1,'Open Reports.','Select the reporting month and report type, then choose Apply.')
step(2,'Review the output.','Check the totals and report rows for the selected month. The application shows current statuses and uses recorded release dates for distributions.')
step(3,'Export.','Choose Download CSV for a spreadsheet file, or Print / Save PDF for a print-ready copy. Store exported files only in an approved location.')
callout('Data handling.','Reports can contain names and assistance details. Verify the reporting period and recipients before sharing or printing.')

# Page 6: Admin dashboard/user management
newpage();H('8. Administrator Guide')
P('Administrators oversee system access and service records. The dashboard provides a summary of seniors, requests, schedules, and recent activity.')
pic(18,'Figure G.13. Administrator dashboard; local demonstration totals.',6.65)
H('Manage user accounts',2)
step(1,'Open Users.','Choose Add user to create an authorized account, or use View/Edit to inspect or update an account.')
step(2,'Check role and status.','Confirm the correct role is assigned. Give each user only the access needed for their work.')
step(3,'Use account actions carefully.','Before changing or removing an account, check the barangay’s records-retention and access procedure. Do not delete records solely to clear a queue.')
pair([(17,'Figure G.14. Manage users; account details redacted.'),(16,'Figure G.15. Senior records; personal rows redacted.')],3.45)
P('The Seniors page is for authorized senior records. Open an individual record only when required to process a service or application.')

# Page 7: Admin review and release
newpage();H('9. Registration Decisions and Assistance Releases')
P('The Administrator makes final decisions on senior registrations and oversees assistance release information.')
pair([(4,'Figure G.16. Assistance request decision; identity and health details redacted.'),(15,'Figure G.17. Released Assistance page; local demo data.')],3.45)
step(1,'Review pending registrations.','Open Registrations, select a pending application, and check the submitted details, identification, requested requirements, and possible duplicate notice.')
step(2,'Record the registration outcome.','Approve a complete eligible application or reject it with clear remarks. The applicant can sign in to read the decision and any document instructions.')
step(3,'Review assistance decisions.','In Requests, inspect the application and attachment. Staff and administrators can process requests according to their assigned permissions. For an approved or scheduled request, the authorized user records release details using the available form. Use Released Assistance to search recorded grants and confirm the grantee, assistance, amount, release date, and receiver before reporting.')

# Page 8: notices and events
newpage();H('10. Announcements and Events')
P('Both staff and administrators can publish community information. Review the audience, date, and wording before saving because senior citizens may use these screens to plan visits.')
pair([(13,'Figure G.18. Administrator announcements.'),(12,'Figure G.19. Administrator events.')],3.45)
H('Publish an announcement',2)
step(1,'Open Announcements.','Choose New announcement.')
step(2,'Enter the notice.','Add a concise title and body. Select the intended audience and mark an emergency notice only when appropriate.')
step(3,'Review and save.','Check dates and details, then save. Confirm that the notice appears in the list.')
H('Add an event',2)
step(1,'Open Events.','Enter the event title, description, location, and date/time.')
step(2,'Save and verify.','Choose Add event and confirm it appears in the event list with the correct location and schedule.')

# Page 9: admin messages, logs, backup
newpage();H('11. SMS Logs, Audit Logs, and Safe Operation')
P('Administrators can send messages and review system records that help follow service activity. Treat logs and exports as confidential because they can contain account and contact information.')
pair([(10,'Figure G.20. Administrator Send SMS page.'),(8,'Figure G.21. SMS Logs page.')],3.45)
step(1,'Send a message.','Open Send SMS, choose the intended recipients, check the message, and send it only when the gateway is configured for the local environment.')
step(2,'Review delivery results.','Open SMS Logs to review the recipient, message status, and sent time. A queued or accepted message does not guarantee that a phone received it.')
pic(9,'Figure G.22. Audit Logs page; user activity rows redacted.',6.55)
H('Backups and account security',2)
P('The Backup page provides a command reference; it does not run automatic backups. Follow the project team’s approved procedure to back up both the database and private uploaded documents, and verify a restore before relying on the backup.')
P('Use strong unique passwords, sign out after every session, keep access role-appropriate, and store downloaded reports and documents securely. Email recovery and SMS require correctly configured services; local screenshots alone do not mean those services are active.')
callout('Before operational use.','Deployment, hosting, secure configuration, account provisioning, data-protection procedures, and email/SMS services must be completed and approved before barangay staff use the system with live records.')

path=OUT/'Appendix_G_User_Guide_Manual_Updated.docx';doc.save(path);print(path)


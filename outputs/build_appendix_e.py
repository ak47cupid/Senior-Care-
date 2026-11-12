from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ROOT=Path.cwd(); OUT=ROOT/'outputs'/'manuscript'; OUT.mkdir(parents=True,exist_ok=True)
FONT='/Windows/Fonts/arial.ttf'; BOLD='/Windows/Fonts/arialbd.ttf'
def font(size,bold=False):
    try:return ImageFont.truetype(BOLD if bold else FONT,size)
    except:return ImageFont.load_default()
def flow_image(path, lanes, steps, title):
    W=1400; pad=46; lane_h=190; box_w=178; gap=24; H=130+len(lanes)*lane_h
    im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    d.text((pad,24),title,font=font(34,True),fill='#17324d')
    colors=['#e8f1fb','#e9f5ef']
    for li,lane in enumerate(lanes):
        y=85+li*lane_h; d.rounded_rectangle((pad,y,pad+W-2*pad,y+lane_h-16),radius=20,fill=colors[li%2],outline='#cbd7e2',width=2)
        d.text((pad+18,y+12),lane,font=font(22,True),fill='#17324d')
        sy=y+58; total=len(steps[li])*box_w+(len(steps[li])-1)*gap; x=pad+(W-2*pad-total)//2
        centers=[]
        for si,label in enumerate(steps[li]):
            lines=label.split('|'); bh=60+len(lines)*24
            d.rounded_rectangle((x,sy,x+box_w,sy+bh),radius=12,fill='white',outline='#5c7b97',width=2)
            for j,line in enumerate(lines):
                bb=d.textbbox((0,0),line,font=font(17)); d.text((x+(box_w-(bb[2]-bb[0]))/2,sy+12+j*24),line,font=font(17),fill='#172b3a')
            centers.append((x+box_w/2,sy+bh/2))
            if si<len(steps[li])-1:
                x2=x+box_w+gap; mid=sy+bh/2; d.line((x+box_w+3,mid,x2-8,mid),fill='#476a86',width=3); d.polygon([(x2-8,mid),(x2-18,mid-7),(x2-18,mid+7)],fill='#476a86')
            x+=box_w+gap
        # vertical handoff connector at right edge of lane
        if li<len(steps)-1:
            x=pad+W-2*pad-38; y1=y+lane_h-17; y2=y+lane_h+28
            d.line((x,y1,x,y2),fill='#476a86',width=3); d.polygon([(x,y2),(x-7,y2-10),(x+7,y2-10)],fill='#476a86')
    im.save(path)

flow_image(OUT/'appendix_e1_flow.png',['Senior / Applicant','Barangay Office'],[
 ['Visit office|and inquire','Provide paper|form and ID','Complete form|and submit'],
 ['Check details|and documents','Record in|paper log','Prepare report|by hand','File records']
],'Illustrative Current Manual Process')
flow_image(OUT/'appendix_e3_flow.png',['Senior Citizen','System','Staff / Administrator'],[
 ['Register online|or sign in','Submit assistance|request'],
 ['Validate and|save records','Notify reviewer|and applicant','Update status,|timeline, reports'],
 ['Review ID and|requirements','Approve or|return request','Record release|and reporting']
],'Proposed System Process')

doc=Document(); sec=doc.sections[0]; sec.top_margin=Inches(.62); sec.bottom_margin=Inches(.62); sec.left_margin=Inches(.72); sec.right_margin=Inches(.72)
styles=doc.styles; styles['Normal'].font.name='Arial'; styles['Normal'].font.size=Pt(10); styles['Normal'].paragraph_format.space_after=Pt(5)
for s in ['Title','Heading 1','Heading 2']:
    styles[s].font.name='Arial'; styles[s].font.color.rgb=RGBColor(23,50,77)
styles['Title'].font.size=Pt(22); styles['Heading 1'].font.size=Pt(16); styles['Heading 2'].font.size=Pt(12)

def para(text='',style=None,boldlead=None):
    p=doc.add_paragraph(style=style)
    if boldlead and text.startswith(boldlead):
        p.add_run(boldlead).bold=True; p.add_run(text[len(boldlead):])
    else:p.add_run(text)
    return p
def heading(t,l=1): doc.add_heading(t,level=l)
def caption(t):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(2); p.paragraph_format.space_after=Pt(8)
    r=p.add_run(t); r.italic=True; r.font.size=Pt(9); r.font.color.rgb=RGBColor(80,96,110)
def shade(cell,fill):
    pr=cell._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd'); sh.set(qn('w:fill'),fill); pr.append(sh)
def table(headers, rows, widths=None):
    t=doc.add_table(rows=1,cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.style='Table Grid'
    for i,h in enumerate(headers):
        c=t.rows[0].cells[i]; c.text=h; shade(c,'17324D')
        for r in c.paragraphs[0].runs:r.bold=True;r.font.color.rgb=RGBColor(255,255,255);r.font.size=Pt(9)
    trpr=t.rows[0]._tr.get_or_add_trPr(); trpr.append(OxmlElement('w:tblHeader'))
    for vals in rows:
        cells=t.add_row().cells
        for i,val in enumerate(vals):
            cells[i].text=val; cells[i].vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for p in cells[i].paragraphs:
                p.paragraph_format.space_after=Pt(2)
                for r in p.runs:r.font.size=Pt(9)
    return t

p=doc.add_paragraph('Appendix E System Flow Diagrams','Title'); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
p=doc.add_paragraph('Senior Citizen Assistance System for Barangay Services'); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
p.runs[0].font.size=Pt(12); p.runs[0].font.color.rgb=RGBColor(80,96,110)
para('This appendix compares an illustrative manual service process with the implemented online workflow and provides sample report formats for comparison. The current-process diagram is a reconstruction for documentation; confirm it against the participating barangay’s actual practice before treating it as observed evidence. Proposed report layouts are mockups and contain no real beneficiary data.')
heading('E.1 Current Manual Flow of the System')
para('The diagram summarizes a common paper-based intake and reporting sequence for senior citizen services. It is provided as a baseline illustration; the barangay may use different forms, approval steps, or record books.')
doc.add_picture(str(OUT/'appendix_e1_flow.png'),width=Inches(6.9)); caption('Figure E.1. Illustrative current/manual flow before automation.')
heading('E.2 Sample Reports Current System')
para('No actual manually generated report or paper record was included with the project materials. The table below is a blank, illustrative register format showing the type of information that may be consolidated manually. It is not a transcription of barangay records.')
table(['Illustrative paper register field','Example entry (fictional)'],[
('Reporting period','Month / Year'),('Applicant reference','[redacted / blank]'),('Service or assistance requested','[enter service]'),('Date received','[enter date]'),('Review outcome','Pending / Approved / Returned / Rejected'),('Release details','Item, quantity, date, recipient signature'),('Prepared and checked by','Name / signature / date')])
caption('Table E.1. Illustrative manual report register; no real personal data shown.')
heading('E.3 Proposed Flow of the System')
para('The application supports public online registration, staff review of submitted requirements, administrator registration decisions, senior assistance requests, role-based review and release recording, and monthly reporting. Notifications and SMS may inform users of updates; SMS delivery depends on gateway configuration.')
doc.add_picture(str(OUT/'appendix_e3_flow.png'),width=Inches(6.9)); caption('Figure E.2. Proposed system flow based on implemented application workflows.')
para('At a glance: seniors submit and track their own applications and requests; staff and administrators review records according to their roles; distribution details are recorded when assistance is released; and authorized staff can generate monthly reports with CSV export or print/save as PDF.')
heading('E.4 Sample Reports Proposed System')
para('The following mockups illustrate report outputs supported by the application. Values are placeholders, not live system data. The monthly reports use current record statuses and recorded releases; they should not be read as historical month-end snapshots.')
heading('Monthly Assistance Summary',2)
table(['Report item','Illustrative output'],[
('Reporting month','[Month YYYY]'),('Requests received','[system total]'),('Approved / scheduled','[system total]'),('Pending review','[system total]'),('Completed releases','[system total]'),('Unique beneficiaries','[system total]'),('Cash assistance released','₱[system total]')])
heading('Distribution Detail',2)
table(['Release date','Beneficiary ref.','Assistance / item','Quantity','Cash amount','Status'],[
('[date]','[masked ID]','[item / assistance]','[qty/unit]','₱[amount]','Released'),('[date]','[masked ID]','[item / assistance]','[qty/unit]','₱[amount]','Released')])
caption('Table E.2. Proposed monthly report and distribution detail mockup; fields and values are illustrative.')
para('The application’s reports page supports filtering by month and year, CSV download, and Print / Save PDF. Report access is limited to administrator and barangay staff roles. Screenshots from a live configured installation may be inserted here when final evidence is available.')
# footer page number
for section in doc.sections:
    f=section.footer.paragraphs[0]; f.alignment=WD_ALIGN_PARAGRAPH.CENTER
    run=f.add_run('Appendix E  |  '); run.font.size=Pt(8); run.font.color.rgb=RGBColor(100,110,120)
    fld=OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),'PAGE'); f._p.append(fld)
path=OUT/'Appendix_E_System_Flow_Diagrams.docx'; doc.save(path); print(path)


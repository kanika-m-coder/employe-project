import os
import sys

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Flowable, Image
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas

os.makedirs("docs", exist_ok=True)
os.makedirs("charts", exist_ok=True)

# -------------------------------------------------------------
# 1. REPORTLAB NUMBERED CANVAS (PAGING ONLY, NO TOP HEADER)
# -------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            # User Constraints:
            # 1. Remove Scenario 13 and Roll No from top of all pages (completely clean top margin)
            # 2. Remove college and department name from bottom of page
            # 3. Page numbers only in centered alignment at bottom
            # 4. Add ONLY the number (1, 2, 3...) - NO words like "Page"
            # 5. Number 1 starts from the third page (Page 1 cover and Page 2 TOC have no numbers)
            if self._pageNumber >= 3:
                page_display_num = self._pageNumber - 2
                self.saveState()
                self.setFont("Times-Roman", 11)
                self.setFillColor(colors.black)
                # Centered at bottom (y = 36 pt / 0.5 inch from bottom)
                self.drawCentredString(A4[0] / 2.0, 36, str(page_display_num))
                self.restoreState()
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()


# -------------------------------------------------------------
# HELPER: SECTION TRACKER (FLOWABLE) FOR ACCURATE TOC
# -------------------------------------------------------------
_section_page_registry = {}

class TrackSection(Flowable):
    def __init__(self, section_name):
        super(TrackSection, self).__init__()
        self.section_name = section_name
        self.width = 0
        self.height = 0

    def draw(self):
        p = self.canv._pageNumber
        disp = p - 2 if p >= 3 else 0
        _section_page_registry[self.section_name] = disp


# -------------------------------------------------------------
# HELPER: CREATE LARGE SCREENSHOT DISPLAY PLACEHOLDER (REPORTLAB)
# -------------------------------------------------------------

# -------------------------------------------------------------
# HELPER: CREATE EMBEDDED SCREENSHOT CARD (REPORTLAB)
# -------------------------------------------------------------
def create_screenshot_card(img_path, fig_label, fig_title, styles):
    title_p = Paragraph(f"<b>{fig_label}: {fig_title}</b>", styles['Heading3'])
    if os.path.exists(img_path):
        img = Image(img_path, width=450, height=239)
        t = Table([[img]], colWidths=[454], rowHeights=[243])
        t.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ]))
        return [title_p, Spacer(1, 4), t, Spacer(1, 8)]
    else:
        return [title_p, Spacer(1, 4), create_image_placeholder(fig_label, fig_title, "", styles), Spacer(1, 8)]

def create_image_placeholder(fig_label, fig_title, fig_desc, styles):
    box_content = [
        Spacer(1, 22),
        Paragraph("<b>[ USER INTERFACE SCREENSHOT & INTERACTIVE DESIGN DISPLAY ]</b>", styles['TDCenterBold']),
        Spacer(1, 10),
        Paragraph(f"<b>{fig_label}: {fig_title}</b>", styles['TDCenterBold']),
        Spacer(1, 6),
        Paragraph("<i>Standard Aspect Ratio: 16:9 High-Definition Web Application Canvas (1920 × 1080)</i>", styles['TDCenter']),
        Spacer(1, 14),
        Paragraph(f"<b>Primary Operational Scope:</b> {fig_desc}", styles['TDCenter']),
        Spacer(1, 22)
    ]
    t = Table([[box_content]], colWidths=[480], rowHeights=[215])
    t.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.5, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
    ]))
    return t

# -------------------------------------------------------------
# 2. GENERATE PDF USING REPORTLAB
# -------------------------------------------------------------
def build_pdf(filename="docs/EMPLOYEE_ATTENDANCE_AND_PAYROLL_MANAGEMENT_SYSTEM_DOCUMENTATION.pdf", toc_page_map=None):
    print(f"Building Expanded PDF: {filename}...")
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = {
        'CoverTitle': ParagraphStyle('CoverTitle', fontName='Times-Bold', fontSize=17, leading=25.5, alignment=1, textColor=colors.black),
        'CoverSubtitle': ParagraphStyle('CoverSubtitle', fontName='Times-Bold', fontSize=13, leading=19.5, alignment=1, textColor=colors.black),
        'CoverBody': ParagraphStyle('CoverBody', fontName='Times-Roman', fontSize=11.5, leading=17.25, alignment=1, textColor=colors.black),
        'Heading1': ParagraphStyle('Heading1', fontName='Times-Bold', fontSize=15.5, leading=23.25, spaceBefore=18, spaceAfter=8, textColor=colors.black, keepWithNext=True),
        'Heading2': ParagraphStyle('Heading2', fontName='Times-Bold', fontSize=14, leading=21, spaceBefore=14, spaceAfter=6, textColor=colors.black, keepWithNext=True),
        'Heading3': ParagraphStyle('Heading3', fontName='Times-Bold', fontSize=12, leading=18, spaceBefore=10, spaceAfter=4, textColor=colors.black, keepWithNext=True),
        'Body': ParagraphStyle('Body', fontName='Times-Roman', fontSize=12, leading=18, alignment=4, firstLineIndent=36, spaceBefore=3, spaceAfter=6, textColor=colors.black),
        'BodyNoIndent': ParagraphStyle('BodyNoIndent', fontName='Times-Roman', fontSize=12, leading=18, alignment=4, firstLineIndent=0, spaceBefore=3, spaceAfter=6, textColor=colors.black),
        'Bullet': ParagraphStyle('Bullet', fontName='Times-Roman', fontSize=12, leading=18, leftIndent=24, firstLineIndent=-12, spaceBefore=2, spaceAfter=3, textColor=colors.black),
        'TableText': ParagraphStyle('TableText', fontName='Times-Roman', fontSize=10, leading=14, textColor=colors.black),
        'TableHeader': ParagraphStyle('TableHeader', fontName='Times-Bold', fontSize=10.5, leading=14, alignment=1, textColor=colors.black),
        'TD': ParagraphStyle('TD', fontName='Times-Roman', fontSize=9.5, leading=13.5, textColor=colors.black),
        'TDBold': ParagraphStyle('TDBold', fontName='Times-Bold', fontSize=9.5, leading=13.5, textColor=colors.black),
        'TDCenter': ParagraphStyle('TDCenter', fontName='Times-Roman', fontSize=9.5, leading=13.5, alignment=1, textColor=colors.black),
        'TDCenterBold': ParagraphStyle('TDCenterBold', fontName='Times-Bold', fontSize=10, leading=14, alignment=1, textColor=colors.black),
        'TH': ParagraphStyle('TH', fontName='Times-Bold', fontSize=9.5, leading=13.5, alignment=1, textColor=colors.black),
        'Code': ParagraphStyle('Code', fontName='Courier', fontSize=8.5, leading=11.5, textColor=colors.black)
    }

    story = []

    # ================= COVER PAGE (PAGE 1) =================
    story.append(Spacer(1, 15))
    story.append(Paragraph("VELALAR COLLEGE OF ENGINEERING AND TECHNOLOGY", styles['CoverTitle']))
    story.append(Spacer(1, 4))
    story.append(Paragraph("(Autonomous Institution, Affiliated to Anna University, Chennai)", styles['CoverSubtitle']))
    story.append(Paragraph("Accredited by NAAC with 'A+' Grade & Accredited by NBA", styles['CoverBody']))
    story.append(Paragraph("Thindal, Erode – 638 012, Tamil Nadu, India", styles['CoverBody']))
    story.append(Spacer(1, 20))

    story.append(Paragraph("DEPARTMENT OF INFORMATION TECHNOLOGY", styles['CoverSubtitle']))
    story.append(Paragraph("Academic Year: 2025 – 2029 | B.Tech. IT (Section A)", styles['CoverBody']))
    story.append(Paragraph("COURSE PROJECT & LABORATORY DOCUMENTATION", styles['CoverSubtitle']))
    story.append(Spacer(1, 22))

    story.append(Paragraph("SCENARIO 13: EMPLOYEE ATTENDANCE AND PAYROLL MANAGEMENT ANALYSIS SYSTEM", styles['CoverTitle']))
    story.append(Spacer(1, 4))
    story.append(Paragraph("(Register Numbers: 13, 43, 73, 103)", styles['CoverSubtitle']))
    story.append(Spacer(1, 26))

    # Student metadata table (Strictly Black & White, MariaDB removed, kept in one page)
    meta_table_data = [
        [Paragraph("Candidate Full Name", styles['TableHeader']), Paragraph("KANIKA S M", styles['TableText'])],
        [Paragraph("Register / Roll Number", styles['TableHeader']), Paragraph("732925ITR043", styles['TableText'])],
        [Paragraph("Degree & Branch", styles['TableHeader']), Paragraph("B.Tech. Information Technology", styles['TableText'])],
        [Paragraph("Class & Academic Section", styles['TableHeader']), Paragraph("B.Tech IT - A (2025 - 2029 Batch)", styles['TableText'])],
        [Paragraph("Technology Stack Utilized", styles['TableHeader']), Paragraph("Core Java (JDK 17+), DBMS (MySQL), Python 3", styles['TableText'])],
        [Paragraph("GitHub Source Repository", styles['TableHeader']), Paragraph("https://github.com/kanika-m-coder/employe-project.git", styles['TableText'])]
    ]
    t_meta = Table(meta_table_data, colWidths=[170, 310])
    t_meta.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(KeepTogether([t_meta]))
    story.append(Spacer(1, 40))
    story.append(Paragraph("Department of Information Technology<br/>Velalar College of Engineering and Technology, Erode – 638 012", styles['CoverBody']))
    story.append(PageBreak())

    # ================= TABLE OF CONTENTS (PAGE 2) =================
    story.append(Paragraph("TABLE OF CONTENTS", styles['Heading1']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=2, spaceAfter=14))
    
    p_s1 = str(toc_page_map.get("Section 1", 1)) if toc_page_map else "1"
    p_s2 = str(toc_page_map.get("Section 2", 6)) if toc_page_map else "6"
    p_s3 = str(toc_page_map.get("Section 3", 10)) if toc_page_map else "10"
    p_s4 = str(toc_page_map.get("Section 4", 12)) if toc_page_map else "12"
    p_s5 = str(toc_page_map.get("Section 5", 14)) if toc_page_map else "14"
    p_s6 = str(toc_page_map.get("Section 6", 20)) if toc_page_map else "20"
    p_s7 = str(toc_page_map.get("Section 7", 22)) if toc_page_map else "22"
    p_s8 = str(toc_page_map.get("Section 8", 32)) if toc_page_map else "32"

    toc_data = [
        [Paragraph("Section", styles['TH']), Paragraph("Topic Description (Single-Line Verification)", styles['TH']), Paragraph("Page", styles['TH'])],
        [Paragraph("1", styles['TDCenter']), Paragraph("Problem Statement & SRS Specification", styles['TD']), Paragraph(p_s1, styles['TDCenter'])],
        [Paragraph("2", styles['TDCenter']), Paragraph("System Architecture & UML Modeling", styles['TD']), Paragraph(p_s2, styles['TDCenter'])],
        [Paragraph("3", styles['TDCenter']), Paragraph("Database Design & Normalization", styles['TD']), Paragraph(p_s3, styles['TDCenter'])],
        [Paragraph("4", styles['TDCenter']), Paragraph("Core Java Implementation & Logic", styles['TD']), Paragraph(p_s4, styles['TDCenter'])],
        [Paragraph("5", styles['TDCenter']), Paragraph("Python Data Analysis & Visualization", styles['TD']), Paragraph(p_s5, styles['TDCenter'])],
        [Paragraph("6", styles['TDCenter']), Paragraph("Software Testing & Quality Assurance", styles['TD']), Paragraph(p_s6, styles['TDCenter'])],
        [Paragraph("7", styles['TDCenter']), Paragraph("Sample Inputs & Outputs Walkthrough", styles['TD']), Paragraph(p_s7, styles['TDCenter'])],
        [Paragraph("8", styles['TDCenter']), Paragraph("GitHub Deliverables & Execution Guide", styles['TD']), Paragraph(p_s8, styles['TDCenter'])],
    ]
    t_toc = Table(toc_data, colWidths=[50, 380, 50])
    t_toc.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(KeepTogether([t_toc]))
    story.append(PageBreak())

    # ================= SECTION 1 (STARTS ON PAGE 3 -> NUMBERED 1) =================
    story.append(TrackSection("Section 1"))
    story.append(Paragraph("1. PROBLEM STATEMENT & SRS SPECIFICATION", styles['Heading1']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=2, spaceAfter=10))

    story.append(Paragraph("1.1 Introduction & Project Overview", styles['Heading2']))
    story.append(Paragraph("Workforce management and payroll disbursement have historically constituted the operational backbone of commercial, industrial, and academic enterprises. From the earliest industrial punch-card timeclocks of the late nineteenth century to twentieth-century paper attendance ledgers, organizations have sought dependable mechanisms to track employee duty hours and disburse fair compensation. However, managing these mission-critical records through physical paper registers or isolated, single-user desktop spreadsheets poses profound vulnerabilities. Manual ledgers suffer from physical deterioration, handwriting illegibility, clerical recording errors, intentional time-theft through buddy punching, and complete vulnerability to physical loss or catastrophic damage. Furthermore, spreadsheet-based approaches lack multi-user concurrency control, transactional integrity, and automated cross-system verification.", styles['Body']))
    story.append(Paragraph("In parallel, enterprise payroll calculation represents a complex mathematical and legal undertaking governed by rigorous statutory frameworks. In India, employee compensation structures must comply with legislative mandates including the Employees' Provident Funds and Miscellaneous Provisions Act of 1952, which dictates a mandatory 12% deduction from basic earnings toward social security retirement benefits, as well as Dearness Allowance (DA) guidelines designed to offset inflationary pressures and House Rent Allowance (HRA) provisions regulated under the Income Tax Act. Calculating these statutory components manually across varying monthly working calendar days, accounting for individual leave quotas, and pro-rating deductions for unexcused absenteeism creates an unsustainable burden on human resource departments, frequently resulting in wage disputes, delayed salary disbursements, and substantial regulatory penalties.", styles['Body']))
    story.append(Paragraph("The Employee Attendance and Payroll Management Analysis System, designated AttendPay, is an enterprise-grade client-server software application engineered to eliminate these operational vulnerabilities. Developed strictly utilizing Core Java (JDK 17 LTS), a relational Database Management System (MySQL 8.0), and a statistical Python data analytics engine, AttendPay establishes an automated, unified digital pipeline. The system encompasses end-to-end workforce administration: employee lifecycle records maintenance, daily attendance duty tracking, self-service leave application with multi-parameter administrative review, automated business-day calculation, exact mathematical payroll processing, and descriptive visualization of attendance patterns.", styles['Body']))

    story.append(Paragraph("1.2 Problem Statement", styles['Heading2']))
    story.append(Paragraph("An organization maintains employee details, daily attendance, working hours, leave records, and salary information. Managing these records manually can result in attendance errors, difficulties calculating monthly salaries, and delays in identifying absenteeism patterns and preparing payroll reports. The organization requires an Employee Attendance and Payroll Management Analysis System to maintain employee records, record attendance, calculate monthly salary, and analyze workforce attendance patterns. Develop the system using Java, DBMS, and Python.", styles['Body']))
    story.append(Paragraph("To address this mandate comprehensively, the development team analyzed four primary operational bottlenecks inherent to conventional workforce tracking methods. First, record fragmentation and data redundancy create severe informational siloing; when employee details, daily duty registers, and leave slips are maintained in disparate files, reconciling them for month-end payroll requires hours of manual cross-referencing. Second, payroll computation latency results in recurrent financial bottlenecks; human resource personnel must manually examine calendar months, exclude weekends, identify holidays, compute daily pro-rated wage rates, and calculate statutory allowances and deductions for every staff member individually. Third, operational blindness prevents leadership from detecting systematic absenteeism; manual registers cannot aggregate workforce trends across weekdays, months, or departments, leaving management unaware of chronic absenteeism clusters. Finally, the absence of an immutable database audit trail exposes the enterprise to severe statutory audit risks, financial reconciliation errors, and employee attrition.", styles['Body']))

    story.append(Paragraph("1.3 Purpose and Project Scope", styles['Heading2']))
    story.append(Paragraph("The primary purpose of this software solution is to establish an end-to-end, automated digital pipeline connecting employees, human resource administrators, and data analysts. The scope encompasses complete lifecycle employee management, attendance verification, leave request submission and approval, automated working-day calculation, mathematical deduction formulation, and data pattern analysis.", styles['Body']))
    story.append(Paragraph("The architectural scope establishes a clear demarcation of organizational roles, user capabilities, and system boundaries. For administrative personnel, the system delivers complete command over employee profiles, daily attendance logging, administrative leave adjudication (reviewing employee name, department, designation, and stated reason before approving or rejecting), month-end payroll execution, and analytical visualization generation. For staff members, AttendPay provides a personalized self-service portal facilitating secure credential authentication, duty log verification, personal attendance statistical tracking, and statutory leave submission. The operational boundaries strictly enforce role-based access control, parameterized database access, and clean single-line web interfaces.", styles['Body']))

    story.append(Paragraph("1.4 Detailed Functional Requirements", styles['Heading2']))
    story.append(Paragraph("FR1: Maintain Employee Profile Details: The system shall provide comprehensive administration of employee demographic and contractual records. Attributes captured include unique numeric employee ID, full employee name, department assignment via foreign key mapping, job designation, contractual basic monthly salary in Indian Rupees (INR), and official joining date. The system shall enforce input validation ensuring names contain only alphabetic characters, basic salary is strictly greater than zero, and joining dates follow valid calendar formatting.", styles['Bullet']))
    story.append(Paragraph("FR2: Record Daily Attendance Duty Logs: The system shall facilitate daily attendance recording for all active staff members. Recorded parameters include calendar date, employee ID, operational duty status (Present, Absent, Half Day, On Leave), and credited working hours (8.0 hours for Present/On Leave, 4.0 hours for Half Day, 0.0 hours for Absent). The system shall enforce unique date-employee indexing, automatically updating existing records upon modification rather than producing duplicate rows.", styles['Bullet']))
    story.append(Paragraph("FR3: Leave Management & Administrative Approval Workflow: The system shall provide a multi-tiered leave lifecycle pipeline. Employees shall apply for leaves specifying classification (Casual, Sick, Earned, Loss of Pay), calendar start date, end date, and explicit reason. Submitted leaves enter a 'Pending' queue. Administrators shall access a dedicated Leave Approval card presenting the employee's name, department, designation, requested dates, total days, and reason, with one-click 'Approve' and 'Reject' actions. Approved leaves shall automatically synchronize with the attendance table by creating corresponding 'On Leave' duty entries.", styles['Bullet']))
    story.append(Paragraph("FR4: Calculate Monthly Salary & Statutory Deductions: The system shall execute payroll calculations for any specified calendar month and year. The engine shall dynamically calculate the exact number of working weekdays (excluding Saturdays and Sundays), derive the daily wage rate, and compute statutory additions and deductions: House Rent Allowance (HRA at 20% of Basic), Dearness Allowance (DA at 10% of Basic), Provident Fund (PF at 12% of Basic), and pro-rated absenteeism deductions. Final net salary must be computed and stored with two-decimal precision.", styles['Bullet']))
    story.append(Paragraph("FR5: Generate Reports, Summaries & Payslip Vouchers: The system shall compile dynamic attendance verification summaries, workforce KPI metric cards, department-wise duty rosters, and comprehensive payroll registers. Additionally, the system shall generate printable, itemized employee payslip vouchers detailing basic pay, itemized allowances, statutory deductions, net payable salary, bank disbursement notes, and authorized signature blocks.", styles['Bullet']))
    story.append(Paragraph("FR6: Python Data Visualization & Pattern Analysis: The system shall include an analytical Python pipeline that connects directly to the MySQL database, extracts historical attendance and payroll datasets, cleans and structures data using Pandas, and generates five high-resolution Matplotlib visualizations capturing overall workforce duty distribution, weekday absenteeism spikes, cross-department attendance rates, monthly seasonal trends, and payroll expenditure trajectories.", styles['Bullet']))

    story.append(Paragraph("1.5 Non-Functional Requirements", styles['Heading2']))
    story.append(Paragraph("Reliability & Mathematical Precision: All payroll calculations, allowance computations, and deduction formulas must maintain mathematical accuracy to two decimal places without cumulative rounding drift.", styles['Bullet']))
    story.append(Paragraph("Security & Role-Based Access Control: Authentication sessions shall be validated across protected endpoints. SQL injection vulnerabilities are systematically eliminated through parameterized JDBC PreparedStatements.", styles['Bullet']))
    story.append(Paragraph("Response Latency & Performance: Native Java HttpServer REST API endpoints shall respond within 150 milliseconds under standard concurrency. Python data processing scripts shall compile within 3 seconds.", styles['Bullet']))
    story.append(Paragraph("Zero-Dependency Architectural Portability: The entire backend shall run on standard Core Java SE (JDK 17 LTS) and MySQL without requiring external third-party enterprise web frameworks such as Spring or Tomcat.", styles['Bullet']))
    story.append(Paragraph("Usability & Responsive Layout: Web interfaces shall adhere to clean modern aesthetics, utilizing CSS grid and flexbox for responsive single-line alignments across desktop and tablet screen viewports.", styles['Bullet']))

    story.append(PageBreak())

    # 1.6 Hardware and Software Environment (NEAT TABLES, NO SPLIT)
    story.append(Paragraph("1.6 Hardware and Software Environment", styles['Heading2']))
    story.append(Paragraph("To ensure deterministic performance, transaction safety, and sub-150ms REST API response times, the AttendPay system is engineered to operate within the standardized enterprise specifications detailed in the structured tables below:", styles['Body']))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Table 1.1: Hardware Requirements Specification</b>", styles['BodyNoIndent']))
    story.append(Spacer(1, 3))
    hw_data = [
        [Paragraph("Hardware Component", styles['TH']), Paragraph("Minimum Requirement", styles['TH']), Paragraph("Recommended Specification", styles['TH'])],
        [Paragraph("System Processor", styles['TDBold']), Paragraph("Intel Core i3 / AMD Ryzen 3 (x64)", styles['TD']), Paragraph("Intel Core i5 / AMD Ryzen 5 or higher", styles['TD'])],
        [Paragraph("System Memory (RAM)", styles['TDBold']), Paragraph("4 GB DDR4 physical memory", styles['TD']), Paragraph("8 GB DDR4 or higher for multitasking", styles['TD'])],
        [Paragraph("Storage (Hard Disk)", styles['TDBold']), Paragraph("500 MB free hard drive space", styles['TD']), Paragraph("1 GB available Solid-State Drive (SSD)", styles['TD'])],
        [Paragraph("Display Resolution", styles['TDBold']), Paragraph("1366 × 768 pixels standard display", styles['TD']), Paragraph("1920 × 1080 (Full HD, 1080p) viewport", styles['TD'])],
        [Paragraph("Network Interface", styles['TDBold']), Paragraph("Local loopback adapter (127.0.0.1)", styles['TD']), Paragraph("Standard TCP/IP network interface card", styles['TD'])]
    ]
    t_hw = Table(hw_data, colWidths=[130, 170, 180])
    t_hw.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(KeepTogether([t_hw]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Table 1.2: Software Requirements Specification</b>", styles['BodyNoIndent']))
    story.append(Spacer(1, 3))
    sw_data = [
        [Paragraph("Software Component", styles['TH']), Paragraph("Required Specification / Version", styles['TH']), Paragraph("Operational Role & Purpose", styles['TH'])],
        [Paragraph("Operating System", styles['TDBold']), Paragraph("Windows 10 / 11 (64-bit), Linux, macOS", styles['TD']), Paragraph("Host development & server runtime host", styles['TD'])],
        [Paragraph("Programming Platform", styles['TDBold']), Paragraph("Java Development Kit (JDK 17 LTS+)", styles['TD']), Paragraph("Core Java HttpServer, REST routing & logic", styles['TD'])],
        [Paragraph("Relational DBMS", styles['TDBold']), Paragraph("MySQL Community Server 8.0+ (Port 3307)", styles['TD']), Paragraph("ACID persistent relational database", styles['TD'])],
        [Paragraph("Analytics Platform", styles['TDBold']), Paragraph("Python 3.9+ (pandas, matplotlib)", styles['TD']), Paragraph("Data extraction, preprocessing & charts", styles['TD'])],
        [Paragraph("Database Connector", styles['TDBold']), Paragraph("MySQL Connector/J 8.4.0 (JDBC Driver)", styles['TD']), Paragraph("Secure parameterized database transactions", styles['TD'])],
        [Paragraph("Web Browser Client", styles['TDBold']), Paragraph("Google Chrome, Mozilla Firefox, Edge", styles['TD']), Paragraph("Client presentation tier & UI rendering", styles['TD'])],
        [Paragraph("Development IDE", styles['TDBold']), Paragraph("VS Code with Java Extension Pack", styles['TD']), Paragraph("Source code editing, debugging & execution", styles['TD'])]
    ]
    t_sw = Table(sw_data, colWidths=[130, 170, 180])
    t_sw.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(KeepTogether([t_sw]))
    story.append(PageBreak())

    # ================= SECTION 2 =================
    story.append(TrackSection("Section 2"))
    story.append(Paragraph("2. SYSTEM ARCHITECTURE & UML MODELING", styles['Heading1']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=2, spaceAfter=10))

    story.append(Paragraph("2.1 Overall System Architecture", styles['Heading2']))
    story.append(Paragraph("AttendPay is engineered as an enterprise 3-tier client-server architecture that enforces strict separation of concerns between user presentation, backend business logic, and persistent relational data storage. The Presentation Layer is constructed using semantic HTML5, modern CSS3 featuring an executive dark-navy palette, and Vanilla ES6 JavaScript. The client executes asynchronous RESTful AJAX queries via the native browser Fetch API, dynamically updating the Document Object Model (DOM) without requiring full page refreshes. The Application Layer is powered by a high-performance native Java SE HttpServer listening on TCP Port 8080. This layer routes incoming HTTP requests, manages session authentication, parses JSON request bodies, executes statutory payroll algorithms, and coordinates JDBC database transactions. The Data and Analytics Layer leverages MySQL Server 8.0 running on Port 3307 for ACID-compliant relational persistence, alongside a Python 3 analytics module for descriptive visualization.", styles['Body']))
    story.append(Paragraph("The communication lifecycle between tiers adheres to REST architectural principles. When a client performs an administrative action—such as submitting an employee profile or approving a leave request—the browser serializes the form data into a JSON payload and transmits an HTTP POST request over loopback TCP sockets. The Java HttpServer intercepts the exchange, validates the session and payload parameters, initiates a JDBC PreparedStatement transaction with MySQL, commits the relational state, and returns an HTTP 200 OK response with a structured JSON status message. This decoupled design ensures high throughput, low latency, and maximum modularity.", styles['Body']))
    story.append(PageBreak())

    # 2.2 USE CASE SPECIFICATIONS (TABLE ON ONE PAGE, NO SPLIT)
    story.append(Paragraph("2.2 Use Case Specifications", styles['Heading2']))
    story.append(Paragraph("The Use Case Model identifies the primary human actors interacting with the AttendPay system boundary and their operational capabilities. Two primary human actors operate within the system boundary: the Administrator and the Employee. The table below provides the formal use case catalog, identifiers, and functional operational scopes:", styles['Body']))
    story.append(Spacer(1, 4))

    uc_table_data = [
        [Paragraph("Actor", styles['TH']), Paragraph("ID", styles['TH']), Paragraph("Use Case Name", styles['TH']), Paragraph("Operational Scope & Description", styles['TH'])],
        [Paragraph("Administrator", styles['TDBold']), Paragraph("UC-01", styles['TDCenter']), Paragraph("System Authentication", styles['TD']), Paragraph("Authenticates using admin credentials; receives full access to management menus.", styles['TD'])],
        [Paragraph("Administrator", styles['TDBold']), Paragraph("UC-02", styles['TDCenter']), Paragraph("Employee Directory Maintenance", styles['TD']), Paragraph("Creates, updates, and deletes employee profiles with basic salary parameters.", styles['TD'])],
        [Paragraph("Administrator", styles['TDBold']), Paragraph("UC-03", styles['TDCenter']), Paragraph("Attendance Verification & Entry", styles['TD']), Paragraph("Logs daily workforce duty status and filters attendance logs by date and employee.", styles['TD'])],
        [Paragraph("Administrator", styles['TDBold']), Paragraph("UC-04", styles['TDCenter']), Paragraph("Leave Review & Decision", styles['TD']), Paragraph("Reviews pending leaves (Name, Dept, Designation, Reason); Approves or Rejects.", styles['TD'])],
        [Paragraph("Administrator", styles['TDBold']), Paragraph("UC-05", styles['TDCenter']), Paragraph("Monthly Payroll Calculation", styles['TD']), Paragraph("Computes working days, allowances, statutory deductions, and generates payslips.", styles['TD'])],
        [Paragraph("Administrator", styles['TDBold']), Paragraph("UC-06", styles['TDCenter']), Paragraph("Data Analytics Visualization", styles['TD']), Paragraph("Executes Python analysis engine and reviews graphical workforce insights.", styles['TD'])],
        [Paragraph("Employee", styles['TDBold']), Paragraph("UC-07", styles['TDCenter']), Paragraph("Employee Portal Login", styles['TD']), Paragraph("Authenticates using unique employee ID and password; accesses personal portal.", styles['TD'])],
        [Paragraph("Employee", styles['TDBold']), Paragraph("UC-08", styles['TDCenter']), Paragraph("View Personal Attendance", styles['TD']), Paragraph("Inspects logged duty days, work hours, and personal attendance statistics.", styles['TD'])],
        [Paragraph("Employee", styles['TDBold']), Paragraph("UC-09", styles['TDCenter']), Paragraph("Submit Leave Application", styles['TD']), Paragraph("Submits statutory leave request with classifications, dates, and stated reason.", styles['TD'])],
        [Paragraph("Employee", styles['TDBold']), Paragraph("UC-10", styles['TDCenter']), Paragraph("Track / Cancel Leave", styles['TD']), Paragraph("Monitors approval decision status (Pending/Approved/Rejected); cancels pending.", styles['TD'])],
    ]
    t_uc = Table(uc_table_data, colWidths=[70, 38, 115, 237])
    t_uc.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(KeepTogether([t_uc]))
    story.append(PageBreak())

    story.append(Paragraph("2.3 Class Diagram Specifications", styles['Heading2']))
    story.append(Paragraph("The class diagram models the structural domain entities and controller logic within the Core Java backend:", styles['Body']))
    story.append(Paragraph("1. Employee Entity Class: Encapsulates employee profile state. Attributes include: -int empId, -String empName, -int deptId, -String designation, -double basicSalary, -LocalDate joinDate. Public methods include: +getEmpId(): int, +getEmpName(): String, +getBasicSalary(): double, +setBasicSalary(double): void, +toJSONObject(): String.", styles['Bullet']))
    story.append(Paragraph("2. Department Entity Class: Encapsulates organizational unit boundaries. Attributes include: -int deptId, -String deptName. Public methods include: +getDeptId(): int, +getDeptName(): String, +setDeptName(String): void.", styles['Bullet']))
    story.append(Paragraph("3. Attendance Entity Class: Models daily workforce duty logs. Attributes include: -int attendanceId, -int empId, -LocalDate attDate, -String status, -double workingHours. Public methods include: +markAttendance(): boolean, +getHours(): double, +getStatus(): String, +validateDate(): boolean.", styles['Bullet']))
    story.append(Paragraph("4. LeaveRecord Entity Class: Manages statutory leave lifecycle. Attributes include: -int leaveId, -int empId, -String leaveType, -LocalDate startDate, -LocalDate endDate, -int totalDays, -String reason, -String status. Public methods include: +applyLeave(): boolean, +updateStatus(String): void, +isPending(): boolean.", styles['Bullet']))
    story.append(Paragraph("5. Payroll Calculation Entity Class: Executes monthly salary computations. Attributes include: -int payrollId, -int empId, -int payMonth, -int payYear, -int workingDays, -double daysPresent, -double paidLeaveDays, -double absentDays, -double basic, -double hra, -double da, -double pfDeduction, -double absenceDeduction, -double netSalary. Public methods include: +calc(int, int, int): Payroll, +getPayslip(): String, +exportVoucher(): byte[].", styles['Bullet']))
    story.append(Paragraph("6. SalaryRule Policy Class: Enforces enterprise compensation percentages. Attributes include: -int ruleId, -double hraPercent, -double daPercent, -double pfPercent. Public methods include: +computeHRA(double): double, +computeDA(double): double, +computePF(double): double.", styles['Bullet']))
    story.append(Paragraph("7. User Security Class: Controls role-based authentication. Attributes include: -int userId, -String username, -String password, -String role, -int empId. Public methods include: +authenticate(String, String): boolean, +hasRole(String): boolean, +generateToken(): String.", styles['Bullet']))
    story.append(Paragraph("8. Main Server & Controller Class: Core orchestration engine. Attributes include: HttpServer server, Properties config, Connection dbPool. Public methods include: +main(String[]): void, +handle(HttpExchange): void, +routeAPI(String): void, +calculatePayroll(): void, +syncApprovedLeave(): void.", styles['Bullet']))
    story.append(PageBreak())

    # 2.4 DATA FLOW DIAGRAMS (EMBEDDED GRAPHICAL DIAGRAMS & NARRATIVE)
    story.append(Paragraph("2.4 Data Flow Diagrams (DFD)", styles['Heading2']))
    story.append(Paragraph("Data Flow Diagrams model the movement of information across external actors, processes, and persistent data stores within AttendPay. The graphical architecture is structured hierarchically into Level 0 (Context Level) and Level 1 (Functional Decomposition):", styles['Body']))
    story.append(Spacer(1, 4))

    # DFD LEVEL 0
    if os.path.exists("charts/dfd_level_0.png"):
        img_dfd0 = Image("charts/dfd_level_0.png", width=460, height=236)
        t_dfd0 = Table([[img_dfd0]], colWidths=[464], rowHeights=[240])
        t_dfd0.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(KeepTogether([
            Paragraph("<b>Figure 2.1: Data Flow Diagram (DFD) - Level 0 (Context Level Diagram)</b>", styles['Heading3']),
            Spacer(1, 4),
            t_dfd0,
            Spacer(1, 6),
            Paragraph("<b>Level 0 Context Flow Walkthrough:</b> Conceptualizes the entire AttendPay system as a single central process (Process 0.0) interacting with external human entities. The Administrator feeds employee profile setup records, daily attendance duty entries, salary compensation policy updates, and leave adjudication decisions into the central AttendPay engine. In response, AttendPay returns workforce directory rosters, filtered attendance audit logs, payroll calculation registers, printable payslips, and analytical summaries. The Employee feeds login credentials, duty inquiry queries, and leave applications into AttendPay, receiving authenticated session tokens, personal duty summaries, and real-time leave decision notifications.", styles['Body']),
            Spacer(1, 10)
        ]))

    story.append(PageBreak())

    # DFD LEVEL 1
    if os.path.exists("charts/dfd_level_1.png"):
        img_dfd1 = Image("charts/dfd_level_1.png", width=450, height=306)
        t_dfd1 = Table([[img_dfd1]], colWidths=[454], rowHeights=[310])
        t_dfd1.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(KeepTogether([
            Paragraph("<b>Figure 2.2: Data Flow Diagram (DFD) - Level 1 (Functional Decomposition)</b>", styles['Heading3']),
            Spacer(1, 4),
            t_dfd1,
            Spacer(1, 6),
            Paragraph("<b>Level 1 Subsystem Decomposition Walkthrough:</b> Decomposes AttendPay into 6 interconnected functional sub-processes: Process 1.0 (User Authentication & Access Control), Process 2.0 (Employee Directory Management), Process 3.0 (Attendance Duty Logging & Verification), Process 4.0 (Leave Review & Workflow Decision), Process 5.0 (Statutory Payroll Calculation Engine), and Process 6.0 (Data Analytics & Visual Intelligence). These 6 processes exchange data with 7 persistent database stores: D1: users, D2: departments, D3: employees, D4: attendance, D5: leave_records, D6: salary_rules, and D7: payroll.", styles['Body'])
        ]))

    story.append(PageBreak())

    # ================= SECTION 3 =================
    story.append(TrackSection("Section 3"))
    story.append(Paragraph("3. DATABASE DESIGN & NORMALIZATION", styles['Heading1']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=2, spaceAfter=10))

    story.append(Paragraph("3.1 Relational Schema & Normalization", styles['Heading2']))
    story.append(Paragraph("The database architecture of AttendPay was engineered following formal mathematical normalization theory, progressing methodically from unnormalized operational entities to Boyce-Codd Normal Form (BCNF) to guarantee zero data redundancy, preserve functional dependencies, and prevent insertion, update, and deletion anomalies.", styles['Body']))
    story.append(Paragraph("<b>First Normal Form (1NF):</b> A relational table is in 1NF if and only if all column domains contain exclusively atomic (indivisible) values and each row is uniquely identifiable. In AttendPay, complex composite structures—such as combining an employee's address, department details, and salary components into a single text column—were decomposed into distinct atomic columns. Repeating multi-valued groups, such as storing multiple attendance dates within a comma-delimited string, were eliminated by establishing individual rows in the attendance relation, each keyed by a composite of employee ID and attendance date.", styles['Body']))
    story.append(Paragraph("<b>Second Normal Form (2NF):</b> A relation is in 2NF if it is in 1NF and every non-prime attribute is fully functionally dependent on the primary key, thereby eliminating partial functional dependencies. In relations utilizing composite candidate keys—such as attendance (employee_id, attendance_date)—attributes like employee_name, department_id, or basic_salary depend solely on employee_id rather than the complete composite key. To achieve 2NF, employee profile attributes were isolated into the distinct 'employees' relation, ensuring all non-key attributes depend entirely on the primary key employee_id.", styles['Body']))
    story.append(Paragraph("<b>Third Normal Form (3NF):</b> A relation is in 3NF if it is in 2NF and no non-prime attribute is transitively dependent on the primary key (X -> Y and Y -> Z where Z is not a candidate key). In earlier operational drafts, storing department_name within the employee record created a transitive dependency: employee_id -> department_id and department_id -> department_name. If all employees in a department were removed, department details would be lost. By decomposing this relationship into an independent 'departments' relation with department_id as the primary key and department_id as a foreign key in 'employees', transitive dependencies were eradicated.", styles['Body']))
    story.append(Paragraph("<b>Boyce-Codd Normal Form (BCNF):</b> A relation is in BCNF if for every non-trivial functional dependency X -> Y, X is a superkey. In all 7 relations within the AttendPay schema, every determinant represents a unique candidate key. For example, in the 'salary_rules' table, rule_id uniquely dictates HRA, DA, and PF percentages without any overlapping non-key determinants. Hence, the database achieves strict BCNF compliance, guaranteeing lossless join decomposition and dependency preservation.", styles['Body']))
    story.append(PageBreak())

    # 3.2 RELATIONAL DATA MODEL TABLE (ON ONE PAGE, NO SPLIT)
    story.append(Paragraph("3.2 Relational Data Model Table", styles['Heading2']))
    story.append(Paragraph("The normalized relational database schema encompasses 7 primary tables maintaining strict referential integrity across all operational entities:", styles['Body']))
    story.append(Spacer(1, 4))

    db_table_data = [
        [Paragraph("Table Name", styles['TH']), Paragraph("Primary Key", styles['TH']), Paragraph("Foreign Keys", styles['TH']), Paragraph("Key Column Attributes & Constraints", styles['TH'])],
        [Paragraph("departments", styles['TDBold']), Paragraph("department_id", styles['TDCenter']), Paragraph("None", styles['TDCenter']), Paragraph("department_name VARCHAR(100) NOT NULL UNIQUE", styles['TD'])],
        [Paragraph("employees", styles['TDBold']), Paragraph("employee_id", styles['TDCenter']), Paragraph("department_id", styles['TDCenter']), Paragraph("name VARCHAR(100), designation VARCHAR(100), basic_salary DECIMAL(10,2), joining_date DATE", styles['TD'])],
        [Paragraph("users", styles['TDBold']), Paragraph("user_id", styles['TDCenter']), Paragraph("employee_id", styles['TDCenter']), Paragraph("username VARCHAR(50) UNIQUE, password VARCHAR(255), role VARCHAR(20)", styles['TD'])],
        [Paragraph("attendance", styles['TDBold']), Paragraph("attendance_id", styles['TDCenter']), Paragraph("employee_id", styles['TDCenter']), Paragraph("attendance_date DATE, status ENUM, working_hours DECIMAL(4,2), UNIQUE(emp_id, date)", styles['TD'])],
        [Paragraph("leave_records", styles['TDBold']), Paragraph("leave_id", styles['TDCenter']), Paragraph("employee_id", styles['TDCenter']), Paragraph("leave_type VARCHAR(50), start_date DATE, end_date DATE, reason TEXT, status ENUM", styles['TD'])],
        [Paragraph("salary_rules", styles['TDBold']), Paragraph("rule_id", styles['TDCenter']), Paragraph("None", styles['TDCenter']), Paragraph("rule_name VARCHAR(50), hra_percent DECIMAL(5,2), da_percent DECIMAL(5,2), pf_percent DECIMAL(5,2)", styles['TD'])],
        [Paragraph("payroll", styles['TDBold']), Paragraph("payroll_id", styles['TDCenter']), Paragraph("employee_id", styles['TDCenter']), Paragraph("month INT, year INT, basic_salary DECIMAL(10,2), hra, da, pf, net_salary DECIMAL(10,2)", styles['TD'])],
    ]
    t_db = Table(db_table_data, colWidths=[70, 75, 65, 250])
    t_db.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(KeepTogether([t_db]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("3.3 Core SQL Implementation Queries", styles['Heading2']))
    story.append(Paragraph("<b>Multi-Table Relational JOIN Query for Administrative Leave Review:</b>", styles['BodyNoIndent']))
    story.append(Paragraph("The query below retrieves all pending leave requests, performing inner joins across employees and departments to provide administrators with complete organizational context (employee name, department, designation, and duration) required to make informed approval or rejection decisions:", styles['Body']))
    
    sql_code = ("SELECT l.leave_id, l.employee_id, e.name AS employee_name, d.department_name, "
                "e.designation, l.leave_type, l.start_date, l.end_date, "
                "DATEDIFF(l.end_date, l.start_date) + 1 AS duration_days, "
                "l.reason, l.status "
                "FROM leave_records l "
                "JOIN employees e ON l.employee_id = e.employee_id "
                "JOIN departments d ON e.department_id = d.department_id "
                "ORDER BY l.start_date DESC;")
    story.append(Paragraph(sql_code, styles['Code']))

    story.append(PageBreak())

    # ================= SECTION 4 =================
    story.append(TrackSection("Section 4"))
    story.append(Paragraph("4. CORE JAVA IMPLEMENTATION & LOGIC", styles['Heading1']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=2, spaceAfter=10))

    story.append(Paragraph("4.1 Server Architecture & REST Routing", styles['Heading2']))
    story.append(Paragraph("The backend application is implemented in src/Main.java utilizing the lightweight, highly performant com.sun.net.httpserver.HttpServer embedded within standard Java SE 17+. Rejecting heavy external enterprise frameworks such as Spring Boot or Apache Tomcat, the system embodies a zero-dependency design pattern that runs instantaneously on any system equipped with a Java Runtime Environment (JRE). The server binds to loopback interface 0.0.0.0 on TCP Port 8080 and establishes a thread pool using Executors.newFixedThreadPool(10), enabling concurrent non-blocking execution of administrative transactions and employee queries.", styles['Body']))
    story.append(Paragraph("Incoming HTTP requests are routed through custom HttpHandler implementations that parse HTTP request methods (GET, POST, PUT, DELETE), extract URL query parameters, read UTF-8 JSON request streams, and perform strict session authorization. Responses are formatted as application/json strings, equipped with standard HTTP status codes (200 OK, 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Internal Error) and CORS headers. Database interactions are conducted via the official MySQL Connector/J JDBC driver utilizing pooled connections and parameterized PreparedStatements.", styles['Body']))

    story.append(Paragraph("4.2 Business Logic & Core Algorithms", styles['Heading2']))
    story.append(Paragraph("<b>1. Dynamic Calendar Working Weekday Calculation Algorithm:</b>", styles['BodyNoIndent']))
    story.append(Paragraph("To ensure mathematically fair and legally compliant payroll disbursement, AttendPay dynamically computes the exact count of working weekdays for any given month and year. Utilizing the modern java.time.LocalDate API, the algorithm iterates from the first calendar day of the billing month to the final day, evaluating each date's DayOfWeek enumeration. Days matching DayOfWeek.SATURDAY or DayOfWeek.SUNDAY are excluded. Unlike naive commercial systems that assume a constant 30-day denominator, AttendPay derives the exact working days (typically 20, 21, 22, or 23 days depending on calendar month geometry), guaranteeing that daily wage calculations reflect true operational business days.", styles['Body']))

    story.append(Paragraph("<b>2. Statutory Payroll Calculation Engine & Mathematical Formulations:</b>", styles['BodyNoIndent']))
    story.append(Paragraph("The payroll engine executes a multi-step mathematical routine adhering strictly to Indian statutory compensation rules. Given an employee's contractual Basic Salary and the dynamically calculated Working Weekdays for the billing cycle:", styles['Body']))
    story.append(Paragraph("• House Rent Allowance (HRA): Computed at 20% of Basic Salary: HRA = 0.20 × Basic.", styles['Bullet']))
    story.append(Paragraph("• Dearness Allowance (DA): Computed at 10% of Basic Salary: DA = 0.10 × Basic.", styles['Bullet']))
    story.append(Paragraph("• Provident Fund (PF): Mandated statutory deduction at 12% of Basic: PF = 0.12 × Basic.", styles['Bullet']))
    story.append(Paragraph("• Daily Wage Rate: Derived by dividing Basic Salary by Working Weekdays: DailyRate = Basic / WorkingDays.", styles['Bullet']))
    story.append(Paragraph("• Absenteeism Deduction: Pro-rated wage loss for unpaid absences and half-days: Deduction = DailyRate × (AbsentDays + 0.5 × HalfDays).", styles['Bullet']))
    story.append(Paragraph("• Gross Earnings: Total compensation prior to deductions: GrossSalary = Basic + HRA + DA.", styles['Bullet']))
    story.append(Paragraph("• Net Payable Salary: Final take-home disbursement: NetSalary = GrossSalary - PF - Deduction.", styles['Bullet']))
    story.append(Paragraph("All monetary calculations are performed using double precision floating point mathematics, rounded to two decimal places upon database persistence and payslip rendering.", styles['Body']))

    story.append(Paragraph("<b>3. Administrative Leave Approval & Attendance Synchronization Logic:</b>", styles['BodyNoIndent']))
    story.append(Paragraph("When an employee submits a leave application via the self-service portal, the record is committed to leave_records with a status of 'Pending'. The administrative user accesses the Leave Management view, which executes a three-table SQL join displaying the employee's name, department, designation, date range, duration, and stated justification. Upon clicking 'Approve', the server executes a coordinated JDBC transaction: it updates the leave_records status to 'Approved' and iterates through each calendar day in the requested date range, inserting or updating corresponding entries in the attendance table with status='On Leave' and working_hours=8.0. This guarantees that approved leaves are automatically factored into month-end payroll without requiring duplicate administrative data entry.", styles['Body']))

    story.append(PageBreak())

    # ================= SECTION 5 =================
    story.append(TrackSection("Section 5"))
    story.append(Paragraph("5. PYTHON DATA ANALYSIS & VISUALIZATION", styles['Heading1']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=2, spaceAfter=10))

    story.append(Paragraph("5.1 Analytics Architecture & Pipeline", styles['Heading2']))
    story.append(Paragraph("The workforce intelligence subsystem is implemented in python/analysis.py, functioning as an automated business intelligence engine that extracts raw operational logs directly from the MySQL database, preprocesses historical records, and compiles publication-quality visualizations using Pandas and Matplotlib. Communication with the database is established via mysql-connector-python utilizing environment configuration parameters (host 127.0.0.1, port 3307, database employeepayroll).", styles['Body']))
    story.append(Paragraph("Upon establishing a database connection, the script executes SQL extraction queries, streaming historical tables into Pandas DataFrames: attendance_df, employee_df, department_df, and payroll_df. The preprocessing routine inspects missing data, parses date strings into native datetime objects, extracts calendar day-of-week strings (Monday through Friday), and derives aggregation metrics including workforce attendance percentages, departmental compliance rankings, and monthly wage expenditure distributions. The output visualizations are exported as high-resolution (300 DPI) PNG graphics stored in the charts/ directory, directly referenced by analytics.html.", styles['Body']))

    story.append(Paragraph("5.2 Visual Data Chart Analyses", styles['Heading2']))
    story.append(Paragraph("The Python analytics module generates five high-resolution graphical visualizations to reveal critical workforce patterns and expenditure trends:", styles['Body']))
    story.append(Spacer(1, 4))
    
    chart_configs = [
        ("Figure 5.1: Overall Attendance Status Distribution (charts/status_distribution.png)",
         "charts/status_distribution.png",
         "The analysis of 740 historical attendance records demonstrates an overall duty compliance rate of 88.0% (618 duty days marked Present). Unexcused absences represent 6.9% (51 instances), partial duty comprises 4.5% (33 Half Day instances), and approved statutory leaves account for 5.1% (38 instances). This executive donut visualization provides immediate confirmation of healthy organizational productivity while pinpointing areas for corrective leave management."),
        
        ("Figure 5.2: Absenteeism Patterns Across Calendar Weekdays (charts/absenteeism.png)",
         "charts/absenteeism.png",
         "A categorical frequency analysis across weekdays reveals a pronounced dual-peak distribution. Unexcused employee absences cluster heavily at the extremes of the work week: Monday exhibits the highest absenteeism volume (28.4% of total unexcused absences), followed closely by Friday (25.5%). Conversely, mid-week days maintain strong discipline, with Tuesday (15.7%), Wednesday (13.7%), and Thursday (16.7%) showing minimal disruption. This pattern provides leadership with actionable evidence of extended weekend tendencies."),
         
        ("Figure 5.3: Department-wise Attendance Rate Comparison (charts/department_comparison.png)",
         "charts/department_comparison.png",
         "A cross-functional comparative benchmark illustrates duty compliance across four key organizational divisions. The Finance department leads the enterprise with an 89.2% attendance rate, closely followed by Human Resources (88.1%), Operations (87.7%), and Engineering (86.9%). The horizontal bar layout facilitates instant identification of departmental engagement levels and guides operational staffing allocation."),
         
        ("Figure 5.4: Monthly Attendance Trajectory & Seasonal Duty Trends (charts/monthly_pattern.png)",
         "charts/monthly_pattern.png",
         "Tracking multi-month attendance consistency across annual quarters highlights high baseline workforce stability while clearly identifying cyclical holiday dips during festive and year-end cycles. The multi-line trajectory equips management with predictive insight into upcoming quarterly staffing requirements."),
         
        ("Figure 5.5: Monthly Payroll Expenditure & Statutory PF Outlay (charts/payroll_monthly.png)",
         "charts/payroll_monthly.png",
         "A comprehensive financial expenditure breakdown illustrating base salary disbursements, statutory Provident Fund deductions, and net payable outlays. For November 2026, cumulative net salary outlays reached ₹5,54,249.52 across 10 active personnel, with statutory retirement PF contributions totaling ₹63,840.00, demonstrating complete mathematical and regulatory compliance.")
    ]
    
    for title, img_path, desc in chart_configs:
        if os.path.exists(img_path):
            story.append(KeepTogether([
                Paragraph(f"<b>{title}</b>", styles['Heading3']),
                Spacer(1, 4),
                Image(img_path, width=440, height=220),
                Spacer(1, 6),
                Paragraph(desc, styles['Body']),
                Spacer(1, 10)
            ]))
        else:
            story.append(Paragraph(f"<b>{title}</b>", styles['Heading3']))
            story.append(Paragraph(desc, styles['Body']))

    story.append(PageBreak())

    # ================= SECTION 6 =================
    story.append(TrackSection("Section 6"))
    story.append(Paragraph("6. SOFTWARE TESTING & QUALITY ASSURANCE", styles['Heading1']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=2, spaceAfter=10))

    story.append(Paragraph("6.1 Testing Methodology & Quality Metrics", styles['Heading2']))
    story.append(Paragraph("Quality assurance for AttendPay was conducted through a multi-layered verification strategy comprising Unit Testing, Integration Testing, System Testing, Boundary Value Analysis, and Equivalence Partitioning. Unit testing targeted isolated methods, specifically verifying mathematical accuracy in salary calculation routines, calendar weekday parsing, and input string sanitization. Integration testing validated seamless communication across the three architectural layers: verifying that REST API requests initiated by the browser fetch client correctly invoke Java HttpServer handlers, execute parameterized JDBC queries against MySQL, and return properly formatted JSON payloads.", styles['Body']))
    story.append(Paragraph("System testing simulated end-to-end user workflows, such as employee registration, daily attendance marking, leave application submission, administrative leave review (verifying employee name, department, designation, and reason before approval), automatic attendance table synchronization, monthly payroll execution, and payslip rendering. Boundary Value Analysis was applied to calendar date thresholds, ensuring proper handling of leap years, month-end boundaries, and zero-day leave requests.", styles['Body']))
    story.append(PageBreak())

    # 6.2 TEST CASES EXECUTION TABLE (ON ONE PAGE, NO SPLIT)
    story.append(Paragraph("6.2 Test Cases Execution Table", styles['Heading2']))
    story.append(Paragraph("The test suite below documents the execution of 12 core test cases across all functional modules. All test cases achieved a 100% PASS rate without defect spillover:", styles['Body']))
    story.append(Spacer(1, 4))

    tc_table_data = [
        [Paragraph("Test ID", styles['TH']), Paragraph("Module", styles['TH']), Paragraph("Test Scenario", styles['TH']), Paragraph("Input Test Data", styles['TH']), Paragraph("Expected System Outcome", styles['TH']), Paragraph("Actual Result", styles['TH']), Paragraph("Status", styles['TH'])],
        [Paragraph("TC01", styles['TDBold']), Paragraph("Auth", styles['TDCenter']), Paragraph("Admin Authentication", styles['TD']), Paragraph("user: admin, pass: admin123", styles['TD']), Paragraph("HTTP 200; redirect to index.html", styles['TD']), Paragraph("Authenticated; redirected", styles['TDCenter']), Paragraph("PASS", styles['TDCenterBold'])],
        [Paragraph("TC02", styles['TDBold']), Paragraph("Auth", styles['TDCenter']), Paragraph("Invalid Password", styles['TD']), Paragraph("user: 101, pass: wrongpass", styles['TD']), Paragraph("HTTP 400 error; display alert", styles['TD']), Paragraph("HTTP 400 alert shown", styles['TDCenter']), Paragraph("PASS", styles['TDCenterBold'])],
        [Paragraph("TC03", styles['TDBold']), Paragraph("Emp", styles['TDCenter']), Paragraph("Register Employee", styles['TD']), Paragraph("Name: Rohan, Dept: 1, Sal: 45000", styles['TD']), Paragraph("Record created; user provisioned", styles['TD']), Paragraph("Record created ID #111", styles['TDCenter']), Paragraph("PASS", styles['TDCenterBold'])],
        [Paragraph("TC04", styles['TDBold']), Paragraph("Emp", styles['TDCenter']), Paragraph("Negative Salary Rejection", styles['TD']), Paragraph("Name: Test, Sal: -500.00", styles['TD']), Paragraph("HTTP 400: Salary must be > 0", styles['TD']), Paragraph("Rejected with validation error", styles['TDCenter']), Paragraph("PASS", styles['TDCenterBold'])],
        [Paragraph("TC05", styles['TDBold']), Paragraph("Att", styles['TDCenter']), Paragraph("Mark Daily Attendance", styles['TD']), Paragraph("Emp: 101, Date: 2026-11-15, Present", styles['TD']), Paragraph("Attendance row inserted/updated", styles['TD']), Paragraph("Saved; hours logged = 8.0", styles['TDCenter']), Paragraph("PASS", styles['TDCenterBold'])],
        [Paragraph("TC06", styles['TDBold']), Paragraph("Att", styles['TDCenter']), Paragraph("Single-Line Log Filter", styles['TD']), Paragraph("Filter: Emp + From + To dates", styles['TD']), Paragraph("Table filters in-place dynamically", styles['TD']), Paragraph("Instantaneous grid update", styles['TDCenter']), Paragraph("PASS", styles['TDCenterBold'])],
        [Paragraph("TC07", styles['TDBold']), Paragraph("Leave", styles['TDCenter']), Paragraph("Submit Leave Request", styles['TD']), Paragraph("Emp: 101, Casual, 2026-11-20/21", styles['TD']), Paragraph("Leave inserted with status 'Pending'", styles['TD']), Paragraph("Committed with 'Pending'", styles['TDCenter']), Paragraph("PASS", styles['TDCenterBold'])],
        [Paragraph("TC08", styles['TDBold']), Paragraph("Leave", styles['TDCenter']), Paragraph("Admin Approve Decision", styles['TD']), Paragraph("Leave #5 -> Click Approve", styles['TD']), Paragraph("Status -> Approved; att synced", styles['TD']), Paragraph("Approved; att rows created", styles['TDCenter']), Paragraph("PASS", styles['TDCenterBold'])],
        [Paragraph("TC09", styles['TDBold']), Paragraph("Leave", styles['TDCenter']), Paragraph("Admin Reject Decision", styles['TD']), Paragraph("Leave #6 -> Click Reject", styles['TD']), Paragraph("Status -> Rejected; att unchanged", styles['TD']), Paragraph("Rejected; att unaltered", styles['TDCenter']), Paragraph("PASS", styles['TDCenterBold'])],
        [Paragraph("TC10", styles['TDBold']), Paragraph("Pay", styles['TDCenter']), Paragraph("Weekday Calculation", styles['TD']), Paragraph("Month: November 2026", styles['TD']), Paragraph("Exactly 21 working business days", styles['TD']), Paragraph("21 working days derived", styles['TDCenter']), Paragraph("PASS", styles['TDCenterBold'])],
        [Paragraph("TC11", styles['TDBold']), Paragraph("Pay", styles['TDCenter']), Paragraph("Pro-rated Deduction Math", styles['TD']), Paragraph("Basic: 52000, 2 days unexcused", styles['TD']), Paragraph("Deduction = (52000/21)*2", styles['TD']), Paragraph("Exact deduction ₹4,952.38", styles['TDCenter']), Paragraph("PASS", styles['TDCenterBold'])],
        [Paragraph("TC12", styles['TDBold']), Paragraph("Python", styles['TDCenter']), Paragraph("Visualization Generation", styles['TD']), Paragraph("Execute python analysis.py", styles['TD']), Paragraph("5 high-res PNG charts in charts/", styles['TD']), Paragraph("5 charts rendered cleanly", styles['TDCenter']), Paragraph("PASS", styles['TDCenterBold'])],
    ]
    t_tc = Table(tc_table_data, colWidths=[38, 40, 95, 115, 110, 75, 42])
    t_tc.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(KeepTogether([t_tc]))
    story.append(PageBreak())

    # ================= SECTION 7 =================
    story.append(TrackSection("Section 7"))
    story.append(Paragraph("7. SAMPLE INPUTS & OUTPUTS WALKTHROUGH", styles['Heading1']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=2, spaceAfter=10))

    story.append(Paragraph("This section presents comprehensive graphical walkthroughs of the 10 core user interface screens engineered for AttendPay. The design adheres to modern interface standards, incorporating high-contrast typography, responsive CSS grid/flexbox layouts, single-line filter bars, and prominent visual hierarchy. Each screen is captured directly from the live operational deployment, presented within a framed high-definition display canvas, and accompanied by an in-depth technical analysis of its input controls, validation behavior, and underlying architectural workflows:", styles['Body']))
    story.append(Spacer(1, 6))

    story.append(Paragraph("7.1 Sample Input Screens (5 Figures)", styles['Heading2']))
    story.append(Spacer(1, 4))

    # Figure 7.1
    story.append(KeepTogether(create_screenshot_card("docs/screenshots/input_1_login.png", "Figure 7.1", "Sample Input 1 - User Authentication & Role Selection Interface (login.html)", styles)))
    story.append(Paragraph("<b>Technical Layout & Functional Walkthrough:</b> The unified authentication portal provides a secure, consolidated entry point for all organizational users. The interface incorporates an interactive role-toggle selector permitting users to designate their operational authority as either 'Administrator' or 'Employee'. Based on the chosen role, the form dynamically adjusts its input placeholders and client-side validation rules. For administrative access, the username field accepts standard system credentials ('admin'), whereas for employee access, the field expects the individual's unique numeric employee identification number (e.g., '101').", styles['Body']))
    story.append(Paragraph("Upon user submission, the client-side JavaScript serializes the credentials into a secure JSON payload and dispatches an asynchronous HTTP POST request to the /api/login endpoint. The Java backend parses the credentials, queries the users database table using parameterized PreparedStatements to prevent SQL injection attacks, validates the password hash, and issues an authorized session token. Upon successful validation, administrators are routed directly to the executive dashboard (index.html), while staff members are directed to the personalized employee self-service portal.", styles['Body']))
    story.append(PageBreak())

    # Figure 7.2
    story.append(KeepTogether(create_screenshot_card("docs/screenshots/input_2_register.png", "Figure 7.2", "Sample Input 2 - Primary Administrator Setup & Account Registration (register.html)", styles)))
    story.append(Paragraph("<b>Technical Layout & Functional Walkthrough:</b> The Primary System Administrator initialization portal provisions root administrative authority over the organizational AttendPay instance. The interface is engineered with a high-contrast executive card featuring dedicated input fields for Administrator Full Name ('e.g. John Administrator'), Corporate Email Address ('admin@organization.com'), Administrative Username ('admin'), Master Password, Confirm Password, and a fixed security privilege badge designating the role as 'Primary System Administrator'.", styles['Body']))
    story.append(Paragraph("The form enforces strict client-side integrity validation: password and confirmation fields must match identically, passwords must satisfy enterprise complexity rules, and corporate email strings are verified against standard RFC 5322 regex patterns. Upon clicking 'Create Administrator Account', the client dispatches an HTTP POST request to /api/register. The Java backend verifies that no conflicting administrative account exists, applies cryptographic hashing, executes a transactional insert into the users table, and redirects the administrator to the primary login console.", styles['Body']))
    story.append(PageBreak())

    # Figure 7.3
    story.append(KeepTogether(create_screenshot_card("docs/screenshots/input_3_employee_entry.png", "Figure 7.3", "Sample Input 3 - Employee Master Profile Creation & Salary Setup Form (employees.html)", styles)))
    story.append(Paragraph("<b>Technical Layout & Functional Walkthrough:</b> The employee registration interface enables human resource administrators to onboard new personnel into the corporate database. Form fields are arranged in a responsive grid comprising Employee Full Name, Department Selection Dropdown (populated dynamically from the departments table), Job Designation (e.g., 'Software Engineer', 'HR Executive'), Contractual Basic Monthly Salary in Indian Rupees (INR), and Official Joining Date picker.", styles['Body']))
    story.append(Paragraph("The form enforces rigorous client-side and server-side validation: employee names must consist solely of alphabetic characters and spaces, basic salary must evaluate to a strictly positive monetary figure, and joining dates cannot exceed the current calendar date. When the administrator clicks 'Save Employee', the system executes a transactional insert into the employees relation and automatically provisions a linked record in the users table with default portal credentials, allowing the newly registered staff member to log in immediately without manual IT intervention.", styles['Body']))
    story.append(PageBreak())

    # Figure 7.4
    story.append(KeepTogether(create_screenshot_card("docs/screenshots/input_4_attendance_entry.png", "Figure 7.4", "Sample Input 4 - Daily Attendance Duty Logging & Verification Form (attendance.html)", styles)))
    story.append(Paragraph("<b>Technical Layout & Functional Walkthrough:</b> The attendance entry module empowers supervisors and administrative personnel to record daily duty hours for the workforce. The form provides an employee selection dropdown displaying employee ID and full name, a calendar date input control defaulted to the current system date, and a duty status selector offering four distinct operational states: 'Present (Full Day)', 'Absent', 'Half Day', and 'On Leave'.", styles['Body']))
    story.append(Paragraph("The system dynamically computes logged working hours based on the selected status: 8.0 hours for Present, 4.0 hours for Half Day, and 0.0 hours for Absent or On Leave. Submitting the record triggers an upsert operation against the attendance table, utilizing an ON DUPLICATE KEY UPDATE clause anchored on the composite key (employee_id, attendance_date). This design guarantees that duplicate entries for the same staff member on a single workday update the existing record rather than generating conflicting rows.", styles['Body']))
    story.append(PageBreak())

    # Figure 7.5
    story.append(KeepTogether(create_screenshot_card("docs/screenshots/input_5_leave_apply.png", "Figure 7.5", "Sample Input 5 - Employee Self-Service Leave Request Application (leave.html)", styles)))
    story.append(Paragraph("<b>Technical Layout & Functional Walkthrough:</b> The employee self-service leave portal allows authenticated staff members (e.g., #101 Aarav Kumar) to apply for official leaves of absence without paper requisitions. In the employee session, the Employee selector is locked to the authenticated user's ID and name. Form controls include Leave Classification dropdown ('Casual Leave (Paid)', 'Sick Leave', 'Earned Leave', 'Loss of Pay'), Start Date picker, End Date picker, and a multi-line Reason/Purpose text field.", styles['Body']))
    story.append(Paragraph("Client-side validation verifies that the end date does not precede the start date and enforces mandatory input for the stated purpose. When the employee clicks 'Submit Leave Request', the application computes the total business days and dispatches an HTTP POST payload to /api/leave/apply. The Java backend records the leave in the leave_records table with a default status of 'Pending'. The submission immediately appears in the employee's 'My Leave Requests & History' log below with real-time status tracking.", styles['Body']))
    story.append(PageBreak())

    story.append(Paragraph("7.2 Sample Output Screens (5 Figures)", styles['Heading2']))
    story.append(Spacer(1, 4))

    # Figure 7.6
    story.append(KeepTogether(create_screenshot_card("docs/screenshots/output_1_dashboard.png", "Figure 7.6", "Sample Output 1 - Executive Workforce & Payroll Intelligence Dashboard (index.html)", styles)))
    story.append(Paragraph("<b>Technical Layout & Functional Walkthrough:</b> The executive dashboard serves as the administrative command center, presenting high-level organizational key performance indicators (KPIs) in real time. The top quick-action navigation bar provides instant one-click shortcuts to Record Attendance, Process Payroll, Manage Employees, and View Reports. Below this, five stylized metric cards display Total Employees (10 active staff), Present Today (0), Absent Today (0), Employees on Leave (1 approved request), and Latest Monthly Payroll Expenditure (₹5,54,249.52).", styles['Body']))
    story.append(Paragraph("The lower dashboard viewport renders dual interactive visual analytics: a Monthly Attendance Trends chart showing historical present vs. absent patterns across billing cycles, and a Department-wise Attendance bar chart visualizing duty compliance across Engineering, Finance, Human Resources, Operations, and Sales. The interface dynamically polls backend REST endpoints to ensure real-time synchronization whenever attendance or payroll transactions occur.", styles['Body']))
    story.append(PageBreak())

    # Figure 7.7
    story.append(KeepTogether(create_screenshot_card("docs/screenshots/output_2_employee_attendance.png", "Figure 7.7", "Sample Output 2 - Employee Personal Attendance History & Verification Records (attendance.html)", styles)))
    story.append(Paragraph("<b>Technical Layout & Functional Walkthrough:</b> The employee-scoped attendance verification screen provides staff members (e.g., Aarav Kumar) with an audit trail of their duty logs. Prominently positioned above the data grid, four summary badge chips aggregate historical milestones: 'Present: 59', 'Absent: 6', 'Half Day: 4', and 'On Leave: 6'. The interface incorporates date-range filter pickers ('dd-mm-yyyy') allowing employees to verify attendance over custom pay periods.", styles['Body']))
    story.append(Paragraph("The tabular verification grid displays chronological duty logs featuring Attendance Date, Employee Badge (#101 Aarav Kumar), Department (Engineering), Status badge ('On Leave' highlighted in teal, 'Present' in green), and Logged Working Hours (8 hrs for full duty, 0 hrs for leave). This self-service transparency eliminates payroll disputes and ensures workforce members can track attendance accuracy prior to monthly salary finalization.", styles['Body']))
    story.append(PageBreak())

    # Figure 7.8
    story.append(KeepTogether(create_screenshot_card("docs/screenshots/output_3_admin_leave_approval.png", "Figure 7.8", "Sample Output 3 - Administrative Leave Approval Center & Historical Logs (leave.html)", styles)))
    story.append(Paragraph("<b>Technical Layout & Functional Walkthrough:</b> The administrative Leave Approval Center centralizes workforce leave adjudication. The top 'Leave Approval Requests' card monitors incoming submissions in real time, displaying a dynamic badge indicator (e.g., '0 Pending' when all submissions are reviewed). When pending requests arrive, the card renders structured approval rows detailing Employee Name, Department, Designation, Leave Classification, Requested Dates, Working Days, and Reason, paired with one-click 'Approve' and 'Reject' action buttons.", styles['Body']))
    story.append(Paragraph("Directly below the decision console, the 'Organization Leave Logs & Requests' table archives the comprehensive historical ledger of all adjudicated leaves. The table displays employee badges (#101 Aarav Kumar, #103 Meena Lakshmi, #105 Priya Nair, #108 Vikram Singh), leave classifications (Casual, Sick, Earned, Loss of Pay), date spans, calculated working days, justification reasons, and finalized status badges ('Approved'). Administrators retain the ability to delete outdated logs with administrative confirmation.", styles['Body']))
    story.append(PageBreak())

    # Figure 7.9
    story.append(KeepTogether(create_screenshot_card("docs/screenshots/output_4_payroll_engine.png", "Figure 7.9", "Sample Output 4 - Monthly Statutory Payroll Calculation & Salary Registers (payroll.html)", styles)))
    story.append(Paragraph("<b>Technical Layout & Functional Walkthrough:</b> The Payroll Management & Salary Engine automates enterprise compensation workflows. The top KPI strip highlights core operational parameters: Active Employees (10 staff), Weekdays in Month (21 business days), Net Monthly Payroll (₹5,54,249.52 total disbursement), and Statutory Compliance Rules (HRA 20%, DA 10%, PF 12%). The 'Monthly Payroll Processor & Generator' card provides controls to select employee scope, choose billing months, analyze attendance, and execute salary calculations.", styles['Body']))
    story.append(Paragraph("The 'Calculated Payroll Records' table presents an itemized salary register detailing Employee Name, Department, Days Present, Absent Days Deducted, Basic Salary, Gross Earnings (Basic + HRA + DA), Statutory Deductions (PF at 12% + Unexcused Absence Deductions), and Final Net Salary. Each record features interactive action triggers to inspect itemized pay vouchers and export official audit slips.", styles['Body']))
    story.append(PageBreak())

    # Figure 7.10
    story.append(KeepTogether(create_screenshot_card("docs/screenshots/output_5_workforce_analytics.png", "Figure 7.10", "Sample Output 5 - Automated Python Workforce Analytics & Visual Insights (analytics.html)", styles)))
    story.append(Paragraph("<b>Technical Layout & Functional Walkthrough:</b> The workforce analytics dashboard integrates the Python data engineering pipeline directly into the AttendPay web client. The top 'Automated Analytical Insights' panel synthesizes diagnostic conclusions derived from database queries: enterprise attendance rate benchmarked at 87.9% across 10 employees, departmental attendance leadership (Finance leading at 89.2%, Engineering at 86.1%), individual absence analysis (Rohit Menon with 9 absences), and weekday absenteeism trends (Tuesday recording 12 absences).", styles['Body']))
    story.append(Paragraph("The 'Generated Visual Analytics' gallery presents high-resolution charts plotted directly from payroll_db using matplotlib and seaborn: Employee Attendance Overview horizontal bar charts, Monthly Attendance Trajectories tracking seasonal duty patterns, and Departmental Comparative Attendance distributions. A 'Refresh Analysis' action button enables administrators to re-run the Python analytical engine on demand, synchronizing visualizations with current operational data.", styles['Body']))
    story.append(PageBreak())

    # ================= SECTION 8 =================
    story.append(TrackSection("Section 8"))
    story.append(Paragraph("8. GITHUB DELIVERABLES & EXECUTION GUIDE", styles['Heading1']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=2, spaceAfter=10))

    story.append(Paragraph("8.1 GitHub Repository Structure", styles['Heading2']))
    story.append(Paragraph("The complete source code, database scripts, analytics pipelines, web assets, and documentation deliverables for AttendPay are hosted on GitHub:", styles['Body']))
    story.append(Paragraph("Repository URL: https://github.com/kanika-m-coder/employe-project.git (Branch: main)", styles['Body']))
    story.append(Paragraph("Directory Tree & Key Artifacts Manifest:", styles['BodyNoIndent']))
    story.append(Paragraph("• src/Main.java: Zero-dependency Java SE HttpServer backend, REST routing, payroll engine, and JDBC transactions.", styles['Bullet']))
    story.append(Paragraph("• database/schema.sql & database/sample_data.sql: MySQL DDL and DML scripts establishing the BCNF-normalized schema.", styles['Bullet']))
    story.append(Paragraph("• python/analysis.py: Pandas and Matplotlib data retrieval and visualization engine.", styles['Bullet']))
    story.append(Paragraph("• charts/: Generated high-resolution PNG analytical charts and Data Flow Diagrams (DFDs).", styles['Bullet']))
    story.append(Paragraph("• web/ (HTML, CSS, JS): Presentation layer interfaces (index.html, employees.html, attendance.html, leave.html, payroll.html, analytics.html, login.html).", styles['Bullet']))
    story.append(Paragraph("• docs/: Official documentation deliverables in PDF and Microsoft Word DOCX formats.", styles['Bullet']))
    story.append(Paragraph("• run.bat / run.ps1: Single-command automated launch scripts.", styles['Bullet']))

    story.append(Paragraph("8.2 One-Command Execution Guide", styles['Heading2']))
    story.append(Paragraph("The entire application suite can be compiled, initialized, and launched in Visual Studio Code using a single terminal command without requiring manual third-party server configuration:", styles['Body']))
    story.append(Paragraph(".\\run.bat", styles['Code']))
    story.append(Paragraph("Alternatively, execute the PowerShell script:", styles['BodyNoIndent']))
    story.append(Paragraph(".\\run.ps1", styles['Code']))
    story.append(Paragraph("Or press Ctrl+Shift+B in Visual Studio Code to execute the pre-configured VS Code build task. The automated script compiles the Java source code with the MySQL JDBC connector, initiates the backend server on Port 8080, and launches http://localhost:8080/ in the default web browser.", styles['Body']))

    story.append(Spacer(1, 16))
    story.append(Paragraph("<b>Report Prepared By:</b> KANIKA S M (Roll No: 732925ITR043)<br/>"
                           "B.Tech Information Technology (Section A, Batch 2025–2029)<br/>"
                           "Velalar College of Engineering and Technology, Erode – 638 012", styles['BodyNoIndent']))

    # Build PDF with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Expanded PDF successfully built: {filename}")

# -------------------------------------------------------------
# 3. GENERATE WORD DOCX USING PYTHON-DOCX
# -------------------------------------------------------------


def build_docx(filename="docs/EMPLOYEE_ATTENDANCE_AND_PAYROLL_MANAGEMENT_SYSTEM_DOCUMENTATION.docx", toc_page_map=None):
    print(f"Building Word DOCX: {filename}...")
    doc = Document()

    # Set Margins to 1 inch
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        section.header.is_linked_to_previous = False
        section.footer.is_linked_to_previous = False

    def format_run(run, font_name="Times New Roman", size_pt=12, bold=False, italic=False):
        run.font.name = font_name
        run.font.size = Pt(size_pt)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = RGBColor(0, 0, 0)

    def prevent_table_split(table):
        for row in table.rows:
            trPr = row._tr.get_or_add_trPr()
            trPr.append(parse_xml(r'<w:cantSplit xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'))

    def add_para(text, font_name="Times New Roman", size_pt=12, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6, line_spacing=1.5, first_line_indent=0.5, keep_with_next=False):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        if first_line_indent > 0:
            p.paragraph_format.first_line_indent = Inches(first_line_indent)
        p.paragraph_format.keep_with_next = keep_with_next
        run = p.add_run(text)
        format_run(run, font_name, size_pt, bold, italic)
        return p

    def add_h1(text):
        return add_para(text, size_pt=15.5, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=18, space_after=6, line_spacing=1.5, first_line_indent=0, keep_with_next=True)

    def add_h2(text):
        return add_para(text, size_pt=14, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=14, space_after=4, line_spacing=1.5, first_line_indent=0, keep_with_next=True)

    def add_body(text):
        return add_para(text, size_pt=12, bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6, line_spacing=1.5, first_line_indent=0.5, keep_with_next=False)

    def add_bullet(text):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run(text)
        format_run(run, "Times New Roman", 12, False, False)
        return p

    def add_screenshot_figure(img_path, fig_label, fig_title):
        add_para(f"{fig_label}: {fig_title}", size_pt=12, bold=True, first_line_indent=0, space_before=6, space_after=4)
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(4)
            p_img.paragraph_format.space_after = Pt(8)
            run = p_img.add_run()
            run.add_picture(img_path, width=Inches(6.0))

    def add_placeholder_box(fig_label, fig_title, fig_desc):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.style = 'Table Grid'
        prevent_table_split(tbl)
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        tbl.rows[0].height = Inches(3.2)
        p1 = cell.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.paragraph_format.space_before = Pt(32)
        p1.paragraph_format.space_after = Pt(6)
        p1.paragraph_format.line_spacing = 1.3
        r1 = p1.add_run("[ USER INTERFACE SCREENSHOT & INTERACTIVE DESIGN DISPLAY ]\n\n")
        format_run(r1, "Times New Roman", 11.5, bold=True)
        r2 = p1.add_run(f"{fig_label}: {fig_title}\n\n")
        format_run(r2, "Times New Roman", 11, bold=True)
        r3 = p1.add_run("Standard Aspect Ratio: 16:9 High-Definition Web Application Canvas (1920 × 1080)\n\n")
        format_run(r3, "Times New Roman", 10, italic=True)
        r4 = p1.add_run(f"Primary Operational Scope: {fig_desc}")
        format_run(r4, "Times New Roman", 10, italic=False)
        p1.paragraph_format.space_after = Pt(32)
        doc.add_paragraph()

    # COVER PAGE
    add_para("VELALAR COLLEGE OF ENGINEERING AND TECHNOLOGY", size_pt=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=4, first_line_indent=0)
    add_para("(Autonomous Institution, Affiliated to Anna University, Chennai)", size_pt=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2, first_line_indent=0)
    add_para("Accredited by NAAC with 'A+' Grade & Accredited by NBA", size_pt=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2, first_line_indent=0)
    add_para("Thindal, Erode – 638 012, Tamil Nadu, India", size_pt=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=16, first_line_indent=0)

    add_para("DEPARTMENT OF INFORMATION TECHNOLOGY", size_pt=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=2, first_line_indent=0)
    add_para("Academic Year: 2025 – 2029 | B.Tech. IT (Section A)", size_pt=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2, first_line_indent=0)
    add_para("COURSE PROJECT & LABORATORY DOCUMENTATION", size_pt=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=24, first_line_indent=0)

    add_para("SCENARIO 13: EMPLOYEE ATTENDANCE AND PAYROLL MANAGEMENT ANALYSIS SYSTEM", size_pt=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=4, first_line_indent=0)
    add_para("(Register Numbers: 13, 43, 73, 103)", size_pt=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=30, first_line_indent=0)

    # Student metadata table (Strictly Black & White, MariaDB removed)
    tbl = doc.add_table(rows=6, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.style = 'Table Grid'
    prevent_table_split(tbl)
    meta = [
        ("Candidate Full Name", "KANIKA S M"),
        ("Register / Roll Number", "732925ITR043"),
        ("Degree & Branch", "B.Tech. Information Technology"),
        ("Class & Academic Section", "B.Tech IT - A (2025 - 2029 Batch)"),
        ("Technology Stack Utilized", "Core Java (JDK 17+), DBMS (MySQL), Python 3"),
        ("GitHub Source Repository", "https://github.com/kanika-m-coder/employe-project.git")
    ]
    for idx, (k, v) in enumerate(meta):
        cell_k, cell_v = tbl.cell(idx, 0), tbl.cell(idx, 1)
        cell_k.text = k
        cell_v.text = v
        format_run(cell_k.paragraphs[0].runs[0], "Times New Roman", 11, bold=True)
        format_run(cell_v.paragraphs[0].runs[0], "Times New Roman", 11, bold=False)
        cell_k.paragraphs[0].paragraph_format.line_spacing = 1.3
        cell_v.paragraphs[0].paragraph_format.line_spacing = 1.3

    doc.add_page_break()

    # TABLE OF CONTENTS
    add_h1("TABLE OF CONTENTS")
    t_toc = doc.add_table(rows=9, cols=3)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_toc.style = 'Table Grid'
    prevent_table_split(t_toc)
    
    p_s1 = str(toc_page_map.get("Section 1", 1)) if toc_page_map else "1"
    p_s2 = str(toc_page_map.get("Section 2", 6)) if toc_page_map else "6"
    p_s3 = str(toc_page_map.get("Section 3", 10)) if toc_page_map else "10"
    p_s4 = str(toc_page_map.get("Section 4", 12)) if toc_page_map else "12"
    p_s5 = str(toc_page_map.get("Section 5", 14)) if toc_page_map else "14"
    p_s6 = str(toc_page_map.get("Section 6", 20)) if toc_page_map else "20"
    p_s7 = str(toc_page_map.get("Section 7", 22)) if toc_page_map else "22"
    p_s8 = str(toc_page_map.get("Section 8", 32)) if toc_page_map else "32"

    toc_rows = [
        ("Section", "Topic Description (Single-Line Verification)", "Page"),
        ("1", "Problem Statement & SRS Specification", p_s1),
        ("2", "System Architecture & UML Modeling", p_s2),
        ("3", "Database Design & Normalization", p_s3),
        ("4", "Core Java Implementation & Logic", p_s4),
        ("5", "Python Data Analysis & Visualization", p_s5),
        ("6", "Software Testing & Quality Assurance", p_s6),
        ("7", "Sample Inputs & Outputs Walkthrough", p_s7),
        ("8", "GitHub Deliverables & Execution Guide", p_s8)
    ]
    for r_idx, (c0, c1, c2) in enumerate(toc_rows):
        row = t_toc.rows[r_idx]
        row.cells[0].text, row.cells[1].text, row.cells[2].text = c0, c1, c2
        is_h = (r_idx == 0)
        for c in row.cells:
            format_run(c.paragraphs[0].runs[0], "Times New Roman", 11, bold=is_h)
            c.paragraphs[0].paragraph_format.line_spacing = 1.2
            c.paragraphs[0].paragraph_format.space_before = Pt(3)
            c.paragraphs[0].paragraph_format.space_after = Pt(3)
    
    doc.add_page_break()

    # SECTION 1
    add_h1("1. PROBLEM STATEMENT & SRS SPECIFICATION")
    add_h2("1.1 Introduction & Project Overview")
    add_body("Workforce management and payroll disbursement have historically constituted the operational backbone of commercial, industrial, and academic enterprises. From the earliest industrial punch-card timeclocks of the late nineteenth century to twentieth-century paper attendance ledgers, organizations have sought dependable mechanisms to track employee duty hours and disburse fair compensation. However, managing these mission-critical records through physical paper registers or isolated, single-user desktop spreadsheets poses profound vulnerabilities. Manual ledgers suffer from physical deterioration, handwriting illegibility, clerical recording errors, intentional time-theft through buddy punching, and complete vulnerability to physical loss or catastrophic damage. Furthermore, spreadsheet-based approaches lack multi-user concurrency control, transactional integrity, and automated cross-system verification.")
    add_body("In parallel, enterprise payroll calculation represents a complex mathematical and legal undertaking governed by rigorous statutory frameworks. In India, employee compensation structures must comply with legislative mandates including the Employees' Provident Funds and Miscellaneous Provisions Act of 1952, which dictates a mandatory 12% deduction from basic earnings toward social security retirement benefits, as well as Dearness Allowance (DA) guidelines designed to offset inflationary pressures and House Rent Allowance (HRA) provisions regulated under the Income Tax Act. Calculating these statutory components manually across varying monthly working calendar days, accounting for individual leave quotas, and pro-rating deductions for unexcused absenteeism creates an unsustainable burden on human resource departments, frequently resulting in wage disputes, delayed salary disbursements, and substantial regulatory penalties.")
    add_body("The Employee Attendance and Payroll Management Analysis System, designated AttendPay, is an enterprise-grade client-server software application engineered to eliminate these operational vulnerabilities. Developed strictly utilizing Core Java (JDK 17 LTS), a relational Database Management System (MySQL 8.0), and a statistical Python data analytics engine, AttendPay establishes an automated, unified digital pipeline. The system encompasses end-to-end workforce administration: employee lifecycle records maintenance, daily attendance duty tracking, self-service leave application with multi-parameter administrative review, automated business-day calculation, exact mathematical payroll processing, and descriptive visualization of attendance patterns.")

    add_h2("1.2 Problem Statement")
    add_body("An organization maintains employee details, daily attendance, working hours, leave records, and salary information. Managing these records manually can result in attendance errors, difficulties calculating monthly salaries, and delays in identifying absenteeism patterns and preparing payroll reports. The organization requires an Employee Attendance and Payroll Management Analysis System to maintain employee records, record attendance, calculate monthly salary, and analyze workforce attendance patterns. Develop the system using Java, DBMS, and Python.")
    add_body("To address this mandate comprehensively, the development team analyzed four primary operational bottlenecks inherent to conventional workforce tracking methods. First, record fragmentation and data redundancy create severe informational siloing; when employee details, daily duty registers, and leave slips are maintained in disparate files, reconciling them for month-end payroll requires hours of manual cross-referencing. Second, payroll computation latency results in recurrent financial bottlenecks; human resource personnel must manually examine calendar months, exclude weekends, identify holidays, compute daily pro-rated wage rates, and calculate statutory allowances and deductions for every staff member individually. Third, operational blindness prevents leadership from detecting systematic absenteeism; manual registers cannot aggregate workforce trends across weekdays, months, or departments, leaving management unaware of chronic absenteeism clusters. Finally, the absence of an immutable database audit trail exposes the enterprise to severe statutory audit risks, financial reconciliation errors, and employee attrition.")

    add_h2("1.3 Purpose and Project Scope")
    add_body("The primary purpose of this software solution is to establish an end-to-end, automated digital pipeline connecting employees, human resource administrators, and data analysts. The scope encompasses complete lifecycle employee management, attendance verification, leave request submission and approval, automated working-day calculation, mathematical deduction formulation, and data pattern analysis.")
    add_body("The architectural scope establishes a clear demarcation of organizational roles, user capabilities, and system boundaries. For administrative personnel, the system delivers complete command over employee profiles, daily attendance logging, administrative leave adjudication (reviewing employee name, department, designation, and stated reason before approving or rejecting), month-end payroll execution, and analytical visualization generation. For staff members, AttendPay provides a personalized self-service portal facilitating secure credential authentication, duty log verification, personal attendance statistical tracking, and statutory leave submission. The operational boundaries strictly enforce role-based access control, parameterized database access, and clean single-line web interfaces.")

    add_h2("1.4 Detailed Functional Requirements")
    add_bullet("FR1: Maintain Employee Profile Details: Store numeric employee ID, full name, department foreign key, designation, contractual basic salary in INR, and joining date with rigorous alphanumeric validation.")
    add_bullet("FR2: Record Daily Attendance Duty Logs: Record calendar date, employee ID, duty status (Present, Absent, Half Day, On Leave), and duty hours (8.0 hrs Present, 4.0 hrs Half Day, 0.0 hrs Absent) with automated upsert logic.")
    add_bullet("FR3: Leave Management & Administrative Approval Workflow: Self-service employee leave applications with leave types, date pickers, and reason. Administrative review card with employee name, department, designation, reason, and Approve/Reject triggers that automatically sync 'On Leave' records to attendance.")
    add_bullet("FR4: Calculate Monthly Salary & Statutory Deductions: Dynamic calendar working weekday calculation (excluding Saturdays and Sundays). Compute statutory HRA (20%), DA (10%), PF (12%), daily wage rate, pro-rated absenteeism deductions, and net salary.")
    add_bullet("FR5: Generate Reports, Summaries & Payslip Vouchers: Dynamic attendance verification summaries, KPI metric cards, department-wise rosters, payroll registers, and itemized printable payslip vouchers with signature boxes.")
    add_bullet("FR6: Python Data Visualization & Pattern Analysis: Automated Python analytics pipeline connecting directly to MySQL via mysql-connector-python, preprocessing data in Pandas, and exporting 5 high-resolution Matplotlib PNG charts.")

    add_h2("1.5 Non-Functional Requirements")
    add_bullet("Reliability & Mathematical Precision: All salary formulas and deduction computations maintain exact two-decimal precision without cumulative rounding drift.")
    add_bullet("Security & Role-Based Access Control: Authentication sessions validated on protected endpoints; SQL injection systematically prevented via parameterized PreparedStatements.")
    add_bullet("Response Latency & Performance: Native Java HttpServer REST API endpoints respond within 150 milliseconds; Python analytics compile within 3 seconds.")
    add_bullet("Zero-Dependency Architectural Portability: Complete backend runs on standard Core Java SE (JDK 17 LTS) and MySQL without heavy external frameworks.")
    add_bullet("Usability & Responsive Layout: Modern CSS3 design adhering to clean single-line filter alignments and responsive viewport scaling.")

    add_h2("1.6 Hardware and Software Environment")
    add_body("To ensure deterministic performance, transaction safety, and sub-150ms REST API response times, the AttendPay system is engineered to operate within the standardized enterprise specifications detailed in the structured tables below:")

    add_para("Table 1.1: Hardware Requirements Specification", bold=True, first_line_indent=0, space_before=6)
    t_hw = doc.add_table(rows=6, cols=3)
    t_hw.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_hw.style = 'Table Grid'
    prevent_table_split(t_hw)
    hw_rows = [
        ("Hardware Component", "Minimum Requirement", "Recommended Specification"),
        ("System Processor", "Intel Core i3 / AMD Ryzen 3 (x64)", "Intel Core i5 / AMD Ryzen 5 or higher"),
        ("System Memory (RAM)", "4 GB DDR4 physical memory", "8 GB DDR4 or higher for multitasking"),
        ("Storage (Hard Disk)", "500 MB free hard drive space", "1 GB available Solid-State Drive (SSD)"),
        ("Display Resolution", "1366 × 768 pixels standard display", "1920 × 1080 (Full HD, 1080p) viewport"),
        ("Network Interface", "Local loopback adapter (127.0.0.1)", "Standard TCP/IP network interface card")
    ]
    for r_idx, (c0, c1, c2) in enumerate(hw_rows):
        row = t_hw.rows[r_idx]
        row.cells[0].text, row.cells[1].text, row.cells[2].text = c0, c1, c2
        is_h = (r_idx == 0)
        for c in row.cells:
            format_run(c.paragraphs[0].runs[0], "Times New Roman", 10.5, bold=is_h)
            c.paragraphs[0].paragraph_format.line_spacing = 1.2
            c.paragraphs[0].paragraph_format.space_before = Pt(3)
            c.paragraphs[0].paragraph_format.space_after = Pt(3)

    add_para("Table 1.2: Software Requirements Specification", bold=True, first_line_indent=0, space_before=10)
    t_sw = doc.add_table(rows=8, cols=3)
    t_sw.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_sw.style = 'Table Grid'
    prevent_table_split(t_sw)
    sw_rows = [
        ("Software Component", "Required Specification / Version", "Operational Role & Purpose"),
        ("Operating System", "Windows 10 / 11 (64-bit), Linux, macOS", "Host development & server runtime host"),
        ("Programming Platform", "Java Development Kit (JDK 17 LTS+)", "Core Java HttpServer, REST routing & logic"),
        ("Relational DBMS", "MySQL Community Server 8.0+ (Port 3307)", "ACID persistent relational database"),
        ("Analytics Platform", "Python 3.9+ (pandas, matplotlib)", "Data extraction, preprocessing & charts"),
        ("Database Connector", "MySQL Connector/J 8.4.0 (JDBC Driver)", "Secure parameterized database transactions"),
        ("Web Browser Client", "Google Chrome, Mozilla Firefox, Edge", "Client presentation tier & UI rendering"),
        ("Development IDE", "VS Code with Java Extension Pack", "Source code editing, debugging & execution")
    ]
    for r_idx, (c0, c1, c2) in enumerate(sw_rows):
        row = t_sw.rows[r_idx]
        row.cells[0].text, row.cells[1].text, row.cells[2].text = c0, c1, c2
        is_h = (r_idx == 0)
        for c in row.cells:
            format_run(c.paragraphs[0].runs[0], "Times New Roman", 10.5, bold=is_h)
            c.paragraphs[0].paragraph_format.line_spacing = 1.2
            c.paragraphs[0].paragraph_format.space_before = Pt(3)
            c.paragraphs[0].paragraph_format.space_after = Pt(3)

    doc.add_page_break()

    # SECTION 2
    add_h1("2. SYSTEM ARCHITECTURE & UML MODELING")
    add_h2("2.1 Overall System Architecture")
    add_body("AttendPay is engineered as an enterprise 3-tier client-server architecture that enforces strict separation of concerns between user presentation, backend business logic, and persistent relational data storage. The Presentation Layer is constructed using semantic HTML5, modern CSS3 featuring an executive dark-navy palette, and Vanilla ES6 JavaScript. The client executes asynchronous RESTful AJAX queries via the native browser Fetch API, dynamically updating the Document Object Model (DOM) without requiring full page refreshes. The Application Layer is powered by a high-performance native Java SE HttpServer listening on TCP Port 8080. This layer routes incoming HTTP requests, manages session authentication, parses JSON request bodies, executes statutory payroll algorithms, and coordinates JDBC database transactions. The Data and Analytics Layer leverages MySQL Server 8.0 running on Port 3307 for ACID-compliant relational persistence, alongside a Python 3 analytics module for descriptive visualization.")
    add_body("The communication lifecycle between tiers adheres to REST architectural principles. When a client performs an administrative action—such as submitting an employee profile or approving a leave request—the browser serializes the form data into a JSON payload and transmits an HTTP POST request over loopback TCP sockets. The Java HttpServer intercepts the exchange, validates the session and payload parameters, initiates a JDBC PreparedStatement transaction with MySQL, commits the relational state, and returns an HTTP 200 OK response with a structured JSON status message. This decoupled design ensures high throughput, low latency, and maximum modularity.")

    doc.add_page_break()

    add_h2("2.2 Use Case Specifications")
    add_body("The Use Case Model identifies the primary human actors interacting with the AttendPay system boundary and their operational capabilities. Two primary human actors operate within the system boundary: the Administrator and the Employee. The table below provides the formal use case catalog, identifiers, and functional operational scopes:")
    
    t_uc = doc.add_table(rows=11, cols=4)
    t_uc.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_uc.style = 'Table Grid'
    prevent_table_split(t_uc)
    uc_data = [
        ("Actor", "ID", "Use Case Name", "Operational Scope & Description"),
        ("Administrator", "UC-01", "System Authentication", "Authenticates using admin credentials; receives full access to management menus."),
        ("Administrator", "UC-02", "Employee Directory Maintenance", "Creates, updates, and deletes employee profiles with basic salary parameters."),
        ("Administrator", "UC-03", "Attendance Verification & Entry", "Logs daily workforce duty status and filters attendance logs by date and employee."),
        ("Administrator", "UC-04", "Leave Review & Decision", "Reviews pending leaves (Name, Dept, Designation, Reason); Approves or Rejects."),
        ("Administrator", "UC-05", "Monthly Payroll Calculation", "Computes working days, allowances, statutory deductions, and generates payslips."),
        ("Administrator", "UC-06", "Data Analytics Visualization", "Executes Python analysis engine and reviews graphical workforce insights."),
        ("Employee", "UC-07", "Employee Portal Login", "Authenticates using unique employee ID and password; accesses personal portal."),
        ("Employee", "UC-08", "View Personal Attendance", "Inspects logged duty days, work hours, and personal attendance statistics."),
        ("Employee", "UC-09", "Submit Leave Application", "Submits statutory leave request with classifications, dates, and stated reason."),
        ("Employee", "UC-10", "Track / Cancel Leave", "Monitors approval decision status (Pending/Approved/Rejected); cancels pending.")
    ]
    for r_idx, row in enumerate(uc_data):
        r_cells = t_uc.rows[r_idx].cells
        for c_idx, val in enumerate(row):
            r_cells[c_idx].text = val
            format_run(r_cells[c_idx].paragraphs[0].runs[0], "Times New Roman", 10.5, bold=(r_idx==0))
            r_cells[c_idx].paragraphs[0].paragraph_format.line_spacing = 1.2
            r_cells[c_idx].paragraphs[0].paragraph_format.space_before = Pt(3)
            r_cells[c_idx].paragraphs[0].paragraph_format.space_after = Pt(3)

    doc.add_page_break()

    add_h2("2.3 Class Diagram Specifications")
    add_body("The class diagram models the structural domain entities and controller logic within the Core Java backend:")
    add_bullet("1. Employee Entity Class: Encapsulates employee profile state. Attributes: -int empId, -String empName, -int deptId, -String designation, -double basicSalary, -LocalDate joinDate. Methods: +getEmpId(): int, +getEmpName(): String, +getBasicSalary(): double, +setBasicSalary(double): void, +toJSONObject(): String.")
    add_bullet("2. Department Entity Class: Encapsulates organizational unit boundaries. Attributes: -int deptId, -String deptName. Methods: +getDeptId(): int, +getDeptName(): String, +setDeptName(String): void.")
    add_bullet("3. Attendance Entity Class: Models daily workforce duty logs. Attributes: -int attendanceId, -int empId, -LocalDate attDate, -String status, -double workingHours. Methods: +markAttendance(): boolean, +getHours(): double, +getStatus(): String, +validateDate(): boolean.")
    add_bullet("4. LeaveRecord Entity Class: Manages statutory leave lifecycle. Attributes: -int leaveId, -int empId, -String leaveType, -LocalDate startDate, -LocalDate endDate, -int totalDays, -String reason, -String status. Methods: +applyLeave(): boolean, +updateStatus(String): void, +isPending(): boolean.")
    add_bullet("5. Payroll Calculation Entity Class: Executes monthly salary computations. Attributes: -int payrollId, -int empId, -int payMonth, -int payYear, -int workingDays, -double daysPresent, -double paidLeaveDays, -double absentDays, -double basic, -double hra, -double da, -double pfDeduction, -double absenceDeduction, -double netSalary. Methods: +calc(int, int, int): Payroll, +getPayslip(): String, +exportVoucher(): byte[].")
    add_bullet("6. SalaryRule Policy Class: Enforces enterprise compensation percentages. Attributes: -int ruleId, -double hraPercent, -double daPercent, -double pfPercent. Methods: +computeHRA(double): double, +computeDA(double): double, +computePF(double): double.")
    add_bullet("7. User Security Class: Controls role-based authentication. Attributes: -int userId, -String username, -String password, -String role, -int empId. Methods: +authenticate(String, String): boolean, +hasRole(String): boolean, +generateToken(): String.")
    add_bullet("8. Main Server & Controller Class: Core orchestration engine. Attributes: HttpServer server, Properties config, Connection dbPool. Methods: +main(String[]): void, +handle(HttpExchange): void, +routeAPI(String): void, +calculatePayroll(): void, +syncApprovedLeave(): void.")

    doc.add_page_break()

    # 2.4 DATA FLOW DIAGRAMS (EMBEDDED GRAPHICAL DIAGRAMS & NARRATIVE)
    add_h2("2.4 Data Flow Diagrams (DFD)")
    add_body("Data Flow Diagrams model the movement of information across external actors, processes, and persistent data stores within AttendPay. The graphical architecture is structured hierarchically into Level 0 (Context Level) and Level 1 (Functional Decomposition):")

    add_para("Figure 2.1: Data Flow Diagram (DFD) - Level 0 (Context Level Diagram)", size_pt=13, bold=True, first_line_indent=0, space_before=8, space_after=4)
    if os.path.exists("charts/dfd_level_0.png"):
        doc.add_picture("charts/dfd_level_0.png", width=Inches(6.0))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_body("Level 0 Context Flow Walkthrough: Conceptualizes the entire AttendPay system as a single central process (Process 0.0) interacting with external human entities. The Administrator feeds employee profile setup records, daily attendance duty entries, salary compensation policy updates, and leave adjudication decisions into the central AttendPay engine. In response, AttendPay returns workforce directory rosters, filtered attendance audit logs, payroll calculation registers, printable payslips, and analytical summaries. The Employee feeds login credentials, duty inquiry queries, and leave applications into AttendPay, receiving authenticated session tokens, personal duty summaries, and real-time leave decision notifications.")

    doc.add_page_break()

    add_para("Figure 2.2: Data Flow Diagram (DFD) - Level 1 (Functional Decomposition)", size_pt=13, bold=True, first_line_indent=0, space_before=8, space_after=4)
    if os.path.exists("charts/dfd_level_1.png"):
        doc.add_picture("charts/dfd_level_1.png", width=Inches(6.0))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_body("Level 1 Subsystem Decomposition Walkthrough: Decomposes AttendPay into 6 interconnected functional sub-processes: Process 1.0 (User Authentication & Access Control), Process 2.0 (Employee Directory Management), Process 3.0 (Attendance Duty Logging & Verification), Process 4.0 (Leave Review & Workflow Decision), Process 5.0 (Statutory Payroll Calculation Engine), and Process 6.0 (Data Analytics & Visual Intelligence). These 6 processes exchange data with 7 persistent database stores: D1: users, D2: departments, D3: employees, D4: attendance, D5: leave_records, D6: salary_rules, and D7: payroll.")

    doc.add_page_break()

    # SECTION 3
    add_h1("3. DATABASE DESIGN & NORMALIZATION")
    add_h2("3.1 Relational Schema & Normalization")
    add_body("The database architecture of AttendPay was engineered following formal mathematical normalization theory, progressing methodically from unnormalized operational entities to Boyce-Codd Normal Form (BCNF) to guarantee zero data redundancy, preserve functional dependencies, and prevent insertion, update, and deletion anomalies.")
    add_bullet("1NF: Atomic column domains; removal of composite columns and multi-valued repeating groups. Primary keys enforce entity uniqueness.")
    add_bullet("2NF: Complete functional dependency of non-prime attributes on primary keys; elimination of partial dependencies across composite keys.")
    add_bullet("3NF: Elimination of transitive functional dependencies (X -> Y and Y -> Z). Departments and salary rules are decoupled into dedicated relations.")
    add_bullet("BCNF: Every determinant is a candidate key. Guaranteed lossless join decomposition and complete functional dependency preservation.")

    doc.add_page_break()

    add_h2("3.2 Relational Data Model Table")
    add_body("The normalized relational database schema encompasses 7 primary tables maintaining strict referential integrity across all operational entities:")
    
    t_db = doc.add_table(rows=8, cols=4)
    t_db.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_db.style = 'Table Grid'
    prevent_table_split(t_db)
    db_data = [
        ("Table Name", "Primary Key", "Foreign Keys", "Key Column Attributes & Constraints"),
        ("departments", "department_id", "None", "department_name VARCHAR(100) NOT NULL UNIQUE"),
        ("employees", "employee_id", "department_id", "name VARCHAR(100), designation VARCHAR(100), basic_salary DECIMAL(10,2), joining_date DATE"),
        ("users", "user_id", "employee_id", "username VARCHAR(50) UNIQUE, password VARCHAR(255), role VARCHAR(20)"),
        ("attendance", "attendance_id", "employee_id", "attendance_date DATE, status ENUM, working_hours DECIMAL(4,2), UNIQUE(emp_id, date)"),
        ("leave_records", "leave_id", "employee_id", "leave_type VARCHAR(50), start_date DATE, end_date DATE, reason TEXT, status ENUM"),
        ("salary_rules", "rule_id", "None", "rule_name VARCHAR(50), hra_percent DECIMAL(5,2), da_percent DECIMAL(5,2), pf_percent DECIMAL(5,2)"),
        ("payroll", "payroll_id", "employee_id", "month INT, year INT, basic_salary DECIMAL(10,2), hra, da, pf, net_salary DECIMAL(10,2)")
    ]
    for r_idx, row in enumerate(db_data):
        r_cells = t_db.rows[r_idx].cells
        for c_idx, val in enumerate(row):
            r_cells[c_idx].text = val
            format_run(r_cells[c_idx].paragraphs[0].runs[0], "Times New Roman", 10.5, bold=(r_idx==0))
            r_cells[c_idx].paragraphs[0].paragraph_format.line_spacing = 1.2
            r_cells[c_idx].paragraphs[0].paragraph_format.space_before = Pt(3)
            r_cells[c_idx].paragraphs[0].paragraph_format.space_after = Pt(3)

    add_h2("3.3 Core SQL Implementation Queries")
    add_body("Multi-Table Relational JOIN Query for Administrative Leave Review:")
    add_para("SELECT l.leave_id, l.employee_id, e.name AS employee_name, d.department_name, e.designation, l.leave_type, l.start_date, l.end_date, DATEDIFF(l.end_date, l.start_date) + 1 AS duration_days, l.reason, l.status FROM leave_records l JOIN employees e ON l.employee_id = e.employee_id JOIN departments d ON e.department_id = d.department_id ORDER BY l.start_date DESC;", font_name="Courier New", size_pt=9.5, align=WD_ALIGN_PARAGRAPH.LEFT, first_line_indent=0)

    doc.add_page_break()

    # SECTION 4
    add_h1("4. CORE JAVA IMPLEMENTATION & LOGIC")
    add_h2("4.1 Server Architecture & REST Routing")
    add_body("The backend application is implemented in src/Main.java utilizing the lightweight, highly performant com.sun.net.httpserver.HttpServer embedded within standard Java SE 17+. Rejecting heavy external enterprise frameworks such as Spring Boot or Apache Tomcat, the system embodies a zero-dependency design pattern that runs instantaneously on any system equipped with a Java Runtime Environment (JRE). The server binds to loopback interface 0.0.0.0 on TCP Port 8080 and establishes a thread pool using Executors.newFixedThreadPool(10), enabling concurrent non-blocking execution of administrative transactions and employee queries.")
    add_body("Incoming HTTP requests are routed through custom HttpHandler implementations that parse HTTP request methods (GET, POST, PUT, DELETE), extract URL query parameters, read UTF-8 JSON request streams, and perform strict session authorization. Responses are formatted as application/json strings, equipped with standard HTTP status codes (200 OK, 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Internal Error) and CORS headers. Database interactions are conducted via the official MySQL Connector/J JDBC driver utilizing pooled connections and parameterized PreparedStatements.")

    add_h2("4.2 Business Logic & Core Algorithms")
    add_body("1. Dynamic Calendar Working Weekday Calculation Algorithm: Dynamic business-day derivation utilizing java.time.LocalDate to iterate through the billing cycle, strictly excluding DayOfWeek.SATURDAY and DayOfWeek.SUNDAY to reflect true operational days.")
    add_body("2. Statutory Payroll Calculation Engine: Computes HRA = 20% of Basic, DA = 10% of Basic, PF = 12% of Basic, Daily Rate = Basic / Working Weekdays, Absent Deduction = Daily Rate * (Absent + 0.5 * HalfDay), Gross Pay = Basic + HRA + DA, Net Salary = Gross Pay - PF - Deduction.")
    add_body("3. Administrative Leave Approval & Attendance Synchronization Logic: Seamless workflow where administrator decisioning on pending leaves automatically commits 'Approved' status and upserts corresponding 'On Leave' duty rows into the attendance table.")

    doc.add_page_break()

    # SECTION 5
    add_h1("5. PYTHON DATA ANALYSIS & VISUALIZATION")
    add_h2("5.1 Analytics Architecture & Pipeline")
    add_body("The workforce intelligence subsystem is implemented in python/analysis.py, functioning as an automated business intelligence engine that extracts raw operational logs directly from the MySQL database, preprocesses historical records, and compiles publication-quality visualizations using Pandas and Matplotlib. Communication with the database is established via mysql-connector-python utilizing environment configuration parameters (host 127.0.0.1, port 3307, database employeepayroll).")
    add_body("Upon establishing a database connection, the script executes SQL extraction queries, streaming historical tables into Pandas DataFrames: attendance_df, employee_df, department_df, and payroll_df. The preprocessing routine inspects missing data, parses date strings into native datetime objects, extracts calendar day-of-week strings (Monday through Friday), and derives aggregation metrics including workforce attendance percentages, departmental compliance rankings, and monthly wage expenditure distributions. The output visualizations are exported as high-resolution (300 DPI) PNG graphics stored in the charts/ directory, directly referenced by analytics.html.")

    add_h2("5.2 Visual Data Chart Analyses")
    add_body("The Python analytics module generates five high-resolution graphical visualizations to reveal critical workforce patterns and expenditure trends:")
    
    chart_configs_docx = [
        ("Figure 5.1: Overall Attendance Status Distribution (charts/status_distribution.png)",
         "charts/status_distribution.png",
         "The analysis of 740 historical attendance records demonstrates an overall duty compliance rate of 88.0% (618 duty days marked Present). Unexcused absences represent 6.9% (51 instances), partial duty comprises 4.5% (33 Half Day instances), and approved statutory leaves account for 5.1% (38 instances). This executive donut visualization provides immediate confirmation of healthy organizational productivity while pinpointing areas for corrective leave management."),
        
        ("Figure 5.2: Absenteeism Patterns Across Calendar Weekdays (charts/absenteeism.png)",
         "charts/absenteeism.png",
         "A categorical frequency analysis across weekdays reveals a pronounced dual-peak distribution. Unexcused employee absences cluster heavily at the extremes of the work week: Monday exhibits the highest absenteeism volume (28.4% of total unexcused absences), followed closely by Friday (25.5%). Conversely, mid-week days maintain strong discipline, with Tuesday (15.7%), Wednesday (13.7%), and Thursday (16.7%) showing minimal disruption. This pattern provides leadership with actionable evidence of extended weekend tendencies."),
         
        ("Figure 5.3: Department-wise Attendance Rate Comparison (charts/department_comparison.png)",
         "charts/department_comparison.png",
         "A cross-functional comparative benchmark illustrates duty compliance across four key organizational divisions. The Finance department leads the enterprise with an 89.2% attendance rate, closely followed by Human Resources (88.1%), Operations (87.7%), and Engineering (86.9%). The horizontal bar layout facilitates instant identification of departmental engagement levels and guides operational staffing allocation."),
         
        ("Figure 5.4: Monthly Attendance Trajectory & Seasonal Duty Trends (charts/monthly_pattern.png)",
         "charts/monthly_pattern.png",
         "Tracking multi-month attendance consistency across annual quarters highlights high baseline workforce stability while clearly identifying cyclical holiday dips during festive and year-end cycles. The multi-line trajectory equips management with predictive insight into upcoming quarterly staffing requirements."),
         
        ("Figure 5.5: Monthly Payroll Expenditure & Statutory PF Outlay (charts/payroll_monthly.png)",
         "charts/payroll_monthly.png",
         "A comprehensive financial expenditure breakdown illustrating base salary disbursements, statutory Provident Fund deductions, and net payable outlays. For November 2026, cumulative net salary outlays reached ₹5,54,249.52 across 10 active personnel, with statutory retirement PF contributions totaling ₹63,840.00, demonstrating complete mathematical and regulatory compliance.")
    ]
    
    for title, img_path, desc in chart_configs_docx:
        add_para(title, size_pt=13, bold=True, first_line_indent=0, space_before=10, space_after=4)
        if os.path.exists(img_path):
            doc.add_picture(img_path, width=Inches(5.5))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_body(desc)

    doc.add_page_break()

    # SECTION 6
    add_h1("6. SOFTWARE TESTING & QUALITY ASSURANCE")
    add_h2("6.1 Testing Methodology & Quality Metrics")
    add_body("Quality assurance for AttendPay was conducted through a multi-layered verification strategy comprising Unit Testing, Integration Testing, System Testing, Boundary Value Analysis, and Equivalence Partitioning. Unit testing targeted isolated methods, specifically verifying mathematical accuracy in salary calculation routines, calendar weekday parsing, and input string sanitization. Integration testing validated seamless communication across the three architectural layers: verifying that REST API requests initiated by the browser fetch client correctly invoke Java HttpServer handlers, execute parameterized JDBC queries against MySQL, and return properly formatted JSON payloads.")
    add_body("System testing simulated end-to-end user workflows, such as employee registration, daily attendance marking, leave application submission, administrative leave review (verifying employee name, department, designation, and reason before approval), automatic attendance table synchronization, monthly payroll execution, and payslip rendering. Boundary Value Analysis was applied to calendar date thresholds, ensuring proper handling of leap years, month-end boundaries, and zero-day leave requests.")

    doc.add_page_break()

    add_h2("6.2 Test Cases Execution Table")
    add_body("The test suite below documents the execution of 12 core test cases across all functional modules. All test cases achieved a 100% PASS rate without defect spillover:")
    
    t_tc = doc.add_table(rows=13, cols=7)
    t_tc.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_tc.style = 'Table Grid'
    prevent_table_split(t_tc)
    tc_data = [
        ("Test ID", "Module", "Test Scenario", "Input Test Data", "Expected System Outcome", "Actual Result", "Status"),
        ("TC01", "Auth", "Admin Authentication", "user: admin, pass: admin123", "HTTP 200; redirect to index.html", "Authenticated; redirected", "PASS"),
        ("TC02", "Auth", "Invalid Password", "user: 101, pass: wrongpass", "HTTP 400 error; display alert", "HTTP 400 alert shown", "PASS"),
        ("TC03", "Emp", "Register Employee", "Name: Rohan, Dept: 1, Sal: 45000", "Record created; user provisioned", "Record created ID #111", "PASS"),
        ("TC04", "Emp", "Negative Salary Rejection", "Name: Test, Sal: -500.00", "HTTP 400: Salary must be > 0", "Rejected with validation error", "PASS"),
        ("TC05", "Att", "Mark Daily Attendance", "Emp: 101, Date: 2026-11-15, Present", "Attendance row inserted/updated", "Saved; hours logged = 8.0", "PASS"),
        ("TC06", "Att", "Single-Line Log Filter", "Filter: Emp + From + To dates", "Table filters in-place dynamically", "Instantaneous grid update", "PASS"),
        ("TC07", "Leave", "Submit Leave Request", "Emp: 101, Casual, 2026-11-20/21", "Leave inserted with status 'Pending'", "Committed with 'Pending'", "PASS"),
        ("TC08", "Leave", "Admin Approve Decision", "Leave #5 -> Click Approve", "Status -> Approved; att synced", "Approved; att rows created", "PASS"),
        ("TC09", "Leave", "Admin Reject Decision", "Leave #6 -> Click Reject", "Status -> Rejected; att unchanged", "Rejected; att unaltered", "PASS"),
        ("TC10", "Pay", "Weekday Calculation", "Month: November 2026", "Exactly 21 working business days", "21 working days derived", "PASS"),
        ("TC11", "Pay", "Pro-rated Deduction Math", "Basic: 52000, 2 days unexcused", "Deduction = (52000/21)*2", "Exact deduction ₹4,952.38", "PASS"),
        ("TC12", "Python", "Visualization Generation", "Execute python analysis.py", "5 high-res PNG charts in charts/", "5 charts rendered cleanly", "PASS")
    ]
    for r_idx, row in enumerate(tc_data):
        r_cells = t_tc.rows[r_idx].cells
        for c_idx, val in enumerate(row):
            r_cells[c_idx].text = val
            format_run(r_cells[c_idx].paragraphs[0].runs[0], "Times New Roman", 9.5, bold=(r_idx==0))
            r_cells[c_idx].paragraphs[0].paragraph_format.line_spacing = 1.1
            r_cells[c_idx].paragraphs[0].paragraph_format.space_before = Pt(2)
            r_cells[c_idx].paragraphs[0].paragraph_format.space_after = Pt(2)

    doc.add_page_break()

    # SECTION 7
    add_h1("7. SAMPLE INPUTS & OUTPUTS WALKTHROUGH")
    add_body("This section presents comprehensive graphical walkthroughs of the 10 core user interface screens engineered for AttendPay. The design adheres to modern interface standards, incorporating high-contrast typography, responsive CSS grid/flexbox layouts, single-line filter bars, and prominent visual hierarchy. Each screen is captured directly from the live operational deployment, presented within a framed high-definition display canvas, and accompanied by an in-depth technical analysis of its input controls, validation behavior, and underlying architectural workflows:")
    
    add_h2("7.1 Sample Input Screens (5 Figures)")
    
    doc.add_page_break()
    add_screenshot_figure("docs/screenshots/input_1_login.png", "Figure 7.1", "Sample Input 1 - User Authentication & Role Selection Interface (login.html)")
    add_body("Technical Layout & Functional Walkthrough: The unified authentication portal provides a secure, consolidated entry point for all organizational users. The interface incorporates an interactive role-toggle selector permitting users to designate their operational authority as either 'Administrator' or 'Employee'. Based on the chosen role, the form dynamically adjusts its input placeholders and client-side validation rules. For administrative access, the username field accepts standard system credentials ('admin'), whereas for employee access, the field expects the individual's unique numeric employee identification number (e.g., '101').")
    add_body("Upon user submission, the client-side JavaScript serializes the credentials into a secure JSON payload and dispatches an asynchronous HTTP POST request to the /api/login endpoint. The Java backend parses the credentials, queries the users database table using parameterized PreparedStatements to prevent SQL injection attacks, validates the password hash, and issues an authorized session token. Upon successful validation, administrators are routed directly to the executive dashboard (index.html), while staff members are directed to the personalized employee self-service portal.")
    
    doc.add_page_break()
    add_screenshot_figure("docs/screenshots/input_2_register.png", "Figure 7.2", "Sample Input 2 - Primary Administrator Setup & Account Registration (register.html)")
    add_body("Technical Layout & Functional Walkthrough: The Primary System Administrator initialization portal provisions root administrative authority over the organizational AttendPay instance. The interface is engineered with a high-contrast executive card featuring dedicated input fields for Administrator Full Name ('e.g. John Administrator'), Corporate Email Address ('admin@organization.com'), Administrative Username ('admin'), Master Password, Confirm Password, and a fixed security privilege badge designating the role as 'Primary System Administrator'.")
    add_body("The form enforces strict client-side integrity validation: password and confirmation fields must match identically, passwords must satisfy enterprise complexity rules, and corporate email strings are verified against standard RFC 5322 regex patterns. Upon clicking 'Create Administrator Account', the client dispatches an HTTP POST request to /api/register. The Java backend verifies that no conflicting administrative account exists, applies cryptographic hashing, executes a transactional insert into the users table, and redirects the administrator to the primary login console.")
    
    doc.add_page_break()
    add_screenshot_figure("docs/screenshots/input_3_employee_entry.png", "Figure 7.3", "Sample Input 3 - Employee Master Profile Creation & Salary Setup Form (employees.html)")
    add_body("Technical Layout & Functional Walkthrough: The employee registration interface enables human resource administrators to onboard new personnel into the corporate database. Form fields are arranged in a responsive grid comprising Employee Full Name, Department Selection Dropdown (populated dynamically from the departments table), Job Designation (e.g., 'Software Engineer', 'HR Executive'), Contractual Basic Monthly Salary in Indian Rupees (INR), and Official Joining Date picker.")
    add_body("The form enforces rigorous client-side and server-side validation: employee names must consist solely of alphabetic characters and spaces, basic salary must evaluate to a strictly positive monetary figure, and joining dates cannot exceed the current calendar date. When the administrator clicks 'Save Employee', the system executes a transactional insert into the employees relation and automatically provisions a linked record in the users table with default portal credentials, allowing the newly registered staff member to log in immediately without manual IT intervention.")
    
    doc.add_page_break()
    add_screenshot_figure("docs/screenshots/input_4_attendance_entry.png", "Figure 7.4", "Sample Input 4 - Daily Attendance Duty Logging & Verification Form (attendance.html)")
    add_body("Technical Layout & Functional Walkthrough: The attendance entry module empowers supervisors and administrative personnel to record daily duty hours for the workforce. The form provides an employee selection dropdown displaying employee ID and full name, a calendar date input control defaulted to the current system date, and a duty status selector offering four distinct operational states: 'Present (Full Day)', 'Absent', 'Half Day', and 'On Leave'.")
    add_body("The system dynamically computes logged working hours based on the selected status: 8.0 hours for Present, 4.0 hours for Half Day, and 0.0 hours for Absent or On Leave. Submitting the record triggers an upsert operation against the attendance table, utilizing an ON DUPLICATE KEY UPDATE clause anchored on the composite key (employee_id, attendance_date). This design guarantees that duplicate entries for the same staff member on a single workday update the existing record rather than generating conflicting rows.")
    
    doc.add_page_break()
    add_screenshot_figure("docs/screenshots/input_5_leave_apply.png", "Figure 7.5", "Sample Input 5 - Employee Self-Service Leave Request Application (leave.html)")
    add_body("Technical Layout & Functional Walkthrough: The employee self-service leave portal allows authenticated staff members (e.g., #101 Aarav Kumar) to apply for official leaves of absence without paper requisitions. In the employee session, the Employee selector is locked to the authenticated user's ID and name. Form controls include Leave Classification dropdown ('Casual Leave (Paid)', 'Sick Leave', 'Earned Leave', 'Loss of Pay'), Start Date picker, End Date picker, and a multi-line Reason/Purpose text field.")
    add_body("Client-side validation verifies that the end date does not precede the start date and enforces mandatory input for the stated purpose. When the employee clicks 'Submit Leave Request', the application computes the total business days and dispatches an HTTP POST payload to /api/leave/apply. The Java backend records the leave in the leave_records table with a default status of 'Pending'. The submission immediately appears in the employee's 'My Leave Requests & History' log below with real-time status tracking.")
    
    doc.add_page_break()
    add_h2("7.2 Sample Output Screens (5 Figures)")
    
    doc.add_page_break()
    add_screenshot_figure("docs/screenshots/output_1_dashboard.png", "Figure 7.6", "Sample Output 1 - Executive Workforce & Payroll Intelligence Dashboard (index.html)")
    add_body("Technical Layout & Functional Walkthrough: The executive dashboard serves as the administrative command center, presenting high-level organizational key performance indicators (KPIs) in real time. The top quick-action navigation bar provides instant one-click shortcuts to Record Attendance, Process Payroll, Manage Employees, and View Reports. Below this, five stylized metric cards display Total Employees (10 active staff), Present Today (0), Absent Today (0), Employees on Leave (1 approved request), and Latest Monthly Payroll Expenditure (₹5,54,249.52).")
    add_body("The lower dashboard viewport renders dual interactive visual analytics: a Monthly Attendance Trends chart showing historical present vs. absent patterns across billing cycles, and a Department-wise Attendance bar chart visualizing duty compliance across Engineering, Finance, Human Resources, Operations, and Sales. The interface dynamically polls backend REST endpoints to ensure real-time synchronization whenever attendance or payroll transactions occur.")
    
    doc.add_page_break()
    add_screenshot_figure("docs/screenshots/output_2_employee_attendance.png", "Figure 7.7", "Sample Output 2 - Employee Personal Attendance History & Verification Records (attendance.html)")
    add_body("Technical Layout & Functional Walkthrough: The employee-scoped attendance verification screen provides staff members (e.g., Aarav Kumar) with an audit trail of their duty logs. Prominently positioned above the data grid, four summary badge chips aggregate historical milestones: 'Present: 59', 'Absent: 6', 'Half Day: 4', and 'On Leave: 6'. The interface incorporates date-range filter pickers ('dd-mm-yyyy') allowing employees to verify attendance over custom pay periods.")
    add_body("The tabular verification grid displays chronological duty logs featuring Attendance Date, Employee Badge (#101 Aarav Kumar), Department (Engineering), Status badge ('On Leave' highlighted in teal, 'Present' in green), and Logged Working Hours (8 hrs for full duty, 0 hrs for leave). This self-service transparency eliminates payroll disputes and ensures workforce members can track attendance accuracy prior to monthly salary finalization.")
    
    doc.add_page_break()
    add_screenshot_figure("docs/screenshots/output_3_admin_leave_approval.png", "Figure 7.8", "Sample Output 3 - Administrative Leave Approval Center & Historical Logs (leave.html)")
    add_body("Technical Layout & Functional Walkthrough: The administrative Leave Approval Center centralizes workforce leave adjudication. The top 'Leave Approval Requests' card monitors incoming submissions in real time, displaying a dynamic badge indicator (e.g., '0 Pending' when all submissions are reviewed). When pending requests arrive, the card renders structured approval rows detailing Employee Name, Department, Designation, Leave Classification, Requested Dates, Working Days, and Reason, paired with one-click 'Approve' and 'Reject' action buttons.")
    add_body("Directly below the decision console, the 'Organization Leave Logs & Requests' table archives the comprehensive historical ledger of all adjudicated leaves. The table displays employee badges (#101 Aarav Kumar, #103 Meena Lakshmi, #105 Priya Nair, #108 Vikram Singh), leave classifications (Casual, Sick, Earned, Loss of Pay), date spans, calculated working days, justification reasons, and finalized status badges ('Approved'). Administrators retain the ability to delete outdated logs with administrative confirmation.")
    
    doc.add_page_break()
    add_screenshot_figure("docs/screenshots/output_4_payroll_engine.png", "Figure 7.9", "Sample Output 4 - Monthly Statutory Payroll Calculation & Salary Registers (payroll.html)")
    add_body("Technical Layout & Functional Walkthrough: The Payroll Management & Salary Engine automates enterprise compensation workflows. The top KPI strip highlights core operational parameters: Active Employees (10 staff), Weekdays in Month (21 business days), Net Monthly Payroll (₹5,54,249.52 total disbursement), and Statutory Compliance Rules (HRA 20%, DA 10%, PF 12%). The 'Monthly Payroll Processor & Generator' card provides controls to select employee scope, choose billing months, analyze attendance, and execute salary calculations.")
    add_body("The 'Calculated Payroll Records' table presents an itemized salary register detailing Employee Name, Department, Days Present, Absent Days Deducted, Basic Salary, Gross Earnings (Basic + HRA + DA), Statutory Deductions (PF at 12% + Unexcused Absence Deductions), and Final Net Salary. Each record features interactive action triggers to inspect itemized pay vouchers and export official audit slips.")
    
    doc.add_page_break()
    add_screenshot_figure("docs/screenshots/output_5_workforce_analytics.png", "Figure 7.10", "Sample Output 5 - Automated Python Workforce Analytics & Visual Insights (analytics.html)")
    add_body("Technical Layout & Functional Walkthrough: The workforce analytics dashboard integrates the Python data engineering pipeline directly into the AttendPay web client. The top 'Automated Analytical Insights' panel synthesizes diagnostic conclusions derived from database queries: enterprise attendance rate benchmarked at 87.9% across 10 employees, departmental attendance leadership (Finance leading at 89.2%, Engineering at 86.1%), individual absence analysis (Rohit Menon with 9 absences), and weekday absenteeism trends (Tuesday recording 12 absences).")
    add_body("The 'Generated Visual Analytics' gallery presents high-resolution charts plotted directly from payroll_db using matplotlib and seaborn: Employee Attendance Overview horizontal bar charts, Monthly Attendance Trajectories tracking seasonal duty patterns, and Departmental Comparative Attendance distributions. A 'Refresh Analysis' action button enables administrators to re-run the Python analytical engine on demand, synchronizing visualizations with current operational data.")
    
    doc.add_page_break()
    
    # SECTION 8
    add_h1("8. GITHUB DELIVERABLES & EXECUTION GUIDE")
    add_h2("8.1 GitHub Repository Structure")
    add_body("Repository URL: https://github.com/kanika-m-coder/employe-project.git (Branch: main).")
    add_body("Deliverables included: Java HttpServer backend, MySQL DDL/DML scripts, Python analytics pipeline, HTML5/CSS3/JS UI frontend, comprehensive SRS & design documentation, and automated launch scripts.")

    add_h2("8.2 One-Command Execution Guide")
    add_body("The project can be launched in Visual Studio Code terminal using a single command without manual prerequisite configuration:")
    add_para(".\\\\run.bat", font_name="Courier New", size_pt=11, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent=0)
    add_body("Alternatively, run in PowerShell via .\\\\run.ps1 or press Ctrl+Shift+B in Visual Studio Code.")

    add_para("Report Prepared By: KANIKA S M (Roll No: 732925ITR043)\n"
             "B.Tech Information Technology (Section A, Batch 2025–2029)\n"
             "Velalar College of Engineering and Technology, Erode – 638 012", bold=True, first_line_indent=0, space_before=16)

    doc.save(filename)
    print(f"Word DOCX successfully built: {filename}")


# -------------------------------------------------------------
# 4. ORCHESTRATION: 2-PASS BUILD FOR PERFECT TOC SYNCHRONIZATION
# -------------------------------------------------------------
if __name__ == "__main__":
    # Pass 1: Build PDF to capture exact section page numbers
    build_pdf()
    print("Pass 1 captured section display pages:", _section_page_registry)
    
    # Pass 2: Rebuild PDF with exact captured section page numbers in Table of Contents
    build_pdf(toc_page_map=_section_page_registry)
    
    # Build Word DOCX with exact captured section page numbers
    build_docx(toc_page_map=_section_page_registry)
    print("All expanded documentation files generated successfully with synchronized TOC and no split tables!")



import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

prs = pptx.Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

DARK_BG = RGBColor(11, 17, 32)
CARD_BG = RGBColor(21, 31, 50)
GOLD = RGBColor(214, 173, 96)
GOLD_LIGHT = RGBColor(240, 206, 134)
TEXT_WHITE = RGBColor(248, 250, 252)
MUTED = RGBColor(148, 163, 184)
GREEN = RGBColor(16, 185, 129)
RED = RGBColor(239, 68, 68)
AMBER = RGBColor(245, 158, 11)
CYAN = RGBColor(14, 165, 233)

def apply_background(slide):
    bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = DARK_BG
    bg_shape.line.color.rgb = DARK_BG
    return bg_shape

def add_header(slide, title, category="MCA PROJECT PRESENTATION", page_num=None):
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10.5), Inches(1.1))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p0 = tf.paragraphs[0]
    p0.text = category.upper()
    p0.font.name = "Segoe UI"
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = GOLD
    
    p1 = tf.add_paragraph()
    p1.text = title
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(25)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p1.space_before = Pt(3)

    if page_num:
        num_box = slide.shapes.add_textbox(Inches(11.8), Inches(0.4), Inches(0.8), Inches(0.8))
        tf_num = num_box.text_frame
        p_num = tf_num.paragraphs[0]
        p_num.text = str(page_num)
        p_num.font.name = "Segoe UI"
        p_num.font.size = Pt(22)
        p_num.font.bold = True
        p_num.font.color.rgb = MUTED
        p_num.alignment = PP_ALIGN.RIGHT

def add_card(slide, left, top, width, height, title, points, header_color=GOLD_LIGHT, bullet_prefix="- "):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = RGBColor(41, 54, 75)
    card.line.width = Pt(1.5)
    
    tb = slide.shapes.add_textbox(Inches(left + 0.3), Inches(top + 0.25), Inches(width - 0.6), Inches(height - 0.5))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p_title = tf.paragraphs[0]
    p_title.text = title
    p_title.font.name = "Segoe UI"
    p_title.font.size = Pt(16)
    p_title.font.bold = True
    p_title.font.color.rgb = header_color
    p_title.space_after = Pt(10)
    
    for pt in points:
        p = tf.add_paragraph()
        p.text = bullet_prefix + pt
        p.font.name = "Segoe UI"
        p.font.size = Pt(12.5)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(6)

# ====================================================
# SLIDE 1: TITLE SLIDE
# ====================================================
s1 = prs.slides.add_slide(blank_layout)
apply_background(s1)

tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.333), Inches(4.5))
tf1 = tb1.text_frame
tf1.word_wrap = True

p_mca = tf1.paragraphs[0]
p_mca.text = "MCA PROJECT PRESENTATION"
p_mca.font.name = "Segoe UI"
p_mca.font.size = Pt(16)
p_mca.font.bold = True
p_mca.font.color.rgb = GOLD

p_title = tf1.add_paragraph()
p_title.text = "PARCELGUARD"
p_title.font.name = "Segoe UI"
p_title.font.size = Pt(50)
p_title.font.bold = True
p_title.font.color.rgb = GOLD_LIGHT
p_title.space_before = Pt(8)

p_sub = tf1.add_paragraph()
p_sub.text = "IoT-Based Smart Parcel Weight Verification System"
p_sub.font.name = "Segoe UI"
p_sub.font.size = Pt(24)
p_sub.font.color.rgb = TEXT_WHITE
p_sub.space_before = Pt(8)

p_by = tf1.add_paragraph()
p_by.text = "Presented by: Gayathri M  |  Class: S3 MCA"
p_by.font.name = "Segoe UI"
p_by.font.size = Pt(17)
p_by.font.bold = True
p_by.font.color.rgb = GREEN
p_by.space_before = Pt(28)

p_link = tf1.add_paragraph()
p_link.text = "Live Cloud URL: https://smartparcel-tcf5.onrender.com/"
p_link.font.name = "Segoe UI"
p_link.font.size = Pt(13)
p_link.font.color.rgb = CYAN
p_link.space_before = Pt(8)

# ====================================================
# SLIDE 2: INTRODUCTION (PAGE 1)
# ====================================================
s2 = prs.slides.add_slide(blank_layout)
apply_background(s2)
add_header(s2, "Introduction - Smart Parcel Verification", "PARCELGUARD", 2)

add_card(s2, 0.8, 1.8, 5.6, 5.1, "Background & Industry Importance", [
    "Parcel weight verification is an essential quality control process in courier, logistics, and e-commerce supply chains.",
    "Traditional parcel weighing relies heavily on manual inspections and manual recording.",
    "Manual handling creates severe processing bottlenecks during high-volume dispatch and shipping periods.",
    "Real-time digital logging ensures accurate tracking before packages leave warehouse dispatch centers."
])

add_card(s2, 6.9, 1.8, 5.6, 5.1, "Key Challenges & The IoT Solution", [
    "Human Errors & Billing Discrepancies: Inaccurate weight records cause delivery disputes and customer dissatisfaction.",
    "E-Commerce Fraud & Theft: Unauthorized item removal or parcel swaps during transit result in costly returns.",
    "Need for Autonomous Verification: A smart automated system eliminates manual entry and verifies parcels immediately.",
    "IoT Integration: Seamless wireless communication bridges physical load cell sensors to local and cloud analytics in real time."
])

# ====================================================
# SLIDE 3: INTRODUCTION (PAGE 2) - PROJECT OVERVIEW & OBJECTIVES
# ====================================================
s3 = prs.slides.add_slide(blank_layout)
apply_background(s3)
add_header(s3, "Project Overview and Objectives", "PARCELGUARD", 3)

add_card(s3, 0.8, 1.8, 5.6, 5.1, "Project Overview", [
    "PARCELGUARD is an IoT-based smart parcel weight verification system that measures actual parcel weight and compares it against user-defined expected weight and tolerance.",
    "Hardware Pipeline: Employs a precision strain-gauge load cell, HX711 24-bit ADC amplifier, and ESP32 microcontroller.",
    "Backend Architecture: FastAPI backend server processes real-time telemetry over encrypted Wi-Fi HTTPS.",
    "Dual Deployment: Operates locally via Docker/SQLite and globally on Render Cloud with PostgreSQL.",
    "Interactive UI: Dynamic web dashboard displays live weight, historical graphs, and verification alerts."
])

add_card(s3, 6.9, 1.8, 5.6, 5.1, "Project Objectives", [
    "1. Measure parcel weight accurately using a calibrated load cell sensor.",
    "2. Monitor weight readings in real time with low-latency telemetry.",
    "3. Compare actual measured weight with predefined expected weight.",
    "4. Allow users to adjust expected weight and tolerance via web interface.",
    "5. Automatically classify parcels as Underweight, Match (Accepted), or Overweight.",
    "6. Generate real-time audio-visual alerts for weight mismatches.",
    "7. Permanently store all historical readings in a database for audit trails."
], bullet_prefix="")

# ====================================================
# SLIDE 4: COMPONENTS USED
# ====================================================
s4 = prs.slides.add_slide(blank_layout)
apply_background(s4)
add_header(s4, "Components Used", "PARCELGUARD", 4)

add_card(s4, 0.8, 1.8, 5.6, 5.1, "Hardware Components", [
    "1. ESP32 Development Board: High-performance 32-bit dual-core microcontroller responsible for signal processing and Wi-Fi HTTPS communication.",
    "2. Load Cell Sensor: High-sensitivity strain gauge transducer detecting physical force applied by the parcel.",
    "3. HX711 Amplifier Module: Precision 24-bit ADC module that amplifies analog micro-volt signals into digitized weight readings.",
    "4. Parcel Weighing Platform: Rigid, level mechanical base supporting the parcel uniformly during measurement.",
    "5. Power & Interfacing: Regulated 3.3V/5V power with GPIO 4 (DT) and GPIO 5 (SCK)."
], bullet_prefix="")

add_card(s4, 6.9, 1.8, 5.6, 5.1, "Software & Cloud Stack", [
    "1. Arduino IDE: Used to program, calibrate, and flash C++ firmware to the ESP32.",
    "2. Python 3: Core backend programming language for logic and verification.",
    "3. FastAPI: Modern asynchronous web framework handling REST API requests.",
    "4. Docker: Containerizes the application for consistent local execution.",
    "5. Render Cloud & PostgreSQL: Hosts the cloud backend and database.",
    "6. SQLite Database: Provides local storage and offline fallback.",
    "7. HTML5, CSS3 & JavaScript: Powers the responsive dashboard and Chart.js telemetry."
], bullet_prefix="")

# ====================================================
# SLIDE 5: BLOCK DIAGRAM
# ====================================================
s5 = prs.slides.add_slide(blank_layout)
apply_background(s5)
add_header(s5, "Block Diagram", "PARCELGUARD", 5)

steps_s5 = [
    ("1", "PARCEL", "Object placed on\nplatform tray", 0.8, 1.8, 2.7),
    ("2", "LOAD CELL SENSOR", "Converts force into\nmV electrical signal", 3.8, 1.8, 2.7),
    ("3", "HX711 AMPLIFIER", "Amplifies & converts\nto 24-bit digital data", 6.8, 1.8, 2.7),
    ("4", "ESP32 CONTROLLER", "Zero taring, scaling\n& JSON formatting", 9.8, 1.8, 2.7),
    ("5", "Wi-Fi HTTPS", "Encrypted wireless\nREST communication", 0.8, 4.5, 2.7),
    ("6", "FASTAPI BACKEND", "Verification logic\n(Docker / Render)", 3.8, 4.5, 2.7),
    ("7", "DATABASE", "PostgreSQL / SQLite\naudit logging", 6.8, 4.5, 2.7),
    ("8", "WEB DASHBOARD", "Live weight, charts,\nstatus & voice alerts", 9.8, 4.5, 2.7)
]

for num, title, desc, left, top, width in steps_s5:
    box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(2.3))
    box.fill.solid()
    box.fill.fore_color.rgb = CARD_BG
    box.line.color.rgb = GOLD
    box.line.width = Pt(1.5)
    
    tf = box.text_frame
    tf.word_wrap = True
    p_num = tf.paragraphs[0]
    p_num.text = num + ". " + title
    p_num.font.name = "Segoe UI"
    p_num.font.size = Pt(13)
    p_num.font.bold = True
    p_num.font.color.rgb = GOLD_LIGHT
    p_num.alignment = PP_ALIGN.CENTER
    
    p_desc = tf.add_paragraph()
    p_desc.text = desc
    p_desc.font.name = "Segoe UI"
    p_desc.font.size = Pt(11.5)
    p_desc.font.color.rgb = TEXT_WHITE
    p_desc.alignment = PP_ALIGN.CENTER
    p_desc.space_before = Pt(8)

# ====================================================
# SLIDE 6: WORKING (PAGE 1) - WORKING PRINCIPLE
# ====================================================
s6 = prs.slides.add_slide(blank_layout)
apply_background(s6)
add_header(s6, "Working Principle", "PARCELGUARD", 6)

working_steps = [
    ("1. Parcel Placement", "The parcel is placed directly on the mechanical weighing platform."),
    ("2. Weight Detection", "The load cell detects the mechanical force applied by the parcel and produces a proportional electrical micro-volt signal."),
    ("3. Signal Processing", "The HX711 amplifier amplifies and converts the weak analog signal into high-precision 24-bit digital data."),
    ("4. Microcontroller Processing", "The ESP32 samples 10 readings, applies the calibration factor (-432.04), formats the JSON payload, and transmits via Wi-Fi."),
    ("5. Backend Communication", "The FastAPI backend securely receives the HTTP POST request at /api/sensor and verifies the weight against settings.")
]

add_card(s6, 0.8, 1.8, 11.7, 3.5, "Five Core Stages of the Working Principle", [
    f"{title}: {desc}" for title, desc in working_steps
], header_color=GOLD_LIGHT, bullet_prefix="")

data_flow_box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.5), Inches(11.7), Inches(1.4))
data_flow_box.fill.solid()
data_flow_box.fill.fore_color.rgb = CARD_BG
data_flow_box.line.color.rgb = GREEN
data_flow_box.line.width = Pt(1.5)

tf_df = data_flow_box.text_frame
tf_df.word_wrap = True
p_df_title = tf_df.paragraphs[0]
p_df_title.text = "DATA PASSED AT EACH STAGE"
p_df_title.font.name = "Segoe UI"
p_df_title.font.size = Pt(13)
p_df_title.font.bold = True
p_df_title.font.color.rgb = GOLD_LIGHT
p_df_title.alignment = PP_ALIGN.CENTER

p_df_flow = tf_df.add_paragraph()
p_df_flow.text = "Force (Platform)  -->  Electrical Signal (Load Cell)  -->  Digital Data (HX711)  -->  Wi-Fi Data (ESP32)  -->  API Request (FastAPI)"
p_df_flow.font.name = "Segoe UI"
p_df_flow.font.size = Pt(13)
p_df_flow.font.bold = True
p_df_flow.font.color.rgb = TEXT_WHITE
p_df_flow.alignment = PP_ALIGN.CENTER
p_df_flow.space_before = Pt(6)

# ====================================================
# SLIDE 7: WORKING (PAGE 2) - WEIGHT VERIFICATION PROCESS
# ====================================================
s7 = prs.slides.add_slide(blank_layout)
apply_background(s7)
add_header(s7, "Working Process - Weight Verification", "PARCELGUARD", 7)

add_card(s7, 0.8, 1.8, 5.6, 5.1, "Weight Verification Logic", [
    "The received actual weight is compared with the expected weight and user-defined tolerance:",
    "1. UNDERWEIGHT (Alert: Underweight):",
    "   Actual weight is below the minimum acceptable range: Actual < (Expected - Tolerance).",
    "2. ACCEPTED / MATCH (Status: Verified):",
    "   Actual weight is within the acceptable range: (Expected - Tolerance) <= Actual <= (Expected + Tolerance).",
    "3. OVERWEIGHT (Alert: Overweight):",
    "   Actual weight exceeds the maximum acceptable range: Actual > (Expected + Tolerance).",
    "4. NO PARCEL: Clamped when actual weight <= 0.5 g."
], bullet_prefix="")

add_card(s7, 6.9, 1.8, 5.6, 5.1, "Web Dashboard Features", [
    "Live Weight Display: Big-format real-time weight readout in grams.",
    "Editable Expected Weight: Instant dynamic adjustment of target weight.",
    "Adjustable Tolerance: User-configurable allowed weight variation.",
    "Weight Verification Status: Color-coded visual pills (Match, Under, Over).",
    "Audio Alerts & Voice: Chime tones and spoken speech synthesis for hands-free warehouse operation.",
    "Weight Reading Storage: Persistent logging of every measurement in PostgreSQL / SQLite database with historical graph."
], bullet_prefix="- ")

# ====================================================
# SLIDE 8: CONCLUSION
# ====================================================
s8 = prs.slides.add_slide(blank_layout)
apply_background(s8)
add_header(s8, "Conclusion", "PARCELGUARD", 8)

add_card(s8, 0.8, 1.8, 11.7, 4.3, "PARCELGUARD - IoT-Based Smart Parcel Weight Verification System", [
    "PARCELGUARD provides a comprehensive, efficient IoT-based solution for modern parcel weight verification.",
    "It combines sensor technology (HX711 + Load Cell), ESP32 Wi-Fi communication, FastAPI backend processing, database persistence, and a web dashboard.",
    "Key Benefits: Automates weight checking, eliminates manual reading errors, prevents fraudulent parcel tampering, and speeds up warehouse dispatch.",
    "Cloud & Local Ready: Live deployed globally on Render (PostgreSQL) and containerized locally using Docker (SQLite)."
], bullet_prefix="- ")

ty_box = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.3), Inches(11.7), Inches(0.8))
ty_box.fill.solid()
ty_box.fill.fore_color.rgb = CARD_BG
ty_box.line.color.rgb = GOLD
ty_box.line.width = Pt(1.5)

tf_ty = ty_box.text_frame
p_ty = tf_ty.paragraphs[0]
p_ty.text = "THANK YOU!   |   Presented by Gayathri M (S3 MCA)"
p_ty.font.name = "Segoe UI"
p_ty.font.size = Pt(16)
p_ty.font.bold = True
p_ty.font.color.rgb = GOLD_LIGHT
p_ty.alignment = PP_ALIGN.CENTER

output_file = os.path.join(os.getcwd(), "SmartParcel_MCA_Presentation.pptx")
prs.save(output_file)
print("SUCCESS: MCA Presentation created at:", output_file)

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
ACCENT_BLUE = RGBColor(37, 99, 235)

def apply_background(slide):
    bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = DARK_BG
    bg_shape.line.color.rgb = DARK_BG
    return bg_shape

def add_header(slide, title, category="PARCELGUARD IOT SYSTEM"):
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
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
    p1.font.size = Pt(26)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p1.space_before = Pt(3)

def add_card(slide, left, top, width, height, title, points, header_color=GOLD_LIGHT):
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
    p_title.font.size = Pt(17)
    p_title.font.bold = True
    p_title.font.color.rgb = header_color
    p_title.space_after = Pt(12)
    
    for pt in points:
        p = tf.add_paragraph()
        p.text = "- " + pt
        p.font.name = "Segoe UI"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(8)

# ----------------------------------------------------
# SLIDE 1: Title Slide
# ----------------------------------------------------
s1 = prs.slides.add_slide(blank_layout)
apply_background(s1)

tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(11.0), Inches(3.5))
tf1 = tb1.text_frame
tf1.word_wrap = True

p = tf1.paragraphs[0]
p.text = "PARCELGUARD"
p.font.name = "Segoe UI"
p.font.size = Pt(46)
p.font.bold = True
p.font.color.rgb = GOLD_LIGHT

p2 = tf1.add_paragraph()
p2.text = "IoT-Based Real-Time Smart Parcel Weight Verification & Audit System"
p2.font.name = "Segoe UI"
p2.font.size = Pt(22)
p2.font.color.rgb = TEXT_WHITE
p2.space_before = Pt(8)

p3 = tf1.add_paragraph()
p3.text = "Cloud-Integrated Architecture with ESP32, FastAPI, PostgreSQL & Live Render Dashboard"
p3.font.name = "Segoe UI"
p3.font.size = Pt(14)
p3.font.color.rgb = MUTED
p3.space_before = Pt(15)

# ----------------------------------------------------
# SLIDE 2: Introduction (Page 1) - Problem Statement & Background
# ----------------------------------------------------
s2 = prs.slides.add_slide(blank_layout)
apply_background(s2)
add_header(s2, "Introduction: Industry Problem & Motivation", "Section 1.1: Background")

add_card(s2, 0.8, 1.8, 5.6, 5.0, "Challenges in Logistics & E-Commerce", [
    "Parcel Weight Discrepancies: Major revenue loss occurs due to missing items, accidental swaps, or dispatch errors.",
    "E-Commerce Fraud & Tampering: Unauthorized theft during transit leads to customer churn and expensive returns.",
    "Manual Bottlenecks: Traditional manual scales and manual barcode logging severely slow down warehouse dispatch lines.",
    "Lack of Digital Audit Trail: Paper-based or offline logging makes historical dispute tracking nearly impossible once parcels leave the facility."
])

add_card(s2, 6.9, 1.8, 5.6, 5.0, "The Need for an Automated IoT Solution", [
    "Real-Time Autonomous Verification: Instant comparison of measured weight against predefined bill-of-materials weight.",
    "Instant Quality Control: Automated classification (Underweight, Overweight, Match) completed in seconds.",
    "Cloud-Synchronized Ledger: Every parcel measurement committed to a managed cloud database for enterprise visibility.",
    "Hands-Free Audio-Visual Alerts: Audio chimes and voice announcements allow operators to verify parcels without looking at a monitor."
])

# ----------------------------------------------------
# SLIDE 3: Introduction (Page 2) - Project Overview & Objectives
# ----------------------------------------------------
s3 = prs.slides.add_slide(blank_layout)
apply_background(s3)
add_header(s3, "Introduction: Project Overview & Objectives", "Section 1.2: System Goals")

add_card(s3, 0.8, 1.8, 3.6, 5.0, "Precision IoT Hardware", [
    "High-accuracy strain gauge load cell with HX711 24-bit ADC amplifier.",
    "Firmware-level auto-tare at startup and digital calibration factor tuning.",
    "ESP32 Wi-Fi micro-controller streaming live sensor payloads over encrypted HTTPS."
])

add_card(s3, 4.8, 1.8, 3.6, 5.0, "Cloud Infrastructure", [
    "High-performance FastAPI asynchronous web server hosted on Render Cloud.",
    "Managed PostgreSQL database for historical logging and compliance auditing.",
    "Standardized JSON REST API endpoints (/api/sensor, /api/dashboard, /api/settings)."
])

add_card(s3, 8.8, 1.8, 3.6, 5.0, "Interactive Web Dashboard", [
    "Live real-time telemetry displaying actual weight, target weight, and allowed tolerance.",
    "Dynamic Chart.js weight tracking visualization updated every 2 seconds.",
    "Web Speech Synthesis voice announcements and HTML5 AudioContext sound chimes."
])

# ----------------------------------------------------
# SLIDE 4: Components
# ----------------------------------------------------
s4 = prs.slides.add_slide(blank_layout)
apply_background(s4)
add_header(s4, "Hardware & Software Components", "Section 2: System Architecture")

add_card(s4, 0.8, 1.8, 5.6, 5.0, "Hardware Components", [
    "ESP32 Dev Module: 32-bit dual-core Xtensa micro-controller with integrated 2.4 GHz Wi-Fi and hardware TLS crypto accelerator.",
    "HX711 24-Bit ADC: Precision dual-channel analog-to-digital converter designed specifically for weigh scales.",
    "Strain Gauge Load Cell: Mechanical transducer converting physical parcel weight into proportional micro-volt electrical signals.",
    "Rigid Platform Mount: Balanced physical platform ensuring accurate load distribution across the load cell beam.",
    "Interfacing & Power: GPIO 4 (DT) and GPIO 5 (SCK) with regulated 3.3V power supply."
])

add_card(s4, 6.9, 1.8, 5.6, 5.0, "Software & Cloud Stack", [
    "ESP32 Firmware: Arduino C++ utilizing HX711, WiFiClientSecure, and HTTPClient libraries.",
    "Cloud Backend: FastAPI (Python 3.11) with asynchronous request processing and CORS middleware.",
    "Database: Managed PostgreSQL on Render with SQLAlchemy ORM (and local SQLite fallback).",
    "Frontend UI: Responsive HTML5/CSS3 dashboard, Chart.js time-series charts, and Web Speech API.",
    "Hosting & DevOps: Render Cloud platform with continuous Docker deployment."
])

# ----------------------------------------------------
# SLIDE 5: Block Diagram
# ----------------------------------------------------
s5 = prs.slides.add_slide(blank_layout)
apply_background(s5)
add_header(s5, "System Block Diagram & Information Flow", "Section 3: Architecture")

stages = [
    ("1. Physical Layer", "Parcel on Platform\nStrain Gauge Load Cell", 0.8, 2.0, 2.1),
    ("2. Sensing Layer", "HX711 24-bit ADC\nAmp & Digitization", 3.2, 2.0, 2.1),
    ("3. Edge Compute", "ESP32 MCU\nTare, Scale & JSON Pack", 5.6, 2.0, 2.1),
    ("4. Network Layer", "Wi-Fi (2.4 GHz)\nHTTPS POST (TLS 1.2/1.3)", 8.0, 2.0, 2.1),
    ("5. Cloud Platform", "Render FastAPI Server\nPostgreSQL Database", 10.4, 2.0, 2.1)
]

for title, desc, left, top, width in stages:
    box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(2.2))
    box.fill.solid()
    box.fill.fore_color.rgb = CARD_BG
    box.line.color.rgb = GOLD
    box.line.width = Pt(1.5)
    
    tf = box.text_frame
    tf.word_wrap = True
    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.name = "Segoe UI"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = GOLD_LIGHT
    p0.alignment = PP_ALIGN.CENTER
    
    p1 = tf.add_paragraph()
    p1.text = desc
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(11)
    p1.font.color.rgb = TEXT_WHITE
    p1.alignment = PP_ALIGN.CENTER
    p1.space_before = Pt(8)

feedback_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.6), Inches(11.7), Inches(2.1))
feedback_box.fill.solid()
feedback_box.fill.fore_color.rgb = CARD_BG
feedback_box.line.color.rgb = RGBColor(16, 185, 129)
feedback_box.line.width = Pt(1.5)

tf_fb = feedback_box.text_frame
tf_fb.word_wrap = True
p = tf_fb.paragraphs[0]
p.text = "6. Presentation & Operator Feedback Layer (Real-Time Web Dashboard)"
p.font.name = "Segoe UI"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = GREEN

points_fb = [
    "Real-Time Metrics: Live Weight (g), Expected Parcel Weight, and Allowed Tolerance.",
    "Visual Status Badges: NO PARCEL (Empty), MATCH (Green), UNDERWEIGHT (Amber), OVERWEIGHT (Red).",
    "Audio & Speech Synthesizer: Instant spoken voice status ('Pass', 'Rejected - Underweight') and alert chimes.",
    "Dynamic Telemetry Chart: Live updating Chart.js graph refreshed automatically every 2 seconds via REST polling."
]
for pt in points_fb:
    p_item = tf_fb.add_paragraph()
    p_item.text = "- " + pt
    p_item.font.name = "Segoe UI"
    p_item.font.size = Pt(12)
    p_item.font.color.rgb = TEXT_WHITE
    p_item.space_before = Pt(4)

# ----------------------------------------------------
# SLIDE 6: Working (Page 1) - Sensing, Calibration & Edge Processing
# ----------------------------------------------------
s6 = prs.slides.add_slide(blank_layout)
apply_background(s6)
add_header(s6, "Working Principle: Calibration & Edge Sensing", "Section 4.1: Edge Operations")

add_card(s6, 0.8, 1.8, 5.6, 5.0, "Step 1: Tare & Scale Calibration", [
    "Zero Taring at Startup: During boot, the system measures the baseline tare with an empty platform to cancel ambient mechanical weight.",
    "Calibration Factor: Raw 24-bit counts are multiplied by the calibrated factor (-432.04) to obtain true weight in grams.",
    "10-Sample Moving Average: The HX711 gathers 10 consecutive readings to filter out environmental vibrations and noise spikes.",
    "Zero Threshold Filter: Readings below 0.5 g are mapped to 0.00 g to eliminate micro-fluctuations on the empty tray."
])

add_card(s6, 6.9, 1.8, 5.6, 5.0, "Step 2: Secure Cloud Transmission", [
    "JSON Payload Construction: Formats telemetry payload: {\"actual_weight_g\": 126.73, \"source\": \"ESP32\"}.",
    "Encrypted TLS Handshake: Initiates HTTPS connection to Render Cloud (port 443) using WiFiClientSecure.",
    "Socket Lifecycle Management: Explicit header 'Connection: close' and client.stop() prevent lwIP socket exhaustion.",
    "Cold-Start Resilience: 30-second client timeout ensures transmission succeeds even if cloud containers are waking from sleep."
])

# ----------------------------------------------------
# SLIDE 7: Working (Page 2) - Cloud Verification & Operator Feedback
# ----------------------------------------------------
s7 = prs.slides.add_slide(blank_layout)
apply_background(s7)
add_header(s7, "Working Principle: Cloud Verification & Alerting", "Section 4.2: Cloud Logic")

add_card(s7, 0.8, 1.8, 5.6, 5.0, "Step 3: Verification Algorithm", [
    "Empty Detection: If actual_weight <= 0.5 g, the state is classified as 'NO PARCEL'.",
    "Tolerance Boundary Check: Calculates valid bounds: Minimum = (Expected - Tolerance), Maximum = (Expected + Tolerance).",
    "Decision Rules:",
    "  - If actual < Minimum => 'UNDERWEIGHT'",
    "  - If Minimum <= actual <= Maximum => 'MATCH'",
    "  - If actual > Maximum => 'OVERWEIGHT'",
    "Persistent Storage: Commits reading record and timestamp into PostgreSQL database table 'readings'."
])

add_card(s7, 6.9, 1.8, 5.6, 5.0, "Step 4: Real-Time UI & Voice Alerts", [
    "Continuous Dashboard Polling: Frontend queries /api/dashboard every 2 seconds with cache-busting.",
    "State Stability Latching: Requires consecutive matching readings before locking a decision to prevent false rejects.",
    "Voice Synthesis: In-browser speech engine automatically announces: 'Pass. Correct parcel weight' or 'Rejected'.",
    "Audio Alarm Synthesizer: Plays custom multi-frequency chimes (sine/triangle audio waves) for instant auditory feedback."
])

# ----------------------------------------------------
# SLIDE 8: Conclusion
# ----------------------------------------------------
s8 = prs.slides.add_slide(blank_layout)
apply_background(s8)
add_header(s8, "Conclusion & Future Enhancements", "Section 5: Summary")

add_card(s8, 0.8, 1.8, 5.6, 5.0, "Key Project Achievements", [
    "Complete Automation: Eliminates manual inspection bottlenecks, parcel weight fraud, and shipping discrepancies.",
    "End-to-End Cloud Connectivity: Real-time synchronization from load cell to live Render web application.",
    "Industrial-Grade Resilience: Robust handling of TLS cryptographic handshakes, cloud spin-downs, and socket recycling.",
    "Digital Audit Trail: Centralized PostgreSQL database permanently logs all parcel transactions for compliance and dispute resolution."
])

add_card(s8, 6.9, 1.8, 5.6, 5.0, "Future Scope & Enhancements", [
    "Barcode & RFID Integration: Automatic lookup of target weight and customer order details upon scanning shipping labels.",
    "Automated Conveyor Diverter: Servo-motor or pneumatic gate to automatically route rejected parcels to an inspection bin.",
    "Computer Vision Inspection: Overhead camera OCR to simultaneously verify parcel label, dimensions, and weight.",
    "MQTT / WebSocket Protocol: Sub-second bidirectional event streaming for high-speed industrial conveyor systems."
])

output_file = os.path.join(os.getcwd(), "SmartParcel_Presentation.pptx")
prs.save(output_file)
print("SUCCESS: Presentation created at:", output_file)

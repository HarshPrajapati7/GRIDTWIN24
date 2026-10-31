from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_THEME_COLOR
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'slides' / 'GRIDTWIN24_pitch.pptx'
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

BG = RGBColor(11,18,32)
PANEL = RGBColor(18,31,49)
PANEL2 = RGBColor(23,45,67)
TEAL = RGBColor(39,207,181)
BLUE = RGBColor(83,166,255)
AMBER = RGBColor(246,184,75)
WHITE = RGBColor(238,244,251)
MUTED = RGBColor(162,181,201)
RED = RGBColor(236,103,103)
GREEN = RGBColor(99,209,151)
FONT = 'Aptos'


def rect(slide, x,y,w,h, fill=PANEL, line=None, radius=True):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
                                   Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid(); shape.fill.fore_color.rgb = fill
    shape.line.fill.background() if line is None else None
    if line is not None:
        shape.line.color.rgb = line; shape.line.width = Pt(1)
    if radius:
        try: shape.adjustments[0] = 0.12
        except Exception: pass
    return shape


def txt(slide, text, x,y,w,h, size=16, color=WHITE, bold=False, font=FONT, align=None, valign=MSO_ANCHOR.TOP, margin=0.02):
    box=slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf=box.text_frame; tf.clear(); tf.word_wrap=True
    tf.margin_left=Inches(margin); tf.margin_right=Inches(margin); tf.margin_top=Inches(margin); tf.margin_bottom=Inches(margin)
    tf.vertical_anchor=valign
    p=tf.paragraphs[0]
    if align is not None: p.alignment=align
    p.space_after=Pt(0)
    r=p.add_run(); r.text=text; r.font.name=font; r.font.size=Pt(size); r.font.bold=bold; r.font.color.rgb=color
    return box


def add_bg(slide):
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb=BG
    # restrained top accent
    rect(slide,0,0,13.333,0.055,TEAL,radius=False)


def header(slide, kicker, title, subtitle=None, n=None):
    txt(slide,kicker.upper(),0.55,0.30,11.9,0.25,9,TEAL,True)
    txt(slide,title,0.55,0.67,12.2,0.55,25,WHITE,True)
    if subtitle: txt(slide,subtitle,0.57,1.26,12.0,0.42,11,MUTED)
    if n: txt(slide,f'{n:02d}',12.35,0.28,0.45,0.25,9,MUTED,True,align=PP_ALIGN.RIGHT)


def bullet_list(slide, items, x,y,w, line_h=0.55, size=14, color=WHITE, bullet_color=TEAL):
    for i,item in enumerate(items):
        yy=y+i*line_h
        rect(slide,x,yy+0.12,0.10,0.10,bullet_color,radius=True)
        txt(slide,item,x+0.22,yy,w-0.22,line_h-0.03,size,color)


def image(slide,path,x,y,w,h=None):
    p=Path(path)
    if not p.exists(): return
    if h is None:
        slide.shapes.add_picture(str(p), Inches(x), Inches(y), width=Inches(w))
    else:
        slide.shapes.add_picture(str(p), Inches(x), Inches(y), width=Inches(w), height=Inches(h))


def card(slide,x,y,w,h,title,body,accent=TEAL, body_size=12):
    rect(slide,x,y,w,h,PANEL)
    rect(slide,x,y,0.07,h,accent,radius=False)
    txt(slide,title,x+0.22,y+0.18,w-0.4,0.34,14,WHITE,True)
    txt(slide,body,x+0.22,y+0.62,w-0.42,h-0.72,body_size,MUTED)

# 1 — Title
s=prs.slides.add_slide(blank); add_bg(s)
txt(s,'TOMORROW’S LOAD  /  TIME SERIES',0.72,0.75,7.3,0.3,11,TEAL,True)
txt(s,'GRIDTWIN-24',0.72,1.38,8.4,0.78,36,WHITE,True)
txt(s,'Forecast-to-Physics Energy Intelligence',0.76,2.27,8.2,0.5,20,MUTED,False)
txt(s,'Tomorrow’s demand. Today’s decisions.',0.76,3.02,7.4,0.42,17,AMBER,True)
rect(s,0.76,4.05,5.65,1.36,PANEL)
txt(s,'24-hour forecast  →  PV / battery scenarios  →  12 V DC bench validation path',1.00,4.34,5.12,0.72,16,WHITE,True)
image(s,ROOT/'diagrams/system_architecture.png',7.35,1.15,5.40,4.90)
txt(s,'Open-source • Gemma 4 operator • 12 V DC bench design',0.78,6.56,8.5,0.3,10,MUTED)
txt(s,'Working project name — trademark/domain check pending',0.78,7.05,8.5,0.2,8,MUTED)

# 2 — Problem
s=prs.slides.add_slide(blank); add_bg(s); header(s,'01 / The official problem','Tomorrow’s load is not just a chart','The organisers ask for the next 24 hourly demand values and a forecast-vs-actual view.',2)
card(s,0.65,2.0,3.8,1.65,'Forecast 24 hours','Predict one complete next-day hourly demand profile from past demand and related data.',TEAL)
card(s,4.75,2.0,3.8,1.65,'Evaluate honestly','Compare against actuals using time-respecting rolling-origin evaluation and a seasonal baseline.',BLUE)
card(s,8.85,2.0,3.8,1.65,'Make it actionable','Show peak windows, uncertainty where calibrated, and explain the operational implications.',AMBER)
rect(s,0.65,4.12,12.0,1.55,PANEL2)
txt(s,'Core rule',0.92,4.38,1.5,0.3,13,TEAL,True)
txt(s,'The provided dataset and the official 24-hour forecasting task remain the product’s source of truth. The hardware, scheduler and Gemma agent are extensions — never substitutes.',2.45,4.31,9.85,0.75,16,WHITE,True)
txt(s,'Source: official Hacktoberfest Hack Day Lucknow problem-statement PDF, page 3.',0.72,6.55,11.6,0.24,9,MUTED)

# 3 — Vision
s=prs.slides.add_slide(blank); add_bg(s); header(s,'02 / Product vision','Close the loop between prediction and action','Forecast → scenario → approval → measured response.',3)
steps=[('01','PREDICT','24-hour demand curve and peak flags'),('02','UNDERSTAND','Uncertainty, drivers and evidence'),('03','SIMULATE','Tariff, capacity and flexible-load scenarios'),('04','VALIDATE','Measure the response on a safe physical DC bench')]
for i,(n,t,b) in enumerate(steps):
    x=0.7+i*3.15
    rect(s,x,2.15,2.8,2.25,PANEL)
    txt(s,n,x+0.22,2.38,0.5,0.25,11,TEAL,True)
    txt(s,t,x+0.22,2.88,2.35,0.35,15,WHITE,True)
    txt(s,b,x+0.22,3.42,2.35,0.65,12,MUTED)
    if i<3: txt(s,'→',x+2.86,3.02,0.28,0.35,18,AMBER,True,align=PP_ALIGN.CENTER)
rect(s,0.7,5.05,11.9,0.9,PANEL2)
txt(s,'The physical rig is a development testbed, not a real grid emulator or a mains controller.',0.95,5.32,11.4,0.3,14,AMBER,True)

# 4 — Everyday use case
s=prs.slides.add_slide(blank); add_bg(s); header(s,'03 / Who benefits','Energy affects everyone; sell first to someone who can act','Start with a facility manager, not “every consumer” as the first customer.',4)
card(s,0.7,2.05,3.7,1.65,'Hostels & campuses','Multiple buildings, pumps, HVAC, kitchens and a facilities owner who can test a plan.',TEAL)
card(s,4.82,2.05,3.7,1.65,'Apartments & clinics','Shared loads, common-area energy, pumps and operating schedules.',BLUE)
card(s,8.94,2.05,3.7,1.65,'Small commercial','Hotels, co-working, retail and workshops with repeated energy bills.',AMBER)
txt(s,'The product should answer',0.78,4.45,3.1,0.35,14,TEAL,True)
txt(s,'“What will our demand look like tomorrow, which hours need attention, and what can we safely move?”',0.78,4.92,11.6,0.75,23,WHITE,True)
txt(s,'Household edition comes later, once data access, meter integrations and the value proposition are validated.',0.78,6.26,11.5,0.3,10,MUTED)

# 5 — Architecture
s=prs.slides.add_slide(blank); add_bg(s); header(s,'04 / Architecture','One system, three bounded layers','Forecasting, decision logic and language interface stay separate.',5)
image(s,ROOT/'diagrams/system_architecture.png',0.72,1.78,11.9,4.9)

# 6 — ML protocol
s=prs.slides.add_slide(blank); add_bg(s); header(s,'05 / Scientific credibility','A forecast only counts if it survives a fair test','No random row split. No future leakage. No interval without calibration.',6)
image(s,ROOT/'diagrams/synthetic_forecast_demo.png',0.68,1.85,7.3,3.55)
card(s,8.25,1.92,4.25,1.14,'Benchmark first','Seasonal-naive baseline; retain it if the ML model fails to beat it.',TEAL,11)
card(s,8.25,3.25,4.25,1.14,'Rolling origin','Each test forecast sees only the history available at that forecast time.',BLUE,11)
card(s,8.25,4.58,4.25,1.14,'Honest uncertainty','Show empirical bands only when calibration residuals support them.',AMBER,11)
txt(s,'Important: this plotted series is synthetic smoke-test data, not the organiser dataset or a claimed result.',0.78,6.0,11.4,0.35,10,AMBER,True)

# 7 — Hardware
s=prs.slides.add_slide(blank); add_bg(s); header(s,'06 / Physical demonstrator','A 12 V DC energy bench designed for safe measurement','12 V DC only • three loads • physical E-stop • local ARM interlock.',7)
image(s,ROOT/'diagrams/hardware_hil.png',0.55,1.82,8.2,4.8)
card(s,8.95,1.98,3.65,1.15,'Controller','ESP32 DevKit + Wi-Fi / MQTT telemetry.',TEAL,11)
card(s,8.95,3.34,3.65,1.15,'Measurement','INA3221: 3-channel voltage/current monitoring; check exact shunt limits.',BLUE,10)
card(s,8.95,4.70,3.65,1.15,'Actuation','Fused DC branches + logic MOSFET drivers + physical E-stop and ARM switch.',AMBER,10)
txt(s,'No AC mains. No building wiring. Commercial control requires certified devices and qualified installation.',0.76,6.68,11.9,0.25,9,RED,True)

# 8 — Gemma
s=prs.slides.add_slide(blank); add_bg(s); header(s,'07 / Gemma 4','The agent operates tools; it does not invent the physics','Native function calling turns an operator question into a verifiable workflow.',8)
card(s,0.7,2.05,3.75,2.2,'Ask in natural language','“Why is tomorrow’s peak at 19:00? Move the demo pump without crossing the capacity limit.”',TEAL,13)
card(s,4.8,2.05,3.75,2.2,'Call deterministic tools','get_forecast()\nexplain_peak()\nrun_load_shift_scenario()\nget_live_telemetry()',BLUE,12)
card(s,8.9,2.05,3.75,2.2,'Return grounded answer','Numbers come from Python. Tool outputs are logged. Hardware changes require confirmation and interlocks.',AMBER,12)
rect(s,0.7,4.85,11.95,0.9,PANEL2)
txt(s,'Gemma 4 supports image / multimodal inputs and function calling; the application must validate and execute tool calls safely.',0.95,5.12,11.3,0.35,13,WHITE,True)
txt(s,'Model reference: official Google AI for Developers Gemma 4 model card and function-calling guide.',0.78,6.28,11.4,0.25,9,MUTED)

# 9 — PV + battery dispatch
s=prs.slides.add_slide(blank); add_bg(s); header(s,'08 / Energy decision engine','Optimise the energy system, not just the next-day curve','A constrained LP models energy balance, battery SOC and real operating limits.',9)
image(s,ROOT/'diagrams/battery_dispatch.png',0.72,1.82,7.55,4.65)
card(s,8.55,1.95,4.05,1.20,'Physical constraints','Charge / discharge power, SOC reserve, efficiencies and grid import cap.',TEAL,11)
card(s,8.55,3.35,4.05,1.20,'Economic objective','Import / export tariff, battery degradation and optional peak-demand charge.',BLUE,11)
card(s,8.55,4.75,4.05,1.20,'No free energy','Terminal battery SOC is forced back to its starting level in the 24-hour simulation.',AMBER,11)
txt(s,'Simulation only: does not control a real battery and does not claim measured savings.',0.78,6.67,11.8,0.25,9,RED,True)

# 10 — Product workflow
s=prs.slides.add_slide(blank); add_bg(s); header(s,'09 / User journey','From “what happens tomorrow?” to measured action','A product loop customers can use every day.',9)
image(s,ROOT/'diagrams/product_flow.png',0.65,2.0,12.0,3.4)
card(s,0.8,5.75,5.5,0.9,'Read-only first','Upload bill / interval data; receive forecast, peak report and scenario.',TEAL,11)
card(s,6.85,5.75,5.5,0.9,'Automation later','Only after paid pilot, approved meter access and certified control equipment.',AMBER,11)

# 10 — Business
s=prs.slides.add_slide(blank); add_bg(s); header(s,'10 / Business model','Start narrow, prove ROI, then expand','Software-first B2B beats selling hardware before product-market fit.',10)
card(s,0.7,2.05,3.7,1.7,'Pilot buyer','Campus / hostel / apartment operator with interval data and a facilities owner.',TEAL)
card(s,4.82,2.05,3.7,1.7,'Recurring value','Peak forecasts, weekly reports, scenario decisions and multi-site comparisons.',BLUE)
card(s,8.94,2.05,3.7,1.7,'Revenue path','Per-site SaaS → paid commissioning → gateway / integrations → multi-site contracts.',AMBER)
txt(s,'The ROI test',0.82,4.45,2.4,0.34,14,TEAL,True)
txt(s,'Baseline meter data → agreed intervention → measured kWh / peak / cost → operational impact check.',0.82,4.9,11.7,0.65,20,WHITE,True)
txt(s,'No savings percentage should be claimed before a real site pilot.',0.82,6.1,11.4,0.28,10,AMBER,True)

# 11 — Existing competition / differentiation
s=prs.slides.add_slide(blank); add_bg(s); header(s,'11 / Competitive reality','Energy dashboards already exist. We must be more specific.','Do not claim that forecasting, digital twins or HIL are globally unprecedented.',11)
card(s,0.72,2.0,3.75,1.8,'Existing landscape','Home Assistant, commercial building-energy platforms and microgrid digital-twin research already cover adjacent capabilities.',RED,11)
card(s,4.8,2.0,3.75,1.8,'Our wedge to test','Vendor-neutral, low-cost forecasting + constrained scenarios + measured low-voltage validation for smaller multi-building sites.',TEAL,11)
card(s,8.88,2.0,3.75,1.8,'What becomes defensible','Real site integrations, forecast calibration, workflow adoption, measured outcomes and trusted deployment.',BLUE,11)
rect(s,0.72,4.5,11.9,0.95,PANEL2)
txt(s,'If a customer cannot share data or identify a recurring decision, do not build a custom hardware product for them.',0.98,4.78,11.3,0.35,14,WHITE,True)

# 12 — Risks / safety
s=prs.slides.add_slide(blank); add_bg(s); header(s,'12 / Red-team review','The project is ambitious, but its claims must stay bounded','These are the conditions that prevent a good demo from becoming a bad product.',12)
risks=[('Data mismatch','Audit timestamp, unit, cadence and timezone.'),('Leakage','Rolling-origin 24-hour evaluation; no random split.'),('False intervals','Calibrate and report coverage, or withhold them.'),('Grid/site mismatch','Keep challenge grid series separate from local site profile.'),('Unsafe control','12 V DC bench, fuse, E-stop, physical ARM, fail OFF.'),('No market proof','Paid read-only pilot before field hardware.')]
for i,(t,b) in enumerate(risks):
    col=i%2; row=i//2; x=0.75+col*6.0; y=1.95+row*1.42
    card(s,x,y,5.65,1.17,t,b,[TEAL,BLUE,AMBER,RED,TEAL,BLUE][i],11)

# 13 — Roadmap / MVP
s=prs.slides.add_slide(blank); add_bg(s); header(s,'13 / Execution','Build the forecast first. Hardware is the final act.','A disciplined order keeps the required problem statement complete.',13)
phases=[('P0','DATA + MODEL','Dataset audit, baseline, rolling evaluation, 24 outputs'),('P1','DASHBOARD','Forecast vs actual, peak windows, explanation and interval'),('P2','AGENT','Gemma 4 tool calling over tested functions'),('P3','HIL','ESP32 + INA3221 + 12 V fused DC energy bench')]
for i,(n,t,b) in enumerate(phases):
    y=2.02+i*0.98
    rect(s,0.82,y,11.7,0.78,PANEL)
    txt(s,n,1.02,y+0.18,0.5,0.25,12,TEAL,True)
    txt(s,t,1.7,y+0.18,2.4,0.25,13,WHITE,True)
    txt(s,b,4.2,y+0.18,7.9,0.35,12,MUTED)

# 14 — close / ask
s=prs.slides.add_slide(blank); add_bg(s)
txt(s,'GRIDTWIN-24',0.85,0.8,6.2,0.65,32,WHITE,True)
txt(s,'Forecast → Decide → Measure',0.88,1.62,8.6,0.45,20,TEAL,True)
txt(s,'We are not building another energy dashboard. We are building a testable path from tomorrow’s demand forecast to a safer, more informed operating decision.',0.9,2.5,8.6,1.35,22,WHITE,True)
rect(s,0.9,4.55,7.9,1.05,PANEL2)
txt(s,'NEXT STEP',1.15,4.77,1.4,0.25,10,AMBER,True)
txt(s,'Run on the real organiser dataset. Then secure one read-only campus / hostel pilot.',2.6,4.72,5.8,0.55,14,WHITE,True)
image(s,ROOT/'diagrams/hardware_hil.png',9.05,1.45,3.55,3.8)
txt(s,'GRIDTWIN-24 • working name',0.92,6.85,4.0,0.25,9,MUTED)

# 15 — references
s=prs.slides.add_slide(blank); add_bg(s); header(s,'Appendix / References','Technical sources and limitations','Use these to ground architecture choices; re-check model and component docs before build.',16)
refs=[
'Official problem statement: Hacktoberfest Hack Day Lucknow PDF, page 3 — Tomorrow’s Load.',
'Gemma 4 model card: ai.google.dev/gemma/docs/core/model_card_4',
'Gemma 4 function calling: ai.google.dev/gemma/docs/capabilities/text/function-calling-gemma4',
'TI INA3221: ti.com/product/INA3221 — 0–26 V, 3-channel monitor; current depends on shunts.',
'Adafruit INA3221 Arduino library: github.com/adafruit/Adafruit_INA3221',
'Energy digital-twin context: Computers and Electrical Engineering, June 2026, DOI 10.1016/j.compeleceng.2026.111100',
'Home Assistant energy docs: home-assistant.io/docs/energy/; Schneider EcoStruxure Building Energy Management.'
]
bullet_list(s,refs,0.86,1.95,11.4,line_h=0.62,size=12)
txt(s,'Synthetic demo data is not organiser data. No measured savings or real-grid control claims are made.',0.85,6.62,11.5,0.3,10,AMBER,True)

prs.save(OUT)
print(OUT)

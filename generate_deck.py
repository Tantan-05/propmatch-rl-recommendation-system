"""
generate_deck.py
Generates a professional 16:9 widescreen PowerPoint presentation for the
PropMatch Real Estate RL + RS project.
"""

from pathlib import Path
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_FILE = Path("PropMatch_RL_RS_Presentation.pptx")

# -------------------------------------------------------------
# Color Palette
# -------------------------------------------------------------
C_BG_DARK       = RGBColor(15, 23, 42)      # #0F172A Slate 900
C_BG_LIGHT      = RGBColor(248, 250, 252)  # #F8FAFC
C_CARD_BG       = RGBColor(255, 255, 255)  # White
C_CARD_BG_ALT   = RGBColor(241, 245, 249)  # Slate 100
C_BORDER        = RGBColor(226, 232, 240)  # Slate 200
C_BORDER_ACCENT = RGBColor(191, 219, 254)  # Blue 200

C_PRIMARY       = RGBColor(30, 41, 59)     # Slate 800 (Main text)
C_MUTED         = RGBColor(100, 116, 139)  # Slate 500
C_SECONDARY     = RGBColor(71, 85, 105)    # Slate 600

C_BLUE          = RGBColor(37, 99, 235)    # #2563EB Royal Blue
C_BLUE_DARK     = RGBColor(29, 78, 216)    # #1D4ED8
C_TEAL          = RGBColor(13, 148, 136)   # #0D9488 Emerald/Teal
C_INDIGO        = RGBColor(79, 70, 229)    # #4F46E5
C_AMBER         = RGBColor(217, 119, 6)    # Amber 600
C_WHITE         = RGBColor(255, 255, 255)

FONT_HEADING = "Calibri"
FONT_BODY    = "Calibri"

def create_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_bg(slide, dark=False):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG_DARK if dark else C_BG_LIGHT
        bg.line.color.rgb = C_BG_DARK if dark else C_BG_LIGHT
        return bg

    def add_header(slide, tag: str, title: str, subtitle: str = ""):
        # Category Tag
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.7), Inches(0.35))
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        tf_tag.margin_left = tf_tag.margin_right = tf_tag.margin_top = tf_tag.margin_bottom = 0
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag.upper()
        p_tag.font.name = FONT_HEADING
        p_tag.font.size = Pt(11)
        p_tag.font.bold = True
        p_tag.font.color.rgb = C_BLUE

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.78), Inches(11.7), Inches(0.65))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_right = tf_title.margin_top = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.name = FONT_HEADING
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = C_PRIMARY

        # Subtitle
        if subtitle:
            sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.42), Inches(11.7), Inches(0.35))
            tf_sub = sub_box.text_frame
            tf_sub.word_wrap = True
            tf_sub.margin_left = tf_sub.margin_right = tf_sub.margin_top = tf_sub.margin_bottom = 0
            p_sub = tf_sub.paragraphs[0]
            p_sub.text = subtitle
            p_sub.font.name = FONT_BODY
            p_sub.font.size = Pt(13)
            p_sub.font.color.rgb = C_MUTED

    def add_card(slide, left, top, width, height, bg_color=C_CARD_BG, border_color=C_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
        return card

    # =========================================================================
    # SLIDE 1: Title Slide (Dark Theme)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1, dark=True)

    # Accent decorative bar
    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(0.9), Inches(0.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = C_BLUE
    bar.line.color.rgb = C_BLUE

    # Title & Subtitle text frame
    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(2.1), Inches(11.7), Inches(2.6))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "PropMatch: Real Estate Recommendation System"
    p.font.name = FONT_HEADING
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    p2 = tf1.add_paragraph()
    p2.text = "Reinforcement Learning & Contextual Bandit Framework for Multi-Constraint Property Matching"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(18)
    p2.font.color.rgb = RGBColor(148, 163, 184)
    p2.space_before = Pt(12)

    # Team Box
    team_card = add_card(s1, Inches(0.8), Inches(5.0), Inches(11.7), Inches(1.7), bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))
    team_box = s1.shapes.add_textbox(Inches(1.1), Inches(5.15), Inches(11.1), Inches(1.4))
    tf_team = team_box.text_frame
    tf_team.word_wrap = True

    p_t1 = tf_team.paragraphs[0]
    p_t1.text = "PROJECT AUTHORS & CONTRIBUTORS"
    p_t1.font.name = FONT_HEADING
    p_t1.font.size = Pt(11)
    p_t1.font.bold = True
    p_t1.font.color.rgb = RGBColor(56, 189, 248) # Light blue

    p_t2 = tf_team.add_paragraph()
    p_t2.text = "• Tanisha Ahuja  (Roll No: R002)\n• Arjun Ghone   (Roll No: R008)"
    p_t2.font.name = FONT_BODY
    p_t2.font.size = Pt(15)
    p_t2.font.bold = True
    p_t2.font.color.rgb = C_WHITE
    p_t2.space_before = Pt(6)

    p_t3 = tf_team.add_paragraph()
    p_t3.text = "Department of Computer Science & Engineering | 4th Year B.Tech | MPSTME, NMIMS"
    p_t3.font.name = FONT_BODY
    p_t3.font.size = Pt(12)
    p_t3.font.color.rgb = RGBColor(203, 213, 225)
    p_t3.space_before = Pt(6)

    # =========================================================================
    # SLIDE 2: Executive Summary & Project Motivation
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2)
    add_header(s2, "Overview", "Executive Summary: The PropMatch Solution", "AI-driven property discovery combining RS candidate selection with RL reward optimization")

    cards_data_s2 = [
        ("The Challenge", "Traditional real estate portals rely on rigid Boolean filters (price <= X, BHK = Y). When an exact match is missing, users face empty results, ignored trade-offs, and duplicate project listings.", C_CARD_BG, C_PRIMARY),
        ("The Approach", "Formulated property matching as a Contextual Bandit RL problem. The system evaluates a 497-dimensional state-action vector to predict holistic property suitability across 10 distinct preference dimensions.", C_CARD_BG, C_BLUE),
        ("The Deliverable", "An end-to-end deployed platform: 60k+ catalog preprocessed on HPC, deep value network trained on 500k interactions, FastAPI backend, and a modern React UI with real-time Top-4 ranking.", C_CARD_BG, C_TEAL)
    ]

    for i, (title, desc, bg, accent) in enumerate(cards_data_s2):
        x = Inches(0.8 + i * 3.95)
        add_card(s2, x, Inches(1.9), Inches(3.8), Inches(4.8), bg_color=bg)
        
        # Color bar on top of card
        top_bar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.9), Inches(3.8), Inches(0.08))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = accent
        top_bar.line.color.rgb = accent

        tb = s2.shapes.add_textbox(x + Inches(0.3), Inches(2.2), Inches(3.2), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEADING
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = accent

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.name = FONT_BODY
        p_desc.font.size = Pt(13)
        p_desc.font.color.rgb = C_SECONDARY
        p_desc.space_before = Pt(14)

    # =========================================================================
    # SLIDE 3: Problem Statement
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3)
    add_header(s3, "Problem Statement", "Why Real Estate Recommendation Requires Both RS & RL", "The limitations of conventional matching algorithms in high-value, multi-criteria domains")

    # Left card: Limitations of Standard Approaches
    add_card(s3, Inches(0.8), Inches(1.9), Inches(5.7), Inches(5.0))
    tb_l = s3.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(5.1), Inches(4.6))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "Limitations of Traditional Real Estate RS"
    p.font.name = FONT_HEADING
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = RGBColor(220, 38, 38) # Red

    points_l = [
        ("Binary Cliff Dilemma", "Properties Rs. 10,000 over budget or 10 sq.ft below min area are completely dropped by SQL WHERE filters, ignoring near-perfect matches."),
        ("No Soft-Constraint Trade-offs", "Real buyers happily trade an extra balcony or 2 years of age for a prime locality or lower price. Traditional RS cannot quantify these trade-offs."),
        ("Catalog Duplication & Clutter", "Prominent towers (e.g. 'Dosti Eastern Bay') flood search results across floors and unit variants, destroying catalog diversity."),
        ("Extreme Cold-Start", "Property transactions are rare; collaborative filtering fails because users don't have rich historical interaction matrices.")
    ]
    for h, b in points_l:
        p_h = tf_l.add_paragraph()
        p_h.text = f"• {h}: "
        p_h.font.name = FONT_BODY
        p_h.font.size = Pt(13)
        p_h.font.bold = True
        p_h.font.color.rgb = C_PRIMARY
        p_h.space_before = Pt(10)
        
        run = p_h.add_run()
        run.text = b
        run.font.bold = False
        run.font.color.rgb = C_SECONDARY

    # Right card: The RLRS Solution
    add_card(s3, Inches(6.8), Inches(1.9), Inches(5.7), Inches(5.0))
    tb_r = s3.shapes.add_textbox(Inches(7.1), Inches(2.1), Inches(5.1), Inches(4.6))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "The RL + RS Formulation Advantage"
    p.font.name = FONT_HEADING
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_BLUE

    points_r = [
        ("Continuous Suitability Scoring", "Transforms discrete search into continuous reward prediction in [0.0, 1.0], rewarding near-matches smoothly."),
        ("Multi-Dimensional Utility", "Integrates 10 weighted attributes simultaneously (budget, locality, BHK, age, amenities) into a single scalar reward signal."),
        ("Contextual Bandit Action Space", "Takes user state (preferences) and chooses action (property recommendation) to maximize expected user satisfaction."),
        ("Top-4 Selection with Deduplication", "Filters and ranks candidates while enforcing unique residential project titles to ensure maximum variety.")
    ]
    for h, b in points_r:
        p_h = tf_r.add_paragraph()
        p_h.text = f"• {h}: "
        p_h.font.name = FONT_BODY
        p_h.font.size = Pt(13)
        p_h.font.bold = True
        p_h.font.color.rgb = C_PRIMARY
        p_h.space_before = Pt(10)

        run = p_h.add_run()
        run.text = b
        run.font.bold = False
        run.font.color.rgb = C_SECONDARY

    # =========================================================================
    # SLIDE 4: End-to-End System Workflow
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4)
    add_header(s4, "System Workflow", "End-to-End Project Architecture & Pipeline", "From raw property catalog to trained neural reward model and live user inference")

    steps_s4 = [
        ("1. Data Pipeline", "• 60,255 real properties\n• 10,000 simulated users\n• 500,000 interactions\n• 20 strong, 15 mod, 15 weak\n• No reward leakage into features"),
        ("2. RL Environment", "• 10-factor reward formula\n• Weighted match score [0, 1]\n• User-level 80/10/10 split\n• 0 user overlap across sets\n• Fitted ColumnTransformer"),
        ("3. Model Training", "• PyTorch Value Network\n• 497 -> 256 -> 128 -> 64 -> 1\n• Sigmoid output layer\n• NVIDIA H100 GPU\n• Early stopping at epoch 20"),
        ("4. Deployment", "• FastAPI backend service\n• Reusable inference module\n• Project title deduplication\n• React + Vite responsive UI\n• Real-time Top-4 ranking")
    ]

    for i, (title, desc) in enumerate(steps_s4):
        x = Inches(0.8 + i * 2.95)
        add_card(s4, x, Inches(1.9), Inches(2.8), Inches(4.8), bg_color=C_CARD_BG)

        # Header tag
        tag_bg = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.9), Inches(2.8), Inches(0.4))
        tag_bg.fill.solid()
        tag_bg.fill.fore_color.rgb = C_BLUE_DARK if i % 2 == 0 else C_BLUE
        tag_bg.line.color.rgb = tag_bg.fill.fore_color.rgb

        tb_step = s4.shapes.add_textbox(x, Inches(1.95), Inches(2.8), Inches(0.35))
        tf_s = tb_step.text_frame
        tf_s.paragraphs[0].text = f"STAGE {i+1}"
        tf_s.paragraphs[0].alignment = PP_ALIGN.CENTER
        tf_s.paragraphs[0].font.name = FONT_HEADING
        tf_s.paragraphs[0].font.size = Pt(11)
        tf_s.paragraphs[0].font.bold = True
        tf_s.paragraphs[0].font.color.rgb = C_WHITE

        # Content
        tb_body = s4.shapes.add_textbox(x + Inches(0.2), Inches(2.45), Inches(2.4), Inches(4.1))
        tf_b = tb_body.text_frame
        tf_b.word_wrap = True
        
        p_title = tf_b.paragraphs[0]
        p_title.text = title
        p_title.font.name = FONT_HEADING
        p_title.font.size = Pt(15)
        p_title.font.bold = True
        p_title.font.color.rgb = C_PRIMARY

        p_desc = tf_b.add_paragraph()
        p_desc.text = desc
        p_desc.font.name = FONT_BODY
        p_desc.font.size = Pt(12)
        p_desc.font.color.rgb = C_SECONDARY
        p_desc.space_before = Pt(12)

    # =========================================================================
    # SLIDE 5: Section Divider - RECOMMENDATION SYSTEM
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5, dark=True)

    div_box = s5.shapes.add_textbox(Inches(1.5), Inches(2.2), Inches(10.3), Inches(3.2))
    tf_div = div_box.text_frame
    tf_div.word_wrap = True

    p = tf_div.paragraphs[0]
    p.text = "PART 1"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_BLUE

    p2 = tf_div.add_paragraph()
    p2.text = "Recommendation System (RS)"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(36)
    p2.font.bold = True
    p2.font.color.rgb = C_WHITE
    p2.space_before = Pt(8)

    p3 = tf_div.add_paragraph()
    p3.text = "Catalog Architecture, High-Dimensional Feature Space, Balanced Candidate Sampling & Project-Level Deduplication"
    p3.font.name = FONT_BODY
    p3.font.size = Pt(16)
    p3.font.color.rgb = RGBColor(148, 163, 184)
    p3.space_before = Pt(12)

    # =========================================================================
    # SLIDE 6: RS - Property Catalog & Feature Representation
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6)
    add_header(s6, "RS Architecture", "Property Catalog & Feature Transformation", "Representing complex multi-attribute real estate entities in high-dimensional vector space")

    # 3 Column Cards
    col_w = Inches(3.8)
    # Card 1: Raw Catalog
    add_card(s6, Inches(0.8), Inches(1.9), col_w, Inches(5.0))
    tb1 = s6.shapes.add_textbox(Inches(1.0), Inches(2.1), col_w - Inches(0.4), Inches(4.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    tf1.paragraphs[0].text = "1. Property Catalog"
    tf1.paragraphs[0].font.name = FONT_HEADING
    tf1.paragraphs[0].font.size = Pt(16)
    tf1.paragraphs[0].font.bold = True
    tf1.paragraphs[0].font.color.rgb = C_PRIMARY

    catalog_bullets = [
        "Dataset Source: filtered_data.csv",
        "Total Listings: 60,255 verified properties",
        "Geographic Scope: Mumbai & MMR localities",
        "11 Key Property Features: Price, Area, Rate/sqft, BHK, Baths, Balconies, Age, Locality, City, Property Type, Furnishing",
        "No Null Values in critical ranking columns"
    ]
    for b in catalog_bullets:
        p = tf1.add_paragraph()
        p.text = f"• {b}"
        p.font.name = FONT_BODY
        p.font.size = Pt(12)
        p.font.color.rgb = C_SECONDARY
        p.space_before = Pt(8)

    # Card 2: User Preference Space
    add_card(s6, Inches(4.75), Inches(1.9), col_w, Inches(5.0))
    tb2 = s6.shapes.add_textbox(Inches(4.95), Inches(2.1), col_w - Inches(0.4), Inches(4.5))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    tf2.paragraphs[0].text = "2. User Preference Vector"
    tf2.paragraphs[0].font.name = FONT_HEADING
    tf2.paragraphs[0].font.size = Pt(16)
    tf2.paragraphs[0].font.bold = True
    tf2.paragraphs[0].font.color.rgb = C_PRIMARY

    user_bullets = [
        "Simulated Cohort: 10,000 synthetic buyer profiles",
        "Numeric Constraints: budget_max, min_area, max_area, bedroom_pref, bathroom_pref, balcony_pref, max_age",
        "Categorical Preferences: locality_pref, city_pref, property_type_pref, furnished_pref",
        "Total Input Columns: 22 cross-joined features (14 numeric, 8 categorical)"
    ]
    for b in user_bullets:
        p = tf2.add_paragraph()
        p.text = f"• {b}"
        p.font.name = FONT_BODY
        p.font.size = Pt(12)
        p.font.color.rgb = C_SECONDARY
        p.space_before = Pt(8)

    # Card 3: ColumnTransformer
    add_card(s6, Inches(8.7), Inches(1.9), col_w, Inches(5.0))
    tb3 = s6.shapes.add_textbox(Inches(8.9), Inches(2.1), col_w - Inches(0.4), Inches(4.5))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    tf3.paragraphs[0].text = "3. 497-Dim Preprocessor"
    tf3.paragraphs[0].font.name = FONT_HEADING
    tf3.paragraphs[0].font.size = Pt(16)
    tf3.paragraphs[0].font.bold = True
    tf3.paragraphs[0].font.color.rgb = C_BLUE

    prep_bullets = [
        "StandardScaler on 14 continuous numeric features (zero mean, unit variance)",
        "OneHotEncoder on 8 categorical fields (localities, cities, property types, furnishings)",
        "Sparse Matrix Output: Dimension expands to 497 input features",
        "Strict Leakage Guard: Fitted solely on training users; saved as preprocessor.joblib",
        "handle_unknown='ignore' enabled for robust cold-start handling"
    ]
    for b in prep_bullets:
        p = tf3.add_paragraph()
        p.text = f"• {b}"
        p.font.name = FONT_BODY
        p.font.size = Pt(12)
        p.font.color.rgb = C_SECONDARY
        p.space_before = Pt(8)

    # =========================================================================
    # SLIDE 7: RS - Candidate Generation & Stratified Sampling
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7)
    add_header(s7, "RS Candidate Strategy", "Stratified Candidate Sampling & Balanced Reward Space", "Overcoming exposure bias to ensure robust exploration and stable model generalization")

    # Top summary card
    add_card(s7, Inches(0.8), Inches(1.9), Inches(11.7), Inches(1.2), bg_color=C_CARD_BG_ALT)
    tb_top = s7.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(11.1), Inches(1.0))
    tf_top = tb_top.text_frame
    tf_top.word_wrap = True
    p = tf_top.paragraphs[0]
    p.text = "Why Not Just Train on Random or Top-Ranked Properties?"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY
    p_sub = tf_top.add_paragraph()
    p_sub.text = "Sampling only high-match properties causes the model to collapse on low-reward nuances. Sampling purely at random yields an extreme class imbalance where >95% of pairs have near-zero rewards. PropMatch uses a 3-tier stratified candidate pool."
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(12)
    p_sub.font.color.rgb = C_SECONDARY
    p_sub.space_before = Pt(4)

    # 3 Tier Cards
    tiers = [
        ("Tier 1: Strong Candidates", "20 Properties / User (40%)", "Properties matching primary constraints (exact locality, budget <= max, BHK matches preference). Produces reward scores in [0.80, 1.00].", C_TEAL),
        ("Tier 2: Moderate Candidates", "15 Properties / User (30%)", "Properties matching city and budget, but deviating in locality, age, or balcony count. Produces reward scores in [0.45, 0.75].", C_BLUE),
        ("Tier 3: Weak / Hard Negatives", "15 Properties / User (30%)", "Properties with notable budget or area mismatch, or opposing property types. Teaches the network what not to recommend [0.10, 0.40].", C_AMBER)
    ]

    for i, (t_title, t_count, t_desc, color) in enumerate(tiers):
        x = Inches(0.8 + i * 3.95)
        add_card(s7, x, Inches(3.3), Inches(3.8), Inches(3.6), bg_color=C_CARD_BG)
        
        top_bar = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(3.3), Inches(3.8), Inches(0.08))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = color
        top_bar.line.color.rgb = color

        tb = s7.shapes.add_textbox(x + Inches(0.25), Inches(3.55), Inches(3.3), Inches(3.2))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = t_title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(16)
        p1.font.bold = True
        p1.font.color.rgb = color

        p2 = tf.add_paragraph()
        p2.text = t_count
        p2.font.name = FONT_BODY
        p2.font.size = Pt(13)
        p2.font.bold = True
        p2.font.color.rgb = C_PRIMARY
        p2.space_before = Pt(4)

        p3 = tf.add_paragraph()
        p3.text = t_desc
        p3.font.name = FONT_BODY
        p3.font.size = Pt(12)
        p3.font.color.rgb = C_SECONDARY
        p3.space_before = Pt(12)

    # =========================================================================
    # SLIDE 8: RS - Ranking & Project Deduplication Algorithm
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_bg(s8)
    add_header(s8, "RS Ranking & Filtering", "Top-K Selection & Project-Level Deduplication", "Ensuring user-facing recommendation diversity by eliminating tower-level listing replication")

    # Left box: The Problem & Pseudo-Algorithm
    add_card(s8, Inches(0.8), Inches(1.9), Inches(5.7), Inches(5.0))
    tb_l = s8.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(5.1), Inches(4.6))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "The Project Duplication Problem"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(220, 38, 38)

    p_body = tf_l.add_paragraph()
    p_body.text = "In raw catalogs, large residential complexes list dozens of apartments differing only by floor or minor square footage (e.g. 711 sq.ft vs 714 sq.ft).\n\nWithout deduplication, User U000004 received 'Dosti Eastern Bay' at ranks 1, 2, 3, and 4. While technically distinct property IDs, this creates an unhelpful user experience."
    p_body.font.name = FONT_BODY
    p_body.font.size = Pt(12)
    p_body.font.color.rgb = C_SECONDARY
    p_body.space_before = Pt(8)

    p_algo = tf_l.add_paragraph()
    p_algo.text = "Deduplication Algorithm Logic:"
    p_algo.font.name = FONT_HEADING
    p_algo.font.size = Pt(14)
    p_algo.font.bold = True
    p_algo.font.color.rgb = C_PRIMARY
    p_algo.space_before = Pt(14)

    p_code = tf_l.add_paragraph()
    p_code.text = "1. Sort all catalog candidates by predicted_reward DESC\n2. Maintain an in-memory set seen_titles = set()\n3. For each candidate in ranked list:\n     if candidate.title not in seen_titles:\n         seen_titles.add(candidate.title)\n         recommendations.append(candidate)\n4. Break when len(recommendations) == 4"
    p_code.font.name = "Consolas"
    p_code.font.size = Pt(11)
    p_code.font.color.rgb = C_BLUE_DARK
    p_code.space_before = Pt(6)

    # Right box: Live Example Before vs After
    add_card(s8, Inches(6.8), Inches(1.9), Inches(5.7), Inches(5.0))
    tb_r = s8.shapes.add_textbox(Inches(7.1), Inches(2.1), Inches(5.1), Inches(4.6))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "Catalog Deduplication Impact (User U000004)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_TEAL

    p_sub1 = tf_r.add_paragraph()
    p_sub1.text = "BEFORE (Naive Top-4 Ranking):"
    p_sub1.font.name = FONT_BODY
    p_sub1.font.size = Pt(12)
    p_sub1.font.bold = True
    p_sub1.font.color.rgb = RGBColor(220, 38, 38)
    p_sub1.space_before = Pt(8)

    p_ex1 = tf_r.add_paragraph()
    p_ex1.text = "#1 Godrej Horizon Phase I (Score: 0.9988)\n#2 Dosti Eastern Bay - Unit A (Score: 0.9987)\n#3 Dosti Eastern Bay - Unit B (Score: 0.9987)\n#4 Dosti Eastern Bay - Unit C (Score: 0.9987)"
    p_ex1.font.name = "Consolas"
    p_ex1.font.size = Pt(11)
    p_ex1.font.color.rgb = C_SECONDARY
    p_ex1.space_before = Pt(4)

    p_sub2 = tf_r.add_paragraph()
    p_sub2.text = "AFTER (PropMatch Title-Deduplicated Top-4):"
    p_sub2.font.name = FONT_BODY
    p_sub2.font.size = Pt(12)
    p_sub2.font.bold = True
    p_sub2.font.color.rgb = C_TEAL
    p_sub2.space_before = Pt(14)

    p_ex2 = tf_r.add_paragraph()
    p_ex2.text = "#1 Godrej Horizon Phase I (Wadala, 2BHK | 0.9988)\n#2 Dosti Eastern Bay (Wadala, 2BHK | 0.9987)\n#3 Lodha New Cuffe Parade (Wadala, 2BHK | 0.9892)\n#4 Ajmera Manhattan (Wadala, 2BHK | 0.9854)"
    p_ex2.font.name = "Consolas"
    p_ex2.font.size = Pt(11)
    p_ex2.font.color.rgb = C_PRIMARY
    p_ex2.space_before = Pt(4)

    # =========================================================================
    # SLIDE 9: Section Divider - REINFORCEMENT LEARNING
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_bg(s9, dark=True)

    div_box2 = s9.shapes.add_textbox(Inches(1.5), Inches(2.2), Inches(10.3), Inches(3.2))
    tf_div2 = div_box2.text_frame
    tf_div2.word_wrap = True

    p = tf_div2.paragraphs[0]
    p.text = "PART 2"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_BLUE

    p2 = tf_div2.add_paragraph()
    p2.text = "Reinforcement Learning (RL)"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(36)
    p2.font.bold = True
    p2.font.color.rgb = C_WHITE
    p2.space_before = Pt(8)

    p3 = tf_div2.add_paragraph()
    p3.text = "Contextual Bandit Formulation, Multi-Factor Reward Engineering, Deep Value Network Architecture & Training"
    p3.font.name = FONT_BODY
    p3.font.size = Pt(16)
    p3.font.color.rgb = RGBColor(148, 163, 184)
    p3.space_before = Pt(12)

    # =========================================================================
    # SLIDE 10: RL - Contextual Bandit Formulation
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_bg(s10)
    add_header(s10, "RL Formulation", "Framing Property Discovery as a Contextual Bandit", "Single-step decision process with contextual user states and action-dependent rewards")

    rl_triad = [
        ("Context / State (s)", "The User Preference Profile", [
            "Budget constraint (budget_max)",
            "Area boundaries [min_area, max_area]",
            "Room requirements (bedrooms, baths, balconies)",
            "Target location (locality, city)",
            "Structure preferences (property type, furnishing, max age)"
        ], C_BLUE),
        ("Action (a)", "Property Catalog Recommendation", [
            "Selecting a specific property candidate from 60,255 available listings",
            "Action space: Discrete listing options with distinct feature sets (price, location, dimensions, amenities)",
            "Top-4 policy: Select argmax_a Q(s, a) subject to title deduplication"
        ], C_INDIGO),
        ("Reward r(s, a)", "Multi-Attribute Suitability", [
            "Scalar feedback score r in [0.0, 1.0]",
            "Measures alignment between user context s and selected property action a",
            "Zero counterfactual bias: Rewards observed only for evaluated (s, a) pairs"
        ], C_TEAL)
    ]

    for i, (title, sub, items, col) in enumerate(rl_triad):
        x = Inches(0.8 + i * 3.95)
        add_card(s10, x, Inches(1.9), Inches(3.8), Inches(4.8), bg_color=C_CARD_BG)

        bar = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.9), Inches(3.8), Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.color.rgb = col

        tb = s10.shapes.add_textbox(x + Inches(0.25), Inches(2.15), Inches(3.3), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(16)
        p1.font.bold = True
        p1.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.name = FONT_BODY
        p2.font.size = Pt(12)
        p2.font.bold = True
        p2.font.color.rgb = C_PRIMARY
        p2.space_before = Pt(4)

        for item in items:
            p = tf.add_paragraph()
            p.text = f"• {item}"
            p.font.name = FONT_BODY
            p.font.size = Pt(11)
            p.font.color.rgb = C_SECONDARY
            p.space_before = Pt(8)

    # =========================================================================
    # SLIDE 11: RL - Reward Engineering (10-Component Function)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_bg(s11)
    add_header(s11, "Reward Engineering", "The 10-Factor Multi-Component Reward Function", "Mathematically defining property suitability r(s, a) as a weighted convex combination")

    # Left: Weights table / Breakdown
    add_card(s11, Inches(0.8), Inches(1.9), Inches(5.7), Inches(5.0))
    tb_w = s11.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(5.1), Inches(4.6))
    tf_w = tb_w.text_frame
    tf_w.word_wrap = True

    p = tf_w.paragraphs[0]
    p.text = "Attribute Weights in Reward Formula"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    weights = [
        ("Budget Match (w1)", "20%", "Continuous decay based on budget overage/surplus"),
        ("Bedroom Alignment (w2)", "15%", "Exact match vs penalty per missing/excess room"),
        ("Locality Match (w3)", "15%", "Strict geographical sub-district alignment"),
        ("Area Fit (w4)", "12%", "Quadratic penalty outside [min_area, max_area]"),
        ("Bathroom Alignment (w5)", "8%", "Count comparison against requested baths"),
        ("City Alignment (w6)", "8%", "City boundary verification (e.g. Mumbai)"),
        ("Property Type (w7)", "7%", "Apartment vs Villa vs Penthouse match"),
        ("Furnished Status (w8)", "6%", "Furnished / Semi-Furnished / Unfurnished"),
        ("Age of Property (w9)", "5%", "New construction vs older building penalty"),
        ("Balcony Count (w10)", "4%", "Amenity bonus for balcony requirements")
    ]
    for name, pct, note in weights:
        p_row = tf_w.add_paragraph()
        p_row.text = f"• {name} [{pct}]: "
        p_row.font.name = FONT_BODY
        p_row.font.size = Pt(11)
        p_row.font.bold = True
        p_row.font.color.rgb = C_BLUE_DARK
        p_row.space_before = Pt(4)

        run = p_row.add_run()
        run.text = note
        run.font.bold = False
        run.font.color.rgb = C_SECONDARY

    # Right: Mathematical formulation & Environment properties
    add_card(s11, Inches(6.8), Inches(1.9), Inches(5.7), Inches(5.0))
    tb_f = s11.shapes.add_textbox(Inches(7.1), Inches(2.1), Inches(5.1), Inches(4.6))
    tf_f = tb_f.text_frame
    tf_f.word_wrap = True

    p_f = tf_f.paragraphs[0]
    p_f.text = "Reward Formula Formulation & Properties"
    p_f.font.name = FONT_HEADING
    p_f.font.size = Pt(16)
    p_f.font.bold = True
    p_f.font.color.rgb = C_TEAL

    p_math = tf_f.add_paragraph()
    p_math.text = "R(s, a) = ∑ (w_i * S_i(s, a))   where ∑ w_i = 1.0\nReward Range: R(s, a) ∈ [0.0, 1.0]"
    p_math.font.name = "Consolas"
    p_math.font.size = Pt(12)
    p_math.font.bold = True
    p_math.font.color.rgb = C_PRIMARY
    p_math.space_before = Pt(8)

    props = [
        ("Bounded Output", "Output strictly resides in [0.0, 1.0], perfectly matching the Sigmoid output activation of the neural network."),
        ("Non-Linear Soft Penalties", "Unlike hard Boolean filtering, a property priced 5% above budget receives a score of ~0.92 instead of being instantly discarded."),
        ("Environment Statistics (500k Rows)", "• Minimum Observed: 0.0721\n• Mean Reward: 0.6873 (± 0.2205)\n• Median Reward: 0.6616\n• Maximum Observed: 1.0000"),
        ("Reward Distribution", "Uniformly populates all quartiles: 140k rows in [0.9-1.0], 195k in [0.5-0.8], 55k in [0.2-0.4], enabling clear contrastive learning.")
    ]
    for h, b in props:
        p_h = tf_f.add_paragraph()
        p_h.text = f"• {h}: "
        p_h.font.name = FONT_BODY
        p_h.font.size = Pt(12)
        p_h.font.bold = True
        p_h.font.color.rgb = C_PRIMARY
        p_h.space_before = Pt(8)

        run = p_h.add_run()
        run.text = b
        run.font.bold = False
        run.font.color.rgb = C_SECONDARY

    # =========================================================================
    # SLIDE 12: RL - Deep Value Network Architecture
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_bg(s12)
    add_header(s12, "Model Architecture", "The PropertyValueNetwork (Deep Q-Predictor)", "PyTorch deep neural network mapping high-dimensional state-action pairs to continuous reward")

    # Layer cards
    layers = [
        ("Input Vector", "497 Dimensions", "14 normalized continuous features + 483 one-hot encoded categorical bins.", C_PRIMARY),
        ("Layer 1 (Dense)", "Linear(497, 256)", "ReLU Activation\nDropout(p=0.10) for regularisation.", C_BLUE),
        ("Layer 2 (Dense)", "Linear(256, 128)", "ReLU Activation\nDropout(p=0.10) for regularisation.", C_BLUE),
        ("Layer 3 (Dense)", "Linear(128, 64)", "ReLU Activation\nFeature compression layer.", C_INDIGO),
        ("Output Layer", "Linear(64, 1) + Sigmoid", "Sigmoid guarantees predicted reward is strictly in [0, 1].", C_TEAL)
    ]

    for i, (l_title, l_dim, l_desc, col) in enumerate(layers):
        x = Inches(0.8 + i * 2.38)
        add_card(s12, x, Inches(1.9), Inches(2.25), Inches(4.8), bg_color=C_CARD_BG)

        bar = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.9), Inches(2.25), Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.color.rgb = col

        tb = s12.shapes.add_textbox(x + Inches(0.15), Inches(2.15), Inches(1.95), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = l_title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.text = l_dim
        p2.font.name = "Consolas"
        p2.font.size = Pt(12)
        p2.font.bold = True
        p2.font.color.rgb = C_PRIMARY
        p2.space_before = Pt(6)

        p3 = tf.add_paragraph()
        p3.text = l_desc
        p3.font.name = FONT_BODY
        p3.font.size = Pt(11)
        p3.font.color.rgb = C_SECONDARY
        p3.space_before = Pt(10)

    # =========================================================================
    # SLIDE 13: RL - Training Pipeline, Splitting & HPC Setup
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    add_bg(s13)
    add_header(s13, "Model Training", "HPC Training Setup & Disjoint User Splitting", "Rigorous isolation of user cohorts to guarantee unbiased evaluation and prevent ID memorization")

    # Left: Disjoint Splits
    add_card(s13, Inches(0.8), Inches(1.9), Inches(5.7), Inches(5.0))
    tb_s = s13.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(5.1), Inches(4.6))
    tf_s = tb_s.text_frame
    tf_s.word_wrap = True

    p = tf_s.paragraphs[0]
    p.text = "Strict User-Level Data Partitioning"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_BLUE_DARK

    split_notes = [
        ("User-Level Partitioning", "Data is partitioned by unique User IDs, not random row permutations. This prevents the model from memorizing individual user profile preferences."),
        ("Training Set (80%)", "8,000 unique users | 400,000 interaction rows"),
        ("Validation Set (10%)", "1,000 unique users | 50,000 interaction rows"),
        ("Test Set (10%)", "1,000 unique users | 50,000 interaction rows"),
        ("Disjointness Audit", "Train ∩ Val = 0 | Train ∩ Test = 0 | Val ∩ Test = 0\nConfirmed 100% disjoint by automated pipeline audit.")
    ]
    for h, b in split_notes:
        p_h = tf_s.add_paragraph()
        p_h.text = f"• {h}: "
        p_h.font.name = FONT_BODY
        p_h.font.size = Pt(12)
        p_h.font.bold = True
        p_h.font.color.rgb = C_PRIMARY
        p_h.space_before = Pt(8)

        run = p_h.add_run()
        run.text = b
        run.font.bold = False
        run.font.color.rgb = C_SECONDARY

    # Right: Hyperparameters & HPC Execution
    add_card(s13, Inches(6.8), Inches(1.9), Inches(5.7), Inches(5.0))
    tb_h = s13.shapes.add_textbox(Inches(7.1), Inches(2.1), Inches(5.1), Inches(4.6))
    tf_h = tb_h.text_frame
    tf_h.word_wrap = True

    p = tf_h.paragraphs[0]
    p.text = "HPC Hardware & Training Hyperparameters"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_TEAL

    hpc_notes = [
        ("Compute Infrastructure", "NVIDIA H100 PCIe MIG (3g.40gb GPU partition)"),
        ("Optimizer", "Adam (Learning Rate = 0.001)"),
        ("Batch Size & Shuffling", "Batch size = 1024 with row index permutation within training set"),
        ("Loss Function", "Mean Squared Error (MSE) between predicted suitability and simulated reward"),
        ("Early Stopping Criterion", "Patience = 5 epochs on validation RMSE; training halted at epoch 25 with best weights restored from epoch 20.")
    ]
    for h, b in hpc_notes:
        p_h = tf_h.add_paragraph()
        p_h.text = f"• {h}: "
        p_h.font.name = FONT_BODY
        p_h.font.size = Pt(12)
        p_h.font.bold = True
        p_h.font.color.rgb = C_PRIMARY
        p_h.space_before = Pt(8)

        run = p_h.add_run()
        run.text = b
        run.font.bold = False
        run.font.color.rgb = C_SECONDARY

    # =========================================================================
    # SLIDE 14: Experimental Results - Training Dynamics & Error Metrics
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    add_bg(s14)
    add_header(s14, "Results & Evaluation", "Model Convergence & Error Metrics", "Empirical validation of reward prediction accuracy across training and held-out test sets")

    # 3 Stat Cards
    metrics_s14 = [
        ("Test MAE", "0.00498", "Average absolute error is less than 0.5% on the [0, 1] reward scale.", C_BLUE),
        ("Test RMSE", "0.00827", "Root Mean Squared Error confirms extreme penalty stability with zero outliers.", C_TEAL),
        ("Test R² Score", "0.9986", "The neural network explains 99.86% of the variance across unseen users.", C_INDIGO)
    ]

    for i, (m_title, m_val, m_desc, col) in enumerate(metrics_s14):
        x = Inches(0.8 + i * 3.95)
        add_card(s14, x, Inches(1.9), Inches(3.8), Inches(2.2), bg_color=C_CARD_BG)

        top_bar = s14.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.9), Inches(3.8), Inches(0.08))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = col
        top_bar.line.color.rgb = col

        tb = s14.shapes.add_textbox(x + Inches(0.2), Inches(2.1), Inches(3.4), Inches(1.9))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = m_title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = C_MUTED

        p2 = tf.add_paragraph()
        p2.text = m_val
        p2.font.name = FONT_HEADING
        p2.font.size = Pt(32)
        p2.font.bold = True
        p2.font.color.rgb = col
        p2.space_before = Pt(2)

        p3 = tf.add_paragraph()
        p3.text = m_desc
        p3.font.name = FONT_BODY
        p3.font.size = Pt(11)
        p3.font.color.rgb = C_SECONDARY
        p3.space_before = Pt(4)

    # Bottom Progression Card
    add_card(s14, Inches(0.8), Inches(4.3), Inches(11.7), Inches(2.6), bg_color=C_CARD_BG)
    tb_b = s14.shapes.add_textbox(Inches(1.1), Inches(4.45), Inches(11.1), Inches(2.3))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True

    p = tf_b.paragraphs[0]
    p.text = "Epoch Progression & Convergence Insights"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    progress_bullets = [
        "Rapid Initial Convergence: Train MSE dropped from 0.00857 (Epoch 1) to 0.00047 (Epoch 5), with Val R² crossing 0.9950 within 5 epochs.",
        "Optimal Checkpoint: Lowest validation error achieved at Epoch 20 (Val MAE: 0.00494, Val RMSE: 0.00844, Val R²: 0.9985).",
        "Early Stopping Triggered: No further validation gains for 5 consecutive epochs (Epochs 21–25), safely terminating without overfitting.",
        "Zero Gradient Explosions: 1024-batch size with Adam stabilized gradient updates across 497 sparse dimensions."
    ]
    for b in progress_bullets:
        p_row = tf_b.add_paragraph()
        p_row.text = f"• {b}"
        p_row.font.name = FONT_BODY
        p_row.font.size = Pt(12)
        p_row.font.color.rgb = C_SECONDARY
        p_row.space_before = Pt(4)

    # =========================================================================
    # SLIDE 15: Experimental Results - Ranking Performance (NDCG@4)
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    add_bg(s15)
    add_header(s15, "RS Evaluation", "Ranking Quality Evaluation: NDCG@4", "Benchmarking top-4 recommendation ordering against mathematical ground truth and baselines")

    # Left: NDCG Metric Comparison
    add_card(s15, Inches(0.8), Inches(1.9), Inches(5.7), Inches(5.0))
    tb_l = s15.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(5.1), Inches(4.6))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "NDCG@4 Evaluation Benchmark"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    p_body = tf_l.add_paragraph()
    p_body.text = "Normalized Discounted Cumulative Gain (NDCG@4) evaluates whether the highest-reward properties appear in the top 4 presentation positions, applying logarithmic position discounting."
    p_body.font.name = FONT_BODY
    p_body.font.size = Pt(12)
    p_body.font.color.rgb = C_SECONDARY
    p_body.space_before = Pt(8)

    p_scores = tf_l.add_paragraph()
    p_scores.text = "PropMatch Model NDCG@4:  0.9994\nRandom Baseline NDCG@4:  0.7080"
    p_scores.font.name = "Consolas"
    p_scores.font.size = Pt(14)
    p_scores.font.bold = True
    p_scores.font.color.rgb = C_TEAL
    p_scores.space_before = Pt(14)

    p_gain = tf_l.add_paragraph()
    p_gain.text = "Relative Improvement: +41.16% over random baseline across 1,000 unseen test users (50 candidates each)."
    p_gain.font.name = FONT_BODY
    p_gain.font.size = Pt(12)
    p_gain.font.bold = True
    p_gain.font.color.rgb = C_PRIMARY
    p_gain.space_before = Pt(8)

    # Right: Case Study / Sample Output
    add_card(s15, Inches(6.8), Inches(1.9), Inches(5.7), Inches(5.0))
    tb_r = s15.shapes.add_textbox(Inches(7.1), Inches(2.1), Inches(5.1), Inches(4.6))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "Sample Test User Recommendations (U000001)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_BLUE_DARK

    p_pref = tf_r.add_paragraph()
    p_pref.text = "Profile: Mira Road | Budget: Rs. 1.5 Cr | 3 BHK | Semi-Furnished"
    p_pref.font.name = FONT_BODY
    p_pref.font.size = Pt(12)
    p_pref.font.bold = True
    p_pref.font.color.rgb = C_PRIMARY
    p_pref.space_before = Pt(6)

    recs = [
        ("#1 Techno Vision Vivanta Marvel", "Rs. 1.38 Cr | 1,210 sq.ft | 4 BHK | Score: 0.9393"),
        ("#2 Aristone Vasudev Paradise", "Rs. 1.46 Cr | 1,400 sq.ft | 3 BHK | Score: 0.9238"),
        ("#3 SK Imperial Garden", "Rs. 1.17 Cr | 1,412 sq.ft | 3 BHK | Score: 0.9236"),
        ("#4 JK IRIS", "Rs. 1.29 Cr | 1,137 sq.ft | 3 BHK | Score: 0.9228")
    ]
    for r_title, r_desc in recs:
        p_t = tf_r.add_paragraph()
        p_t.text = r_title
        p_t.font.name = FONT_BODY
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = C_TEAL
        p_t.space_before = Pt(6)

        p_d = tf_r.add_paragraph()
        p_d.text = r_desc
        p_d.font.name = "Consolas"
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = C_SECONDARY

    # =========================================================================
    # SLIDE 16: System Deployment - FastAPI & React Web App
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    add_bg(s16)
    add_header(s16, "Full-Stack Deployment", "Production Serving Architecture: FastAPI + React", "Operationalizing the trained offline PyTorch model for interactive real-time inference")

    dep_cards = [
        ("Inference Engine (inference.py)", [
            "Loads preprocessor.joblib & best_model.pth into memory once",
            "Validates user inputs with strict type guards",
            "Transforms catalog candidates in 2048-row mini-batches",
            "Applies project-level title deduplication",
            "Execution latency: < 80ms on CPU"
        ], C_PRIMARY),
        ("REST Backend (FastAPI)", [
            "GET /api/health: Validates availability of model weights and catalog",
            "POST /api/recommendations: Accepts JSON payload with 11 user preference keys",
            "CORS middleware configured for secure local and cloud clients",
            "Includes 36 automated unit & integration tests"
        ], C_BLUE),
        ("Client Frontend (React + Vite)", [
            "Modern responsive interface (PropMatch)",
            "Dynamic sliders & dropdowns for budget, area, BHK, locality",
            "Top-4 property cards displaying prices, photos, and match scores",
            "Cold-start handling and human-friendly suitability score notes"
        ], C_TEAL)
    ]

    for i, (title, items, col) in enumerate(dep_cards):
        x = Inches(0.8 + i * 3.95)
        add_card(s16, x, Inches(1.9), Inches(3.8), Inches(4.8), bg_color=C_CARD_BG)

        bar = s16.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.9), Inches(3.8), Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.color.rgb = col

        tb = s16.shapes.add_textbox(x + Inches(0.25), Inches(2.15), Inches(3.3), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEADING
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = col

        for item in items:
            p_i = tf.add_paragraph()
            p_i.text = f"• {item}"
            p_i.font.name = FONT_BODY
            p_i.font.size = Pt(11)
            p_i.font.color.rgb = C_SECONDARY
            p_i.space_before = Pt(8)

    # =========================================================================
    # SLIDE 17: Critical Analysis - Synthetic vs Real-World Bandit Feedback
    # =========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    add_bg(s17)
    add_header(s17, "Critical Discussion", "Synthetic Formula Learning vs Online Bandit Feedback", "Understanding the boundary between simulated reward fitting and real-world human preferences")

    # Left Box: Honest Appraisal of Current Stage
    add_card(s17, Inches(0.8), Inches(1.9), Inches(5.7), Inches(5.0))
    tb_l = s17.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(5.1), Inches(4.6))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "Current Stage: Offline Synthetic Policy"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    curr_points = [
        ("Deterministic Target", "In the simulated environment, reward is an exact algebraic function of 22 features. R² = 0.9986 proves the neural network successfully approximates this complex non-linear mapping."),
        ("No Data Leakage", "All preprocessing and splits are strictly isolated. No test user or reward column ever entered the feature matrices."),
        ("The Generalisation Nuance", "Metrics prove the pipeline functions with mathematical rigor. However, real users may have latent preferences (e.g. natural sunlight, floor preference) that depart from our simulated weights.")
    ]
    for h, b in curr_points:
        p_h = tf_l.add_paragraph()
        p_h.text = f"• {h}: "
        p_h.font.name = FONT_BODY
        p_h.font.size = Pt(12)
        p_h.font.bold = True
        p_h.font.color.rgb = C_BLUE_DARK
        p_h.space_before = Pt(8)

        run = p_h.add_run()
        run.text = b
        run.font.bold = False
        run.font.color.rgb = C_SECONDARY

    # Right Box: Online Fine-Tuning Roadmap
    add_card(s17, Inches(6.8), Inches(1.9), Inches(5.7), Inches(5.0))
    tb_r = s17.shapes.add_textbox(Inches(7.1), Inches(2.1), Inches(5.1), Inches(4.6))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "Next Phase: Online Bandit Fine-Tuning"
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_TEAL

    next_points = [
        ("Click / Selection Bandit Feedback", "Record user actions on the frontend: r = 1.0 for chosen/inquired property, r = 0.0 for shown but unchosen properties."),
        ("Warm-Start Fine-Tuning", "Existing best_model.pth serves as the initialization point. Low learning rate (1e-4) fine-tuning prevents catastrophic forgetting."),
        ("Exploration Strategies", "Implement ε-greedy (ε = 0.10) or Thompson Sampling (noise injection on predicted rewards) to discover unranked listings."),
        ("Batch Experience Replay", "Accumulate 100-session feedback buffers and mix with original training data to maintain catalog coverage.")
    ]
    for h, b in next_points:
        p_h = tf_r.add_paragraph()
        p_h.text = f"• {h}: "
        p_h.font.name = FONT_BODY
        p_h.font.size = Pt(12)
        p_h.font.bold = True
        p_h.font.color.rgb = C_TEAL
        p_h.space_before = Pt(8)

        run = p_h.add_run()
        run.text = b
        run.font.bold = False
        run.font.color.rgb = C_SECONDARY

    # =========================================================================
    # SLIDE 18: Conclusion & Key Takeaways
    # =========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    add_bg(s18, dark=True)

    # Header
    tb_c_hdr = s18.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(0.9))
    tf_ch = tb_c_hdr.text_frame
    p_t = tf_ch.paragraphs[0]
    p_t.text = "CONCLUSION & SUMMARY"
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(12)
    p_t.font.bold = True
    p_t.font.color.rgb = C_BLUE

    p_m = tf_ch.add_paragraph()
    p_m.text = "Key Project Achievements & Deliverables"
    p_m.font.name = FONT_HEADING
    p_m.font.size = Pt(28)
    p_m.font.bold = True
    p_m.font.color.rgb = C_WHITE
    p_m.space_before = Pt(4)

    # 4 Summary Cards
    cards_c = [
        ("Unified RS + RL Architecture", "Successfully solved the real estate search problem by combining candidate generation with a deep Contextual Bandit value network.", RGBColor(30, 41, 59)),
        ("High-Precision Reward Learning", "Achieved Test R² = 0.9986, Test RMSE = 0.0083, and NDCG@4 = 0.9994 (+41% over baseline) across 1,000 unseen test users.", RGBColor(30, 41, 59)),
        ("Catalog Diversity & Deduplication", "Eliminated project title replication in top-k rankings, ensuring diverse, relevant property presentation.", RGBColor(30, 41, 59)),
        ("Production-Ready Full Stack", "Integrated FastAPI backend with sub-80ms inference and a responsive React UI ready for online user feedback collection.", RGBColor(30, 41, 59))
    ]

    for i, (title, desc, bg) in enumerate(cards_c):
        x = Inches(0.8 + (i % 2) * 5.95)
        y = Inches(1.8 + (i // 2) * 2.3)
        add_card(s18, x, y, Inches(5.75), Inches(2.05), bg_color=bg, border_color=RGBColor(51, 65, 85))

        # Accent dot/bar
        bar = s18.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Inches(0.08), Inches(2.05))
        bar.fill.solid()
        bar.fill.fore_color.rgb = C_BLUE
        bar.line.color.rgb = C_BLUE

        tb = s18.shapes.add_textbox(x + Inches(0.3), y + Inches(0.2), Inches(5.2), Inches(1.65))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(16)
        p1.font.bold = True
        p1.font.color.rgb = C_WHITE

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(12)
        p2.font.color.rgb = RGBColor(203, 213, 225)
        p2.space_before = Pt(8)

    # Save presentation
    prs.save(OUTPUT_FILE)
    print(f"Presentation saved successfully to: {OUTPUT_FILE.resolve()}")

if __name__ == "__main__":
    create_deck()

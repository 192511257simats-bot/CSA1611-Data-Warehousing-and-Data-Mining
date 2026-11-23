from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os
NAVY=RGBColor(0x1f,0x4e,0x79)
D=Document()
sec=D.sections[0]; sec.page_width=Cm(21); sec.page_height=Cm(29.7)
for a in ("left_margin","right_margin"): setattr(sec,a,Cm(2))
sec.top_margin=Cm(2); sec.bottom_margin=Cm(2)
st=D.styles["Normal"]; st.font.name="Calibri"; st.font.size=Pt(11); st.element.rPr.rFonts.set(qn("w:eastAsia"),"Calibri")
st.paragraph_format.space_after=Pt(5)
for n,sz in (("Heading 1",17),("Heading 2",13.5),("Heading 3",11.5)):
    h=D.styles[n]; h.font.name="Calibri"; h.font.size=Pt(sz); h.font.bold=True; h.font.color.rgb=NAVY
    h.element.rPr.rFonts.set(qn("w:eastAsia"),"Calibri"); h.paragraph_format.space_before=Pt(12); h.paragraph_format.space_after=Pt(5); h.paragraph_format.keep_with_next=True
def shade(cell,color):
    tcPr=cell._tc.get_or_add_tcPr(); s=OxmlElement("w:shd"); s.set(qn("w:val"),"clear"); s.set(qn("w:color"),"auto"); s.set(qn("w:fill"),color); tcPr.append(s)
def P(text="",bold=False,italic=False,size=None,align=None,color=None,style=None,after=None):
    p=D.add_paragraph(style=style); 
    if text: add_runs(p,text,bold,italic,size,color)
    if align=="c": p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    if after is not None: p.paragraph_format.space_after=Pt(after)
    return p
def add_runs(p,text,bold=False,italic=False,size=None,color=None):
    parts=text.split("**")
    for i,t in enumerate(parts):
        if not t: continue
        r=p.add_run(t); r.bold=bold or (i%2==1); r.italic=italic
        if size: r.font.size=Pt(size)
        if color: r.font.color.rgb=color
def B(text,level=0):
    p=D.add_paragraph(style="List Bullet"); add_runs(p,text); p.paragraph_format.space_after=Pt(2)
    if level: p.paragraph_format.left_indent=Cm(1.2)
    return p
def H(t,l=1): return D.add_heading(t,l)
def T(rows,widths=None,header=True,size=9.5,hdrcolor="1F4E79",first_bold=False,align_center_cols=()):
    t=D.add_table(rows=len(rows),cols=len(rows[0])); t.style="Table Grid"; t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for i,row in enumerate(rows):
        for j,val in enumerate(row):
            c=t.cell(i,j); c.text=""; p=c.paragraphs[0]; p.paragraph_format.space_after=Pt(1)
            lines=str(val).split("\n")
            for k,ln in enumerate(lines):
                if k: p=c.add_paragraph(); p.paragraph_format.space_after=Pt(1)
                add_runs(p,ln,bold=(header and i==0) or (first_bold and j==0),size=size,color=RGBColor(255,255,255) if (header and i==0) else None)
                if j in align_center_cols or (header and i==0): p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            if header and i==0: shade(c,hdrcolor)
    if widths:
        t.autofit=False
        for j,w in enumerate(widths): t.columns[j].width=Cm(w)
        for row in t.rows:
            for j,w in enumerate(widths): row.cells[j].width=Cm(w)
    if header:
        trPr=t.rows[0]._tr.get_or_add_trPr(); e=OxmlElement("w:tblHeader"); e.set(qn("w:val"),"true"); trPr.append(e)
    D.add_paragraph().paragraph_format.space_after=Pt(2)
    return t
FIG=[0]; TAB=[0]
def cap(kind,text):
    if kind=="Figure": FIG[0]+=1; n=FIG[0]
    else: TAB[0]+=1; n=TAB[0]
    p=P(f"{kind} {n}: {text}",italic=True,size=9.5,align="c",color=RGBColor(0x44,0x44,0x44)); return n
def IMG(path,w=16,caption=None):
    p=D.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next=True
    p.add_run().add_picture(path,width=Cm(w))
    if caption: return cap("Figure",caption)
def CODE(text,size=7.5):
    t=D.add_table(rows=1,cols=1); t.style="Table Grid"; c=t.cell(0,0); shade(c,"F3F3F3"); c.text=""
    lines=text.rstrip("\n").split("\n"); p=c.paragraphs[0]
    for i,l in enumerate(lines):
        if i: p=c.add_paragraph()
        p.paragraph_format.space_after=Pt(0); p.paragraph_format.line_spacing=1.0
        r=p.add_run(l if l else " "); r.font.name="Consolas"; r.font.size=Pt(size); r._element.rPr.rFonts.set(qn("w:eastAsia"),"Consolas")
    D.add_paragraph().paragraph_format.space_after=Pt(2)
def PB(): D.add_page_break()
def MATH(lines):
    for l in lines:
        p=D.add_paragraph(); p.paragraph_format.left_indent=Cm(1); p.paragraph_format.space_after=Pt(1)
        r=p.add_run(l); r.font.name="Cambria"; r.font.size=Pt(10.5)
# footer page number
f=sec.footer.paragraphs[0]; f.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=f.add_run("CSA16 Data Warehousing and Data Mining | Assignment 5 (CO5) | Page "); r.font.size=Pt(9)
r2=f.add_run(); r2.font.size=Pt(9)
for t_,txt in (("begin",None),(None,"PAGE"),("end",None)):
    if t_: e=OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"),t_); r2._r.append(e)
    else: e=OxmlElement("w:instrText"); e.set(qn("xml:space"),"preserve"); e.text=txt; r2._r.append(e)

# ================= EVALUATION KEY PAGES =================
P("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING",bold=True,size=13,align="c",color=NAVY,after=0)
P("CSA16 Data Warehousing and Data Mining",bold=True,size=13,align="c",after=0)
P("Assignment 5 – CO5 | Total Marks: 50 | Individual work",size=11,align="c",after=2)
P("Design and Evaluate an Integrated Data Warehousing and Mining System for a Smart-City Citizen Services Platform",bold=True,size=12,align="c",after=8)
T([["Student Name",""],["Register / Roll No.",""],["Section / Batch",""],["GitHub repository (source code + output screenshots)","https://github.com/<your-username>/dwdm-assignment5   ← paste your repository link here after uploading the folder"]],widths=[6,11],header=False,first_bold=True,size=10)
H("MARK SHEET (Rubric-based Evaluation)",1)
rows=[["Task","Task Title","Max Marks","Marks Awarded","Remarks"],
["1","Text Data Analysis and Information Retrieval","5","",""],
["2","Text Mining Implementation (Code)","6","",""],
["3","Web Mining: Structure, Usage and Page Importance","5","",""],
["4","Automatic Classification of Web Documents","5","",""],
["5","Spatial Data and Spatial Association Patterns","6","",""],
["6","Spatial Clustering of Incident Locations (Code)","5","",""],
["7","Social Impacts and Privacy","4","",""],
["8","Design the Integrated System","6","",""],
["9","Day-4 Design Challenge (A, B, C, D)","8","",""],
["","TOTAL","50","",""]]
T(rows,widths=[1.3,8,2,2.5,3.2],size=10,align_center_cols=(0,2))
T([["OVERALL REMARKS",""],["Student Signature",""],["Faculty Signature",""],["Program Director",""]],widths=[5,12],header=False,first_bold=True,size=10)
PB()
H("MANDATORY SUBMISSION EVIDENCE CHECK",1)
ev=[["Task","Evidence expected","Status","Note (where in this document)"],
["1","Term matrix, IDF/TF–IDF table, cosine-similarity ranking, precision/recall at rank 2, short discussion of limitations of keyword retrieval","☒ Provided","Section 1; Tables 1–4"],
["2","Experimental tables (3+ feature settings, 2 classifiers), confusion matrix, per-class P/R, k-means vs categories, misclassified-document analysis","☒ Provided","Section 2; Tables 5–9; Figures 1–2 (screenshots); code in Appendix A"],
["3","Web-mining categories with examples, PageRank iterations (hand), hub/authority explanation, layout-structure discussion","☒ Provided","Section 3; Tables 10–11; Figure 3"],
["4","Labelled pipeline diagram, web-specific feature table with justification, challenges/remedies, evaluation and retraining plan","☒ Provided","Section 4; Figure 4; Tables 12–13"],
["5","Spatial data types/relationships with city examples, spatial autocorrelation, participation ratio/index for each pair, prevalent co-locations, triple {A,B,C}, co-location vs association rule","☒ Provided","Section 5; Tables 14–16"],
["6","Plots, k-distance parameter selection, effect of ε, noise points, interpreted k-means vs DBSCAN comparison, CLARANS discussion","☒ Provided","Section 6; Figures 5–8; Tables 17–18; code in Appendix B"],
["7","k-anonymity analysis, anonymised table, information lost, risk–safeguard table","☒ Provided","Section 7; Tables 19–21"],
["8","Architecture diagram, dimensional design, requirement-to-technique mapping, privacy controls, evaluation plan","☒ Provided","Section 8; Figure 9; Tables 22–24"],
["9","A. Impact analysis; B. Evaluation of original design; C. Revised design (changes shown); D. Evidence-based defence with trade-off","☒ Provided","Section 9; Figures 10–12; Tables 25–28; code in Appendix C"]]
T(ev,widths=[1.2,8.3,2.2,5.3],size=9,align_center_cols=(0,))
H("IMPLEMENTATION AND EXPERIMENT EVIDENCE CHAIN (Tasks 2 and 6, supporting Task 9)",2)
ch=[["Evidence item","Status","Observation"],
["Source code (Tasks 2 & 6)","☒ Provided","Appendix A (task2_text_mining.py + corpus.py), Appendix B (task6_spatial_clustering.py), Appendix C (Task 9 experiments); also in the GitHub folder"],
["Test inputs / datasets","☒ Provided","Task 2: 600 documented synthetic complaints (5 classes, seed 42). Task 6: 1,400 synthetic GPS incidents near Chennai (numpy seed 7), saved as incidents.csv"],
["Expected behaviour","☒ Provided","Task 2: >95 % accuracy on clear complaints, errors only on mixed-topic ones. Task 6: DBSCAN finds 3 arbitrary-shape hot-spots + noise; k-means cannot"],
["Actual output / screen results","☒ Provided","Figures 1–2 (Task 2 terminal), Figure 5 (Task 6 terminal), Figure 10 (Task 9 terminal) – real program output"],
["Intermediate algorithmic / measurement evidence","☒ Provided","Feature-setting table, 5-fold CV scores, k-distance graph, ε sweep table, grid-size sweep table"],
["Boundary / failure tests","☒ Provided","Vocabulary cut to 40 words (accuracy drops to 0.75–0.80); ε too small (22 clusters) / too large (1 cluster); 500 m–2 km grids; English-only model on Hindi/Tamil (chance level)"],
["Interpretation linked to theory","☒ Provided","Density-reachability vs centroid partitioning; TF-IDF/feature selection; k-anonymity/generalisation trade-off"],
["Code, data and report consistent","☒ Provided","All numbers in the report are copied from the program outputs shown in the screenshots"]]
T(ch,widths=[4.6,2.4,10],size=9)
H("SUBMISSION CHECKLIST (not separately marked)",2)
cl=[["Requirement","Status"],
["All tasks (1–9) answered","☒ Yes   ☐ Partly   ☐ No"],
["Hand calculations shown for TF–IDF, PageRank, participation index, k-anonymity","☒ Yes   ☐ Partly   ☐ No"],
["Text-mining implementation with feature settings, 2 classifiers, k-means and error analysis (Task 2)","☒ Yes   ☐ Partly   ☐ No"],
["Web mining / web-document classification pipeline (Tasks 3–4)","☒ Yes   ☐ Partly   ☐ No"],
["Spatial co-location and spatial clustering with plots (Tasks 5–6)","☒ Yes   ☐ Partly   ☐ No"],
["k-anonymity table and risk–safeguard table (Task 7)","☒ Yes   ☐ Partly   ☐ No"],
["Source code for every program that produced reported data (Tasks 2, 6, 9)","☒ Yes   ☐ Partly   ☐ No"],
["Tables, graphs and diagrams for experimental results","☒ Yes   ☐ Partly   ☐ No"],
["Figures / screen outputs included in the document (not only referenced)","☒ Yes   ☐ Partly   ☐ No"],
["Cross-references and table / figure numbering correct","☒ Yes   ☐ Partly   ☐ No"],
["Work consistent throughout","☒ Yes   ☐ Partly   ☐ No"],
["No unfilled template placeholders (apart from name, roll number and GitHub link above)","☐ Yes   ☒ Partly   ☐ No"],
["Design Challenge (impact / evaluation / adaptation / defence) complete","☒ Yes   ☐ Partly   ☐ No"],
["Viva readiness (able to run the programs and explain results)","☐ Yes   ☐ No   (student to tick)"]]
T(cl,widths=[11.5,5.5],size=9.5)
PB()

# ================= SOLUTION =================
H("SOLUTION DOCUMENT",1)
P("Scenario: Metro City Corporation (4 million residents, about 5,000 complaints/day). This report designs and evaluates an integrated warehouse + mining platform. Hand calculations are the primary evidence for Tasks 1, 3, 5 and 7; the Python program hand_calc_verification.py was run only to cross-check them (Figures 13–14 in Appendix D). Source code, data and screenshots are in the GitHub repository named on the first page. Random seeds: 42 (Task 2 and 9), 7 (Task 6 data and k-means).",size=10.5)

# ---- TASK 1
H("TASK 1 – Text Data Analysis and Information Retrieval (5 marks)",1)
H("1.1 Pre-processing",2)
B("**Tokenisation** – split each text into lower-case words at spaces/punctuation.")
B("**Stop-word removal** – delete function words that carry no topic: here on, not, near (a locative preposition). Note: removing “not” loses negation (“light not working”), which is acceptable for topic retrieval but would hurt sentiment analysis.")
B("**Stemming** (Porter-style suffix stripping) – reduce words to a common stem so that variants match: pothole→pothol, garbage→garbag, collected→collect, working→work, leakage→leakag.")
cap("Table","Result of pre-processing (the terms used below)")
T([["Doc","Original text","After tokenisation + stop-word removal","After stemming (final terms)"],
["D1","pothole on main road near school","pothole main road school","pothol main road school"],
["D2","garbage not collected near school road","garbage collected school road","garbag collect school road"],
["D3","street light not working on main road","street light working main road","street light work main road"],
["D4","water leakage near school gate","water leakage school gate","water leakag school gate"],
["Query","school road garbage","school road garbage","school road garbag"]],widths=[1.5,5,5.5,5],size=9)
H("1.2 Term-frequency matrix, IDF and TF–IDF",2)
P("N = 4 documents. Raw term frequency (count in the document); every term occurs once in every document that contains it. IDF = log10(N/df).")
cap("Table","Term-frequency matrix, document frequency and IDF")
tf=[["Term","D1","D2","D3","D4","df","IDF = log10(4/df)"]]
data=[("pothol",1,0,0,0,1,"0.6021"),("main",1,0,1,0,2,"0.3010"),("road",1,1,1,0,3,"0.1249"),("school",1,1,0,1,3,"0.1249"),("garbag",0,1,0,0,1,"0.6021"),("collect",0,1,0,0,1,"0.6021"),("street",0,0,1,0,1,"0.6021"),("light",0,0,1,0,1,"0.6021"),("work",0,0,1,0,1,"0.6021"),("water",0,0,0,1,1,"0.6021"),("leakag",0,0,0,1,1,"0.6021"),("gate",0,0,0,1,1,"0.6021")]
for d in data: tf.append([d[0]]+[str(x) for x in d[1:5]]+[str(d[5]),d[6]])
T(tf,widths=[2.6,1.6,1.6,1.6,1.6,1.6,4.4],size=9.5,align_center_cols=(1,2,3,4,5,6))
P("Working: df(road)=3 → log10(4/3)=0.1249; df(main)=2 → log10(2)=0.3010; df=1 → log10(4)=0.6021. TF–IDF weight = tf × IDF (tf = 1 here), so the weights equal the IDF of each term present.",size=10.5)
cap("Table","TF–IDF weights (non-zero entries only)")
T([["Term","D1","D2","D3","D4","Query"],["pothol","0.6021","–","–","–","–"],["main","0.3010","–","0.3010","–","–"],["road","0.1249","0.1249","0.1249","–","0.1249"],["school","0.1249","0.1249","–","0.1249","0.1249"],["garbag","–","0.6021","–","–","0.6021"],["collect","–","0.6021","–","–","–"],["street, light, work","–","–","0.6021 each","–","–"],["water, leakag, gate","–","–","–","0.6021 each","–"]],widths=[4,2.4,2.4,2.8,2.8,2.4],size=9.5,align_center_cols=(1,2,3,4,5))
H("1.3 Ranking by cosine similarity",2)
P("cos(q,d) = (q·d) / (|q|·|d|). Vector lengths (square root of the sum of squared weights):")
MATH(["|D1| = √(0.6021² + 0.3010² + 0.1249² + 0.1249²) = √(0.3625+0.0906+0.0156+0.0156) = √0.4843 = 0.6959",
"|D2| = √(0.6021² + 0.6021² + 0.1249² + 0.1249²) = √0.7562 = 0.8696",
"|D3| = √(3×0.3625 + 0.0906 + 0.0156) = √1.1937 = 1.0925",
"|D4| = √(3×0.3625 + 0.0156) = √1.1031 = 1.0503",
"|q|  = √(0.1249² + 0.1249² + 0.6021²) = √(0.0156+0.0156+0.3625) = √0.3937 = 0.6275"])
P("Dot products (only terms shared with the query count) and cosine values:")
cap("Table","Cosine-similarity calculation and ranking")
T([["Doc","q · d (shared terms)","Calculation","cos(q,d)","Rank"],
["D2","garbag + school + road = 0.3625+0.0156+0.0156 = 0.3937","0.3937 / (0.8696 × 0.6275 = 0.5457)","0.7216","1"],
["D1","school + road = 0.0156+0.0156 = 0.0312","0.0312 / (0.6959 × 0.6275 = 0.4367)","0.0715","2"],
["D4","school = 0.0156","0.0156 / (1.0503 × 0.6275 = 0.6591)","0.0237","3"],
["D3","road = 0.0156","0.0156 / (1.0925 × 0.6275 = 0.6856)","0.0228","4"]],widths=[1.2,6,5.5,2,1.3],size=9,align_center_cols=(0,3,4))
H("1.4 Precision and recall at rank 2",2)
P("Relevant set = {D1, D2}. Top-2 retrieved = {D2, D1}, both relevant.")
MATH(["Precision@2 = relevant retrieved / retrieved = 2/2 = 1.00","Recall@2 = relevant retrieved / total relevant = 2/2 = 1.00"])
P("**What it reveals:** the ranking is perfect at rank 2 – no irrelevant document is above a relevant one. But the scores show how fragile this is: D2 scores 0.72 because it contains the rare, high-IDF word “garbage”, while D1 scores only 0.07 – barely above D4 (0.024), which is irrelevant. D1 is only second because it shares the two low-weight common words (school, road). Precision/recall at one cut-off ignores the score margin and the tiny collection (4 documents), so the result should not be generalised.")
H("1.5 Weakness of keyword matching and a remedy",2)
B("**Weakness – synonyms and polysemy:** a complaint saying “rubbish/trash not picked up near school” never matches the query “garbage” (synonymy → low recall); “light” in “light traffic” and “street light” are the same string with different meanings (polysemy → low precision).")
B("**Remedy:** query expansion with a thesaurus/WordNet (garbage ≈ rubbish ≈ waste ≈ trash) or semantic indexing (Latent Semantic Analysis / word embeddings), which map related words to nearby vectors.")

# ---- TASK 2
PB()
H("TASK 2 – Text Mining Implementation (6 marks)",1)
H("2.1 Data set and set-up",2)
P("**Corpus (documented):** the standard 20 Newsgroups download was not reachable from the offline work-space, so, as the task permits, a **synthetic complaint corpus** was generated (corpus.py, seed 42): 600 complaints, 5 categories × 120 – Roads, Water, Sanitation, Electricity, Health. Each complaint has 2–3 category words, a generic phrase (e.g. “near school”, “main road area”), and filler words. About 12 % contain one distractor word from another category and 6 % are genuinely mixed-topic, to imitate real ambiguity. Stratified 70/30 train/test split (420/180), random_state = 42. Vectorisation: scikit-learn CountVectorizer / TfidfVectorizer with a custom analyzer for stop-word removal and suffix stemming. Classifiers: Multinomial Naïve Bayes and Linear SVM. Code: Appendix A. Real terminal output: Figures 1–2.")
IMG("../shots/task2_1.png",16.5,"Task 2 program output – feature-setting comparison, confusion matrices, per-class precision/recall (screenshot, part 1)")
IMG("../shots/task2_2.png",16.5,"Task 2 program output – misclassified documents and k-means vs categories (screenshot, part 2)")
H("2.2 Comparison of feature settings (accuracy on the 180 test documents; 5-fold CV on training data in brackets)",2)
cap("Table","Feature settings × classifiers")
T([["Setting","|V|","Naïve Bayes","Linear SVM"],
["F1 binary weights, no stop-word removal, no stemming","93","0.983 (0.986)","0.989 (0.979)"],
["F2 TF–IDF, stop-words removed, no stemming","77","0.983 (0.986)","0.983 (0.983)"],
["F3 TF–IDF, stop-words removed + stemming","70","0.983 (0.986)","0.983 (0.986)"],
["F4 as F3 but vocabulary limited to 40 terms","40","0.750 (0.786)","0.800 (0.790)"]],widths=[9,1.5,3.2,3.2],size=9.5,align_center_cols=(1,2,3))
P("**Interpretation.** (i) Binary vs TF–IDF and stop-word removal/stemming make almost no difference here (≤ 0.6 points) because the synthetic complaints are short and contain few filler words; in real, longer text these steps matter more, and stemming reduced |V| from 77 to 70 by merging leak/leaks/leaking. (ii) Vocabulary size matters greatly: cutting |V| to 40 discards discriminative words and accuracy falls by 18–23 points – feature selection must keep category words. (iii) Naïve Bayes and the linear SVM perform equally well on this easy, nearly separable data.")
H("2.3 Best setting (F3): confusion matrix and per-class precision/recall – both classifiers gave identical results",2)
cap("Table","Confusion matrix, rows = true class, columns = predicted (test set, n = 180)")
T([["True \\ Pred","Roads","Water","Sanit.","Electr.","Health"],["Roads","35","0","1","0","0"],["Water","0","35","0","0","1"],["Sanitation","0","0","35","0","1"],["Electricity","0","0","0","36","0"],["Health","0","0","0","0","36"]],widths=[3,2,2,2,2,2],size=9.5,align_center_cols=(1,2,3,4,5))
cap("Table","Per-class precision / recall / F1 (accuracy = 0.983)")
T([["Class","Precision","Recall","F1"],["Roads","1.000","0.972","0.986"],["Water","1.000","0.972","0.986"],["Sanitation","0.972","0.972","0.972"],["Electricity","1.000","1.000","1.000"],["Health","0.947","1.000","0.973"],["Macro average","0.984","0.983","0.983"]],widths=[4,3,3,3],size=9.5,align_center_cols=(1,2,3))
H("2.4 k-means clustering of the unlabelled documents (k = 5, TF–IDF F3, n_init = 10, seed 42)",2)
cap("Table","Cluster vs true category counts")
T([["Cluster","Electricity","Health","Roads","Sanitation","Water","Top terms"],
["0","106","1","104","0","0","meter, road, pole, outage, footpath"],
["1","12","8","15","5","12","please, urgently, act, hospital, footpath"],
["2","1","0","1","114","0","toilet, sewage, dump, dustbin, stench"],
["3","0","111","0","1","1","doctor, mosquito, clinic, dengue, medicine"],
["4","1","0","0","0","107","tap, drink, pipeline, pressure, leak"]],widths=[1.6,2.2,1.8,1.8,2.2,1.8,5.6],size=9,align_center_cols=(0,1,2,3,4,5))
P("**Agreement:** purity = 0.755, adjusted Rand index = 0.687, NMI = 0.750. Sanitation, Health and Water form clean, pure clusters (about 95 % of each). Roads and Electricity are **merged** in cluster 0, and cluster 1 is a small “generic/urgent-words” cluster (52 documents spread over all classes). Reason: k-means groups by the words that dominate the vectors; both Roads and Electricity complaints mention roads/streets and location phrases (“main road area”, “streetlight”), and complaints with weak category words are pulled together by generic words such as “please urgently act”. So clusters agree with categories where the vocabulary is distinct, and disagree where vocabularies overlap.")
H("2.5 Analysis of misclassified documents",2)
cap("Table","The 3 misclassified test complaints (both classifiers)")
T([["True → Predicted","Complaint text","Why it was misclassified"],
["Roads → Sanitation","stop diversion are traffic the toilet near a sewage bus","Two Roads words (diversion, traffic) vs two Sanitation words (sewage, toilet): a mixed-topic complaint with a tie in evidence; the Sanitation words have higher weights"],
["Water → Health","leak mosquito since a last tank are hospital the week","Two Water words (leak, tank) vs two Health words (mosquito, hospital) – equal evidence; Health words are rarer so TF–IDF weights them more"],
["Sanitation → Health","ambulance since has clinic week drain a last waste for","Two Health words (ambulance, clinic) vs two Sanitation words (drain, waste) – equal counts"]],widths=[3.2,6,7.8],size=9)
P("All errors are complaints that genuinely contain two topics with equal evidence (my 6 % mixed-topic complaints); a bag-of-words model has no information on which topic is the primary one. Remedies: multi-label classification, use of word position/the first noun phrase, or routing low-margin documents to a human. **Limitation:** accuracy near 98 % is a property of this clean synthetic corpus; real complaints would score lower.")

# ---- TASK 3
PB()
H("TASK 3 – Web Mining: Structure, Usage and Page Importance (5 marks)",1)
H("3.1 Three kinds of web mining",2)
cap("Table","Web content, structure and usage mining")
T([["Type","What it mines","Use in Metro City"],
["Web content mining","The text/images/multimedia inside pages","Classify service-information and news pages into Roads/Water/… and extract the service text"],
["Web structure mining","The hyperlink graph between pages (PageRank, HITS)","Find which portal pages are most important/authoritative (e.g. Complaints page) and decide what to show on the home page"],
["Web usage mining","Server logs / click-streams of visitors","Find that many users go Home → Services → Complaints and abandon, then redesign the navigation or add a shortcut"]],widths=[3.4,5.6,8],size=9.5)
H("3.2 PageRank (d = 0.85, N = 5, initial rank 0.2 for every page)",2)
IMG("../figs/fig_linkgraph.png",7,"Link graph of the portal (H→S,C; S→C; C→H; N→H,C,A; A→N)")
P("Formula: PR(p) = (1 − d)/N + d × Σ PR(q)/L(q) over pages q that link to p, where L(q) is the number of out-links of q. (1 − d)/N = 0.15/5 = 0.03. Out-links: L(H)=2, L(S)=1, L(C)=1, L(N)=3, L(A)=1. In-links: H ← C, N; S ← H; C ← H, S, N; N ← A; A ← N. Both iterations use the ranks of the previous iteration.")
H("Iteration 1 (all PR = 0.2)",3)
MATH(["PR(H) = 0.03 + 0.85 × (PR(C)/1 + PR(N)/3) = 0.03 + 0.85 × (0.2 + 0.0667) = 0.03 + 0.2267 = 0.2567",
"PR(S) = 0.03 + 0.85 × (PR(H)/2) = 0.03 + 0.85 × 0.1 = 0.1150",
"PR(C) = 0.03 + 0.85 × (PR(H)/2 + PR(S)/1 + PR(N)/3) = 0.03 + 0.85 × (0.1 + 0.2 + 0.0667) = 0.03 + 0.3117 = 0.3417",
"PR(N) = 0.03 + 0.85 × PR(A)/1 = 0.03 + 0.17 = 0.2000",
"PR(A) = 0.03 + 0.85 × PR(N)/3 = 0.03 + 0.0567 = 0.0867        (sum = 1.0001 ✓)"])
H("Iteration 2 (using iteration-1 values)",3)
MATH(["PR(H) = 0.03 + 0.85 × (0.3417 + 0.2000/3) = 0.03 + 0.85 × 0.4083 = 0.03 + 0.3471 = 0.3771",
"PR(S) = 0.03 + 0.85 × (0.2567/2) = 0.03 + 0.1091 = 0.1391",
"PR(C) = 0.03 + 0.85 × (0.2567/2 + 0.1150 + 0.2000/3) = 0.03 + 0.85 × 0.3100 = 0.03 + 0.2635 = 0.2935",
"PR(N) = 0.03 + 0.85 × 0.0867 = 0.1037",
"PR(A) = 0.03 + 0.85 × (0.2000/3) = 0.0867        (sum = 1.0001 ✓)"])
cap("Table","PageRank values")
T([["Page","Start","After iteration 1","After iteration 2","Converged (100 iterations)"],["H (Home)","0.2000","0.2567","0.3771","0.348"],["S (Services)","0.2000","0.1150","0.1391","0.178"],["C (Complaints)","0.2000","0.3417","0.2935","0.350"],["N (News)","0.2000","0.2000","0.1037","0.073"],["A (Archive)","0.2000","0.0867","0.0867","0.051"]],widths=[3.5,2.4,3.4,3.4,4.3],size=9.5,align_center_cols=(1,2,3,4))
P("**Most important page:** after the two required iterations **Home (H)** has the highest rank (0.377). The reason is that H receives the entire rank of C (C has a single out-link, to H) and a third of N’s rank, while C itself is fed by three pages (H, S, N). C and H are therefore tied at the top: running the iteration to convergence gives C = 0.350 and H = 0.348, i.e. Complaints and Home form a strongly connected core that circulates rank, whereas Archive and News (only linked from each other) are least important. The ranking at iteration 2 is not final; the converged result is in the last column.")
H("3.3 Hubs and authorities (HITS)",2)
P("An **authority** is a page with good content, pointed to by many good hubs; a **hub** is a page that points to many good authorities. A page’s authority score is the sum of the hub scores of the pages linking to it, and its hub score is the sum of the authority scores of the pages it links to, iterated. Here **Complaints (C)** has three in-links (H, S, N) so it is the main authority, and Home (H) is the second authority (linked from C, N). **News (N)** (links to H, C, A) and **Home (H)** (links to S, C) are the best hubs; Archive (one out-link) and Complaints (one out-link) are weak hubs.")
H("3.4 Web page layout structure",2)
P("A web page is a **DOM tree** of nested HTML elements (html → body → div/table → p, a, img). **Block segmentation** (e.g. VIPS) partitions the rendered page into visual blocks – header, navigation menu, main article, side panel, advertisement, footer – using tags, visual separators and layout positions. Menus and ads must be separated from the main content before mining because they are repeated on every page: they inflate term frequencies for words like “home, login, offers”, make unrelated pages look similar (hurting clustering and classification), create false links that distort PageRank (every page links to the menu), and distort usage statistics. Mining only the main content block gives cleaner features and more accurate topics.")

# ---- TASK 4
H("TASK 4 – Automatic Classification of Web Documents (5 marks)",1)
H("4.1 Pipeline (Roads, Water, Sanitation, Electricity, Health, Other)",2)
IMG("../figs/fig_web_pipeline.png",16.5,"Labelled pipeline for classifying portal and news pages")
B("**Collection:** crawl portal pages and news URLs (respect robots.txt), store raw HTML + URL + in-links; label a sample (about 300 pages/class) with the department staff.")
B("**Cleaning:** parse the DOM, drop script/style/tags, remove navigation/ads/footers using block segmentation, normalise text, detect language.")
B("**Feature extraction:** TF–IDF of body text plus the web-specific features of Table 12.")
B("**Training:** Naïve Bayes or linear SVM (both fast and strong on sparse text), class weights for rare classes.")
B("**Evaluation:** stratified hold-out + k-fold cross-validation (see 4.4).   **Deployment:** batch classification of new pages, low-confidence pages sent to a human reviewer, results stored in the warehouse.")
H("4.2 Web-page-specific features",2)
cap("Table","Features specific to web pages")
T([["Feature","How it helps"],
["Title","Short and highly topical (“Water supply interruption notice”); give it a higher weight than body words"],
["Headings (h1–h3)","Summarise sections; strong topic signal and help with multi-topic pages"],
["URL tokens","/roads/pothole-repair already reveals the class even when the body is short or dynamic"],
["Anchor text of in-links","Other pages describe the target in a few words (“report a leak”) – a human-written label"],
["Hyperlinks from / to neighbouring pages","Linked pages usually share a topic; add the neighbours’ predicted labels as features (relational classification)"],
["Meta keywords / description, image alt text","Extra concise text when the body is image-heavy"],
["HTML structure (tables, forms, list density)","Distinguishes service-request forms and notices from news articles"]],widths=[5,12],size=9.5)
H("4.3 Challenges and remedies",2)
cap("Table","Challenges of web data")
T([["Challenge","Remedy"],
["Noise (menus, ads, comments, scripts)","Boilerplate removal / block segmentation; use only the main-content block"],
["Multi-topic pages","Classify per block or paragraph, or allow multi-label output with probability thresholds"],
["Dynamic content (JavaScript-rendered, changing pages)","Use a headless-browser crawler or the site’s API; store dated snapshots"],
["Class imbalance (few Electricity/Health pages, many Other)","Class weights, oversampling the rare classes (SMOTE) and judging by per-class F1, not overall accuracy"]],widths=[6,11],size=9.5)
H("4.4 Evaluation and retraining plan",2)
B("Hold out 30 % stratified + 5-fold cross-validation; report accuracy, per-class precision, recall, F1 and the confusion matrix; macro-F1 as the headline number because of imbalance.")
B("After deployment, audit a random weekly sample of 100 predicted pages by staff, and track the share of low-confidence predictions.")
B("**Retrain when** weekly sampled accuracy or macro-F1 drops more than 5 points below the validation value, when the share of “Other”/low-confidence pages rises sharply, or when out-of-vocabulary terms exceed a threshold (concept drift, e.g. a new scheme name or language); also retrain on a regular quarterly schedule.")

# ---- TASK 5
PB()
H("TASK 5 – Spatial Data and Spatial Association Patterns (6 marks)",1)
H("5.1 Spatial data types and relationships",2)
cap("Table","Spatial data types with city examples")
T([["Type","Meaning","Example from Metro City data"],["Point","A single coordinate","Location of one accident or one complaint (lat, lon)"],["Line","Ordered sequence of points","A road, water pipeline or power cable"],["Polygon","Closed region","Ward boundary, flood zone, school campus"],["Raster","Grid of cells with a value","Satellite image / pollution or heat map, population-density grid"]],widths=[2.6,4.8,9.6],size=9.5)
cap("Table","Spatial relationships with examples")
T([["Relationship","Meaning","Example"],["Topological","Intersects, touches, contains, within, disjoint (independent of distance)","The accident point lies WITHIN Ward 12; the pipeline CROSSES Anna Salai"],["Distance","Metric distance between objects","The accident is 80 m from the nearest bar; hospital within 2 km"],["Direction","Orientation relative to another object","The junction lies NORTH-EAST of the bus terminus"]],widths=[3,6,8],size=9.5)
H("5.2 Spatial autocorrelation",2)
P("Spatial autocorrelation means that values at nearby locations are more similar (positive) or more different (negative) than at random – Tobler’s first law: “near things are more related than distant things”. Accidents cluster around the same junctions, and neighbouring wards have similar complaint rates. Standard statistics (t-tests, linear regression, classical confidence intervals) assume **independent** observations. With autocorrelated data the effective sample size is smaller than the number of points, so standard errors are too small, p-values are over-optimistic, and models appear significant when they are not and show spatially structured residuals. Spatial methods (Moran’s I, spatial lag/error models, geographically weighted regression, spatial cross-validation) are required.")
H("5.3 Co-location mining: participation ratio and index",2)
P("Instance counts: A = 4 (A1–A4), B = 5 (B1–B5), C = 3 (C1–C3). **Participation ratio** PR(f, {f,g}) = (number of distinct instances of f taking part in neighbouring pairs of the pattern) / (total instances of f). **Participation index** PI = minimum of the participation ratios. A pattern is prevalent if PI ≥ 0.5.")
cap("Table","Participation ratio and index for each pair")
T([["Pair","Distinct instances taking part","Participation ratios","PI = min","Prevalent (≥ 0.5)?"],
["A–B","A: A1, A2, A3 (3);  B: B1, B2, B4 (3)","PR(A) = 3/4 = 0.750;  PR(B) = 3/5 = 0.600","0.600","Yes"],
["A–C","A: A1, A2, A3 (3);  C: C1, C2 (2)","PR(A) = 3/4 = 0.750;  PR(C) = 2/3 = 0.667","0.667","Yes"],
["B–C","B: B1, B2 (2);  C: C1 (1)","PR(B) = 2/5 = 0.400;  PR(C) = 1/3 = 0.333","0.333","No"]],widths=[1.4,5.2,5.6,1.8,3],size=9,align_center_cols=(0,3,4))
P("**Prevalent size-2 co-locations (threshold 0.5): {A,B} and {A,C}.** {B,C} is not prevalent (PI = 0.333).")
H("5.4 The triple {A, B, C}",2)
P("Row instances: (A1,B1,C1), (A1,B2,C1), (A2,B2,C1). Distinct instances: A = {A1, A2} → PR(A) = 2/4 = 0.500; B = {B1, B2} → PR(B) = 2/5 = 0.400; C = {C1} → PR(C) = 1/3 = 0.333.")
MATH(["PI({A,B,C}) = min(0.500, 0.400, 0.333) = 0.333 < 0.5  →  NOT prevalent"])
P("This agrees with the anti-monotone property of the participation index: since {B,C} (PI = 0.333) is not prevalent, no superset containing B and C can be prevalent, so {A,B,C} could have been pruned without even counting its instances.")
H("5.5 Co-location vs market-basket association rule",2)
P("Market-basket mining works on **transactions** – discrete baskets in which items either co-occur or not – and measures support and confidence. Spatial data have no natural transactions: objects lie in continuous space and instances of different features are related by a **neighbourhood relation** (distance), so the “baskets” would have to be artificially created (e.g. by grid cells), which is arbitrary and can split or double-count neighbours. Co-location uses the participation index, which is based on the fraction of each feature’s instances taking part, so a rare feature is treated fairly and the measure is anti-monotone (supporting pruning). Support in transaction data counts baskets; here the same instance can take part in many neighbour pairs, so counting pairs would be biased towards frequent features. Co-location patterns are also symmetric sets (no “if A then B” direction/confidence), though conditional probability rules can be derived afterwards.")

# ---- TASK 6
PB()
H("TASK 6 – Spatial Clustering of Incident Locations (5 marks)",1)
H("6.1 Data source (documented)",2)
P("No public incident file with these properties was reachable from the offline work-space, so **synthetic GPS data** were generated (task6_spatial_clustering.py, numpy seed 7), centred on Chennai (13.0827° N, 80.2707° E), 1,400 points saved in incidents.csv: hot-spot 1 – a round Gaussian cluster of 380 points (σ = 0.35 km, a busy junction); hot-spot 2 – a crescent of 420 points (a curved flyover approach); hot-spot 3 – an elongated corridor of 400 points (an arterial road); plus 200 uniformly scattered noise points over a 13 km × 12 km area. Lat/lon are also projected to kilometres (x, y) so that ε is in km.")
IMG("../shots/task6_1.png",16.5,"Task 6 program output – k-means, k-distance knee, effect of ε, DBSCAN result (screenshot)")
H("6.2 Methods and parameter selection",2)
B("**k-means (k = 4)** partitions the points into k convex groups around centroids, minimising squared distance; every point (including noise) is forced into a cluster.")
B("**DBSCAN** defines a cluster as a maximal set of density-connected points: a core point has ≥ MinPts points within ε; clusters grow through core points; points not reachable from any core point are noise.")
B("**CLARANS (discussion only):** a randomised, medoid-based method (like k-medoids/PAM) where cluster centres are actual data points, found by searching a limited number of neighbouring medoid swaps. Compared with k-means it is more robust to outliers and works with any distance, but it still needs k in advance, forms compact convex-ish clusters around medoids (so the crescent and the road corridor would still be cut), has no notion of noise, and costs about O(n²) per search – hence it would improve on k-means for noisy points but not match DBSCAN for arbitrary shapes.")
P("**Choosing ε and MinPts.** MinPts = 10 (rule of thumb ≥ 2 × dimensions, increased for 1,400 noisy points). For every point the distance to its 10th nearest neighbour was computed and sorted (k-distance graph, Figure 6). Points inside hot-spots have small k-distances; noise points have large ones, so the curve rises sharply at the “knee”. The knee (point of maximum distance from the chord of the curve) is at rank 1180, **ε = 0.286 km (≈ 286 m)**.")
IMG("../figs/fig_kdist.png",9.5,"k-distance graph (k = MinPts = 10) with chosen ε")
H("6.3 Effect of changing ε",2)
cap("Table","DBSCAN with MinPts = 10 and different ε (ARI = adjusted Rand index vs the generated hot-spot labels)")
T([["ε (km)","Clusters found","Noise points","ARI","Comment"],["0.114 (0.4 × ε)","22","655","0.196","Too small: hot-spots fragment, many real points called noise"],["0.286 (chosen)","3","190","0.975","Three hot-spots found; 187 of 200 true noise points detected"],["0.572 (2 × ε)","3","173","0.958","Still 3 clusters, but some noise absorbed at the cluster edges"],["1.716 (6 × ε)","1","5","0.002","Too large: everything merges into one cluster"]],widths=[3.2,2.4,2.4,1.6,7.4],size=9,align_center_cols=(1,2,3))
IMG("../figs/fig_eps_effect.png",16.5,"DBSCAN results for four values of ε (noise = grey ×)")
H("6.4 Clusters, noise and comparison",2)
IMG("../figs/fig_kmeans_vs_dbscan.png",16.5,"Ground truth, k-means (k = 4) and DBSCAN (ε = 0.29 km, MinPts = 10); noise points are the grey ×")
cap("Table","k-means vs DBSCAN on the incident data")
T([["Aspect","k-means (k = 4)","DBSCAN (ε = 0.286 km, MinPts = 10)"],["Cluster sizes","505, 406, 440, 49","377, 428, 405 (+190 noise)"],["ARI vs truth","0.686","0.975"],["Noise","None – all 1,400 points assigned (the 200 scattered points inflate and shift clusters)","190 points marked noise (187 of the 200 true noise points)"],["Crescent / corridor","Cut into pieces; a centroid sits in empty space between points","Followed exactly, because density connectivity can bend"],["Needs k in advance","Yes (4 chosen by us)","No – found 3 automatically; needs ε, MinPts"]],widths=[3.6,6.4,7],size=9)
P("**Which is better and why:** DBSCAN represents the hot-spots far better (ARI 0.975 vs 0.686). A hot-spot is by nature a *dense area of arbitrary shape*; DBSCAN defines a cluster exactly that way (density-connected points) and explicitly labels isolated incidents as noise. k-means defines a cluster as the points closest to a centroid, which favours compact, similarly sized spherical groups: it splits the crescent and the road corridor, merges noise into clusters and forces the user to guess k. Weakness of DBSCAN: a single ε cannot handle hot-spots of very different densities, and it is sensitive to ε (Table 17).")

# ---- TASK 7
PB()
H("TASK 7 – Social Impacts and Privacy (4 marks)",1)
H("7.1 k-anonymity of the table as given",2)
P("k-anonymity = size of the smallest group of records that share the same values of the quasi-identifiers (Age, PIN code). Original table (Complaint type is the sensitive attribute):")
cap("Table","Original extract and equivalence classes")
T([["Age","PIN code","Complaint","Group (Age, PIN) size"],["23","600041","Garbage","1"],["27","600042","Garbage","1"],["24","600041","Water","1"],["52","600087","Roads","1"],["58","600088","Roads","1"],["55","600087","Water","1"]],widths=[2.5,3.5,4,5],size=9.5,align_center_cols=(0,1,3))
P("Every (Age, PIN) combination is unique, so every group has size 1: **the table is 1-anonymous (k = 1)**. Anyone who knows a neighbour’s age and PIN code can single out the row and learn the complaint.")
H("7.2 Generalisation to achieve 2-anonymity",2)
P("Generalise Age to 10-year ranges and PIN code to its first five digits (the last digit replaced by *):")
cap("Table","Anonymised table")
T([["Age range","PIN code","Complaint"],["20–29","60004*","Garbage"],["20–29","60004*","Garbage"],["20–29","60004*","Water"],["50–59","60008*","Roads"],["50–59","60008*","Roads"],["50–59","60008*","Water"]],widths=[4,4,5],size=9.5,align_center_cols=(0,1))
P("Two equivalence classes remain, each of size 3, so the table is **3-anonymous**, which satisfies the required 2-anonymity (the next-smaller generalisation of only the PIN code would leave groups of size 1 or 2 for age, so both attributes had to be generalised). Each group also contains two different complaint types, so it has some diversity (an attacker cannot be sure of the complaint, though a homogeneous group would reveal it). **Information lost:** exact age (±5 years uncertainty), the exact PIN – the researcher cannot tell 600041 from 600042 (neighbouring areas) or separate 23- from 27-year-olds; fine-grained neighbourhood patterns and age-specific analysis are no longer possible. The complaint type is untouched.")
H("7.3 Social risks and safeguards",2)
cap("Table","Risk–safeguard table")
T([["Social risk of mining the platform’s data","Safeguard"],
["**Profiling of individuals** – complaint history/locations can reveal a person’s habits, home, health or political activity","Remove identifiers at ETL, pseudonymise, generalise location (k-anonymity), data minimisation and retention limits, purpose-limited access with audit logs"],
["**Bias against neighbourhoods** – hot-spot or complaint-volume maps can label an area as “problematic”; poorer areas that complain less (under-reporting) get fewer services, and feedback loops reinforce this","Normalise by population and reporting rate, bias audits of the models, human review before resource allocation, publish methodology"],
["**Misuse / function creep** – data collected for services used for surveillance, policing or by third parties; re-identification when released datasets are linked with other data","Legal data-sharing agreements, anonymised/aggregated releases with small-cell suppression, role-based access, ethics/privacy review board, transparency to citizens and an opt-out/grievance process"]],widths=[8,9],size=9.5)

# ---- TASK 8
PB()
H("TASK 8 – Design the Integrated System (6 marks)",1)
H("8.1 Architecture",2)
IMG("../figs/fig_architecture.png",17,"Original architecture: sources → ETL → warehouse/stores → mining → reporting, with privacy & governance")
P("**Reasoning.** Structured data (service requests) go through a classic relational ETL into a star-schema warehouse so OLAP summary reports are fast and consistent. **Unstructured text** is loaded through a text ETL (clean → tokenise → stop-word/stem → TF–IDF vectors and topic/urgency labels) and stored in a text index linked to the fact table by request_id, because free text cannot be summed or sliced directly. **Spatial data** are validated, converted to points/grid cells and stored in a spatial store with a ward/zone polygon reference; the warehouse holds only the location *key*. Web data are crawled and sessionised separately. Mining modules read from the stores and write results (topic, urgency, hot-spot id) back as new attributes so reports can use them.")
H("8.2 Dimensional design (star schema) for service requests",2)
cap("Table","Fact table and dimensions")
T([["Table","Key and attributes","Notes"],
["Fact_ServiceRequest (grain: one service request)","request_key; time_key (created), time_key_closed; location_key; category_key; dept_key; channel_key; citizen_pseudo_id; measures: request_count (1), resolution_hours, cost, urgency_score, reopen_flag","Measures are additive (count, cost) or averaged (hours)"],
["Dim_Time","time_key; date, day, week, month, quarter, year, day-of-week, is_holiday, hour/time band","Hierarchy: hour → day → week → month → quarter → year"],
["Dim_Location","location_key; ward, zone, district, city; latitude/longitude (point) or cell_id; polygon reference","Hierarchy: street/point → ward → zone → city; used for spatial roll-up"],
["Dim_Category","category_key; topic (from classifier), sub-topic, urgency class","Roads, Water, Sanitation, Electricity, Health, Other"],
["Dim_Dept / Dim_Channel","department, officer team; channel (app, portal, social, phone)","Supports workload and channel analysis"]],widths=[4.2,8.2,4.6],size=9)
H("8.3 Requirement → technique mapping",2)
cap("Table","Mapping of the Commissioner’s requirements to techniques")
T([["Requirement","Technique","Reason"],
["Retrieve and group complaints by topic and urgency","TF–IDF vector-space retrieval; Naïve Bayes/SVM topic classifier; k-means for discovering new topics (Tasks 1–2)","Fast, interpretable on short text; classifier needs labels, k-means finds unlabelled themes; urgency uses keywords (“school”, “hospital”, “live wire”) as features"],
["Understand portal usage and classify portal/news pages","Web usage mining (sessions, paths); web content classifier; PageRank/HITS (Tasks 3–4)","Usage logs show user journeys; classifier categorises pages; link analysis finds important pages"],
["Find geographic hot-spots and spatial relationships","DBSCAN on incident points; co-location mining with participation index (Tasks 5–6)","Hot-spots have arbitrary shape and noise, which DBSCAN handles; co-location finds feature pairs (accidents near bars)"],
["Summary reports from the data warehouse","Star schema, OLAP roll-up/drill-down, dashboards","Fast aggregation by time, location, category"],
["Protect citizen privacy","Anonymisation at ETL, k-anonymity, access control (Task 7)","Privacy must be built in, not added after"]],widths=[4.2,6.2,6.6],size=9)
H("8.4 Privacy controls built into the design",2)
B("Direct identifiers (name, phone, exact address) are not loaded into the warehouse; complaints keep a pseudonymous citizen id.")
B("Role-based access, encrypted storage and audit logs; mining analysts see only aggregated or generalised data.")
B("Location generalised (ward/zone) in reports; small-cell suppression (cells with < 5 incidents are hidden); k-anonymity ≥ 3 for any released extract (Task 7).")
B("Free text is scanned for phone numbers/names and masked before indexing; retention limits and a deletion process.")
H("8.5 How each module is evaluated",2)
cap("Table","Evaluation plan")
T([["Module","How it is evaluated","Target / trigger"],
["ETL / warehouse","Row-count reconciliation with source, null/duplicate checks, report totals vs operational DB, load time","100 % reconciled; daily load < 1 hour"],
["Text retrieval","Precision/recall@k, MAP on judged queries","P@10 ≥ 0.8"],
["Topic/urgency classifier","Accuracy, per-class precision/recall/F1, confusion matrix on a held-out labelled sample; weekly audit","Macro-F1 ≥ 0.9; retrain on a 5-point drop"],
["Web mining","Page classifier F1; PageRank sanity vs click counts; usage-path validation against known journeys","Macro-F1 ≥ 0.85"],
["Spatial hot-spots","Stability of clusters under resampling; comparison with police/accident records; noise share","Same hot-spots found in ≥ 90 % of resamples"],
["Privacy","k-anonymity test on every extract; re-identification attack test; access-log audit","k ≥ 3, no direct identifier"]],widths=[3.6,8.4,5],size=9)

# ---- TASK 9
PB()
H("TASK 9 – DAY-4 DESIGN CHALLENGE: Re-evaluate and Adapt the Design (8 marks)",1)
P("**Changed requirement:** exact residential locations and personal identifiers may no longer be stored in the analytical platform; complaints arrive in English, Tamil and Hindi; volume rises from 5,000 to 20,000 complaints/day. The experiments below were run with task9_adaptation_experiments.py (Appendix C).")
H("A. Impact analysis (2 marks)",2)
cap("Table","Which modules are affected")
T([["Module","Affected?","Why"],
["ETL","**Yes – major**","Must remove/obfuscate identifiers and exact GPS before loading; needs language detection and per-language processing; 4× volume"],
["Warehouse dimensions","**Yes**","Dim_Location can no longer hold exact points (use ward → zone → grid cell); Dim_Language added; citizen id becomes a keyed pseudonym; fact table unchanged otherwise"],
["Text mining","**Yes – major**","Vocabulary triples, English-trained classifier cannot read Tamil/Hindi, tokenisation of non-Latin scripts"],
["Spatial mining","**Yes**","DBSCAN and co-location now work on generalised locations; ε and MinPts must be re-tuned"],
["Reports","**Partly**","Same OLAP structure; location drill-down stops at grid cell/ward; small-cell suppression; add language dimension"],
["Web mining (usage, PageRank, page classifier)","No (minor)","Based on page links and logs, not on residential locations; only IP/user ids in logs must be pseudonymised, and Tamil/Hindi pages need the same multilingual features as complaints"]],widths=[3.8,2.8,10.4],size=9)
H("B. Evaluation of the original design under the new conditions (2 marks)",2)
P("The original design was tested with real experiments (Figure 10 shows the terminal output):")
IMG("../shots/task9_1.png",16.5,"Task 9 program output – grid-generalisation test and multilingual test (screenshot)")
H("B1. Location generalisation on hot-spot results",3)
P("The exact GPS points were replaced by the centre of a grid cell (100 m … 2 km) and DBSCAN re-run (MinPts = 10).")
cap("Table","Effect of replacing exact GPS by grid-cell centres")
T([["Grid cell","ε used (km)","Clusters","Noise","ARI vs truth","ARI vs original DBSCAN"],
["Exact GPS","0.286","3","190","0.975","1.000"],["100 m","0.286","3","190","0.975","0.997"],["250 m","0.286","3","188","0.975","0.997"],["250 m","0.375 (1.5 × cell)","3","183","0.973","0.989"],
["500 m","0.286","42","302","0.157","0.153"],["500 m","0.750","2","139","0.557","0.569"],["1 km","0.286","22","220","0.265","0.262"],["1 km","1.500","1","6","0.003","0.003"],["2 km","0.286 / 3.0","15 / 1","127 / 0","0.328 / 0.000","0.331 / 0.000"]],widths=[2.4,3.3,2,2,3,4.3],size=9,align_center_cols=(1,2,3,4,5))
IMG("../figs/fig_grid_effect.png",16.5,"DBSCAN on 250 m, 500 m and 1 km grid-cell centres (ε = 1.5 × cell size, noise = grey ×)")
P("**Finding:** up to a 250 m grid the three hot-spots are preserved almost exactly (ARI 0.975, 0.997 agreement with the original clusters). At 500 m the grid is wider than the road corridor (≈ 200 m) and the cell centres form a lattice, so DBSCAN either fragments into 42 clusters (small ε) or merges (larger ε); at 1 km it collapses completely. The original design would therefore fail if the privacy rule were met by coarse generalisation only.")
H("B2. Multilingual text on vocabulary and classifier",3)
cap("Table","English-only vs trilingual classifier (test accuracy; 5 classes → chance = 0.20)")
T([["Model","|V|","English","Hindi","Tamil"],
["Original: English-only (Naïve Bayes and SVM)","30 (core-word test set)","1.000","**0.200**","**0.200**"],
["Trilingual: trained on English + Hindi + Tamil","90","1.000","1.000","1.000"],
["Pivot-to-English (dictionary standing in for machine translation) then English model","30","1.000","1.000","1.000"]],widths=[7.5,3.5,2,2,2],size=9,align_center_cols=(1,2,3,4))
P("**Findings:** (i) the English-only model is exactly at chance on Hindi and Tamil – none of their words is in its vocabulary. (ii) The vocabulary triples (30 → 90) – more features, more memory and a greater need for labelled examples in each language. (iii) The default tokenizer pattern \\w\\w+ **breaks Tamil/Hindi words** (the vowel sign/virama is not a word character: அவசரம் became அவசரம), so tokenisation had to be changed to whitespace/Unicode-aware splitting. (iv) Throughput is not a problem: vectorising and classifying 20,000 complaints took 0.05 s on one core; the 4× volume affects mainly language detection, translation and storage. *Caveat:* the 100 % scores come from a small synthetic test set (5 core words/class/language) and an idealised dictionary translator; real data will be lower.")
H("C. Adaptation / redesign (2 marks)",2)
IMG("../figs/fig_architecture_revised.png",17,"Revised architecture – orange boxes are the changed parts")
cap("Table","What is retained, modified or redesigned")
T([["Part","Decision","Change"],
["Web mining, reports structure, star-schema fact table","**Retain**","No change to PageRank/HITS, usage mining, OLAP design"],
["Spatial ETL and Dim_Location","**Modify**","Exact GPS converted to a 250 m grid-cell id **inside the ETL staging area**, raw GPS discarded; hierarchy ward → zone → grid cell; no street/address attribute; DBSCAN run on cell centres with ε = 0.29–0.38 km; cells with < 5 incidents suppressed in reports"],
["Relational ETL / citizen id","**Modify**","Name, phone, address dropped; citizen id replaced by a keyed hash (HMAC) whose key is kept outside the platform; text scanned and masked for phone numbers and names"],
["Text mining","**Redesign**","Add language detection (script/Unicode block + n-gram model); Unicode-aware tokeniser; per-language stop-words and stemmers; either (a) a multilingual classifier trained on labelled data in all three languages, or (b) translate to a pivot language; add Dim_Language; urgency lexicons for each language"],
["Capacity","**Modify**","Batch/stream ETL scaled to 20,000/day (4×); partition the text index by language and day"]],widths=[4.4,2.4,10.2],size=9)
H("D. Evidence-based defence (2 marks)",2)
B("**Location – decision: 250 m grid at ETL.** Evidence (Table 26): at 250 m the hot-spot clusters are almost identical to those from exact GPS (ARI 0.975, 0.997 agreement), while 500 m and above destroy them (ARI ≤ 0.56). A 250 m cell is also coarse enough that no exact residence can be recovered, and, combined with suppression of cells under 5 incidents, gives k-anonymity-style protection (Task 7). **Trade-off accepted:** we lose street-level precision and the ability to say which house/building; a hot-spot cannot be located more finely than ≈ 250 m, and ε must be re-tuned (1.5 × cell). Evidence in Task 6: ε is critical (22 clusters at ε/2.5, 1 cluster at 6ε), so the re-tuning step is mandatory and part of the deployment checklist. *Limitation:* the safe cell size depends on hot-spot width; the data are synthetic, so the real threshold must be re-tested on the city’s data.")
B("**Text – decision: language detection + trilingual (or pivot) features.** Evidence (Table 27): the English-only model scores 0.20 (chance) on Hindi and Tamil, the trilingual one 1.00 on the test set. Task 2 showed that vocabulary size drives accuracy (limiting vocabulary to 40 terms lost 18–23 points), so the trilingual vocabulary (3×) must not be truncated aggressively; stemming/stop-word changes hardly mattered (≤ 0.6 points), so the effort should go into labelled examples per language and a proper tokeniser rather than elaborate pre-processing. **Trade-off accepted:** more storage and labelling effort, and (if translation is used) some accuracy loss from translation errors; the mixed-topic errors found in Task 2.5 remain.")
B("**Privacy vs accuracy overall:** we accept a small accuracy loss for spatial results (≈ 0.3 % disagreement with exact GPS at 250 m) in return for removing exact residential locations entirely; the platform meets the rule, and capacity is ample (20,000 complaints classified in 0.05 s).")

# ================= APPENDIX
PB()
H("APPENDIX A – Source code, Task 2 (also in GitHub: code/corpus.py, code/task2_text_mining.py)",1)
for fn in ("corpus.py","task2_text_mining.py"):
    P(fn,bold=True,size=10); CODE(open(fn).read())
H("APPENDIX B – Source code, Task 6 (code/task6_spatial_clustering.py)",1)
CODE(open("task6_spatial_clustering.py").read())
H("APPENDIX C – Source code, Task 9 experiments (code/task9_adaptation_experiments.py)",1)
CODE(open("task9_adaptation_experiments.py").read())
H("APPENDIX D – Verification of hand calculations (code/hand_calc_verification.py)",1)
P("The hand calculations for Tasks 1, 3, 5 and 7 above were cross-checked with this program (the values match; D3’s length is 1.0925).")
IMG("../shots/calc_1.png",16.5,"Verification output – Task 1 (TF–IDF, cosine, P/R)")
IMG("../shots/calc_2.png",16.5,"Verification output – Tasks 3, 5 and 7")
CODE(open("hand_calc_verification.py").read())
H("APPENDIX E – Reproducing the results / GitHub contents",1)
CODE("""pip install numpy pandas scikit-learn matplotlib pillow
cd code
python3 task2_text_mining.py             # Task 2  -> outputs/task2_output.txt
python3 task6_spatial_clustering.py      # Task 6  -> outputs/incidents.csv, figs/*.png
python3 task9_adaptation_experiments.py  # Task 9  -> outputs/task9_output.txt, figs/fig_grid_effect.png
python3 hand_calc_verification.py        # verifies Tasks 1, 3, 5, 7""",8.5)
P("Repository layout: code/ (all .py files), outputs/ (text outputs, incidents.csv), figs/ (plots and diagrams), shots/ (terminal screenshots), README.md. Seeds: 42 (text corpus, split, k-means, SVM), 7 (GPS data and k-means).",size=10)
D.save("../DWDM_Assignment5_Solution.docx")
print("saved",FIG[0],"figures",TAB[0],"tables")

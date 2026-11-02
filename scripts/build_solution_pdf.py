"""Build the submission solution document from saved measurements; no network calls."""
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted
from reportlab.lib.pagesizes import letter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/customer_support_solution.pdf'
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Body',fontName='Helvetica',fontSize=10,leading=14,spaceAfter=9))
styles.add(ParagraphStyle(name='SmallBody',fontName='Helvetica',fontSize=9,leading=12,spaceAfter=7))
styles['Title'].fontSize=22
styles['Title'].leading=27
styles['Title'].alignment=TA_LEFT
styles['Heading1'].fontSize=15
styles['Heading1'].leading=19
styles['Heading1'].textColor=colors.HexColor('#243B53')
story=[]
def p(text,style='Body'):
    story.append(Paragraph(text,styles[style]))
def h(text):p(text,'Heading1')
def table(rows,widths):
    cells=[[Paragraph(escape(str(c)),styles['SmallBody']) for c in row] for row in rows]
    t=Table(cells,colWidths=widths,hAlign='LEFT',repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E7EDF3')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#243B53'))]))
    story.extend([t,Spacer(1,10)])
ids=['baseline-001','baseline-2048-001','improved-2048-001']
metrics=[json.loads((ROOT/'artifacts/runs'/rid/'metrics.json').read_text()) for rid in ids]
p('Customer Support<br/>Agent Evaluation','Title')
p('Week 4 core track | Ramesh Suthan Palani | November 2, 2026','SmallBody')
h('Goal and evaluation question')
p('Route e-commerce tickets to the correct support team under a human-reviewed business policy. Does an explicit product-versus-refund priority rule improve classification while keeping response validity, latency and cost acceptable?')
p('The agent is a single-node LangGraph classifier using Muse Spark Open on Fireworks AI. It returns one category and a short explanation. LangSmith records ticket-level inputs, outputs, reference IDs and nested model traces. Expected labels are not included in model messages.')
h('Three controlled runs')
rows=[['Metric','Original 1024','Control 2048','Improved 2048']]
for label,key,fmt in [('Accuracy','accuracy','.0%'),('Macro F1','macro_f1','.3f'),('Valid responses','valid_response_rate','.0%'),('p95 latency (s)','p95_latency_seconds','.2f'),('Known cost (USD)','known_cost_usd','.6f'),('Cost coverage','cost_coverage','.0%')]:
    rows.append([label,*[format(m[key],fmt) for m in metrics]])
table(rows,[153,113,113,113])
p('<b>Main finding:</b> the same-settings prompt comparison improved accuracy from 96% to 98%. It fixed all four targeted routing errors, but two previously valid responses became invalid after reaching the output limit. This is a measured tradeoff, not a claim of production readiness.')
p('All runs contain the same 100 cases. Errors remain in the denominator. The original run was resumed only for unattempted cases after provider failures; no failed result was replaced.','SmallBody')
story.append(PageBreak())
h('Dataset and reviewed routing policy')
p('All 100 ticket texts came from the supplied CSV and were human reviewed before freezing. They comprise 25 related seed families. Four source labels (t004-t007) changed to refund_request. Descriptive tags add detail; they do not create new routing categories.')
table([['Category','Reviewed meaning'],['order_status','Tracking and delivery questions without an explicit non-delivery refund request.'],['refund_request','Non-delivery refunds, returns, cancellations, overcharges and refund follow-up.'],['product_issue','Damaged/wrong/misdescribed goods, damaged packaging and missing instructions. Damaged-product refund requests stay here.'],['account_help','Login/session issues, account security concerns, address and payment-method updates.'],['other','General shipping policy, feedback, stock, discounts and sale questions.']],[112,380])
h('Scoring and pass bars')
p('PASS means a valid output whose category exactly matches the reviewed label. Wrong categories, invalid responses and provider failures are FAIL. Accuracy uses all 100 cases; macro F1 averages the five categories. p95 latency uses linear interpolation. Costs use the saved Fireworks price snapshot and reported token usage; unknown usage is never treated as zero.')
table([['Metric','Target','Improved result'],['Accuracy','At least 95%','98% - met'],['Macro F1','At least 0.90','0.990 - met'],['Valid responses','100%','98% - not met'],['p95 latency','At most 15 seconds','13.21 seconds - met'],['Mean inference cost','At most $0.02 per case','$0.002790 - met']],[154,165,173])
h('Original failure groups')
p('4 damaged-product/refund priority errors (t044-t047); 1 packaging/manual scope error (t059); 2 output-limit failures (t015, t058); and 2 HTTP 500 provider failures (t026, t055). The first two groups concern prompt coverage; the latter groups concern response completion and infrastructure.')
story.append(PageBreak())
h('Prompt change and controlled comparison')
p('First, the unchanged baseline prompt was rerun with max_tokens increased from 1024 to 2048. Then one focused priority clarification was added at 2048. Dataset, model, temperature zero, timeout and no-retry policy were unchanged. Packaging/manual wording was not expanded.')
p('<b>Original prompt</b>')
for line in (ROOT/'prompts/baseline.txt').read_text().splitlines():
    if line:p(escape(line),'SmallBody')
p('<b>Added instruction</b>')
base=(ROOT/'prompts/baseline.txt').read_text()
improved=(ROOT/'prompts/improved.txt').read_text()
added=improved.split('When a ticket reports')[1].split('Treat the next message')[0]
p(escape('When a ticket reports'+added).replace('\n',' '),'SmallBody')
h('Observed fixes and regressions')
table([['Cases','Control 2048','Improved 2048'],['t044-t047','refund_request (wrong)','product_issue (correct)'],['t004-t007','refund_request (correct)','refund_request (correct)'],['t058','product_issue (correct)','Invalid response; output limit'],['t083','other (correct)','Invalid response; output limit']],[110,191,191])
p('The prompt pair has 4 fixes, 2 regressions and 94 unchanged correct results. Both invalid responses used 2048 output tokens, including 2045 reported reasoning tokens. Their model traces show finish_reason=length. Increasing the limit did not eliminate this failure mode.','SmallBody')
story.append(PageBreak())
h('Trace evidence and repository guide')
workspace='82c36783-971e-46c1-862e-a27d43bbcba3'
dataset='892c6169-ac98-4d08-b4be-8363f254cc11'
for label,project in [('Control 2048 experiment','fbf15121-6924-4b0a-9c37-de46208b0b45'),('Improved 2048 experiment','a6ba6566-3751-417b-95cc-0de7e769182f')]:
    url=f'https://smith.langchain.com/o/{workspace}/datasets/{dataset}/compare?selectedSessions={project}'
    p(f'<link href="{url}" color="#245AA5">{label}</link>')
evidence=json.loads((ROOT/'reports/trace_evidence/improved_samples.json').read_text())
for r in evidence:
    if r['case_id'] in ['course-t044','course-t083']:
        p(f'<link href="{escape(r["trace_url"])}" color="#245AA5">{r["case_id"]}: '+('targeted routing fix' if r['case_id']=='course-t044' else 'output-limit regression')+'</link>','SmallBody')
p('LangSmith links require access to the project workspace. The repository also contains saved ticket outputs, metadata and inspected trace evidence so the numerical findings can be reviewed without account access.','SmallBody')
table([['Artifact','Purpose'],['reports/customer_support_evaluation.xlsx','Source tabs plus Our Summary, Our Results, Our Reviewed Labels, Our Failure Analysis and Our Paired Results. Correct=1 means PASS; Correct=0 means FAIL.'],['notebooks/customer_support_evaluation.ipynb','Executed analysis notebook. Paid flags are off; saved-results replay makes no model calls.'],['data/frozen/v1 and artifacts/runs','Frozen labels, three original result sets, run specifications and metrics.'],['prompts and src/support_eval','Versioned prompt text and independently written agent/evaluation code.'],['reports/DEMO_SCRIPT.md','Narration and screen sequence for the remaining Loom recording.']],[185,307])
h('Cost, limitations and attribution')
p('Known project cost including the pilot is $0.79069535, excluding two original requests with unknown usage. Retaining both full-context reserves gives $3.42083935 conservative exposure under the approved $5 ceiling. These reserves are not measured charges.')
p('The same synthetic set was used for diagnosis and reevaluation. Single runs cannot fully separate intervention effects from generation variability or provider conditions. Further work would test response completion on independent tickets. No extra experiment, LLM judge, deployment or external submission was performed.','SmallBody')
p('Source tickets and baseline category descriptions: The Gen Academy, repository revision ef517b274cf86a2c4fa8ae72fdc89b3dce80f41d. The source workbook has 150 cases while the CSV has 100; only one shared ID has identical text. Supplied scores were not reused. This follows the Customer Support track; the separate Own Use Case checklist does not define this project\'s scope.','SmallBody')
p('AI assistance was used for implementation, analysis and documentation. Ramesh made the ground-truth and routing-policy decisions and approved the experiment design. A presentation-style video with synthetic narration is included in reports/video. Loom hosting remains pending if required by the portal.','SmallBody')
def footer(canvas,doc):
    canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#52606D'))
    canvas.drawString(54,31,'Week 4 | Customer Support Agent Evaluation')
    canvas.drawRightString(558,31,f'{doc.page}')
SimpleDocTemplate(str(OUT),pagesize=letter,rightMargin=60,leftMargin=60,topMargin=45,bottomMargin=48,title='Customer Support Agent Evaluation - Solution',author='Ramesh Suthan Palani').build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)

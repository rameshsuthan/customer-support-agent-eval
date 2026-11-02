"""Create a captioned artifact walkthrough with macOS synthetic narration."""
import json, math, re, subprocess, textwrap, wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1]
TMP=Path('/private/tmp/week4-video'); TMP.mkdir(exist_ok=True)
OUT=ROOT/'reports/video';OUT.mkdir(exist_ok=True)
FF=imageio_ffmpeg.get_ffmpeg_exe()
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def font(size,bold=False):return ImageFont.truetype(BOLD if bold else FONT,size)
chapters=[
('Customer Support Agent Evaluation','Week 4 core track',[
 '100 human-reviewed tickets',
 'Fireworks Muse Spark Open + LangGraph',
 'LangSmith experiments and model traces'],[
 'This is a walkthrough of Ramesh\'s Week Four customer support agent evaluation. The project asks whether an explicit routing rule can improve an agent\'s decisions without hiding failures.',
 'The classifier uses Muse Spark Open through Fireworks, with a single LangGraph node. It returns one support category and a short explanation for each customer ticket.',
 'LangSmith records the individual model calls. This presentation uses saved project evidence and a standard synthetic narrator. All measurements shown come from our own experiments, not the starter scores.']),
('Define success before measuring','Frozen dataset v1',[
 'Five routes: order status, refunds, product, account, other',
 'PASS = valid category matching the reviewed label',
 'Wrong, invalid and provider-error responses all FAIL'],[
 'The dataset contains one hundred supplied ticket texts. Ramesh reviewed every label before evaluation, and the project froze those decisions so predictions could not influence the answers.',
 'Five categories cover order status, refunds, product issues, account help and other requests. A pass requires a valid output that exactly matches the reviewed category.',
 'Wrong categories, incomplete responses and provider errors remain failures in the one hundred case denominator. Expected labels stay outside the model messages, preventing reference-answer leakage.']),
('A deliberate business distinction','Human-reviewed routing policy',[
 'Missing delivery + explicit refund → refund_request',
 'Damaged product + explicit refund → product_issue',
 'Packaging damage / missing instructions → product_issue'],[
 'The policy distinguishes two similar situations. An undelivered order with an explicit request for money back goes to the refund team, rather than order status.',
 'A damaged product stays with the product team, even when the customer asks for a refund or rejects a replacement. These are ownership decisions, not universal intent labels.',
 'Packaging damage and missing instructions also belong to product issues. The supplied labels were corrected where necessary, and descriptive tags were kept separate from the five routing categories.']),
('Original baseline: 91% accuracy','1,024-token output limit',[
 '4 damaged-product / refund priority errors',
 '1 packaging/manual error + 2 truncated responses',
 '2 HTTP 500 errors; unknown usage retained'],[
 'The original baseline achieved ninety one percent accuracy. Four damaged laptop tickets were routed to refunds, because the prompt described both categories without saying which one took priority.',
 'One packaging and manual complaint went to other. Two responses reached the output limit, and two calls failed with provider server errors and no reported usage.',
 'All nine failures were preserved. Interrupted runs resumed only unattempted tickets. This avoided replacing difficult or failed outputs with retries until they happened to pass.']),
('Separate the two interventions','Controlled experiment design',[
 'A: Baseline prompt, 1,024 tokens → 91%',
 'B: Same prompt, 2,048 tokens → 96%',
 'C: Priority edit, 2,048 tokens → 98%'],[
 'We first changed only the output limit, from one thousand twenty four to two thousand forty eight tokens. The unchanged prompt then scored ninety six percent, with all responses valid.',
 'Next, we kept that higher limit fixed and added one priority instruction. Damaged product requests remain product issues even if the customer explicitly asks for a refund.',
 'Missing delivery refund requests still go to refunds. The model, dataset and other settings stayed fixed. Therefore, the controlled prompt comparison is ninety six to ninety eight percent.']),
('Inspect a targeted fix','Saved LangSmith evidence: course-t044',[
 '“My laptop arrived damaged and I want a full refund,',
 'not a replacement.”',
 'Control: refund_request  →  Improved: product_issue'],[
 'Consider ticket forty four: My laptop arrived damaged and I want a full refund, not a replacement. The control predicted refund request, which conflicts with the reviewed policy.',
 'With the priority rule, the agent returned product issue. Its explanation explicitly referred to the damaged laptop and said that the product category applies despite the refund request.',
 'All four targeted damaged laptop variants were fixed. The four missing delivery refund cases also remained correct. Inspected LangSmith model child traces support these individual results.']),
('Keep the regressions visible','Saved LangSmith evidence: t058 and t083',[
 '4 fixes + 2 regressions + 94 unchanged correct',
 'Both regressions: finish_reason = length',
 '2,048 output tokens; 2,045 reported reasoning tokens'],[
 'The prompt change was not a perfect improvement. Ticket fifty eight, about packaging and missing instructions, and ticket eighty three, about shipping policy, became invalid responses.',
 'Both used the full two thousand forty eight output tokens, with two thousand forty five reported as reasoning. The model traces confirm that generation stopped because of length.',
 'The paired result is four fixes, two regressions and ninety four unchanged correct cases. Accuracy improved, but valid responses fell from one hundred to ninety eight percent.']),
('Results, costs and limitations','Evidence over a perfect-looking score',[
 'Control / improved p95: 11.65 s / 13.21 s',
 'Known project estimate: $0.791; two costs unknown',
 'Same synthetic diagnosis set; no held-out claim'],[
 'The improved run met the accuracy, macro F one, latency and mean cost targets, but missed the one hundred percent validity target. Its ninety fifth percentile latency was thirteen point two one seconds.',
 'Known project cost including the pilot was about seventy nine cents, excluding two original calls with unknown usage. Conservative reserves kept exposure near three dollars forty two, within the five dollar ceiling.',
 'These are related synthetic cases reused for diagnosis and evaluation. The results do not prove production readiness or independent generalization. The repository contains the workbook, executed notebook, prompts, results and solution document.'])]

def wrap(draw,text,f,maxwidth):
    words=text.split();lines=[];line=''
    for w in words:
        candidate=(line+' '+w).strip()
        if draw.textlength(candidate,font=f)>maxwidth and line:lines.append(line);line=w
        else:line=candidate
    if line:lines.append(line)
    return lines
def render(chapter,caption,index):
    title,sub,points,_=chapter
    im=Image.new('RGB',(1920,1080),'#101D2D');d=ImageDraw.Draw(im)
    d.rectangle((0,0,1920,12),fill='#59D0BA')
    d.text((100,62),f'{index+1:02d} / 08   CUSTOMER SUPPORT EVALUATION',font=font(26,True),fill='#59D0BA')
    d.text((100,140),title,font=font(62,True),fill='white')
    d.text((100,232),sub,font=font(32),fill='#ADC1D5')
    y=342
    for point in points:
        d.rounded_rectangle((100,y-12,1820,y+92),radius=15,fill='#1D3046')
        lines=wrap(d,point,font(37),1620)
        for j,line in enumerate(lines):d.text((132,y+7+j*43),line,font=font(37),fill='#F4F7FB')
        y+=124
    d.rectangle((0,800,1920,1000),fill='#08121F')
    lines=wrap(d,caption,font(35),1690)
    for j,line in enumerate(lines):
        width=d.textlength(line,font=font(35))
        d.text(((1920-width)/2,830+j*46),line,font=font(35),fill='white')
    d.text((100,1030),'Ramesh Suthan Palani  |  Synthetic narration  |  Saved project evidence',font=font(23),fill='#ADC1D5')
    d.text((1540,1030),'November 2, 2026',font=font(23),fill='#ADC1D5')
    return im

def timestamp(t):
    ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'

segments=[];cues=[];elapsed=0;manifest=[]
for ci,ch in enumerate(chapters):
    start=elapsed
    for si,speech in enumerate(ch[3]):
        stem=f'{ci:02}-{si:02}';txt=TMP/f'{stem}.txt';txt.write_text(speech)
        aiff=TMP/f'{stem}.aiff';wav=TMP/f'{stem}.wav';png=TMP/f'{stem}.png';video=TMP/f'{stem}.mp4'
        subprocess.run(['say','-v','Samantha','-r','145','-f',str(txt),'-o',str(aiff)],check=True)
        subprocess.run([FF,'-v','error','-y','-i',str(aiff),'-ar','24000','-ac','1',str(wav)],check=True)
        with wave.open(str(wav)) as w:duration=w.getnframes()/w.getframerate()
        if duration<2:raise ValueError('Narration missing or too short')
        duration=math.ceil((duration+.35)*12)/12
        render(ch,speech,ci).save(png)
        subprocess.run([FF,'-v','error','-y','-loop','1','-framerate','12','-i',str(png),'-i',str(wav),'-t',str(duration),'-vf','format=yuv420p','-af','apad','-c:v','libx264','-preset','veryfast','-crf','24','-c:a','aac','-b:a','96k','-movflags','+faststart',str(video)],check=True)
        cues.append(f'{len(cues)+1}\n{timestamp(elapsed)} --> {timestamp(elapsed+duration)}\n{speech}\n')
        elapsed+=duration;segments.append(video)
    manifest.append({'chapter':ci+1,'title':ch[0],'start_seconds':start,'end_seconds':elapsed})
    print(f'Chapter {ci+1}/8 encoded; duration so far {elapsed:.1f}s',flush=True)
concat=TMP/'concat.txt';concat.write_text(''.join(f"file '{p}'\n" for p in segments))
subprocess.run([FF,'-v','error','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(OUT/'customer_support_demo.mp4')],check=True)
(OUT/'customer_support_demo.srt').write_text('\n'.join(cues))
(OUT/'video_manifest.json').write_text(json.dumps({'duration_seconds':elapsed,'resolution':'1920x1080','fps':12,'voice':'macOS Samantha, synthetic','chapters':manifest},indent=2)+'\n')
(OUT/'transcript.txt').write_text('\n\n'.join(ch[0]+'\n'+' '.join(ch[3]) for ch in chapters)+'\n')
print(f'Created {OUT}/customer_support_demo.mp4 ({elapsed:.1f}s)',flush=True)

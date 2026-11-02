// Run after prepare_submission.py; uses the bundled artifact-tool dependency.
import fs from 'node:fs/promises';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';
const root=process.cwd();
const data=JSON.parse(await fs.readFile(`${root}/reports/submission_data.json`,'utf8'));
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(`${root}/${data.source_file}`));
// The importer reads some empty inline strings as shared-string indices.
// Restore only those cells from an independent, read-only source extraction.
for(const [name, cells] of Object.entries(data.source_empty_cells)) {
  const sheet=wb.worksheets.getItem(name);
  for(const address of cells) sheet.getRange(address).values=[['']];
}
const summary=wb.worksheets.add('Our Summary');
const results=wb.worksheets.add('Our Results');
const review=wb.worksheets.add('Our Reviewed Labels');
const analysis=wb.worksheets.add('Our Failure Analysis');
const paired=wb.worksheets.add('Our Paired Results');
function table(sheet, headers, rows, widths) {
  const end=String.fromCharCode(64+headers.length);
  sheet.showGridLines=false;
  sheet.getRange(`A4:${end}${rows.length+4}`).values=[headers,...rows];
  sheet.getRange(`A4:${end}${rows.length+4}`).format.font={name:'Arial',size:10};
  sheet.getRange(`A4:${end}4`).format={fill:'#243B53',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:32,wrapText:true};
  sheet.getRange(`A5:${end}${rows.length+4}`).format.rowHeight=28;
  sheet.getRange(`A5:${end}${rows.length+4}`).format.verticalAlignment='center';
  widths.forEach((width,i)=>{sheet.getRangeByIndexes(0,i,rows.length+4,1).format.columnWidth=width;});
  sheet.freezePanes.freezeRows(4);
  sheet.getRange('A2').values=[[sheet.name]];
  sheet.getRange('A2').format.font={name:'Arial',size:14,bold:true};
}
const resultRows=data.results.map(r=>[r.run_id,r.case_id,r.ticket_text,r.expected_category,r.predicted_category??'No prediction',r.status,r.explanation??'',r.elapsed_seconds,r.cost_usd,r.trace_url]);
table(results,['Run','Case','Ticket','Reviewed label','Prediction','Status','Explanation','Latency (s)','Known cost (USD)','Trace'],resultRows,[27,19,65,22,22,12,65,15,20,24]);
results.getRange(`C5:C${resultRows.length+4}`).format.wrapText=true;
results.getRange(`G5:G${resultRows.length+4}`).format.wrapText=true;
results.getRange(`A5:J${resultRows.length+4}`).format.rowHeight=80;
results.getRange(`H5:H${resultRows.length+4}`).setNumberFormat('0.00');
results.getRange(`I5:I${resultRows.length+4}`).setNumberFormat('$0.000000');
results.getRange(`F5:F${resultRows.length+4}`).conditionalFormats.add('containsText',{text:'error',format:{fill:'#FEE2E2'}});
results.getRange(`K4:L${resultRows.length+4}`).values=[['Correct','Usage known'],...data.results.map(()=>[null,null])];
for(let i=5;i<resultRows.length+5;i++) results.getRange(`K${i}:L${i}`).formulas=[[`=IF(AND(D${i}=E${i},F${i}="ok"),1,0)`,`=IF(ISNUMBER(I${i}),1,0)`]];
results.getRange('K4:L4').format={fill:'#243B53',font:{color:'#FFFFFF',bold:true},columnWidth:15};
table(review,['Case','Ticket','Source label','Reviewed label','Review status','Tags','Review note'],data.review,[19,70,22,22,18,32,65]);
review.getRange('B5:B104').format.wrapText=true;
review.getRange('G5:G104').format.wrapText=true;
review.getRange('A5:G104').format.rowHeight=80;
review.getRange('A3').values=[['Source: The Gen Academy, revision ef517b274cf86a2c4fa8ae72fdc89b3dce80f41d; human-reviewed dataset v1.']];
table(analysis,['Case','Failure group','Reviewed label','Baseline prediction','Annotation'],data.failures,[19,35,22,22,90]);
analysis.getRange('E5:E13').format.wrapText=true;
analysis.getRange('A5:E13').format.rowHeight=70;
analysis.getRange('A16').values=[['Approved change: damaged-product routing takes priority over refund wording.']];
analysis.getRange('A18').values=[['Non-delivery + explicit refund remains refund_request. Packaging/manual wording is unchanged.']];
analysis.getRange('A20').values=[['Two separate comparisons isolate output-limit and prompt changes; all 100 cases are retained.']];
const metrics=['Output token limit','Cases','Accuracy','Macro F1','Valid response rate','p95 latency (s)','Known cost (USD)','Cost coverage','Mean cost (USD)'];
table(summary,['Metric',...data.runs.map(r=>r.label)],metrics.map(m=>[m,null,null,null]),[27,27,27,27]);
const last=resultRows.length+4;
data.runs.forEach((r,j)=>{
  const col=String.fromCharCode(66+j), criterion=`"${r.run_id}"`;
  const sum=(column)=>`SUMIFS('Our Results'!$${column}$5:$${column}$${last},'Our Results'!$A$5:$A$${last},${criterion})`;
  summary.getRange(`${col}5`).values=[[r.max_tokens]];
  summary.getRange(`${col}6`).formulas=[[`=COUNTIFS('Our Results'!$A$5:$A$${last},${criterion})`]];
  summary.getRange(`${col}7`).formulas=[[`=${sum('K')}/${col}6`]];
  summary.getRange(`${col}8`).values=[[r.metrics.macro_f1]];
  summary.getRange(`${col}9`).formulas=[[`=COUNTIFS('Our Results'!$A$5:$A$${last},${criterion},'Our Results'!$F$5:$F$${last},"ok")/${col}6`]];
  summary.getRange(`${col}10`).values=[[r.metrics.p95_latency_seconds]];
  summary.getRange(`${col}11`).formulas=[[`=${sum('I')}`]];
  summary.getRange(`${col}12`).formulas=[[`=${sum('L')}/${col}6`]];
  summary.getRange(`${col}13`).formulas=[[`=IF(${col}12=1,${col}11/${col}6,"Unknown")`]];
});
summary.getRange('B7:D9').setNumberFormat('0.0%');
summary.getRange('B8:D8').setNumberFormat('0.000');
summary.getRange('B10:D10').setNumberFormat('0.00');
summary.getRange('B11:D11').setNumberFormat('$0.0000');
summary.getRange('B12:D12').setNumberFormat('0%');
summary.getRange('B13:D13').setNumberFormat('$0.0000');
summary.getRange('A16').values=[['Macro F1 and p95 are saved analysis results; other headline metrics calculate from Our Results.']];
summary.getRange('A18').values=[['Unknown costs are excluded from known totals. Conservative reserves are not measured charges.']];
summary.getRange('A20').values=[['Course source tabs are preserved reference material; their supplied scores are not our results.']];
summary.getRange('A22').values=[['Same synthetic diagnosis set: measured improvement does not establish held-out generalization.']];
summary.getRange('A24').values=[[`Budget ceiling: $5. Conservative project exposure: $${data.budget_exposure.toFixed(6)}.`]];
summary.freezePanes.unfreeze();
table(paired,['Comparison','Case','Reviewed label','Before prediction','After prediction','Outcome'],data.paired_rows,[22,19,22,24,24,24]);
paired.getRange('F5:F204').conditionalFormats.add('containsText',{text:'regression',format:{fill:'#FEE2E2',font:{color:'#991B1B'}}});
paired.getRange('H4:L4').values=[['Comparison','Fixed','Regressions','Unchanged correct','Unchanged wrong']];
for(const [i,name] of ['output_limit','prompt'].entries()) {
  paired.getRange(`H${i+5}`).values=[[name]];
  paired.getRange(`I${i+5}:L${i+5}`).formulas=[['fixed','regression','unchanged_correct','unchanged_wrong'].map(outcome=>`=COUNTIFS(A5:A204,H${i+5},F5:F204,"${outcome}")`)];
}
paired.getRange('H4:L6').format.columnWidth=24;
paired.getRange('H4:L4').format={fill:'#243B53',font:{color:'#FFFFFF',bold:true},wrapText:true,rowHeight:32};
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'Our Summary!A4:D13',include:'values,formulas',tableMaxRows:10,tableMaxCols:4,maxChars:4500})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:20},maxChars:1500})).ndjson);
await fs.mkdir(`${root}/reports/workbook_previews`,{recursive:true});
for(let i=0;i<data.source_sheet_count+5;i++){
  const sheet=wb.worksheets.getItemAt(i);
  if(process.env.RENDER_SHEETS && !process.env.RENDER_SHEETS.split(',').includes(sheet.name)) continue;
  const range=sheet.name==='Our Summary'?'A1:D24':sheet.name==='Our Results'?'A1:G8':sheet.name==='Our Reviewed Labels'?'A1:G8':sheet.name==='Our Failure Analysis'?'A1:E8':'A1:F8';
  const png=await wb.render({sheetName:sheet.name,range,scale:1,format:'png'});
  await fs.writeFile(`${root}/reports/workbook_previews/sheet-${i}.png`,new Uint8Array(await png.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(wb)).save(`${root}/reports/customer_support_evaluation.xlsx`);

"use client";

import { useEffect, useState } from "react";
const api = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function InvestigationFeedback({ incidentId }: { incidentId:string }) {
  const [trace, setTrace] = useState<{tool:string;result_summary:string}[]>([]); const [saved, setSaved] = useState(false);
  useEffect(() => { fetch(`${api}/incidents/${incidentId}/trace`).then(r => r.json()).then(setTrace).catch(() => setTrace([])); }, [incidentId]);
  async function submit(action:string) { await fetch(`${api}/incidents/${incidentId}/feedback`, {method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({id:`feedback-${Date.now()}`,incident_id:incidentId,action,note:"Operator review"})}); setSaved(true); }
  return <section className="mt-6 grid gap-5 lg:grid-cols-2"><div className="surface-card p-6"><p className="eyebrow">Why this appeared</p><h2 className="section-title mt-2">Investigation trace</h2>{trace.map(item => <p className="mt-4 border-l-2 border-[var(--accent)] pl-3 text-sm" key={item.tool}><strong className="capitalize">{item.tool.replaceAll("_"," ")}</strong><br/><span className="mt-1 block leading-6 text-muted">{item.result_summary}</span></p>)}</div><div className="surface-card p-6"><p className="eyebrow">Human judgment</p><h2 className="section-title mt-2">Close the review loop</h2><p className="page-copy mt-3 text-sm">Your assessment is recorded for this demo run and reflected in evaluation metrics.</p><div className="mt-5 flex flex-wrap gap-3"><button className="button-primary" onClick={() => submit("confirm")}>Confirm incident</button><button className="button-secondary" onClick={() => submit("false_positive")}>Mark as false positive</button></div>{saved && <p role="status" className="mt-4 text-sm font-medium text-success">Review recorded for this demo run.</p>}</div></section>;
}

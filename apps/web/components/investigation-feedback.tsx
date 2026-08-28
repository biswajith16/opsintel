"use client";

import { useEffect, useState } from "react";
const api = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function InvestigationFeedback({ incidentId }: { incidentId:string }) {
  const [trace, setTrace] = useState<{tool:string;result_summary:string}[]>([]); const [saved, setSaved] = useState(false);
  useEffect(() => { fetch(`${api}/incidents/${incidentId}/trace`).then(r => r.json()).then(setTrace).catch(() => setTrace([])); }, [incidentId]);
  async function submit(action:string) { await fetch(`${api}/incidents/${incidentId}/feedback`, {method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({id:`feedback-${Date.now()}`,incident_id:incidentId,action,note:"Operator review"})}); setSaved(true); }
  return <section className="mt-6 grid gap-6 lg:grid-cols-2"><div className="rounded-lg border border-[var(--border)] bg-surface p-5"><h2 className="text-lg font-semibold">Investigation trace</h2>{trace.map(item => <p className="mt-3 text-sm" key={item.tool}><strong>{item.tool.replaceAll("_"," ")}</strong><br/><span className="text-muted">{item.result_summary}</span></p>)}</div><div className="rounded-lg border border-[var(--border)] bg-surface p-5"><h2 className="text-lg font-semibold">Operator review</h2><p className="mt-2 text-sm text-muted">Record your assessment for future evaluation.</p><div className="mt-4 flex flex-wrap gap-3"><button className="rounded bg-accent px-3 py-2 text-sm font-medium text-white" onClick={() => submit("confirm")}>Confirm incident</button><button className="rounded border border-[var(--border)] px-3 py-2 text-sm font-medium" onClick={() => submit("false_positive")}>Mark false positive</button></div>{saved && <p role="status" className="mt-3 text-sm text-success">Feedback recorded for this demo run.</p>}</div></section>;
}

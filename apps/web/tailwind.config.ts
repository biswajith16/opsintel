import type { Config } from "tailwindcss";
export default { content:["./app/**/*.{ts,tsx}","./components/**/*.{ts,tsx}"], theme:{extend:{colors:{surface:"var(--surface)",canvas:"var(--canvas)",ink:"var(--ink)",muted:"var(--muted)",accent:"var(--accent)",success:"var(--success)",danger:"var(--danger)"}}}, plugins:[] } satisfies Config;

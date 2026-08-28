# UX plan

## Navigation and page responsibilities

| Page | Primary responsibility | Primary action |
| --- | --- | --- |
| Landing | Explain the prototype and enter the demo | Explore operations |
| Operations Overview | Prioritized current operational state | Open investigation |
| Live Operations | Control and observe deterministic event flow | Start / pause / reset |
| Incident Center | Filterable investigation queue | Review incident |
| Incident Detail | Evidence, baseline change, causes, feedback | Confirm / correct / resolve |
| Pattern of Life | Show expected routes/ranges/sequences | Compare period |
| Asset Explorer | Trace one asset across time and zones | Inspect history |
| What-If Lab | Run a bounded counterfactual investigation | Run investigation |
| AI Performance | Show synthetic evaluation and feedback outcomes | Inspect metric definition |
| Architecture | Explain data and reasoning flow | View data contract |
| About Project | Scope, disclosure, limitations | Read methodology |

## Information hierarchy

The persistent shell uses a labeled left navigation and a concise global facility/time context. Screens lead with the decision to make, then supporting evidence—not a wall of KPI cards. An incident detail leads with severity, confidence, affected operation, and recommended review action; then timeline/baseline delta; then graph and competing causes; raw records stay inspectable in a disclosure.

## Interface system decisions

- Calm neutral surfaces, one restrained blue/teal interaction accent, and distinct semantic status colors. Tokens are semantic (`--color-text-secondary`, `--color-status-critical`), not component- or hue-named; status also has text/icon labels.
- Dense professional-tool type scale: readable 16px body where prose occurs; compact 14px UI text at 400+ weight; tabular numerals for changing telemetry; balanced headings and reachable full values for truncated labels.
- Group with whitespace before separators; shared alignment edges; content-led breakpoints; controls stay within mobile safe-area margins and no critical control is clipped at 320px/200% zoom.
- Native controls, visible `:focus-visible` rings, 44px preferred touch targets, named icon buttons, semantic landmarks/one h1, and reduced-motion guards. A keyboard-only operator can complete all primary flows.
- Motion is restrained: fast feedback at 150ms or less, exact-property transitions, and a static state cue. No decorative dashboards, radar, neon, pervasive glass, or chatbot-first navigation.
- Copy is calm, plain, sentence case, and action-led: “Run investigation”, “Review incident”, “Reset demo”. Errors say what failed and how to recover.

## States and responsive behavior

Every data surface designs loading (structured skeleton with stable labels), empty (what belongs here plus one next action), error (plain recovery action and retained filter context), and degraded API state. Tables collapse to labeled records, secondary panels become disclosed sections, and the What-If form becomes one-column on narrow widths. No state relies on color or animation alone.

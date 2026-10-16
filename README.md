# yasaswinpalukuri.github.io

Personal portfolio for **Yasaswin Palukuri** — Full-Stack AI & Data Engineer, Toronto.

**Live:** https://yasaswinpalukuri.github.io

Built to be read in about sixty seconds by someone who screens a lot of resumes, and to hold up
when an engineer digs deeper. No framework, no build step, no dependencies beyond Google Fonts —
every page is a single self-contained HTML file.

---

## Pages

| Page | What it is |
|------|------------|
| [`index.html`](index.html) | The portfolio: projects, skills, experience, credentials, contact |
| [`groot.html`](groot.html) | Case study of Groot OS — architecture, hybrid RAG, constraint engineering, evals |
| [`live.html`](live.html) | Live telemetry from the machine Groot runs on, polled from a status endpoint |
| [`resume.html`](resume.html) | Resume with an inline PDF preview and download links |

## Stack

Plain HTML, CSS and vanilla JavaScript. Dark GitHub-style palette (`#0D1117` base, `#58A6FF`
accent), Inter for prose and JetBrains Mono for anything machine-flavoured.

Everything that moves is CSS or a single `IntersectionObserver`: scroll reveals, the typing
rotation in the hero, animated evaluation bars, and the nav highlighting the section you are in.
Motion is limited to `transform` and `opacity` so nothing reflows, and all of it is disabled
under `prefers-reduced-motion`.

Responsive at 900 / 768 / 640 / 480px, with a hamburger nav below 768.

## Resume

The one-page PDF is generated from the structured resume data rather than hand-edited:

```bash
python3 build_resume_pdf.py path/to/master_resume.json Yasaswin_Palukuri_Resume.pdf
```

`build_resume_pdf.py` (reportlab) renders summary, skills, experience, projects, additional
experience, and education + certifications, and keeps live links intact in the PDF. Both the
PDF and a `.docx` copy are served from `resume.html`.

## Contact form

The contact section posts to [Formspree](https://formspree.io) over `fetch`, so the page never
navigates away. It includes a honeypot field for bots, disables the submit button while sending,
and reports success or failure inline. No email address or phone number is published on the page.

## Live uptime

Three uptime figures in `index.html` — the hero terminal, the Groot stats grid, and the footer —
are kept current by a daily job on the M720Q that bumps them and pushes. That is what the
`chore: update Groot uptime to NNNNh` commits are.

`live.html` is the real-time version: it polls a status endpoint on the machine itself and falls
back to the last known snapshot, clearly labelled as such, whenever that endpoint is unreachable.

## Running locally

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

A plain static server is enough. Open the files directly over `file://` if you prefer, though
the root-relative favicon paths and the resume preview behave better over HTTP.

---

<sub>Running on a Lenovo M720Q in Toronto, Canada.</sub>

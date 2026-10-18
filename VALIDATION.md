# Requirements and validation record

Validated on 17 October 2026. Both Moodle deadlines are Sunday, 18 October 2026, 11:59 PM.

## C3

| Requirement | Evidence and status |
| --- | --- |
| Business identity, mission, services, team, distinctive offer | Included in both business documents |
| PDF and business summary | Included; PDF rendered and visually inspected; `summary.txt` alias included |
| Separate persona and instructions | Clearly labeled notebook/code sections |
| Three-way router | General, lead, and feedback observed in real runs |
| Two model-requested tools and schemas | Actual action/observation traces and local receipts saved |
| Both documents used | PDF-only 24-hour policy answered correctly |
| Gemini and short-term memory | Final six-turn notebook demo completed; name and needs retained until email arrived |
| Gradio ChatInterface | Desktop browser walkthrough and screenshots captured |
| Successful notebook execution | Fresh kernel passed, excluding package reinstallation and public launch |
| Repository and functionality video | Video completed; remote repository publication awaits GitHub sign-in |
| Optional reflection | Actual draft and reviewed reply saved; the correct draft remained unchanged |
| Optional Hugging Face deployment | Not performed or claimed |

## C4

| Requirement | Evidence and status |
| --- | --- |
| Goal, audience, tools, constraints | Notebook business/use-case section |
| One named framework | LangGraph 1.2.16 |
| Manual ReAct loop | Own state, model/action/observation nodes, conditional edges, parsing, limits; no prebuilt executor |
| At least two persona/role/configuration combinations | Sheriff, Patch, Professor Pip; all tested |
| Explained-decision comparison | Same six cases, with/without a brief visible rationale |
| Zero-shot versus few-shot | Same cases; ablation removed worked demonstrations |
| System versus in-message instructions | Same operational instructions, different placement |
| Configuration variations | Separate temperature, top-p, and top-k ablations |
| Logged comparison | 54 completed live turns, 80 model steps, 26 successful tool actions; raw rows retained |
| Clear instructions and example | Dedicated rules, explicit input/output format, three worked examples in production |
| Reflection | All five questions answered in notebook and `REFLECTION.md` using actual evidence |
| Final contact-data and memory regression | Two live turns passed on the final C4 implementation |
| Fresh notebook execution | Passed, excluding dependency reinstallation and public launch |

## Evidence limits and development history

The Gemini 3.5 Flash-Lite matrix had 54 completed turns; 53 passed all narrow automatic checks. The zero-shot unknown-certification case omitted the feedback call and inferred that an unlisted service did not exist. This failure is retained and discussed. Word/tool checks do not prove complete correctness or naturalness.

The matrix predates final browser-driven hardening. Its prompt definitions are in `C4/results/matrix_prompt_v1.json`. Later changes added actual-customer provenance validation, aligned visible/model history, selected Patch as default, and clarified unknown-fact wording. Final notebook and regression evidence checks these changes separately.

`verification.json` records 86 passing offline integration checks with scripted SDK responses. These verify tool validation, storage, opaque-signature preservation, loop limits, truncation, reflection, memory, and UI reset paths. They are not Gemini quality trials.

The interface was revised after review: an off-white background, serif heading, green controls, a service list with aligned prices, and a separate chat panel. Wording stays brief; settings and activity remain collapsed. App/browser and notebook titles are just “Byte Club Studio.” The 86 checks passed again, and the browser demo was recaptured against the updated apps, including a real request sent with the Send button. These edits do not change the model prompts, tools, or experiment results.

The earlier Gemini 3.8 pilot and quota failure are separate. The 71-second captioned video uses actual browser screenshots and synthetic contacts, with pauses condensed and persona changes. It is not an uninterrupted screen recording. A mobile viewport override could not be verified in this browser, so no mobile-test result is claimed.

The export excludes `.env`, runtime logs, caches, and bytecode. A scan for the configured key found no credential in candidate submission files. No Moodle submission was made; Ismail handles final Moodle submission as agreed.

## Colab copies

- [C3 business notebook](https://colab.research.google.com/drive/1BaJ_CW_EFNjf66WRa41ZVTdqAQzshhbx)
- [C4 ReAct notebook](https://colab.research.google.com/drive/18sxUWaPAp_phlh2PDL66JRn3Xn7nYq3H)
- [Drive folder](https://drive.google.com/drive/folders/1LAQsfbPgM6i18xrXqfcr3fSdnjE0enJq)

Uploaded metadata was read back successfully. Notebook execution was verified in local Jupyter; Google-hosted runtime execution is not claimed.

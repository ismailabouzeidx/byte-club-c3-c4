# C4 reflection - Byte Club Studio

Ismail Abou Zeid

## Evidence and scope

The main experiment used Gemini 3.5 Flash-Lite on 17 October 2026. Nine setups each received the same six synthetic cases with empty conversation history: 54 completed turns. Fifty-three passed all four narrow automatic checks. These checks cover completion, router label, expected successful tool use, and selected factual terms. They are not a comprehensive quality score.

The earlier Gemini 3.8 pilot is retained separately in `results/pilot_gemini38.jsonl`: eleven successful turns followed by a provider error. A diagnostic response identified its daily free-tier request limit. I did not pool those pilot results with the main model comparison.

The main matrix used the prompt definitions recorded in `results/matrix_prompt_v1.json`. Later browser testing exposed example-contact leakage and led to additional prompt clarification and a deterministic contact-provenance check. Final regression evidence is separate from the original comparison; the development history is not presented as one unchanged experiment.

| Setup | Cases passing narrow checks | Mean seconds per turn | Total tokens reported |
| --- | --- | --- | --- |
| Patch baseline | 6/6 | 4.14 | 16,937 |
| Explained decision | 6/6 | 3.89 | 17,137 |
| Zero-shot ablation | 5/6 | 4.65 | 13,009 |
| Instructions in message | 6/6 | 5.90 | 17,009 |
| Temperature 0.80 | 6/6 | 3.18 | 16,903 |
| Top-p 0.95 | 6/6 | 3.25 | 16,905 |
| Top-k 40 | 6/6 | 2.45 | 16,924 |
| Sheriff preset | 6/6 | 3.31 | 17,046 |
| Professor Pip preset | 6/6 | 4.73 | 17,400 |

Times include model/tool work but exclude the pause between cases. Token counts use Gemini's reported total and may include internal processing; they are not just visible answer lengths. Each condition had one repeat. Request order, provider load, and sampling randomness confound timing, so I do not infer that a parameter change caused a speed improvement.

## 1. Which persona gave the most helpful or natural results?

Patch was the most useful default for factual business scoping. Its price answer was a single precise sentence giving USD 25 and 60 minutes. It asked directly for the missing email and did not add much unrelated text. This fits a small business help desk where accurate terms and a clear next step matter.

Sheriff sounded most natural for welcoming a lead: its greeting and occasional frontier expression made intake feel distinctive, and its completed-lead reply clearly described the local receipt. Professor Pip was better suited to beginners who want explanations; its bicycle analogy made guided learning approachable. Pip was also much longer, so I would not use it as the default for a simple price question.

The automatic scores were 6/6 for all three persona packages. The preference above is my qualitative reading of the saved replies, not a measured superiority claim. One Sheriff certification answer added a broader implication about credentials than the documents justified; the automatic checks did not catch that nuance. Passing a tool check does not guarantee perfect wording.

## 2. Which prompt and configuration combination performed best for your use case?

I prefer Patch's production preset: system-level operational instructions, worked examples, temperature 0.15, top-p 0.75, top-k 20, and 2,048 maximum output tokens. It met every baseline check and kept answers short. The other sampling settings also achieved 6/6, so this small study does not establish an optimal numerical configuration.

The clearest observed difference was the unknown-certification case. With examples, the baseline acknowledged that certification was not listed and called `record_feedback`. Without examples, the model asserted that the company did not offer certifications and made no feedback call. That failed the required tool check and overstated what absence from the documents means. The zero-shot setup used fewer reported tokens, but that saving came with a concrete failure in this case.

The explained-decision setup added a short factual justification without changing the six case outcomes. For example, it separated the published tutoring rate from the guided-learning scope. I would enable it for a recommendation and keep direct answers for simple factual questions. This prompt comparison measures a visible explanation request; it does not inspect private reasoning or prove that the direct condition did no internal reasoning.

## 3. How well did your agent reason and use tools?

I assessed observable decisions: answering published facts directly, requesting a tool for an authorized lead or feedback, using the returned receipt, and asking for missing information. The recorded matrix completed all 54 turns in 80 model steps, with 26 successful tool actions. Fifty-three turns passed all narrow checks. The zero-shot unknown-certification case was the main failure: it treated missing information as a negative fact and omitted the feedback tool. The trace supports an assessment of these decisions and tool use; it does not expose private reasoning or prove general reasoning ability.

In the successful cases, the model requested a declared function, my action node validated and executed it, the observation returned to Gemini, and the next model step produced the final customer reply. Lead records contained the supplied name, email, and notes. Feedback and unknown-question cases produced real local records and receipt identifiers.

LangGraph controlled the edges, while my own functions handled action detection, argument validation, execution, observations, and final parsing. A five-model-step limit and a separate graph recursion limit bounded failure. I used no prebuilt executor. Local integration checks also covered invalid names/arguments, duplicate writes, incomplete output, history trimming, and reflection.

The most important discovered failure happened outside the original six-case matrix: I reused the example customer's name but omitted the email. The model copied the example email and attempted to record a complete lead. Prompt rules alone were insufficient. The final implementation uses Patch as the default, explicitly prohibits inferring that an unlisted service does not exist, and now verifies that both name and email occur in the actual customer's messages before writing a record, and returns a failed observation otherwise. Synthetic SDK regression tests force this bad action to ensure the guard works even when the model ignores the instruction.

## 4. Did your instructions block change the agent's behavior in a noticeable way? How?

Moving the same instructions into the user message still produced 6/6 narrow checks in this test set, so I saw no measurable case-score benefit from location alone. I kept the production rules in the system prompt because that makes their role clearer and avoids mixing application rules with the customer message. This experiment did not test adversarial resistance.

The worked-example ablation did change unknown-question handling as described above. I cannot attribute that result to every rule in the dedicated instructions block, because I did not run a complete removal-of-instructions experiment. Explicit input/output rules and action receipts make the intended behavior auditable, while code validates contact provenance and tool arguments where relying only on wording proved inadequate.

## 5. What were the biggest challenges in implementation?

1. Keeping persona style separate from factual and action rules. A friendly voice must not invent availability or promise a callback from a local-only demo.
2. Making tool calls real: the model requests actions, but my code must validate, execute, and return results itself.
3. Preserving Gemini's opaque continuation signatures while excluding private thought text from visible traces.
4. Keeping the manual graph understandable and bounded, without delegating its execution to a prebuilt agent.
5. Matching visible and model history when Gradio users clear, undo, retry, or switch personas.
6. Managing API quotas and keeping failed attempts and model changes separate from successful evidence.

This remains a prototype assistant with short memory, a heuristic router, generated replies, and local logging. Production use would require authentication, retention controls, customer consent handling, a durable data store, more varied evaluations, and an actual business workflow for following up on contact requests.

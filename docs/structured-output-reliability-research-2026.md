# Structured Output Reliability Research 2026

**Summary**

หน้านี้สรุปข้อมูลที่ค้นจากเอกสารทางการและงานวิจัยล่าสุด ณ วันที่ 2026-05-20 เพื่อช่วยตัดสินใจรอบถัดไป หลัง smoke test ของ `openai-compatible` / fine-tuned path ยังตอบ JSON/schema ได้เพียง 1/5 samples แม้ปรับ prompt contract, OpenAI SDK path และ `responses_parse` แล้ว

ข้อสรุปหลักคือปัญหาปัจจุบันไม่ควรถูกแก้ด้วย prompt หรือ Pydantic validation อย่างเดียวอีกต่อไป เพราะ path ที่มีอยู่ตอนนี้ยังดูเหมือนเป็น validate-after-generation ไม่ใช่ server-side constrained decoding แบบ token masking ดังนั้นงานถัดไปควรพิสูจน์ runtime enforcement ก่อน retrain หรือ fixed-split comparison

**Sources**

- `reports/structured-output/smoke/openai-compatible-eval-model-v2-output-v1.json` สำหรับ smoke metric ล่าสุด: JSON/schema success `0.2`, invalid output `4/5`, evidence/severity match `0.0` (source: reports/structured-output/smoke/openai-compatible-eval-model-v2-output-v1.json)
- `docs/output-contract-hardening.md` สำหรับสิ่งที่แก้ไปแล้วใน prompt `triage-json-v2`, OpenAI SDK adapter, schema sanitizer และ smoke split (source: docs/output-contract-hardening.md)
- `docs/model-output/v2-lfm2-350m-security-triage-responses-parse.md` สำหรับ v2 failure mode: `responses_parse` ยังไม่บังคับ generation ให้เป็น JSON object ล้วน (source: docs/model-output/v2-lfm2-350m-security-triage-responses-parse.md)
- OpenAI Structured Outputs docs สำหรับ `json_schema`, `text.format`, JSON mode limitations, schema tips และ Pydantic/Zod helper path: https://platform.openai.com/docs/guides/structured-outputs
- OpenAI Structured Outputs announcement สำหรับเหตุผลว่า strict structured output ต้องใช้ constrained decoding ไม่ใช่ prompt-only: https://openai.com/index/introducing-structured-outputs-in-the-api/
- vLLM Structured Outputs docs สำหรับ `structured_outputs` API, JSON schema, regex, grammar และ XGrammar/guidance backend: https://docs.vllm.ai/en/v0.21.0/features/structured_outputs/
- SGLang Structured Outputs docs สำหรับ JSON schema, regex, EBNF และ XGrammar default backend: https://docs.sglang.io/docs/advanced_features/structured_outputs
- Ollama Structured Outputs docs สำหรับ local `format` schema path และข้อจำกัดว่า Ollama Cloud ยังไม่รองรับ structured outputs: https://docs.ollama.com/capabilities/structured-outputs
- LM Studio Structured Output docs สำหรับ OpenAI-compatible `response_format` schema และ warning ว่าไม่ใช่ทุก model โดยเฉพาะต่ำกว่า 7B จะทำ structured output ได้ดี: https://lmstudio.ai/docs/developer/openai-compat/structured-output
- Hugging Face TGI Guidance docs สำหรับ grammar parameter, Pydantic/JSON Schema/regex และ grammar compilation cache: https://huggingface.co/docs/text-generation-inference/en/guidance
- Outlines docs สำหรับ structured generation ระหว่าง generation ไม่ใช่ post-processing: https://dottxt-ai.github.io/outlines/latest/
- LM Format Enforcer README สำหรับ token filtering ต่อ timestep, vLLM integration และ JSON Schema support: https://github.com/noamgat/lm-format-enforcer
- LangChain Structured Output docs สำหรับ provider-native strategy, tool-calling strategy และ validation retry feedback: https://docs.langchain.com/oss/python/langchain/structured-output
- Instructor Retry Mechanisms docs สำหรับ validation-error feedback loop: https://python.useinstructor.com/learning/validation/retry_mechanisms/
- Pydantic AI Output docs สำหรับ tool/native/prompted output modes และ `ModelRetry`: https://pydantic.dev/docs/ai/core-concepts/output/
- JSONSchemaBench สำหรับ benchmark constrained decoding ด้าน efficiency, coverage และ quality: https://arxiv.org/abs/2501.10868
- XGrammar-2 สำหรับ dynamic structured generation และ near-zero overhead claim ใน serving systems: https://arxiv.org/abs/2601.04426
- Draft-Conditioned Constrained Decoding สำหรับข้อสังเกตว่า constrained decoding อาจทำให้ semantic quality แย่ลงถ้า hard constraints บิด trajectory: https://arxiv.org/abs/2603.03305
- Schema Key Wording as an Instruction Channel สำหรับผลปี 2026 ว่า wording ของ schema keys เป็น instruction channel ได้: https://arxiv.org/abs/2604.14862
- When Correct Isn't Usable สำหรับ format reliability gap ใน small language models และ markdown-fence failure: https://arxiv.org/abs/2605.02363
- TruncProof สำหรับ guardrail เรื่อง JSON valid ภายใต้ token-length constraints: https://arxiv.org/abs/2605.13076

**Last updated**

2026-05-20

## Current Diagnosis

สถานะ repo ล่าสุดคือ smoke output-contract split 5 records ยังผ่าน JSON parse และ schema เพียง 1 record โดย `invalid_output_count=4`, `label_accuracy=0.2`, `severity_accuracy=0.0`, `evidence_partial_match=0.0` (source: reports/structured-output/smoke/openai-compatible-eval-model-v2-output-v1.json)

เราปรับไปแล้วหลายชั้น: prompt `triage-json-v2`, OpenAI SDK adapter, Pydantic `responses_parse`, schema sanitizer, deterministic smoke split และ direct probe แต่ผลยังไม่ดีขึ้น จึงน่าจะไม่ใช่แค่ LangChain wrapper หรือ prompt wording ชั้นบนสุด (source: docs/output-contract-hardening.md, source: docs/model-output/v2-lfm2-350m-security-triage-responses-parse.md)

ความหมายเชิงวิศวกรรมคือ `responses_parse` ใน endpoint ปัจจุบันช่วยจับ failure ได้ชัดขึ้น แต่ยังไม่ได้พิสูจน์ว่า backend บังคับ token-level constrained decoding จริง หาก model ยังสร้าง markdown fence ได้ 4/5 ครั้ง แปลว่าตัว sampler ยังปล่อย token นอก JSON object ได้อยู่

## Key Findings

| Finding | Implication for this repo |
| --- | --- |
| JSON mode ไม่พอ เพราะรับประกันแค่ JSON parse ได้ ไม่รับประกัน schema; OpenAI docs แนะนำ Structured Outputs หรือ validation/retry ถ้า structured outputs ใช้ไม่ได้ | `json_object` หรือ prompt-only ไม่ควรถูกนับเป็น final fix |
| Strict structured outputs ที่เชื่อถือได้ต้องเกิดที่ inference engine โดย mask invalid tokens ตาม schema/grammar ระหว่าง sampling | ต้องตรวจ backend serving path ไม่ใช่แก้ evaluator อย่างเดียว |
| vLLM รุ่นปัจจุบันใช้ `structured_outputs` แทน field เก่าอย่าง `guided_json`; docs ระบุว่า old guided fields ถูกถอดตั้งแต่ v0.12.0 | probe ของเราควรแยก version และไม่สรุปจาก `guided_json` ถ้า server เป็น vLLM รุ่นใหม่ |
| SGLang, vLLM, TGI, Ollama และ LM Studio ต่างมี structured-output path แต่ syntax, backend และ model support ไม่เท่ากัน | ต้องทำ backend capability matrix แบบ empirical ด้วย smoke split เดียวกัน |
| LM Studio เตือนว่าไม่ใช่ทุก model ทำ structured output ได้ โดยเฉพาะ model ต่ำกว่า 7B | LFM2-350M อาจเล็กเกินไปสำหรับ schema-following แบบไม่มี constrained decoding |
| งานวิจัยปี 2026 ชี้ว่า constrained decoding แก้ syntax ได้ แต่บางครั้งทำให้ semantic accuracy แย่ลง | หลัง JSON/schema ผ่าน ต้องวัด label/severity/evidence แยก ไม่ใช่จบที่ parse ผ่าน |
| Schema key names/descriptions มีผลต่อ generation quality ภายใต้ constrained decoding | schema/prompt ของเราอาจต้องออกแบบ field descriptions และ key wording เพื่อช่วย semantics แต่ทำหลัง runtime enforce ได้แล้ว |
| Validation+retry ช่วยได้ใน production แต่เป็น repair loop ไม่ใช่ guarantee | ใช้เป็น fallback/debug ได้ แต่ไม่ควรซ่อน `invalid_output_count` ใน evaluator หลัก |

## Practical Options

### Option A: Keep Current Endpoint And Add More Prompting

ความพยายามนี้ทำไปแล้วบางส่วน และ smoke ยัง 1/5 จึงไม่ควรเป็น path หลักต่อ ยกเว้นจะใช้เป็น experiment สั้น ๆ เพื่อพิสูจน์งานวิจัยแบบ prompt optimizer เช่น AloLab จาก paper `When Correct Isn't Usable`

สถานะ: ไม่แนะนำเป็น final Day 6 fix

เหตุผล: prompt-only ไม่มี token-level guarantee และตอนนี้ markdown fence ยังหลุดมาชัดเจน

### Option B: Switch Or Reconfigure Runtime To Real Constrained Decoding

นี่คือ path ที่ควรทำก่อน retrain:

- ถ้าใช้ vLLM ให้ยืนยัน version และใช้ `extra_body={"structured_outputs": {"json": schema}}` หรือ `response_format={"type":"json_schema", ...}` ตาม docs รุ่นนั้น ไม่พึ่ง `guided_json` เป็นหลัก
- ถ้าใช้ SGLang ให้ลอง `json_schema` ด้วย XGrammar default backend
- ถ้าใช้ TGI ให้ลอง grammar JSON schema path
- ถ้าใช้ LM Studio/Ollama ให้ลอง schema-native mode เพื่อดูว่า artifact เดียวกันดีขึ้นไหม แต่ต้องแยกเป็น runtime comparison ไม่ใช่ model-quality comparison

สถานะ: แนะนำเป็น next implementation path

เหตุผล: ถ้ารัน constrained decoding จริง model ไม่ควรตอบ markdown fence ได้เลย

### Option C: Add Validation-Retry Loop

ใช้ Pydantic/JSON Schema validation error ส่งกลับไปให้ model retry ได้ เช่น Instructor, LangChain ToolStrategy หรือ Pydantic AI `ModelRetry`

สถานะ: ใช้เป็น fallback หลังมี capability matrix แล้ว

ข้อดี: แก้ง่ายกว่าย้าย runtime และช่วย field completeness

ข้อเสีย: เพิ่ม latency, อาจยังไม่แก้ semantic drift และไม่ควรถูกใช้กลบ metric `invalid_output_count`

### Option D: Retrain V3 With Output-Only Discipline

ควรทำหลังพิสูจน์ runtime แล้วเท่านั้น ยกเว้นต้องการทดลอง model behavior แบบแยกต่างหาก

สิ่งที่ v3 training ควรเปลี่ยน:

- render training examples ด้วย prompt/runtime contract เดียวกับ evaluator
- assistant output ต้องเป็น raw JSON object เท่านั้น ไม่มี markdown fence ทุกตัวอย่าง
- เพิ่ม examples ที่เน้น field completeness เช่น `recommended_action` ห้ามหาย
- เพิ่ม schema/key descriptions ที่ช่วย semantics เช่น evidence ต้องเป็น substring จาก input
- เพิ่ม hard cases ของ 5 labels ที่ v2 สับกัน เช่น SQLi vs SSH brute force, traversal vs failed login, port scan vs normal

สถานะ: ทำหลัง runtime decision หรือทำเป็น parallel experiment ขนาดเล็ก

ข้อควรระวัง: retrain ไม่ควรถูกใช้แทน constrained decoding เพราะถ้า sampler ยัง unconstrained ก็ยังมีโอกาสหลุด prose/markdown

### Option E: Use A Larger Or More Tool/JSON-Capable Model Candidate

เก็บ LFM2-350M เป็น resource-constrained POC candidate ได้ แต่ควรมี diagnostic run กับ model ที่ใหญ่กว่าและขึ้นชื่อเรื่อง structured output เช่น 7B/8B instruct family เพื่อแยกว่า failure มาจาก runtime หรือ model capacity

สถานะ: แนะนำเป็น diagnostic ไม่ใช่เปลี่ยน project goal ทันที

เหตุผล: ถ้า 7B + constrained runtime ผ่าน 5/5 แต่ LFM2-350M ยัง fail semantics แปลว่าปัญหาหลังจากนั้นคือ model capacity/training data

## Decision Matrix

| Path | Effort | Expected contract gain | Semantic risk | Recommended use |
| --- | ---: | ---: | ---: | --- |
| More prompt wording only | Low | Low | Medium | Stop after one controlled prompt-optimizer experiment |
| Pydantic validation + retry | Medium | Medium | Medium | Fallback path; keep metrics transparent |
| vLLM `structured_outputs` | Medium | High | Medium | Primary self-hosted OpenAI-compatible candidate |
| SGLang XGrammar | Medium | High | Medium | Strong alternate runtime candidate |
| TGI grammar JSON | Medium | High | Medium | Useful if HF serving path is easier |
| LM Studio/Ollama schema mode | Low | Medium to High | Medium | Fast local diagnostic, model/support dependent |
| Retrain v3 only | Medium to High | Uncertain | Medium | Do after runtime enforcement proof |
| Larger model diagnostic | Medium | Medium to High | Lower | Distinguish capacity issue from runtime issue |

## Recommended Next Plan

1. Freeze `data/splits/test.jsonl`; do not run final fixed-split comparison while smoke contract is still 1/5 (source: docs/Day6.md)
2. Create mode-specific reports so results stop overwriting `reports/structured-output/smoke/openai-compatible-eval-model-v2-output-v1.json`, for example `reports/structured-output/smoke/openai-compatible-vllm-structured-outputs-smoke.json`
3. Add or extend the direct probe to include an adversarial format prompt that asks for markdown fence; a true constrained decoder should still return only the JSON object
4. Identify the actual serving backend, version, launch command, model alias, response model, and whether it supports token-level schema constraints
5. Test vLLM current `structured_outputs` syntax first if the backend is vLLM; otherwise test SGLang XGrammar as the cleanest constrained decoding alternative
6. Run the 5-sample smoke split and require `json_parse_success_rate=1.0`, `schema_success_rate=1.0`, `invalid_output_count=0` before any fixed split run
7. After contract is stable, run a 20-25 sample mini semantic eval to inspect label/severity/evidence quality before spending endpoint time on the 75-sample test split
8. If contract passes but semantics remain poor, prepare v3 training data with output-only JSON discipline and label-confusion examples
9. If LFM2-350M remains weak even with constrained runtime, run a diagnostic model-capacity comparison before changing the POC model strategy

แผนลงมือทำจากรายการนี้ถูกแยกไว้ที่ [[structured-output-fix-plan]] เพื่อให้ใช้เป็น checklist, phase gate และ deliverable list ได้โดยไม่ต้องไล่ตีความจาก research note นี้ใหม่

## What We Still Need

- Exact backend name and version behind the current OpenAI-compatible endpoint
- Server launch command or UI settings used to load `unsloth_LFM2-350M_1779162226`
- Confirmation whether LoRA serving path supports server-side constrained decoding or only client-side parsing
- Mode-specific raw outputs for all 5 smoke examples, not just aggregate metrics
- A backend capability table covering `responses_parse`, `json_schema`, `structured_outputs`, `guided_json`, `json_object`, and any native local schema mode
- A clear pass/fail gate for smoke before moving to fixed split
- A decision on whether LFM2-350M remains the first promoted candidate or becomes only the resource-constrained baseline after a larger-model diagnostic

## Do Not Do Yet

- Do not relax evaluator strictness to extract JSON from markdown fences in the main metric path
- Do not run `data/splits/test.jsonl` as final comparison while smoke is 1/5
- Do not broaden labels beyond the current five-label taxonomy
- Do not claim model readiness from one schema-valid smoke sample
- Do not merge/export GGUF as the evaluation artifact until output contract and semantic quality are separately measured

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-20 | Treat current 1/5 smoke as runtime enforcement failure first, not model-quality failure only | `responses_parse` validates after generation, while 4/5 outputs can still be markdown-fenced or invalid | Next work should prove real constrained decoding before retrain or fixed split |
| 2026-05-20 | Make vLLM `structured_outputs` or SGLang XGrammar the next primary candidate paths | Current internet docs point to token-level JSON schema/grammar constraints as the reliable fix for broken JSON | Day 6 should shift from prompt hardening to runtime capability testing |
| 2026-05-20 | Keep validation/retry as fallback, not evaluator workaround | Retry loops can improve valid output rate but hide the root problem if used to overwrite invalid metrics | Reports should preserve invalid counts and retry counts separately |

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-20 | Codex | Researched 2026 structured-output reliability approaches and mapped them to the repo's 1/5 smoke failure | `docs/structured-output-reliability-research-2026.md` | Done |
| 2026-05-20 | Codex | Linked the implementation fix plan derived from this research note | `docs/structured-output-fix-plan.md` | Done |

## Related pages

- [[output-contract-hardening]]
- [[structured-output-fix-plan]]
- [[model-output/v2-lfm2-350m-security-triage-responses-parse]]
- [[Day6]]
- [[fine-tuning-notes]]
- [[evaluation-metrics-rationale]]
- [[triage-output-schema]]

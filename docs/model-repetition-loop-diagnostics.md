# Model Repetition Loop Diagnostics

**Summary**

บันทึกนี้อธิบายสาเหตุที่โมเดลอาจวน token หรือ phrase ซ้ำ ๆ ระหว่าง inference และให้ checklist สำหรับแยกปัญหาในโปรเจกต์ `AI Security Log Triage Assistant`

**Sources**

- `AGENTS.md` สำหรับ mission, output schema, label scope และข้อกำหนดว่า evaluation สำคัญกว่าความสวยงาม (source: AGENTS.md)
- `docs/poc-plan.md` สำหรับ POC scope, fixed test split discipline และ metric เป้าหมาย (source: docs/poc-plan.md)
- `docs/output-structure-fix/phase-5-mini-semantic-eval.md` สำหรับอาการ Phase 5 ที่มี `APITimeoutError` บน port-scan samples และ prediction drift (source: docs/output-structure-fix/phase-5-mini-semantic-eval.md)
- Hugging Face text generation guide สำหรับ `repetition_penalty`, `eos_token_id`, `max_new_tokens` และ decoding controls: https://huggingface.co/docs/transformers/llm_tutorial
- Hugging Face Transformers generation config สำหรับ `repetition_penalty`, `no_repeat_ngram_size`, `temperature`, `top_p`, `top_k`, `eos_token_id` และ `renormalize_logits`: https://huggingface.co/docs/transformers/main_classes/text_generation
- Hugging Face TRL SFTTrainer docs สำหรับคำเตือนเรื่องการ align EOS token กับ chat template เพื่อให้ response terminate ถูกต้อง: https://huggingface.co/docs/trl/main/sft_trainer
- Hugging Face chat templating docs สำหรับ chat/control token consistency ระหว่าง fine-tune และ inference: https://huggingface.co/docs/transformers/v4.41.2/chat_templating
- vLLM sampling params สำหรับ `temperature`, `top_p`, `top_k`, `repetition_penalty`, `stop`, `stop_token_ids`, `ignore_eos` และ `structured_outputs`: https://docs.vllm.ai/en/latest/api/vllm/sampling_params/
- OpenAI Structured Outputs blog สำหรับ constrained decoding และ valid-token filtering ระหว่าง generate: https://openai.com/index/introducing-structured-outputs-in-the-api/
- OpenAI structured outputs guide สำหรับความต่างระหว่าง JSON mode และ schema-constrained output รวมถึง warning เรื่อง unending JSON/whitespace stream ถ้า instruction ไม่ชัด: https://platform.openai.com/docs/guides/structured-outputs
- Holtzman et al., "The Curious Case of Neural Text Degeneration" สำหรับ evidence ว่า maximization-based decoding เช่น beam search/greedy decoding ทำให้ repetitive loops ได้: https://arxiv.org/abs/1904.09751

**Last updated**

2026-05-20

## Why This Matters

ในโปรเจกต์นี้ token loop ไม่ใช่แค่ปัญหา UX เพราะ evaluator จะนับเป็น latency spike, timeout, invalid output หรือ schema failure ได้โดยตรง (source: AGENTS.md, docs/poc-plan.md)

Phase 5 พบ `APITimeoutError` 3 ตัวบน `port_scan_or_recon` samples ภายใต้ vLLM `structured_outputs` และยังมี semantic drift ไปทาง `failed_login_bruteforce` สูงมาก จึงควรแยกว่า timeout มาจาก generation loop, constrained decoding, stop token, runtime setting, training format หรือ model capacity ก่อนแตะ fixed `test.jsonl` (source: docs/output-structure-fix/phase-5-mini-semantic-eval.md)

## Common Causes

| Cause | What it looks like | Why it happens | First check |
| --- | --- | --- | --- |
| Decoding degeneration | คำหรือ token เดิมวนซ้ำจนชน limit | Greedy/beam decoding เลือก token ความน่าจะเป็นสูงสุดซ้ำ ๆ แล้วติด loop | เทียบ `temperature=0` กับ sampling แบบ `temperature>0`, `top_p`, `top_k` |
| Missing repetition controls | phrase เดิมกลับมาซ้ำหลายรอบ | ไม่มี penalty ต่อ token หรือ n-gram ที่ออกไปแล้ว | ลอง `repetition_penalty > 1.0` หรือ `no_repeat_ngram_size` |
| EOS หรือ stop token ผิด | output ถูกต้องช่วงแรกแต่ไม่หยุด | inference ไม่รู้ token ที่ควร terminate หรือ config ใช้ EOS คนละตัวกับ training | ตรวจ `eos_token_id`, `stop_token_ids`, chat template และ special tokens |
| Chat template mismatch | model ต่อบทสนทนาเองหรือ generate role tag แปลก ๆ | format ตอน train ไม่เหมือน format ตอน inference | ใช้ `tokenizer.apply_chat_template` path เดียวกันตอน train/infer |
| Fine-tuning data ไม่มี end marker | answer จบแล้วต่อข้อความอื่นเอง | model ไม่ได้เรียนรู้ว่าท้าย assistant answer ต้องมี EOS/EOT | ตรวจ rendered training sample ว่ามี EOS/EOT หลัง assistant JSON |
| `pad_token` กับ `eos_token` ใช้ผิด | fine-tuned model ไม่ generate EOS | loss masking อาจทำให้ EOS ถูกมองเป็น padding และไม่ถูกเรียนรู้ | ตรวจ tokenizer config และ label masking |
| Structured output ทางตัน | JSON ยัง valid แต่ generate ยาวหรือ timeout | constrained decoder บังคับเฉพาะ token ที่ valid ตาม schema ถ้า schema/prompt เปิดทางให้ string/array ยาวมากก็อาจไม่หยุดง่าย | จำกัด output length, schema length, stop condition และเทียบ mode ไม่บังคับ schema |
| Prompt/schema conflict | model พยายามทำตาม instruction แต่ token ที่ schema อนุญาตไม่พอ | prompt บอกสิ่งหนึ่ง แต่ JSON schema บังคับอีกสิ่งหนึ่ง | ลด instruction ที่ขัดกัน และเขียน schema description ให้ตรง task |
| Runtime/serving issue | loop เกิดเฉพาะ backend หรือเฉพาะ batch/concurrency | engine, tokenizer, stop handling, KV cache, guided decoding หรือ quantization path ทำงานต่างกัน | เทียบ vLLM กับ Transformers/Unsloth Studio และรัน sample เดียวแบบไม่ batch |
| Quantization/numerical issue | output เพี้ยนหรือซ้ำมากกว่า full precision | low-bit quantization อาจเปลี่ยน logits หรือ attention behavior | เทียบ BF16/FP16 กับ quantized checkpoint |
| Context truncation | model ลืม instruction หรือ schema แล้วต่อมั่ว | prompt ยาวจน context สำคัญถูก truncate | log token counts และลด prompt/schema |

## Project Diagnostic Order

เริ่มจากถูกที่สุดและแยกชั้นปัญหาได้เร็วที่สุด:

1. Reproduce กับ sample เดิม

ใช้ sample ที่ timeout ซ้ำใน Phase 5 ก่อน เช่น `sample-000437`, `sample-000458`, `sample-000485` เพื่อดูว่าอาการเกิดซ้ำแบบ deterministic หรือเป็น runtime noise (source: docs/output-structure-fix/phase-5-mini-semantic-eval.md)

2. Cap output length

ตั้ง `max_tokens` หรือ `max_new_tokens` ให้ต่ำพอสำหรับ schema นี้ เช่น `256` หรือ `512` เพราะ triage JSON ควรสั้น ถ้า cap แล้วหาย timeout แปลว่า loop/unbounded generation มีส่วนสูง

3. Compare response modes

รัน prompt เดียวกันกับ:

- no structured output
- JSON mode หรือ `json_object`
- schema-constrained mode เช่น vLLM `structured_outputs`

ถ้า loop เกิดเฉพาะ schema-constrained mode ให้สงสัย constrained decoding, schema openness หรือ backend guided-decoding path ก่อน model semantics

4. Compare decoding settings

รัน matrix เล็ก:

| Setting | Purpose |
| --- | --- |
| `temperature=0` | baseline deterministic path |
| `temperature=0.2` หรือ `0.7` | ดูว่า greedy loop คลายไหม |
| `top_p=0.9` | จำกัด nucleus ของ candidate tokens |
| `repetition_penalty=1.1` ถึง `1.2` | ลงโทษ token ที่ออกซ้ำ |
| `no_repeat_ngram_size=3` หรือ `4` | ใช้เฉพาะ debug เพราะอาจทำให้ JSON หรือ evidence แปลกได้ |

5. Inspect stop and tokenizer config

ตรวจว่า serving endpoint ใช้ tokenizer, special tokens, `eos_token_id`, chat template และ stop token ตรงกับ checkpoint ที่ fine-tune จริงหรือไม่ โดยเฉพาะเมื่อ merge LoRA หรือ serve ผ่าน OpenAI-compatible runtime

6. Inspect rendered training examples

สุ่มดู training text ที่เข้า trainer จริง ไม่ใช่แค่ source JSONL:

- system/user/assistant role อยู่ครบหรือไม่
- assistant content เป็น JSON object เดียวหรือไม่
- มี EOS/EOT หลัง assistant JSON หรือไม่
- ไม่มีตัวอย่างที่ assistant answer ต่อหลาย response ใน record เดียว
- label และ schema field order ไม่สร้าง pattern ซ้ำที่ไม่ตั้งใจ

7. Compare base, adapter, and merged checkpoint

ถ้า base model ไม่ loop แต่ LoRA หรือ merged checkpoint loop ให้สงสัย fine-tuning format, overfitting, learning rate, train steps, special-token handling หรือ merge/export path

8. Compare precision/backend

ถ้า loop เกิดเฉพาะ quantized หรือเฉพาะ vLLM ให้เทียบ BF16/FP16 และ backend อื่นก่อนสรุปว่า dataset ผิด

## Structured Output Specific Notes

Structured outputs ช่วยให้ syntax/schema ถูกขึ้น แต่ไม่ได้รับประกัน semantic correctness และไม่ได้รับประกันว่า generation จะเร็วเสมอไป

Constrained decoding ทำงานโดยกรอง candidate token ให้เหลือเฉพาะ token ที่ยังทำให้ output valid ตาม schema ในแต่ละ step ถ้า schema อนุญาต string หรือ array แบบเปิดกว้าง model อาจยัง generate ต่อได้เรื่อย ๆ แม้ทุก token ยัง valid อยู่

สำหรับ schema ของโปรเจกต์นี้ สิ่งที่ควรระวังคือ:

- `reason` และ `recommended_action` เป็น string ที่มีโอกาสยาวเกินจำเป็น
- `evidence` เป็น array ของ string จึงควรมีจำนวน item และความยาวที่เหมาะสมใน schema หรือ prompt
- ถ้า model ไม่มั่นใจ label อาจเติม explanation ซ้ำใน field ที่ยัง valid แทนการหยุด
- ถ้า stop/EOS ไม่ถูก respected อาจได้ JSON ที่ครบแล้วแต่ decoder ยังพยายามต่อ

## Signals To Record In Reports

เวลาพบ loop หรือ timeout ให้บันทึกข้อมูลเหล่านี้ใน report เสมอ:

| Field | Why |
| --- | --- |
| sample id | ผูกกลับไปยัง split โดยไม่แตะ fixed test ผิดจังหวะ |
| expected label | ดูว่า loop กระจุกใน label ใด เช่น `port_scan_or_recon` |
| response mode | แยก schema-constrained issue จาก normal generation |
| decoding params | ทำให้ reproduce ได้ |
| max token setting | แยก unbounded generation จาก slow generation |
| timeout seconds | แยก timeout config จาก runtime hang |
| latency ms | เห็น spike ก่อน timeout |
| finish reason | ดูว่า stop, length, content filter หรือ error |
| raw output prefix/suffix | เห็น pattern ซ้ำโดยไม่ต้องเก็บ output ยาวเกิน |
| generated token count | ใช้ยืนยันว่า model ชน cap หรือหยุดเอง |
| backend and precision | แยก vLLM/Unsloth/Transformers และ quantization |

## Recommended Next Experiments For This Repo

| Experiment | Expected interpretation |
| --- | --- |
| Run Phase 5 timeout samples with `max_tokens=256` and no retry | ถ้าหาย timeout ให้ถือว่า output length cap เป็น mitigation สำคัญ |
| Run same samples with structured output disabled | ถ้าหาย loop ให้สงสัย constrained decoding/schema path |
| Run same samples with `repetition_penalty=1.1` | ถ้าหาย loop แต่ semantics ยังผิด ให้แยก decoding problem จาก training problem |
| Run one known-good brute-force sample and one timeout port-scan sample side by side | ดูว่า port-scan text pattern ทำให้ decoder ติดเฉพาะ label หรือไม่ |
| Dump rendered prompt and token counts | ตรวจว่า prompt/schema ยาวเกินหรือ instruction ถูก truncate |
| Compare base model, LoRA adapter, and merged model | แยกว่า loop มาจาก fine-tune หรือ serving/export |

## Mitigation Rules

- อย่าแก้ด้วยการเพิ่ม timeout อย่างเดียว เพราะอาจซ่อน generation loop และทำให้ average latency แย่ลง
- อย่าใช้ fixed `data/splits/test.jsonl` เพื่อ tune decoding parameters ให้ใช้ mini split หรือ diagnostic split ก่อน (source: docs/poc-plan.md)
- ถ้า schema-valid แต่ semantic ผิด ให้ถือเป็น model/data/training issue ไม่ใช่ output-contract success
- ถ้า timeout เกิดเฉพาะ structured output mode ให้ทดลอง schema tightening และ output cap ก่อนตัดสินใจ retrain
- ถ้า EOS/chat template ผิด ให้แก้ training render และ serving tokenizer config ก่อนปรับ dataset semantics
- บันทึก limitation ตรง ๆ ว่าโมเดลกำลัง triage suspicious patterns ไม่ใช่พิสูจน์ compromise (source: AGENTS.md)

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-20 | Codex | Created repetition-loop diagnostics page | `docs/model-repetition-loop-diagnostics.md` | Documents likely causes, project diagnostic order, structured-output notes, report fields, and next experiments |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-20 | Treat repeated-token loops as a cross-layer diagnosis, not only a model-quality issue | Internet sources and Phase 5 symptoms point to possible decoding, EOS/template, constrained decoding, runtime, quantization, and fine-tuning-format causes | Phase 6 diagnostics should compare response mode, output cap, decoding params, stop tokens, rendered training examples, backend, and precision before deciding retrain |

## Related pages

- [[structured-output-fix-plan]]
- [[structured-output-reliability-research-2026]]
- [[output-structure-fix/phase-5-mini-semantic-eval]]
- [[output-structure-fix/phase-6-v3-or-runtime-decision]]
- [[fine-tuning-notes]]
- [[data-formats-for-llm-training]]

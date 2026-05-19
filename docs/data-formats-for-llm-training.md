# Data Formats For LLM Training

**Summary**

เอกสารนี้สรุปรูปแบบข้อมูลที่พบบ่อยสำหรับการ train และ fine-tune LLM โดยแยกให้ชัดว่าแต่ละ format เหมาะกับงานแบบไหน สำหรับโปรเจกต์ `AI Security Log Triage Assistant` แนวทางที่เหมาะที่สุดคือเก็บ dataset ต้นทางเป็น `instruction`, `input`, `output` แล้วแปลงเป็น `messages` ตอนทำ SFT/LoRA เพื่อให้ assistant เรียนรู้การตอบ JSON ล้วนตาม schema เดิม (source: docs/dataset-input-output-format.md, ml/unsloth/training_format.py)

**Sources**

- `AGENTS.md` สำหรับ mission, dataset rules และ expected output schema ของ POC (source: AGENTS.md)
- `docs/dataset-input-output-format.md` สำหรับ canonical dataset shape ของโปรเจกต์นี้ (source: docs/dataset-input-output-format.md)
- `docs/fine-tuning-notes.md` สำหรับ Unsloth/LoRA training path และข้อจำกัดของ output contract รอบ v1 (source: docs/fine-tuning-notes.md)
- `ml/unsloth/training_format.py` สำหรับการแปลง `instruction/input/output` เป็น chat messages ตอน fine-tune (source: ml/unsloth/training_format.py)
- `scripts/model_adapters/prompt_contract.py` สำหรับ prompt contract และ JSON-only output expectation (source: scripts/model_adapters/prompt_contract.py)
- `docs/model-output/v1-lfm2-350m-security-triage.md` สำหรับ failure mode ที่ model ตอบ prose/prose+JSON แทน JSON object ล้วน (source: docs/model-output/v1-lfm2-350m-security-triage.md)

**Last updated**

2026-05-19

## Big Picture

คำว่า data format สำหรับ LLM training มักมี 2 ชั้น:

- **File container**: รูปแบบไฟล์ เช่น JSONL, JSON, CSV, Parquet หรือ plain text
- **Record shape**: โครงสร้างข้างในแต่ละ sample เช่น `text`, `prompt/completion`, `instruction/input/output`, `messages`, `chosen/rejected`

งาน fine-tuning ส่วนใหญ่ใช้ `JSONL` เป็น container เพราะอ่านทีละบรรทัดได้ง่าย stream ได้ง่าย และเหมาะกับ dataset ขนาดใหญ่ แต่สิ่งที่สำคัญกว่าคือ record shape ต้องตรงกับ behavior ที่อยากให้ model เรียนรู้

สำหรับ POC นี้ เราไม่ได้ train ให้ model เขียน prose เรื่อง security logs เก่งขึ้น แต่ train ให้ model ทำ task เดิมซ้ำ ๆ: รับ log แล้วคืน structured triage result ตาม schema เดิม ดังนั้น format ที่เหมาะต้องทำให้ instruction, input และ expected JSON output ชัดตั้งแต่ต้น

## Common Formats

### 1. Raw Text

ใช้กับ continued pretraining หรือ domain adaptation ที่อยากให้ model ซึมซับภาษา โดเมน หรือ style จาก corpus ยาว ๆ

```json
{"text":"Security logs often include source IP, destination port, timestamp, action, and status code."}
```

เหมาะกับ:

- continued pretraining
- domain language adaptation
- เอกสารยาว, log explanation, runbook, policy text

ไม่เหมาะกับ:

- งานที่ต้องตอบ schema คงที่
- งานที่ต้องวัด label accuracy หรือ JSON validity

ข้อควรระวังสำหรับโปรเจกต์นี้: raw text อาจทำให้ model รู้คำศัพท์ security มากขึ้น แต่ไม่ได้สอนให้ตอบ `label`, `severity`, `evidence`, `reason`, `recommended_action` ให้ครบ

### 2. Prompt Completion

เป็นรูปแบบเก่าที่จับคู่ prompt กับ completion โดยตรง

```json
{
  "prompt": "Analyze this log:\nGET /login?user=admin' OR '1'='1\n\nAnswer:",
  "completion": "{\"label\":\"sql_injection_attempt\",\"severity\":\"high\",\"is_suspicious\":true}"
}
```

เหมาะกับ:

- completion model หรือ training pipeline รุ่นเก่า
- task ที่เป็น one-shot completion ตรง ๆ

ข้อจำกัด:

- แยก `system`, `user`, `assistant` ไม่ชัด
- ใช้กับ chat template ของ instruct model ได้ไม่สะอาดเท่า `messages`
- ถ้า prompt มี wording หลวม model อาจเรียนรู้ prose wrapper ได้ง่าย

สำหรับ POC นี้ format นี้ใช้ได้ในเชิงแนวคิด แต่ไม่ใช่ shape หลัก เพราะ path ปัจจุบันใช้ chat-template rendering ผ่าน tokenizer ของ LFM2

### 3. Instruction Tuning

เป็น format ที่เหมาะกับงานสอน model ให้ทำตามคำสั่ง มี instruction, input และ output แยกกัน

```json
{
  "id": "sample-000001",
  "instruction": "Analyze this security log and classify whether it is suspicious.",
  "input": "192.168.1.20 GET /login?user=admin' OR '1'='1",
  "output": {
    "label": "sql_injection_attempt",
    "severity": "high",
    "is_suspicious": true,
    "evidence": ["admin' OR '1'='1"],
    "reason": "The request contains a common SQL injection pattern.",
    "recommended_action": "Review web application logs and block or rate-limit the source IP."
  }
}
```

เหมาะกับ:

- supervised fine-tuning
- classification plus structured generation
- dataset ที่ต้องใช้ร่วมกันระหว่าง train, validation, test และ evaluator

ข้อดีสำหรับโปรเจกต์นี้:

- อ่านง่ายและ debug ง่าย
- evaluator ใช้ `input` และ `output` เดิมได้ตรง ๆ
- dataset generator สร้าง sample แบบ deterministic ได้
- schema validation ทำกับ `output` ได้ก่อน train

นี่ควรเป็น canonical source format ของโปรเจกต์นี้ต่อไป

### 4. Chat Messages

เป็น format ที่สะท้อน chat/instruct model โดยตรง แยก role เป็น `system`, `user`, `assistant`

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Return only one valid JSON object."
    },
    {
      "role": "user",
      "content": "Analyze this security log and classify whether it is suspicious.\n\nLog:\nGET /../../etc/passwd"
    },
    {
      "role": "assistant",
      "content": "{\"label\":\"directory_traversal_attempt\",\"severity\":\"high\",\"is_suspicious\":true,\"evidence\":[\"../../etc/passwd\"],\"reason\":\"The request attempts to access a parent directory path.\",\"recommended_action\":\"Review web access logs and block or rate-limit the source IP.\"}"
    }
  ]
}
```

เหมาะกับ:

- SFT บน chat/instruct model
- LoRA/QLoRA ที่ต้องผ่าน tokenizer chat template
- งานที่ต้องควบคุม system prompt และ assistant output ให้เหมือน runtime

ข้อควรระวัง:

- `assistant.content` ต้องเป็น output ที่อยากให้ model เลียนแบบจริง ๆ
- ถ้า assistant มีคำอธิบายนำหน้า, markdown fence หรือคำว่า `Output schema:` model ก็มีโอกาสเรียนรู้ pattern นั้น
- system prompt ที่ยาวหรือมี example ที่ชวนเลียนแบบ prose อาจส่งผลต่อ output behavior ได้

สำหรับ POC นี้ `messages` ควรเป็น training render format ไม่ใช่ source-of-truth dataset format เพราะ source format แบบ `instruction/input/output` ใช้กับ evaluator และ docs ได้ตรงกว่า

### 5. Multi-Turn Chat

ใช้เมื่อ dataset ต้องสอนการคุยหลายรอบ เช่น user ถามต่อ model ชี้แจง หรือ model ขอข้อมูลเพิ่ม

```json
{
  "messages": [
    {"role": "system", "content": "You are a security log triage assistant."},
    {"role": "user", "content": "Analyze this log:\nGET /search?q=SLEEP(5)"},
    {"role": "assistant", "content": "{\"label\":\"sql_injection_attempt\",\"severity\":\"high\",\"is_suspicious\":true,\"evidence\":[\"SLEEP(5)\"],\"reason\":\"The request contains a timing-based SQL injection indicator.\",\"recommended_action\":\"Review web application logs and check whether the request reached the database layer.\"}"},
    {"role": "user", "content": "Why is this suspicious?"},
    {"role": "assistant", "content": "The payload includes SLEEP(5), which is commonly used to test timing-based SQL injection behavior."}
  ]
}
```

เหมาะกับ:

- support bot
- security assistant ที่ต้องตอบ follow-up
- incident investigation workflow หลายขั้น

ยังไม่เหมาะกับ POC รอบนี้ เพราะ scope ตอนนี้คือ one-log, one-output, fixed schema ถ้าใส่ multi-turn เร็วเกินไป evaluation จะซับซ้อนขึ้นโดยยังไม่ได้ช่วยแก้ output contract หลัก

### 6. Preference Data

ใช้กับ DPO, ORPO หรือ preference tuning โดยให้ model เห็นคำตอบที่ดีกว่าและแย่กว่า

```json
{
  "prompt": "Analyze this security log:\nGET /search?q=SLEEP(5)",
  "chosen": "{\"label\":\"sql_injection_attempt\",\"severity\":\"high\",\"is_suspicious\":true,\"evidence\":[\"SLEEP(5)\"],\"reason\":\"The request contains a timing-based SQL injection indicator.\",\"recommended_action\":\"Review web application logs and check whether the request reached the database layer.\"}",
  "rejected": "The log looks suspicious because it may be SQL injection. You should investigate it."
}
```

เหมาะกับ:

- ลด behavior ที่ไม่ต้องการ เช่น prose wrapper หรือ hallucinated evidence
- สอน model ว่าคำตอบ JSON-only ดีกว่าคำตอบอธิบายยาว
- fine-tuning รอบหลังจากมี SFT baseline แล้ว

น่าสนใจสำหรับโปรเจกต์นี้ในรอบถัดไป เพราะ v1 ล้มที่ output contract ชัดเจน เราสามารถสร้าง rejected examples จาก raw failure เช่น prose ก่อน JSON, label นอก taxonomy, หรือ JSON ที่ field ไม่ครบ แล้วจับคู่กับ chosen ที่เป็น schema-valid JSON

### 7. Ranking Or Scored Responses

คล้าย preference data แต่มีหลาย candidate และอาจมี score

```json
{
  "prompt": "Analyze this security log:\nGET /../../etc/passwd",
  "responses": [
    {
      "text": "{\"label\":\"directory_traversal_attempt\",\"severity\":\"high\",\"is_suspicious\":true,\"evidence\":[\"../../etc/passwd\"],\"reason\":\"The path attempts directory traversal.\",\"recommended_action\":\"Review web access logs and block or rate-limit the source IP.\"}",
      "score": 1.0
    },
    {
      "text": "This looks like SQL injection.",
      "score": 0.0
    }
  ]
}
```

เหมาะกับ:

- reward model
- reranker
- offline preference analysis

สำหรับ POC นี้ยังไม่ใช่ priority เพราะตอนนี้ต้องทำ SFT output contract ให้ผ่านก่อน

### 8. Tool Calling Or Function Calling

ใช้เมื่ออยากให้ model คืน tool call หรือ function arguments แทนข้อความธรรมดา

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Analyze this security log: GET /../../etc/passwd"
    },
    {
      "role": "assistant",
      "tool_calls": [
        {
          "type": "function",
          "function": {
            "name": "triage_log",
            "arguments": "{\"label\":\"directory_traversal_attempt\",\"severity\":\"high\",\"is_suspicious\":true,\"evidence\":[\"../../etc/passwd\"],\"reason\":\"The path attempts directory traversal.\",\"recommended_action\":\"Review web access logs and block or rate-limit the source IP.\"}"
          }
        }
      ]
    }
  ]
}
```

เหมาะกับ:

- agent workflow
- runtime ที่รองรับ tool calling จริง
- application ที่ต้องแยก natural language response ออกจาก structured action

สำหรับ POC นี้ยังไม่จำเป็น เว้นแต่ serving endpoint รองรับ structured output หรือ guided JSON ได้ดีพอ และเราตัดสินใจให้ model output เป็น function arguments แทน plain JSON

### 9. Evaluation JSONL

ใช้สำหรับวัดผล ไม่ควรปนกับ training split

```json
{
  "id": "sample-000001",
  "input": "GET /login?user=admin' OR '1'='1",
  "output": {
    "label": "sql_injection_attempt",
    "severity": "high",
    "is_suspicious": true,
    "evidence": ["admin' OR '1'='1"],
    "reason": "The request contains a common SQL injection pattern.",
    "recommended_action": "Review web application logs and block or rate-limit the source IP."
  }
}
```

ใน repo นี้ evaluator ใช้ `input` เป็นโจทย์ และใช้ `output` เป็น expected answer เพื่อวัด:

- label accuracy
- JSON parse success rate
- schema success rate
- severity accuracy
- evidence partial match
- average latency
- invalid output count

test split ต้องคงที่ และไม่ควรใช้ปรับ prompt หรือ train เพราะจะทำให้ comparison ระหว่าง baseline กับ fine-tuned model ไม่แฟร์

## Recommendation For This Project

รูปแบบที่ควรใช้ในโปรเจกต์นี้:

1. เก็บ source dataset เป็น `instruction/input/output` JSONL
2. validate `output` ด้วย schema ก่อน train
3. split เป็น `train`, `validation`, `test` แบบคงที่
4. ตอน train ให้แปลงเป็น `messages`
5. ให้ `assistant.content` เป็น JSON string ล้วน ไม่มี prose, markdown หรือ schema heading
6. ใช้ evaluator เดิมวัด fixed test split หลัง train เท่านั้น

ภาพรวม flow:

```text
instruction/input/output JSONL
  -> schema validation
  -> train/validation/test split
  -> chat messages rendering
  -> tokenizer chat template
  -> LoRA/QLoRA fine-tuning
  -> strict JSON evaluation on fixed test split
```

ถ้าต้องแก้ปัญหา model output ของ v1 รอบถัดไป ให้เริ่มจาก SFT ด้วย chat render ที่สะอาดก่อน เมื่อ JSON/schema validity ยังไม่นิ่งค่อยพิจารณาเพิ่ม preference data เพื่อสอนว่า prose wrapper และ field-missing output เป็นคำตอบที่แย่กว่า

## Format Decision Table

| Format | ใช้ทำอะไร | ควรใช้ใน POC นี้ไหม |
| --- | --- | --- |
| Raw text | continued pretraining, domain adaptation | ยังไม่ใช่ priority |
| Prompt completion | completion-style SFT | ไม่ใช่ path หลัก |
| Instruction tuning | canonical supervised dataset | ใช้เป็น source format |
| Chat messages | train chat/instruct model | ใช้เป็น render format |
| Multi-turn chat | assistant conversation หลายรอบ | เลื่อนไป future work |
| Preference data | ลดคำตอบที่ไม่ต้องการ | ใช้รอบหลังถ้า SFT ยังหลุด prose |
| Ranking/scored responses | reward model หรือ reranker | ยังไม่จำเป็น |
| Tool/function calling | structured tool output | optional ถ้า runtime รองรับ |
| Evaluation JSONL | fixed split สำหรับวัดผล | ใช้เสมอ |

## Work Log

Append-only log สำหรับบันทึกว่าเอกสารนี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-19 | Codex | Created the LLM training data format guide and tied it to the project fine-tuning path | `docs/data-formats-for-llm-training.md` | Drafted |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-19 | ใช้ `instruction/input/output` เป็น source format และ `messages` เป็น training render format | source format นี้เหมาะกับ evaluator และ schema validation ส่วน chat messages เหมาะกับ tokenizer chat template ตอน fine-tune | dataset ยังอ่านง่ายและวัดผลได้ตรง ขณะเดียวกัน training path ยังเข้ากับ LFM2/Unsloth |

## Related pages

- [[dataset-input-output-format]]
- [[fine-tuning-notes]]
- [[model-output/v1-lfm2-350m-security-triage]]
- [[triage-output-schema]]
- [[evaluation-metrics-rationale]]

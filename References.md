# References.md

ไฟล์นี้รวม reference หลักที่ใช้วางแนวทางให้ POC `AI Security Log Triage Assistant`

เป้าหมายของไฟล์นี้ไม่ใช่เก็บ link ไว้เฉย ๆ แต่บอกให้ชัดว่าแต่ละ repo หรือเอกสารเอามาอ้างอิงส่วนไหนของงานเราได้บ้าง

Last checked: 2026-05-16

## 1. Fine-Tuning References

### Unsloth

- Link: https://unsloth.ai/docs
- GitHub: https://github.com/unslothai/unsloth
- ใช้อ้างอิงเรื่อง: LoRA, QLoRA, small model fine-tuning, notebook-style training workflow

Unsloth เหมาะกับ POC นี้เพราะเราอยากพิสูจน์ว่า small model สามารถทำงานเฉพาะทางได้ดีขึ้นหลัง fine-tune โดยไม่ต้องเริ่มจากโมเดลใหญ่

สิ่งที่ควรยืมมาใช้กับ repo นี้:

- วาง training script ไว้แยกใน `ml/unsloth/`
- เริ่มจาก LoRA หรือ QLoRA ก่อน full fine-tuning
- ทำ notebook หรือ markdown guide สำหรับรันบน Colab/GPU
- export adapter/checkpoint แล้วค่อยเอามาต่อกับ inference path

สิ่งที่ยังไม่ควรทำใน POC แรก:

- train หลายโมเดลพร้อมกัน
- optimize VRAM/throughput ลึกเกินไป
- merge model และ deploy production ตั้งแต่รอบแรก

### Axolotl

- Link: https://github.com/axolotl-ai-cloud/axolotl
- Docs: https://docs.axolotl.ai/
- ใช้อ้างอิงเรื่อง: config-driven fine-tuning, YAML config, separation ระหว่าง model, dataset, training params และ evaluation

Axolotl เป็นตัวอย่าง repo fine-tuning ที่จัด workflow เป็นระบบมาก จุดที่ควรเอามาเป็นแบบคือการให้ config เป็นศูนย์กลาง ไม่ hard-code ค่า training กระจายอยู่ใน script

สิ่งที่ควรยืมมาใช้กับ repo นี้:

- มีไฟล์ `ml/unsloth/config.example.yaml`
- แยกค่า `base_model`, `dataset_path`, `output_dir`, `learning_rate`, `epochs`, `lora_rank`
- ทำให้ training run แต่ละครั้งย้อนดู configuration ได้

เราไม่จำเป็นต้องใช้ Axolotl เป็น dependency ตั้งแต่ต้น แต่ควรเอาวิธีคิดเรื่อง config และ reproducibility มาใช้

### Hugging Face TRL

- Link: https://github.com/huggingface/trl
- Docs: https://huggingface.co/docs/trl/
- ใช้อ้างอิงเรื่อง: `SFTTrainer`, supervised fine-tuning, post-training workflow

TRL เป็น reference ที่ดีสำหรับเข้าใจ supervised fine-tuning pipeline โดยเฉพาะการเตรียม dataset ให้เข้ากับ trainer และการวัดผลระหว่าง train

สิ่งที่ควรยืมมาใช้กับ repo นี้:

- format training sample ให้ชัดว่า prompt/input/output อยู่ตรงไหน
- แยก train/validation/test ตั้งแต่แรก
- ใช้เป็น fallback path ถ้า Unsloth ไม่เหมาะกับ environment บางแบบ

สำหรับ POC แรก ให้ Unsloth เป็น path หลัก ส่วน TRL เป็น reference และ fallback

## 2. Evaluation References

### EleutherAI lm-evaluation-harness

- Link: https://github.com/EleutherAI/lm-evaluation-harness
- ใช้อ้างอิงเรื่อง: evaluation harness, task abstraction, model adapter, metrics

lm-evaluation-harness เป็นตัวอย่างที่ดีมากของการแยก evaluation ออกจากตัว model ตัว evaluator ไม่ควรสนใจว่าเบื้องหลังเป็น OpenAI-compatible endpoint, local model, heuristic baseline หรือ fine-tuned checkpoint

สิ่งที่ควรยืมมาใช้กับ repo นี้:

- แยก `task`, `dataset`, `model adapter`, `metric` ออกจากกัน
- ทำ evaluator ที่รันซ้ำได้จาก command เดียว
- เก็บผลเป็น machine-readable JSON และ human-readable markdown
- ให้ baseline และ fine-tuned model ใช้ test split เดียวกัน

สิ่งที่ต้องระวัง:

- งานของเราเป็น structured JSON triage ไม่ใช่ benchmark language modeling ทั่วไป
- metric ต้องมีเรื่อง JSON validity, schema validity และ evidence match เพิ่มจาก accuracy ปกติ

## 3. Log And Security Dataset References

### Loghub

- Link: https://github.com/logpai/loghub
- ใช้อ้างอิงเรื่อง: log analytics dataset, log source variety, data documentation

Loghub เป็นแหล่งอ้างอิงที่ดีสำหรับงาน log analytics โดยเฉพาะวิธีคิดเรื่อง dataset จากหลายระบบ แม้ POC แรกของเราจะใช้ synthetic security log ก่อน แต่ Loghub ช่วยให้เห็นว่าเมื่อขยายงานจริงควรจัดการ data source อย่างไร

สิ่งที่ควรยืมมาใช้กับ repo นี้:

- แยก `data/raw/`, `data/generated/`, `data/splits/`
- เขียน `docs/data-card.md`
- ระบุที่มาของ log, format, label, limitation และ license
- ใช้ log จริงเป็น reference ในรอบหลัง ไม่ใช่ปนกับ synthetic data แบบไม่บอกที่มา

### Splunk BOTS

- Link: https://github.com/splunk/botsv1
- ใช้อ้างอิงเรื่อง: SOC scenario, investigation-style dataset, multi-source security events

Splunk BOTS เหมาะเป็น reference ด้าน scenario มากกว่าการเอามา train ตรง ๆ ในรอบแรก เพราะข้อมูลลักษณะนี้มักมีหลาย sourcetype และต้องเข้าใจ context ของ incident

สิ่งที่ควรยืมมาใช้กับ repo นี้:

- วิธีคิดแบบ analyst: ดู evidence แล้วถามว่าควรตรวจอะไรต่อ
- ใช้สำหรับออกแบบ demo scenario ในอนาคต
- ใช้เป็นแรงบันดาลใจให้ `recommended_action` ไม่ generic เกินไป

สำหรับ POC แรก ให้ยังไม่ import BOTS เข้ามาใน repo

### OTRF / Mordor

- GitHub: https://github.com/OTRF/mordor
- Docs: https://msticpy.readthedocs.io/en/latest/data_acquisition/MordorData.html
- ใช้อ้างอิงเรื่อง: adversary-emulation logs, attack-pattern datasets, Windows/Linux/cloud telemetry

Mordor หรือ OTRF Security Datasets เหมาะกับรอบที่อยากเพิ่ม realism ให้มากขึ้น เพราะข้อมูลถูกออกแบบให้สะท้อนพฤติกรรม adversary มากกว่า log ระบบทั่วไป

สิ่งที่ควรยืมมาใช้กับ repo นี้:

- scenario-based test case
- mapping ระหว่าง log evidence กับ attack behavior
- แนวทางทำ evaluation ที่ไม่ใช่ดู log เส้นเดียวเสมอไป

สำหรับ POC แรก ให้เก็บเป็น reference ก่อน ยังไม่ต้องผูกเข้ากับ training path

## 4. Detection And Taxonomy References

### SigmaHQ

- Main repo: https://github.com/SigmaHQ/sigma
- Docs: https://sigmahq.io/docs/
- ใช้อ้างอิงเรื่อง: detection rule structure, `logsource`, `detection`, `falsepositives`, severity/level

SigmaHQ ช่วยให้เราออกแบบ output และ dataset ให้ใกล้การทำงานของ detection engineer มากขึ้น ไม่ใช่ให้ model ตอบ label อย่างเดียว

สิ่งที่ควรยืมมาใช้กับ repo นี้:

- concept ของ `logsource`
- field แบบ `evidence`, `false_positive_notes`, `level`
- เขียน reason โดยโยงกับ pattern ที่ตรวจเจอ
- ระวัง false positive เสมอ

ใน POC แรก output schema ยังไม่ต้อง copy Sigma format ตรง ๆ แต่ควรยืมวิธีคิดเรื่อง evidence และ false positive

### OWASP Attacks

- Attack index: https://owasp.org/www-community/attacks/
- SQL Injection: https://owasp.org/www-community/attacks/SQL_Injection
- Path Traversal: https://owasp.org/www-community/attacks/Path_Traversal
- Brute Force Attack: https://owasp.org/www-community/attacks/Brute_force_attack
- ใช้อ้างอิงเรื่อง: attack taxonomy, web attack definition, common pattern

OWASP เหมาะกับ label ชุดแรกของ POC เพราะ label ที่เราเลือกส่วนใหญ่เป็น web/security pattern ที่อธิบายได้ด้วย taxonomy พื้นฐานของ OWASP

สิ่งที่ควรยืมมาใช้กับ repo นี้:

- นิยามของ SQL injection, path traversal และ brute force
- ตัวอย่าง pattern ที่ใช้สร้าง synthetic dataset
- คำอธิบายที่ไม่ overclaim ว่า attack สำเร็จแล้ว

ตัวอย่างการ map กับ label:

```text
OWASP SQL Injection   -> sql_injection_attempt
OWASP Path Traversal  -> directory_traversal_attempt
OWASP Brute Force     -> failed_login_bruteforce
Recon/scan behavior   -> port_scan_or_recon
Benign access pattern -> normal
```

## 5. How These References Map To This Repo

```text
Unsloth
  -> ml/unsloth/train_lora.py
  -> ml/unsloth/inference.py
  -> docs/fine-tuning-notes.md

Axolotl
  -> ml/unsloth/config.example.yaml
  -> reproducible training config

Hugging Face TRL
  -> fallback SFT reference
  -> dataset formatting reference

lm-evaluation-harness
  -> frontend/lib/evaluation/
  -> scripts/evaluate.ts
  -> reports/*.json

Loghub
  -> docs/data-card.md
  -> data/raw/ and data/splits/ structure

Splunk BOTS
  -> future SOC scenario design
  -> future demo examples

OTRF / Mordor
  -> future adversary-emulation test cases
  -> future multi-log evaluation

SigmaHQ
  -> evidence, logsource, false positive thinking
  -> possible future rule-like metadata

OWASP
  -> first label taxonomy
  -> synthetic pattern generation
```

## 6. What Not To Copy Blindly

อย่า copy architecture ใหญ่ทั้งหมดเข้ามาใน POC นี้ทันที

สิ่งที่ยังไม่ควรทำ:

- ทำ training framework ใหญ่แบบ Axolotl เต็มตัว
- ทำ benchmark system ใหญ่เท่า lm-evaluation-harness
- เอา dataset จริงเข้ามาโดยไม่อ่าน license และไม่ทำ data-card
- ทำให้ UI กลายเป็น SIEM dashboard เต็มรูปแบบ
- อ้างว่า model detect การถูก hack ได้แน่นอนจาก log เส้นเดียว

แนวทางที่ถูกคือยืมหลักคิดจาก repo ใหญ่ แล้วทำเวอร์ชันเล็กที่วัดผลได้จริงก่อน

## 7. Priority For This POC

ลำดับที่ควรอ้างอิงก่อน:

1. OWASP สำหรับ label และ synthetic attack pattern
2. SigmaHQ สำหรับ evidence และ false positive mindset
3. lm-evaluation-harness สำหรับ evaluator structure
4. Unsloth สำหรับ fine-tuning path
5. Axolotl สำหรับ config discipline
6. Loghub สำหรับ data-card และ dataset structure
7. Splunk BOTS กับ OTRF/Mordor สำหรับรอบที่อยากเพิ่ม scenario จริงจังขึ้น

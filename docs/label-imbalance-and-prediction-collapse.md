# Label Imbalance And Prediction Collapse

**Summary**

เอกสารนี้สรุปวิธีรับมือกรณี label บางตัวมีจำนวนมากเกินไป หรือโมเดลทาย label บางตัวมากผิดปกติใน Phase 6 ของ `AI Security Log Triage Assistant` จุดสำคัญคือแยกให้ได้ก่อนว่าเป็น **data imbalance จริง** หรือเป็น **prediction collapse** เพราะวิธีแก้ไม่เหมือนกัน

**Sources**

- `AGENTS.md` สำหรับ label scope, fixed split rule, evaluation rule และ guardrail ว่าระบบนี้เป็น triage assistant ไม่ใช่ระบบยืนยัน compromise (source: AGENTS.md)
- `docs/poc-plan.md` สำหรับ dataset plan, label-balanced first split และ fixed test split comparison (source: docs/poc-plan.md)
- `scripts/generate_dataset.py` สำหรับค่าตั้งต้น `PER_LABEL = 100`, `TRAIN_PER_LABEL = 70`, `VALIDATION_PER_LABEL = 15`, `TEST_PER_LABEL = 15` (source: scripts/generate_dataset.py)
- `scripts/create_mini_semantic_eval_split.py` สำหรับ Phase 5 mini split ที่เลือกแบบ label-balanced จาก validation split (source: scripts/create_mini_semantic_eval_split.py)
- `docs/output-structure-fix/phase-5-mini-semantic-eval.md` สำหรับผล Phase 5 ที่ prediction เอนหนักไปทาง `failed_login_bruteforce` (source: docs/output-structure-fix/phase-5-mini-semantic-eval.md)
- `docs/output-structure-fix/phase-6-v3-or-runtime-decision.md` สำหรับ Phase 6 decision point ระหว่าง runtime, v3 training data, schema/prompt wording และ model capacity (source: docs/output-structure-fix/phase-6-v3-or-runtime-decision.md)
- Johnson and Khoshgoftaar, "Survey on deep learning with class imbalance" สำหรับกรอบ data-level, algorithm-level และ hybrid approaches: https://link.springer.com/article/10.1186/s40537-019-0192-5
- Lin et al., "Focal Loss for Dense Object Detection" สำหรับแนวคิดลดน้ำหนัก easy examples ที่ครอบ training: https://openaccess.thecvf.com/content_iccv_2017/html/Lin_Focal_Loss_for_ICCV_2017_paper.html
- Cui et al., "Class-Balanced Loss Based on Effective Number of Samples" สำหรับ class-balanced loss ที่ใช้ effective number of samples: https://openaccess.thecvf.com/content_CVPR_2019/html/Cui_Class-Balanced_Loss_Based_on_Effective_Number_of_Samples_CVPR_2019_paper.html
- Rahman et al., "Multi-class Network Intrusion Detection with Class Imbalance via LSTM & SMOTE" สำหรับตัวอย่าง security/IDS ที่ใช้ SMOTE และ focal loss: https://arxiv.org/abs/2310.01850
- Lee et al., "Effectiveness of Focal Loss for Minority Classification in Network Intrusion Detection Systems" สำหรับ focal-loss IDS baseline บน imbalanced NIDS datasets: https://www.mdpi.com/2073-8994/13/1/4
- Scikit-learn model evaluation guide สำหรับ balanced accuracy และ macro-style metric ที่ไม่หลงกับ majority class: https://sklearn.org/stable/modules/model_evaluation.html
- Imbalanced-learn user guide สำหรับ over-sampling, under-sampling, combined sampling, ensemble และ metrics: https://imbalanced-learn.org/stable/user_guide.html
- Xie et al., "DoReMi: Optimizing Data Mixtures Speeds Up Language Model Pretraining" สำหรับแนวคิด data mixture/domain reweighting ใน language model training: https://proceedings.neurips.cc/paper_files/paper/2023/hash/dcba6be91359358c2355cd920da3fcbd-Abstract-Conference.html

**Last updated**

2026-05-21

## Current Diagnosis

Phase 6 มีสัญญาณสองเรื่องที่ต้องแยกกันให้ชัด:

- runtime/output issue: `port_scan_or_recon` บางตัวทำให้ constrained JSON mode วนใน `evidence` จน timeout หรือชน token cap (source: docs/output-structure-fix/phase-6-v3-or-runtime-decision.md)
- semantic issue: โมเดลทาย `failed_login_bruteforce` มากเกินไป แม้ mini eval split จะ balanced แล้ว (source: docs/output-structure-fix/phase-5-mini-semantic-eval.md)

ตัว source dataset รอบแรกไม่ได้เอียง:

| Split | Count | Label distribution |
| --- | ---: | --- |
| `data/generated/synthetic-security-triage.jsonl` | 500 | 100 ต่อ label |
| `data/splits/train.jsonl` | 350 | 70 ต่อ label |
| `data/splits/validation.jsonl` | 75 | 15 ต่อ label |
| `data/splits/test.jsonl` | 75 | 15 ต่อ label |
| `data/splits/mini-semantic-eval.jsonl` | 25 | 5 ต่อ label |
| `data/splits/smoke-output-contract.jsonl` | 5 | 1 ต่อ label |
| `data/splits/phase6-timeout-only.jsonl` | 3 | `port_scan_or_recon` 3 ตัว ตั้งใจใช้เป็น diagnostic split เท่านั้น |

ดังนั้น ณ Phase 6 ปัญหาไม่ควรถูกสรุปเร็ว ๆ ว่า "label ใน training เยอะเกิน" แต่ควรเรียกว่า **prediction collapse toward `failed_login_bruteforce`** จนกว่าจะพิสูจน์ด้วย distribution report ว่า training source เอียงจริง

## Decision Rule

เวลาพบว่า label บางตัวเยอะผิดปกติ ให้ดูสอง distribution แยกกัน:

| สิ่งที่นับ | ถ้าเอียงแปลว่า | วิธีแก้หลัก |
| --- | --- | --- |
| `expected/output.label` ใน train/validation/test | data imbalance หรือ split imbalance | stratified split, cap per label, oversample minority, undersample majority, data-card update |
| `predicted.label` ใน evaluation report | model bias, prompt/schema ambiguity, training format issue หรือ model capacity limit | confusion analysis, hard contrast examples, prompt/schema wording, balanced sampling, capacity diagnostic |

กติกาสำหรับ repo นี้:

- ถ้า source split ไม่ balanced ให้แก้ generator/split ก่อน train ใหม่
- ถ้า source split balanced แต่ prediction เอนไป label เดียว ให้ทำ semantic error analysis ก่อนเพิ่มหรือลด data
- ถ้า output contract ยังไม่ผ่าน `1.0` ให้ซ่อม contract/runtime ก่อน fixed test comparison
- ห้ามใช้ `data/splits/test.jsonl` เพื่อ tune sampling, prompt หรือ schema

## Research Pattern

งานวิจัยเรื่อง class imbalance มักแบ่งวิธีแก้ออกเป็น 3 ชั้น:

1. **Data-level**

ปรับ distribution ของข้อมูลก่อน training เช่น random over-sampling, under-sampling, SMOTE, data augmentation หรือ balanced batch sampler ข้อดีคือใช้กับ model ได้กว้างและอธิบายง่าย ข้อเสียคืออาจทำให้ majority class สูญข้อมูล หรือ minority class ถูก duplicate จน overfit ได้

2. **Algorithm-level**

ปรับ objective หรือ loss เช่น class-weighted loss, focal loss, class-balanced loss หรือ margin/loss แบบ long-tailed learning งาน Focal Loss ใช้แนวคิดลดน้ำหนักตัวอย่างที่โมเดลตอบง่าย เพื่อไม่ให้ตัวอย่าง easy/majority ครอบ gradient ส่วน Class-Balanced Loss ใช้ effective number of samples แทนการหารด้วย frequency ตรง ๆ

3. **Hybrid**

ผสม data-level กับ algorithm-level เช่น SMOTE + focal loss หรือ resampling + ensemble ในงาน intrusion detection มีตัวอย่างชัด เพราะ traffic/log จริงมักมี normal เยอะและ attack บางชนิดน้อยมาก งาน IDS หลายชิ้นจึงใช้ oversampling, focal loss หรือ ensemble เพื่อช่วย rare attack classes

สำหรับ LLM และ instruction tuning ให้คิดเพิ่มอีกชั้นคือ **data mixture**: แต่ละ label หรือ attack pattern เป็น bucket ที่มี sampling weight ของตัวเอง แนวคิดนี้คล้าย data mixture optimization ใน LM training เช่น DoReMi ที่ปรับสัดส่วน domain ก่อน train model ใหญ่กว่า

## Recommended Path For This Project

สำหรับ Phase 6 ของโปรเจกต์นี้ แนะนำลำดับแก้ดังนี้:

1. **ปิด runtime/output loop ก่อน**

ทำ Phase 6.1 ให้จบก่อน โดยบังคับ `evidence` เป็น 1-3 exact substrings และ rerun timeout-only/smoke split ถ้ายัง loop อย่าเพิ่งสรุปเรื่อง semantic quality เพราะ output ยังใช้เป็น metric ไม่ได้ (source: docs/output-structure-fix/phase-6-1-evidence-constraints.md)

2. **ทำ predicted-label distribution gate**

หลัง output contract ผ่าน ให้ evaluator/report แสดง expected distribution, predicted distribution และ confusion matrix ทุกครั้ง ถ้า mini eval balanced แต่ prediction label ใด label หนึ่งเกิน 50-60% ให้ fail semantic gate แม้ label accuracy ดูไม่เป็นศูนย์

3. **เพิ่ม hard contrast examples ไม่ใช่เพิ่ม data แบบสุ่ม**

เพิ่ม v3 data เฉพาะจุดที่ Phase 5 พลาด:

- `normal` hard negatives ที่คล้าย brute force แต่ไม่ใช่ เช่น single failed login, routine health check, ordinary search query ที่มีคำอย่าง `select` หรือ `union` ในความหมายปกติ
- `sql_injection_attempt` ที่ evidence ชัด เช่น quote, tautology, `UNION SELECT`, `SLEEP(`, `information_schema`
- `directory_traversal_attempt` ที่มี `../`, encoded traversal, Windows path หรือ path probing
- `port_scan_or_recon` ที่มี port list, `unique_ports`, `nmap fingerprint`, `SYN scan detected`
- paired contrast examples เช่น log คล้ายกันแต่ต่างกันตรง `failed_attempts=1` เทียบกับ `failed_attempts=12`

4. **ใช้ balanced sampling เฉพาะ training**

ถ้าขยาย dataset แล้ว label บางตัวมีเยอะกว่า ให้ sampling ตอน train ไม่จำเป็นต้องตาม raw distribution เสมอ ทางปลอดภัยคือ cap หรือ weighted sample ให้ label อยู่ในช่วงไม่ต่างกันเกิน 2-3 เท่าในแต่ละ epoch แล้วเก็บ raw distribution ไว้ใน data card

5. **เพิ่ม metric สำหรับ imbalance**

รอบแรกมี `label_accuracy` อยู่แล้ว แต่ถ้าเจอ prediction collapse ควรเพิ่ม:

- per-label precision/recall/F1
- macro-F1
- balanced accuracy
- confusion matrix
- predicted-label distribution
- false positive rate ของ `normal`
- false negative rate ของ suspicious labels

metric เหล่านี้ช่วยกันภาพลวงที่ accuracy สูงเพราะโมเดลทาย majority class หรือ label เดิมซ้ำ ๆ

6. **แยก balanced eval กับ real-prior eval**

เมื่อเริ่มใช้ log จริงในอนาคต ให้เก็บสองชุด evaluation:

- balanced eval: label ละใกล้เคียงกัน ใช้วัดว่าโมเดลแยก taxonomy ได้จริงไหม
- real-prior eval หรือ shadow eval: distribution ใกล้ production ใช้วัด false positive, analyst workload และ calibration

อย่าปนสองเป้าหมายนี้เป็นตัวเลขเดียว เพราะ balanced eval ตอบเรื่องความสามารถในการแยก class ส่วน real-prior eval ตอบเรื่องความเหมาะกับ workflow จริง

## What Not To Do

- อย่า downsample `failed_login_bruteforce` ทันทีถ้า source training split balanced อยู่แล้ว
- อย่าเพิ่ม timeout เพื่อซ่อน generation loop เพราะ latency metric จะเสียและ root cause ยังอยู่
- อย่าเพิ่ม synthetic records จำนวนมากโดยไม่มี hard-case rationale
- อย่าใช้ fixed test split เพื่อเลือก sampling weight หรือ prompt wording
- อย่า claim ว่าโมเดล detect compromise ได้ ให้ใช้ภาษา triage เช่น suspicious pattern, evidence, recommended investigation

## Implementation Checklist

- [ ] เพิ่ม distribution report ใน evaluator: expected labels, predicted labels, invalid count
- [ ] เพิ่ม confusion matrix ใน markdown report
- [ ] เพิ่ม macro-F1 หรือ balanced accuracy หลัง output contract stable
- [ ] สร้าง v3 hard-case plan จาก Phase 5/6 confusion
- [ ] เพิ่ม training sampler หรือ data-mixture config ถ้า v3 dataset ไม่ balanced
- [ ] อัปเดต `docs/data-card.md` เมื่อเปลี่ยน source distribution หรือ sampling policy
- [ ] รัน smoke/mini eval ก่อนแตะ fixed test split

## Work Log

Append-only log สำหรับบันทึกว่าเอกสารนี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-21 | Codex | Created label imbalance and prediction collapse guidance page | `docs/label-imbalance-and-prediction-collapse.md` | Drafted |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-21 | Treat Phase 6 label skew as prediction collapse unless source distribution proves otherwise | Current generated/train/validation/test/mini splits are label-balanced, while Phase 5 predictions over-concentrate on `failed_login_bruteforce` | Phase 6 v3 work should focus on output contract stability, confusion analysis, hard contrast examples, and imbalance-aware metrics before changing the fixed split |

## Related pages

- [[poc-plan]]
- [[evaluation-metrics-rationale]]
- [[data-card]]
- [[dataset-input-output-format]]
- [[output-structure-fix/phase-5-mini-semantic-eval]]
- [[output-structure-fix/phase-6-v3-or-runtime-decision]]
- [[output-structure-fix/phase-6-1-evidence-constraints]]
- [[References]]

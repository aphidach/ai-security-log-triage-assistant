# Model Output Notes

**Summary**

พื้นที่นี้ใช้เก็บบันทึกผลลัพธ์ของ model แต่ละ version แยกจาก day plan เพื่อให้เทียบ run ได้ง่ายว่า config ไหน train อย่างไร serve อย่างไร output หลุดตรงไหน และควรแก้รอบถัดไปอย่างไร

**Sources**

- `AGENTS.md` สำหรับ schema contract และ evaluation rules ของ POC (source: AGENTS.md)
- `docs/Day6.md` สำหรับสถานะ GPU training, smoke evaluation และ comparison gap ล่าสุด (source: docs/Day6.md)
- `ml/unsloth/config.example.yaml` สำหรับ config path แรกของ LFM2-350M + LoRA (source: ml/unsloth/config.example.yaml)
- `reports/openai-finetune-eval.json` สำหรับ smoke evaluation ของ OpenAI-compatible endpoint (source: reports/openai-finetune-eval.json)
- `reports/openai-compatible-eval.json` สำหรับ prompt v2 structured-output smoke evaluation ล่าสุด (source: reports/openai-compatible-eval.json)
- Unsloth Studio run note และ screenshot วันที่ 2026-05-19 สำหรับ artifact `unsloth_LFM2-350M_1779162226`, instruction tuning files และ LoRA 16-bit load profile (source: user-provided Codex thread note, 2026-05-19)

**Last updated**

2026-05-19

## Pages

- [[model-output/v1-lfm2-350m-security-triage]]: บันทึก v1 baseline และ latest v2 smoke run ของ `unsloth_LFM2-350M_1779162226` บน base `unsloth/LFM2-350M` เดิม
- [[model-output/template]]: template สำหรับบันทึก model output version ถัดไป

## How To Use

เมื่อมีการ train หรือ serve model รอบใหม่ ให้ copy โครงจาก [[model-output/template]] แล้วตั้งชื่อแบบ:

```text
docs/model-output/vN-short-model-name.md
```

แต่ละหน้าควรบันทึกอย่างน้อย:

- model/base/adapter config
- dataset และ split ที่ใช้
- training profile
- serve/runtime path
- local inference examples
- API/evaluator results
- failure modes
- decision ว่ารอบถัดไปจะปรับอะไร

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-18 | Codex | Created model-output documentation area for versioned model behavior notes | `docs/model-output/README.md` | Done |
| 2026-05-19 | Codex | Linked the latest prompt v2 structured-output smoke result from the v1 model-output notes | `docs/model-output/v1-lfm2-350m-security-triage.md`, `reports/openai-compatible-eval.json` | Done |
| 2026-05-19 | Codex | Clarified that the latest prompt v2 smoke belongs to the new Unsloth Studio artifact `unsloth_LFM2-350M_1779162226`, served as a LoRA run on the same LFM2-350M base | `docs/model-output/v1-lfm2-350m-security-triage.md` | Done |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-18 | แยกบันทึก model output ออกจาก Day plan | Day plan บอกสถานะงาน ส่วน model-output ต้องเก็บ behavior ของแต่ละ model version เพื่อเทียบซ้ำได้ | version ถัดไปจะมี template เดียวกันและไม่ปนกับ log รายวัน |
| 2026-05-19 | ใช้หน้า v1 เป็นบันทึกต่อเนื่องของ latest v2 smoke ชั่วคราว | ผู้ใช้ต้องการแก้หน้าเดิมให้สะท้อนว่า run ล่าสุดเป็น model artifact ใหม่ แต่ base model ยังเดิม | เอกสารแยก identity ระหว่าง base model, served alias และ trained artifact ให้ชัดขึ้น |

## Related pages

- [[Day6]]
- [[fine-tuning-notes]]
- [[triage-output-schema]]
- [[evaluation-metrics-rationale]]

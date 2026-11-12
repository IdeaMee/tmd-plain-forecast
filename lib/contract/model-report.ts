// รายงานโมเดลของหน้า /model (Zod) เขียนมือให้ตรงกับ lib/generated/model-report.schema.json
// (สร้างโดย scripts/export_model_report.py จาก src/tmd_plain/model_report.py) · model-report.test.ts ตรวจทั้งสองฝั่ง
import { z } from "zod";

const num = z.number();
const record = z.record(z.string(), num);

const wordScore = z.strictObject({ word: z.string(), score: num });

export const MODEL_REPORT_IDS = ["sentence-role", "warning-role"] as const;

export const modelReportItemSchema = z.strictObject({
  id: z.enum(MODEL_REPORT_IDS),
  title_th: z.string(),
  group_th: z.string(),
  split_note_th: z.string(),
  labels: z.array(z.string()).min(1),
  labels_th: z.record(z.string(), z.string()),
  chosen: z.string(),
  label_source_th: z.string(),
  pipeline: z.array(
    z.strictObject({ id: z.string(), title_th: z.string(), kind: z.enum(["rule", "ml"]), detail_th: z.string() }),
  ),
  splits: z.array(z.strictObject({ split: z.string(), total: z.number().int(), by_label: record })),
  by_doc_type: z.record(z.string(), record),
  token_examples: z.array(
    z.strictObject({
      unit_id: z.string(),
      label: z.string(),
      text: z.string(),
      tokens: z.array(z.string()),
      dropped: z.array(z.string()),
      kept: z.array(z.string()),
      counts: record,
    }),
  ),
  top_words: z.record(z.string(), z.array(wordScore)),
  nb_examples: z.array(
    z.strictObject({
      unit_id: z.string(),
      text: z.string(),
      true_label: z.string(),
      predicted: z.string(),
      correct: z.boolean(),
      log_prior: record,
      log_score: record,
      posterior: record,
      push_words: z.array(wordScore),
      unknown_words: z.array(z.string()),
    }),
  ),
  knn_examples: z.array(
    z.strictObject({
      unit_id: z.string(),
      text: z.string(),
      true_label: z.string(),
      predicted: z.string(),
      neighbors: z.array(
        z.strictObject({ unit_id: z.string(), text: z.string(), label: z.string(), distance: num }),
      ),
    }),
  ),
  tuning: z.strictObject({
    nb_m_factor: z.array(z.strictObject({ value: num, dev_accuracy: num })),
    knn_k: z.array(z.strictObject({ value: num, dev_accuracy: num })),
    best_m_factor: num,
    best_k: z.number().int(),
    vocab_train: z.number().int(),
  }),
  results: z.array(
    z.strictObject({ name: z.string(), dev: num, test_all: num, test_all_weighted: num.nullable(), test_new: num }),
  ),
  confusion: z.array(z.strictObject({ name: z.string(), matrix: z.array(z.array(z.number().int())) })),
  learning_curve: z.array(
    z.strictObject({
      fraction: num,
      train_groups: z.number().int(),
      train_units: z.number().int(),
      nb_dev_accuracy: num,
      nb_dev_macro_f1: num,
      knn_dev_accuracy: num,
      knn_dev_macro_f1: num,
    }),
  ),
  mistakes: z.array(
    z.strictObject({
      unit_id: z.string(),
      text: z.string(),
      true_label: z.string(),
      predicted: z.string(),
      confidence: num,
      note_th: z.string(),
    }),
  ),
  facts: z.strictObject({
    total_units: z.number().int(),
    keyword_agrees_with_labels: z.number().int(),
    other_units: z.number().int(),
    vocab_all: z.number().int(),
    num_token: z.string(),
  }),
});

export const modelReportSchema = z.strictObject({
  version: z.string(),
  models: z.array(modelReportItemSchema).min(1),
});

export type ModelReport = z.infer<typeof modelReportSchema>;
export type SentenceRoleReport = z.infer<typeof modelReportItemSchema>;
export type ModelReportId = (typeof MODEL_REPORT_IDS)[number];

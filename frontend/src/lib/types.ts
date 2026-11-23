export type VerdictType = "danger" | "caution" | "fewer_concerns";

export interface ExtractedField {
  value?: string | null;
  confidence: number;
  source_snippet?: string;
}

export interface RedFlag {
  id?: string;
  rule_id?: string;
  title: string;
  severity: "high" | "medium" | "low" | "danger" | "caution";
  explanation?: string;
  description?: string;
  evidence_snippet?: string;
}

export interface QuestionToAsk {
  question: string;
  reason?: string;
}

export interface Helpline {
  name: string;
  number: string;
  hours?: string;
  description?: string;
}

export interface AnalysisResponse {
  verdict: VerdictType;
  score: number;
  language: string;
  input_summary: string;
  extracted: Record<string, ExtractedField>;
  flags: RedFlag[];
  missing_clauses: string[];
  questions_to_ask: QuestionToAsk[];
  unverifiable: string[];
  helplines: Helpline[];
  audio_script_bn: string;
}

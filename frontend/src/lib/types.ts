/**
 * TypeScript type definitions.
 * Supports Indonesian values: HIJAU, KUNING, MERAH, POSITIF, NETRAL, NEGATIF
 */

export type RiskLevel = "HIJAU" | "KUNING" | "MERAH";
export type SentimentLabel = "POSITIF" | "NETRAL" | "NEGATIF";

export interface SentimentScore {
  vader_scores: {
    compound: number;
    positive: number;
    negative: number;
    neutral: number;
  };
  transformer_scores: {
    label: string;
    score: number;
    confidence: number;
  };
  consensus_score: number;
  sentiment_label: SentimentLabel;
  confidence: number;
  text_length: number;
}

export interface SentimentAnalysis {
  total_texts: number;
  valid_analyses: number;
  average_score: number;
  std_dev?: number;
  min_score?: number;
  max_score?: number;
  positive_count: number;
  neutral_count: number;
  negative_count: number;
  details: SentimentScore[];
}

export interface LegalCase {
  case_number: string;
  case_date: string;
  case_title?: string;
  case_type: string; // pidana, perdata, tata usaha negara, niaga
  verdict_summary?: string;
  severity: "tinggi" | "sedang" | "rendah" | "tidak ada";
  source_url?: string;
}

export interface LegalRecords {
  company_name: string;
  cases_found: number;
  cases: LegalCase[];
  max_severity: string; // tinggi, sedang, rendah, tidak ada
  timestamp: string;
  source: string;
  error?: string;
}

export interface RiskAssessment {
  risk_score: number;
  risk_level: RiskLevel;
  sentiment_component: number;
  mentions_component: number;
  legal_component: number;
  details: {
    total_texts_analyzed: number;
    positive_texts: number;
    negative_texts: number;
    legal_cases_found: number;
    max_case_severity: string;
  };
  recommendation: string; // Bahasa Indonesia
}

export interface NewsArticle {
  title: string;
  summary: string;
  source_url: string;
  date?: string;
  sentiment_label: SentimentLabel;
  sentiment_score: number;
  confidence: number;
}

export interface NewsAnalysis {
  company_name: string;
  total_articles: number;
  positive_count: number;
  neutral_count: number;
  negative_count: number;
  articles: NewsArticle[];
  timestamp: string;
  status: "sukses" | "gagal";
  error?: string;
}

export interface CompanyAnalysisResult {
  company_name: string;
  status: "success" | "error";
  analysis: {
    risk_assessment: RiskAssessment;
    sentiment_analysis: SentimentAnalysis;
    legal_records: LegalRecords;
    news_analysis?: NewsAnalysis;
    perplexity_sources?: string[];
    perplexity_news_sources?: string[];
  };
  timestamp: string;
  error?: string;
}

export interface AnalysisState {
  isLoading: boolean;
  result: CompanyAnalysisResult | null;
  error: string | null;
  history: CompanyAnalysisResult[];
}


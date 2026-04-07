export interface HealthResponse {
  message: string;
}

export interface UploadResponse {
  message: string;
  filename: string;
  saved_path: string;
  suggested_metadata?: {
    subject: string;
    grade: string;
    topic: string;
  };
}

export interface IndexResponse {
  message: string;
  chunk_count: number;
  source_count: Record<string, number>;
}

export interface QueryRequest {
  query: string;
  source_names?: string[];
  subject?: string;
  grade?: string;
  topic?: string;
  exclude_ocr?: boolean;
  teaching_mode?: string;
  explanation_depth?: string;
}

export interface ExerciseRequest {
  query: string;
  style: '1' | '2' | '3';
  source_names?: string[];
  subject?: string;
  grade?: string;
  topic?: string;
  exclude_ocr?: boolean;
  difficulty?: string;
  expected_count?: number;
}

export interface MaterialSummary {
  id: string;
  filename: string;
  source_type: string;
  parser_name: string;
  is_ocr: boolean;
  chunk_count: number;
  status: string;
  subject: string;
  grade: string;
  topic: string;
  subject_source: 'manual' | 'ai' | 'empty';
  grade_source: 'manual' | 'ai' | 'empty';
  topic_source: 'manual' | 'ai' | 'empty';
  suggested_subject: string;
  suggested_grade: string;
  suggested_topic: string;
}

export interface MaterialsResponse {
  materials: MaterialSummary[];
}

export interface DeleteMaterialResponse {
  message: string;
  filename: string;
  index_ready: boolean;
  chunk_count: number;
}

export interface UpdateMaterialMetadataRequest {
  subject: string;
  grade: string;
  topic: string;
}

export interface UpdateMaterialMetadataResponse {
  message: string;
  filename: string;
  metadata: UpdateMaterialMetadataRequest;
}

export interface SuggestMaterialMetadataResponse {
  message: string;
  filename: string;
  suggested_metadata: UpdateMaterialMetadataRequest;
}

export interface SourceSummary {
  source_types: string[];
  primary_source_type: string;
  contains_ocr: boolean;
  note: string;
}

export interface RetrievedChunk {
  id: string;
  source: string;
  source_type: string;
  parser_name: string;
  is_ocr: boolean;
  content: string;
  distance: number;
  keyword_score?: number;
}

export interface TextModeResponse {
  mode: 'qa' | 'teaching';
  display_type: 'text';
  query: string;
  answer: string;
  source_summary: SourceSummary;
  retrieved_chunks: RetrievedChunk[];
}

export interface ExerciseItem {
  title: string;
  problem: string;
  intent: string;
  hint: string;
  answer?: string;
  explanation?: string;
}

export interface ExerciseAnswer {
  topic: string;
  grade: string;
  difficulty?: string;
  requested_count?: number;
  exercises: ExerciseItem[];
}

export interface ExerciseResponse {
  mode: 'exercise';
  display_type: 'exercise_set';
  query: string;
  style: '1' | '2' | '3';
  answer: ExerciseAnswer;
  source_summary: SourceSummary;
  retrieved_chunks: RetrievedChunk[];
}

export interface ApiErrorResponse {
  error?: string;
  detail?: string | { msg?: string }[];
  message?: string;
}

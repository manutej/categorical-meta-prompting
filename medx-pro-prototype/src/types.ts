/**
 * MedX Pro - Core Types
 * Clean, practical type definitions for the voice-first clinical platform
 */

// ============================================================================
// VOICE & TRANSCRIPTION
// ============================================================================

export interface TranscriptionResult {
  text: string;
  confidence: number;
  language: string;
  isFinal: boolean;
  timestamp: number;
}

export interface VoiceCaptureConfig {
  apiKey: string;
  language: 'es-MX' | 'es-ES' | 'en-US';
  sampleRate: number;
}

// ============================================================================
// MEDICAL ENTITIES
// ============================================================================

export type EntityType = 'diagnosis' | 'medication' | 'procedure' | 'vital' | 'allergy' | 'symptom';

export interface MedicalEntity {
  type: EntityType;
  value: string;
  code?: {
    system: 'ICD-10' | 'RxNorm' | 'CPT' | 'LOINC';
    code: string;
    display: string;
  };
  confidence: number;
}

// ============================================================================
// CLINICAL DOCUMENTS
// ============================================================================

export interface SOAPNote {
  id: string;
  patientId: string;
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
  entities: MedicalEntity[];
  status: 'draft' | 'review' | 'final';
  createdAt: Date;
  updatedAt: Date;
}

export type SOAPSection = 'subjective' | 'objective' | 'assessment' | 'plan';

// ============================================================================
// VOICE COMMANDS
// ============================================================================

export type CommandIntent =
  | 'nuevo_paciente'
  | 'seccion'
  | 'guardar'
  | 'corregir'
  | 'dictar'
  | 'leer'
  | 'siguiente'
  | 'anterior'
  | 'cancelar'
  | 'ayuda';

export interface VoiceCommand {
  intent: CommandIntent;
  args: Record<string, string>;
  confidence: number;
  rawText: string;
}

export interface CommandResult {
  success: boolean;
  intent: CommandIntent;
  message: string;
  data?: unknown;
}

// ============================================================================
// APPLICATION STATE
// ============================================================================

export interface AppState {
  isRecording: boolean;
  currentSection: SOAPSection;
  note: SOAPNote;
  mode: 'command' | 'dictation';
  history: string[];
}

// ============================================================================
// EVENTS
// ============================================================================

export type MedXEvent =
  | { type: 'TRANSCRIPTION'; data: TranscriptionResult }
  | { type: 'ENTITIES_EXTRACTED'; data: MedicalEntity[] }
  | { type: 'COMMAND_DETECTED'; data: VoiceCommand }
  | { type: 'COMMAND_EXECUTED'; data: CommandResult }
  | { type: 'NOTE_UPDATED'; data: SOAPNote }
  | { type: 'SECTION_CHANGED'; data: SOAPSection }
  | { type: 'MODE_CHANGED'; data: 'command' | 'dictation' }
  | { type: 'ERROR'; error: Error };

export type EventHandler = (event: MedXEvent) => void;

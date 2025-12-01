/**
 * MedX Pro - Core Application
 *
 * Simplified, practical implementation of the voice-first
 * clinical documentation platform.
 */

import {
  TranscriptionResult,
  MedicalEntity,
  EntityType,
  SOAPNote,
  SOAPSection,
  VoiceCommand,
  CommandIntent,
  CommandResult,
  AppState,
  MedXEvent,
  EventHandler
} from './types';

// ============================================================================
// EVENT BUS
// ============================================================================

class EventBus {
  private handlers: EventHandler[] = [];

  on(handler: EventHandler): () => void {
    this.handlers.push(handler);
    return () => {
      this.handlers = this.handlers.filter(h => h !== handler);
    };
  }

  emit(event: MedXEvent): void {
    this.handlers.forEach(h => h(event));
  }
}

export const eventBus = new EventBus();

// ============================================================================
// VOICE COMMAND RECOGNIZER
// ============================================================================

interface CommandPattern {
  intent: CommandIntent;
  patterns: RegExp[];
  extract: (match: RegExpMatchArray, rawText?: string) => Record<string, string>;
}

const COMMANDS: CommandPattern[] = [
  {
    intent: 'nuevo_paciente',
    patterns: [/^nuevo\s+paciente$/i, /^nueva\s+consulta$/i],
    extract: () => ({})
  },
  {
    intent: 'seccion',
    patterns: [/^(?:ir\s+a\s+)?secci[oó]n\s+(.+)$/i, /^(subjetivo|objetivo|evaluaci[oó]n|plan)$/i],
    extract: (m) => ({ section: normalizeSection(m[1]) })
  },
  {
    intent: 'guardar',
    patterns: [/^guardar$/i, /^guardar\s+y\s+cerrar$/i],
    extract: (_match, text) => ({ close: text?.includes('cerrar') ? 'true' : 'false' })
  },
  {
    intent: 'dictar',
    patterns: [/^dictar$/i, /^modo\s+dictado$/i],
    extract: () => ({})
  },
  {
    intent: 'siguiente',
    patterns: [/^siguiente$/i, /^siguiente\s+secci[oó]n$/i],
    extract: () => ({})
  },
  {
    intent: 'anterior',
    patterns: [/^anterior$/i, /^atr[aá]s$/i],
    extract: () => ({})
  },
  {
    intent: 'leer',
    patterns: [/^leer$/i, /^repetir$/i],
    extract: () => ({})
  },
  {
    intent: 'cancelar',
    patterns: [/^cancelar$/i, /^deshacer$/i],
    extract: () => ({})
  },
  {
    intent: 'ayuda',
    patterns: [/^ayuda$/i, /^comandos$/i],
    extract: () => ({})
  }
];

const SECTION_MAP: Record<string, SOAPSection> = {
  'subjetivo': 'subjective',
  'subjetiva': 'subjective',
  'objetivo': 'objective',
  'objetiva': 'objective',
  'evaluación': 'assessment',
  'evaluacion': 'assessment',
  'valoración': 'assessment',
  'diagnostico': 'assessment',
  'plan': 'plan',
  'tratamiento': 'plan'
};

function normalizeSection(input: string): string {
  const normalized = input.toLowerCase().trim();
  return SECTION_MAP[normalized] || normalized;
}

export function recognizeCommand(text: string): VoiceCommand | null {
  const normalized = text.toLowerCase().trim().replace(/[.,!?¿¡]/g, '');

  for (const cmd of COMMANDS) {
    for (const pattern of cmd.patterns) {
      const match = normalized.match(pattern);
      if (match) {
        return {
          intent: cmd.intent,
          args: cmd.extract(match),
          confidence: 0.9,
          rawText: text
        };
      }
    }
  }
  return null;
}

// ============================================================================
// MEDICAL ENTITY EXTRACTOR
// ============================================================================

interface MedicalTerm {
  term: string;
  aliases: string[];
  type: EntityType;
  code?: { system: 'ICD-10' | 'RxNorm' | 'CPT' | 'LOINC'; code: string; display: string };
}

const MEDICAL_TERMS: MedicalTerm[] = [
  // Diagnoses
  { term: 'diabetes tipo 2', aliases: ['diabetes', 'dm2'], type: 'diagnosis',
    code: { system: 'ICD-10', code: 'E11', display: 'Type 2 diabetes' }},
  { term: 'hipertensión', aliases: ['presión alta', 'hta'], type: 'diagnosis',
    code: { system: 'ICD-10', code: 'I10', display: 'Hypertension' }},
  { term: 'dolor torácico', aliases: ['dolor de pecho'], type: 'symptom',
    code: { system: 'ICD-10', code: 'R07.9', display: 'Chest pain' }},
  { term: 'cefalea', aliases: ['dolor de cabeza', 'migraña'], type: 'symptom',
    code: { system: 'ICD-10', code: 'R51', display: 'Headache' }},

  // Medications
  { term: 'metformina', aliases: ['glucophage'], type: 'medication',
    code: { system: 'RxNorm', code: '6809', display: 'Metformin' }},
  { term: 'lisinopril', aliases: [], type: 'medication',
    code: { system: 'RxNorm', code: '29046', display: 'Lisinopril' }},
  { term: 'aspirina', aliases: ['asa'], type: 'medication',
    code: { system: 'RxNorm', code: '1191', display: 'Aspirin' }},
  { term: 'omeprazol', aliases: [], type: 'medication',
    code: { system: 'RxNorm', code: '7646', display: 'Omeprazole' }},

  // Allergies
  { term: 'alergia a penicilina', aliases: ['alérgico a penicilina'], type: 'allergy',
    code: { system: 'RxNorm', code: '7984', display: 'Penicillin allergy' }},

  // Procedures
  { term: 'electrocardiograma', aliases: ['ekg', 'ecg'], type: 'procedure',
    code: { system: 'CPT', code: '93000', display: 'ECG' }},
  { term: 'radiografía de tórax', aliases: ['rx tórax', 'placa'], type: 'procedure',
    code: { system: 'CPT', code: '71046', display: 'Chest X-ray' }},
];

// Vital sign patterns
const VITAL_PATTERNS = {
  bp: /(\d{2,3})\s*[\/\\]\s*(\d{2,3})/,
  hr: /(\d{2,3})\s*(?:lpm|latidos)/i,
  temp: /(\d{2}(?:\.\d)?)\s*(?:°|grados)/i,
  spo2: /(\d{2,3})\s*%/
};

export function extractEntities(text: string): MedicalEntity[] {
  const entities: MedicalEntity[] = [];
  const normalized = text.toLowerCase();

  // Extract medical terms
  for (const term of MEDICAL_TERMS) {
    const allPatterns = [term.term, ...term.aliases];
    for (const pattern of allPatterns) {
      if (normalized.includes(pattern)) {
        entities.push({
          type: term.type,
          value: term.term,
          code: term.code,
          confidence: 0.9
        });
        break;
      }
    }
  }

  // Extract vital signs
  const bpMatch = text.match(VITAL_PATTERNS.bp);
  if (bpMatch) {
    entities.push({
      type: 'vital',
      value: `Presión: ${bpMatch[1]}/${bpMatch[2]} mmHg`,
      code: { system: 'LOINC', code: '85354-9', display: 'Blood pressure' },
      confidence: 0.95
    });
  }

  const hrMatch = text.match(VITAL_PATTERNS.hr);
  if (hrMatch) {
    entities.push({
      type: 'vital',
      value: `FC: ${hrMatch[1]} lpm`,
      code: { system: 'LOINC', code: '8867-4', display: 'Heart rate' },
      confidence: 0.95
    });
  }

  return entities;
}

// ============================================================================
// SOAP NOTE MANAGER
// ============================================================================

export function createNote(patientId: string): SOAPNote {
  return {
    id: crypto.randomUUID?.() || `note-${Date.now()}`,
    patientId,
    subjective: '',
    objective: '',
    assessment: '',
    plan: '',
    entities: [],
    status: 'draft',
    createdAt: new Date(),
    updatedAt: new Date()
  };
}

export function updateNoteSection(note: SOAPNote, section: SOAPSection, content: string): SOAPNote {
  return {
    ...note,
    [section]: note[section] + (note[section] ? ' ' : '') + content,
    updatedAt: new Date()
  };
}

export function addEntitiesToNote(note: SOAPNote, entities: MedicalEntity[]): SOAPNote {
  const existingValues = new Set(note.entities.map(e => e.value));
  const newEntities = entities.filter(e => !existingValues.has(e.value));

  return {
    ...note,
    entities: [...note.entities, ...newEntities],
    updatedAt: new Date()
  };
}

// ============================================================================
// MAIN APPLICATION CLASS
// ============================================================================

export class MedXPro {
  private state: AppState;
  private sections: SOAPSection[] = ['subjective', 'objective', 'assessment', 'plan'];

  constructor(patientId: string = 'demo-patient') {
    this.state = {
      isRecording: false,
      currentSection: 'subjective',
      note: createNote(patientId),
      mode: 'command',
      history: []
    };
  }

  /**
   * Process incoming transcription
   */
  processTranscription(result: TranscriptionResult): void {
    eventBus.emit({ type: 'TRANSCRIPTION', data: result });

    // Check if it's a command
    const command = recognizeCommand(result.text);

    // Navigation commands ALWAYS work (even in dictation mode)
    const alwaysActiveCommands: CommandIntent[] = [
      'siguiente', 'anterior', 'seccion', 'guardar', 'cancelar', 'ayuda', 'nuevo_paciente'
    ];

    if (command && (this.state.mode === 'command' || alwaysActiveCommands.includes(command.intent))) {
      eventBus.emit({ type: 'COMMAND_DETECTED', data: command });
      const cmdResult = this.executeCommand(command);
      eventBus.emit({ type: 'COMMAND_EXECUTED', data: cmdResult });
      return;
    }

    // It's dictation content
    if (this.state.mode === 'dictation' || !command) {
      // Extract medical entities
      const entities = extractEntities(result.text);
      if (entities.length > 0) {
        eventBus.emit({ type: 'ENTITIES_EXTRACTED', data: entities });
        this.state.note = addEntitiesToNote(this.state.note, entities);
      }

      // Add content to current section
      this.state.note = updateNoteSection(
        this.state.note,
        this.state.currentSection,
        result.text
      );
      this.state.history.push(result.text);

      eventBus.emit({ type: 'NOTE_UPDATED', data: this.state.note });
    }
  }

  /**
   * Execute a voice command
   */
  private executeCommand(command: VoiceCommand): CommandResult {
    switch (command.intent) {
      case 'nuevo_paciente':
        this.state.note = createNote(`patient-${Date.now()}`);
        this.state.currentSection = 'subjective';
        return { success: true, intent: command.intent, message: 'Nueva consulta iniciada' };

      case 'seccion':
        const section = command.args.section as SOAPSection;
        if (this.sections.includes(section)) {
          this.state.currentSection = section;
          eventBus.emit({ type: 'SECTION_CHANGED', data: section });
          return { success: true, intent: command.intent, message: `Sección: ${section}` };
        }
        return { success: false, intent: command.intent, message: 'Sección no válida' };

      case 'dictar':
        this.state.mode = 'dictation';
        eventBus.emit({ type: 'MODE_CHANGED', data: 'dictation' });
        return { success: true, intent: command.intent, message: 'Modo dictado activado' };

      case 'siguiente':
        const nextIdx = (this.sections.indexOf(this.state.currentSection) + 1) % 4;
        this.state.currentSection = this.sections[nextIdx];
        eventBus.emit({ type: 'SECTION_CHANGED', data: this.state.currentSection });
        return { success: true, intent: command.intent, message: `Siguiente: ${this.state.currentSection}` };

      case 'anterior':
        const prevIdx = this.sections.indexOf(this.state.currentSection) - 1;
        this.state.currentSection = this.sections[prevIdx < 0 ? 3 : prevIdx];
        eventBus.emit({ type: 'SECTION_CHANGED', data: this.state.currentSection });
        return { success: true, intent: command.intent, message: `Anterior: ${this.state.currentSection}` };

      case 'leer':
        const content = this.state.note[this.state.currentSection];
        return { success: true, intent: command.intent, message: content || 'Sin contenido', data: { content } };

      case 'guardar':
        this.state.note.status = 'review';
        return { success: true, intent: command.intent, message: 'Nota guardada', data: this.state.note };

      case 'cancelar':
        if (this.state.history.length > 0) {
          this.state.history.pop();
          return { success: true, intent: command.intent, message: 'Última entrada cancelada' };
        }
        return { success: false, intent: command.intent, message: 'Nada que cancelar' };

      case 'ayuda':
        const commands = ['nuevo paciente', 'sección [nombre]', 'dictar', 'siguiente', 'anterior', 'leer', 'guardar', 'cancelar'];
        return { success: true, intent: command.intent, message: `Comandos: ${commands.join(', ')}` };

      default:
        return { success: false, intent: command.intent, message: 'Comando no reconocido' };
    }
  }

  /**
   * Get current state
   */
  getState(): AppState {
    return { ...this.state };
  }

  /**
   * Get current note
   */
  getNote(): SOAPNote {
    return { ...this.state.note };
  }

  /**
   * Switch to command mode
   */
  setCommandMode(): void {
    this.state.mode = 'command';
    eventBus.emit({ type: 'MODE_CHANGED', data: 'command' });
  }

  /**
   * Switch to dictation mode
   */
  setDictationMode(): void {
    this.state.mode = 'dictation';
    eventBus.emit({ type: 'MODE_CHANGED', data: 'dictation' });
  }
}

// Export for testing
export { COMMANDS, MEDICAL_TERMS, SECTION_MAP };

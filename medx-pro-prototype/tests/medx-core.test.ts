/**
 * MedX Pro - Core Tests
 *
 * Tests for voice command recognition, entity extraction, and SOAP note management
 */

import {
  MedXPro,
  recognizeCommand,
  extractEntities,
  createNote,
  updateNoteSection,
  addEntitiesToNote
} from '../src/medx-core';
import { TranscriptionResult, SOAPNote, MedicalEntity } from '../src/types';

// ============================================================================
// VOICE COMMAND RECOGNITION TESTS
// ============================================================================

describe('Voice Command Recognition', () => {
  test('recognizes "nuevo paciente" command', () => {
    const cmd = recognizeCommand('nuevo paciente');
    expect(cmd).not.toBeNull();
    expect(cmd?.intent).toBe('nuevo_paciente');
  });

  test('recognizes "nueva consulta" command', () => {
    const cmd = recognizeCommand('nueva consulta');
    expect(cmd).not.toBeNull();
    expect(cmd?.intent).toBe('nuevo_paciente');
  });

  test('recognizes section navigation commands', () => {
    const tests = [
      { input: 'sección subjetivo', section: 'subjective' },
      { input: 'sección objetivo', section: 'objective' },
      { input: 'sección evaluación', section: 'assessment' },
      { input: 'sección plan', section: 'plan' },
      { input: 'ir a sección plan', section: 'plan' }
    ];

    for (const t of tests) {
      const cmd = recognizeCommand(t.input);
      expect(cmd).not.toBeNull();
      expect(cmd?.intent).toBe('seccion');
      expect(cmd?.args.section).toBe(t.section);
    }
  });

  test('recognizes "siguiente" command', () => {
    const cmd = recognizeCommand('siguiente');
    expect(cmd?.intent).toBe('siguiente');
  });

  test('recognizes "anterior" command', () => {
    const cmd = recognizeCommand('anterior');
    expect(cmd?.intent).toBe('anterior');

    const cmd2 = recognizeCommand('atrás');
    expect(cmd2?.intent).toBe('anterior');
  });

  test('recognizes "guardar" command', () => {
    const cmd = recognizeCommand('guardar');
    expect(cmd?.intent).toBe('guardar');
    expect(cmd?.args.close).toBe('false');
  });

  test('recognizes "guardar y cerrar" command', () => {
    const cmd = recognizeCommand('guardar y cerrar');
    expect(cmd?.intent).toBe('guardar');
  });

  test('recognizes "dictar" command', () => {
    const cmd = recognizeCommand('dictar');
    expect(cmd?.intent).toBe('dictar');
  });

  test('recognizes "ayuda" command', () => {
    const cmd = recognizeCommand('ayuda');
    expect(cmd?.intent).toBe('ayuda');
  });

  test('returns null for non-command text', () => {
    const cmd = recognizeCommand('El paciente presenta dolor de cabeza');
    expect(cmd).toBeNull();
  });

  test('is case insensitive', () => {
    const cmd = recognizeCommand('NUEVO PACIENTE');
    expect(cmd?.intent).toBe('nuevo_paciente');
  });

  test('handles punctuation', () => {
    const cmd = recognizeCommand('¿Ayuda?');
    expect(cmd?.intent).toBe('ayuda');
  });
});

// ============================================================================
// MEDICAL ENTITY EXTRACTION TESTS
// ============================================================================

describe('Medical Entity Extraction', () => {
  test('extracts diagnoses', () => {
    const entities = extractEntities('Paciente con hipertensión y diabetes tipo 2');

    expect(entities.length).toBeGreaterThanOrEqual(2);
    expect(entities.some(e => e.type === 'diagnosis' && e.value.includes('hipertensión'))).toBe(true);
    expect(entities.some(e => e.type === 'diagnosis' && e.value.includes('diabetes'))).toBe(true);
  });

  test('extracts medications', () => {
    const entities = extractEntities('Toma metformina 500 mg y lisinopril diario');

    expect(entities.some(e => e.type === 'medication' && e.value === 'metformina')).toBe(true);
    expect(entities.some(e => e.type === 'medication' && e.value === 'lisinopril')).toBe(true);
  });

  test('extracts symptoms', () => {
    const entities = extractEntities('Presenta cefalea y dolor torácico');

    expect(entities.some(e => e.type === 'symptom' && e.value === 'cefalea')).toBe(true);
    expect(entities.some(e => e.type === 'symptom' && e.value === 'dolor torácico')).toBe(true);
  });

  test('extracts allergies', () => {
    const entities = extractEntities('Tiene alergia a penicilina');

    expect(entities.some(e => e.type === 'allergy')).toBe(true);
  });

  test('extracts blood pressure vitals', () => {
    const entities = extractEntities('Presión arterial 140/90 mmHg');

    const bp = entities.find(e => e.type === 'vital' && e.value.includes('140/90'));
    expect(bp).toBeDefined();
    expect(bp?.code?.system).toBe('LOINC');
  });

  test('extracts heart rate vitals', () => {
    const entities = extractEntities('Frecuencia cardíaca 72 lpm');

    const hr = entities.find(e => e.type === 'vital' && e.value.includes('72'));
    expect(hr).toBeDefined();
  });

  test('extracts procedures', () => {
    const entities = extractEntities('Solicitar electrocardiograma');

    expect(entities.some(e => e.type === 'procedure' && e.value === 'electrocardiograma')).toBe(true);
  });

  test('includes medical codes when available', () => {
    const entities = extractEntities('Diagnóstico de hipertensión');

    const htn = entities.find(e => e.value.includes('hipertensión'));
    expect(htn?.code?.system).toBe('ICD-10');
    expect(htn?.code?.code).toBe('I10');
  });

  test('returns empty array for text without medical content', () => {
    const entities = extractEntities('Buenos días, cómo está');
    expect(entities.length).toBe(0);
  });
});

// ============================================================================
// SOAP NOTE MANAGEMENT TESTS
// ============================================================================

describe('SOAP Note Management', () => {
  test('creates a new note with all sections empty', () => {
    const note = createNote('patient-123');

    expect(note.id).toBeDefined();
    expect(note.patientId).toBe('patient-123');
    expect(note.subjective).toBe('');
    expect(note.objective).toBe('');
    expect(note.assessment).toBe('');
    expect(note.plan).toBe('');
    expect(note.status).toBe('draft');
    expect(note.entities).toEqual([]);
  });

  test('updates note section with content', () => {
    const note = createNote('p1');
    const updated = updateNoteSection(note, 'subjective', 'Dolor de cabeza');

    expect(updated.subjective).toBe('Dolor de cabeza');
    expect(updated.objective).toBe('');
  });

  test('appends content to existing section', () => {
    let note = createNote('p1');
    note = updateNoteSection(note, 'subjective', 'Primera parte.');
    note = updateNoteSection(note, 'subjective', 'Segunda parte.');

    expect(note.subjective).toBe('Primera parte. Segunda parte.');
  });

  test('adds entities to note', () => {
    const note = createNote('p1');
    const entities: MedicalEntity[] = [
      { type: 'diagnosis', value: 'hipertensión', confidence: 0.9 },
      { type: 'medication', value: 'metformina', confidence: 0.9 }
    ];

    const updated = addEntitiesToNote(note, entities);

    expect(updated.entities.length).toBe(2);
    expect(updated.entities[0].value).toBe('hipertensión');
  });

  test('does not add duplicate entities', () => {
    let note = createNote('p1');
    const entity: MedicalEntity = { type: 'diagnosis', value: 'hipertensión', confidence: 0.9 };

    note = addEntitiesToNote(note, [entity]);
    note = addEntitiesToNote(note, [entity]);

    expect(note.entities.length).toBe(1);
  });
});

// ============================================================================
// INTEGRATED MEDX PRO APPLICATION TESTS
// ============================================================================

describe('MedXPro Application', () => {
  let app: MedXPro;

  beforeEach(() => {
    app = new MedXPro('test-patient');
  });

  test('initializes with correct default state', () => {
    const state = app.getState();

    expect(state.isRecording).toBe(false);
    expect(state.currentSection).toBe('subjective');
    expect(state.mode).toBe('command');
    expect(state.note.patientId).toBe('test-patient');
  });

  test('processes "nuevo paciente" command', () => {
    const result: TranscriptionResult = {
      text: 'nuevo paciente',
      confidence: 0.95,
      language: 'es-MX',
      isFinal: true,
      timestamp: Date.now()
    };

    app.processTranscription(result);

    const state = app.getState();
    expect(state.currentSection).toBe('subjective');
  });

  test('navigates sections with "siguiente" command', () => {
    const commands = ['siguiente', 'siguiente', 'siguiente', 'siguiente'];
    const expectedSections = ['objective', 'assessment', 'plan', 'subjective'];

    commands.forEach((cmd, i) => {
      app.processTranscription({
        text: cmd,
        confidence: 0.95,
        language: 'es-MX',
        isFinal: true,
        timestamp: Date.now()
      });

      expect(app.getState().currentSection).toBe(expectedSections[i]);
    });
  });

  test('switches to dictation mode', () => {
    app.processTranscription({
      text: 'dictar',
      confidence: 0.95,
      language: 'es-MX',
      isFinal: true,
      timestamp: Date.now()
    });

    expect(app.getState().mode).toBe('dictation');
  });

  test('adds content in dictation mode', () => {
    app.setDictationMode();

    app.processTranscription({
      text: 'Paciente con diabetes',
      confidence: 0.95,
      language: 'es-MX',
      isFinal: true,
      timestamp: Date.now()
    });

    const note = app.getNote();
    expect(note.subjective).toContain('Paciente con diabetes');
    expect(note.entities.length).toBeGreaterThan(0);
  });

  test('extracts entities from dictated content', () => {
    app.setDictationMode();

    app.processTranscription({
      text: 'Toma metformina y lisinopril para hipertensión',
      confidence: 0.95,
      language: 'es-MX',
      isFinal: true,
      timestamp: Date.now()
    });

    const note = app.getNote();
    expect(note.entities.some(e => e.type === 'medication')).toBe(true);
    expect(note.entities.some(e => e.type === 'diagnosis')).toBe(true);
  });

  test('saves note and changes status', () => {
    app.processTranscription({
      text: 'guardar',
      confidence: 0.95,
      language: 'es-MX',
      isFinal: true,
      timestamp: Date.now()
    });

    expect(app.getNote().status).toBe('review');
  });
});

// ============================================================================
// EDGE CASES & ERROR HANDLING
// ============================================================================

describe('Edge Cases', () => {
  test('handles empty transcription', () => {
    const cmd = recognizeCommand('');
    expect(cmd).toBeNull();
  });

  test('handles whitespace-only transcription', () => {
    const cmd = recognizeCommand('   ');
    expect(cmd).toBeNull();
  });

  test('handles very long text', () => {
    const longText = 'palabra '.repeat(1000);
    const entities = extractEntities(longText);
    expect(Array.isArray(entities)).toBe(true);
  });

  test('handles mixed case in medical terms', () => {
    const entities = extractEntities('HIPERTENSIÓN arterial');
    expect(entities.length).toBeGreaterThan(0);
  });

  test('handles accented characters correctly', () => {
    const cmd = recognizeCommand('sección evaluación');
    expect(cmd?.args.section).toBe('assessment');
  });
});

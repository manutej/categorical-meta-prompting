/**
 * MedX Pro - Interactive Demo
 *
 * Demonstrates the complete voice-first clinical documentation workflow:
 * 1. Voice commands for navigation
 * 2. Real-time transcription (simulated)
 * 3. Medical entity extraction
 * 4. SOAP note generation
 */

import { MedXPro, eventBus, extractEntities, recognizeCommand } from './medx-core';
import { SimulatedTranscriber, createVoiceCapture } from './voice-capture';
import { TranscriptionResult, MedXEvent } from './types';

// ============================================================================
// DEMO SCENARIOS
// ============================================================================

const DEMO_ENCOUNTER = [
  // Commands
  { type: 'command', text: 'nuevo paciente', delay: 500 },

  // Dictation in Subjective section
  { type: 'dictation', text: 'dictar', delay: 800 },
  { type: 'content', text: 'Paciente masculino de 55 años que acude por dolor torácico de 2 horas de evolución', delay: 1500 },
  { type: 'content', text: 'Refiere dolor opresivo en región precordial que irradia a brazo izquierdo', delay: 1500 },
  { type: 'content', text: 'Tiene antecedentes de hipertensión y diabetes tipo 2', delay: 1500 },
  { type: 'content', text: 'Toma metformina 500 mg y lisinopril 10 mg diario', delay: 1500 },
  { type: 'content', text: 'Alergia a penicilina documentada', delay: 1000 },

  // Navigate to Objective
  { type: 'command', text: 'siguiente', delay: 800 },
  { type: 'content', text: 'Signos vitales: presión arterial 150/95 mmHg, frecuencia cardíaca 92 lpm', delay: 1500 },
  { type: 'content', text: 'Saturación de oxígeno 96%', delay: 1000 },
  { type: 'content', text: 'Paciente diaforético, ansioso, sin cianosis', delay: 1200 },

  // Navigate to Assessment
  { type: 'command', text: 'sección evaluación', delay: 800 },
  { type: 'content', text: 'Síndrome coronario agudo a descartar', delay: 1200 },
  { type: 'content', text: 'Hipertensión arterial descontrolada', delay: 1000 },
  { type: 'content', text: 'Diabetes mellitus tipo 2', delay: 1000 },

  // Navigate to Plan
  { type: 'command', text: 'siguiente', delay: 800 },
  { type: 'content', text: 'Solicitar electrocardiograma urgente', delay: 1200 },
  { type: 'content', text: 'Enzimas cardíacas troponina y CPK', delay: 1200 },
  { type: 'content', text: 'Administrar aspirina 300 mg sublingual', delay: 1200 },
  { type: 'content', text: 'Oxígeno suplementario si saturación menor a 94%', delay: 1200 },

  // Save
  { type: 'command', text: 'guardar', delay: 1000 }
];

// ============================================================================
// DEMO RUNNER
// ============================================================================

export class MedXDemo {
  private app: MedXPro;
  private transcriber: SimulatedTranscriber;
  private isRunning = false;

  constructor() {
    this.app = new MedXPro('demo-patient-001');

    // Set up event logging
    eventBus.on((event: MedXEvent) => {
      this.logEvent(event);
    });

    // Create simulated transcriber
    this.transcriber = createVoiceCapture(null, {
      onTranscript: (result) => this.app.processTranscription(result),
      onError: (error) => console.error('Error:', error),
      onClose: () => console.log('Closed')
    }) as SimulatedTranscriber;
  }

  /**
   * Log events with formatting
   */
  private logEvent(event: MedXEvent): void {
    const timestamp = new Date().toISOString().slice(11, 19);

    switch (event.type) {
      case 'TRANSCRIPTION':
        console.log(`[${timestamp}] 🎤 "${event.data.text}"`);
        break;

      case 'COMMAND_DETECTED':
        console.log(`[${timestamp}] ⚡ Comando: ${event.data.intent} ${JSON.stringify(event.data.args)}`);
        break;

      case 'COMMAND_EXECUTED':
        const icon = event.data.success ? '✅' : '❌';
        console.log(`[${timestamp}] ${icon} ${event.data.message}`);
        break;

      case 'ENTITIES_EXTRACTED':
        const entities = event.data.map(e => `${e.type}:${e.value}`).join(', ');
        console.log(`[${timestamp}] 🏥 Entidades: ${entities}`);
        break;

      case 'SECTION_CHANGED':
        console.log(`[${timestamp}] 📑 Sección: ${event.data}`);
        break;

      case 'MODE_CHANGED':
        console.log(`[${timestamp}] 🔄 Modo: ${event.data}`);
        break;

      case 'NOTE_UPDATED':
        // Silent - too verbose
        break;

      case 'ERROR':
        console.error(`[${timestamp}] ❌ Error:`, event.error);
        break;
    }
  }

  /**
   * Run the complete demo scenario
   */
  async runDemo(): Promise<void> {
    if (this.isRunning) {
      console.log('Demo already running');
      return;
    }

    this.isRunning = true;
    console.log('\n╔═══════════════════════════════════════════════════════════╗');
    console.log('║          MedX Pro - Demo de Documentación Clínica         ║');
    console.log('║                 "Speak. Heal. Done."                       ║');
    console.log('╚═══════════════════════════════════════════════════════════╝\n');

    await this.transcriber.connect();

    for (const step of DEMO_ENCOUNTER) {
      await this.delay(step.delay);

      // Simulate the transcription
      this.transcriber.simulateTranscription(step.text);
    }

    await this.delay(1000);
    this.printSummary();
    this.isRunning = false;
  }

  /**
   * Print final SOAP note summary
   */
  private printSummary(): void {
    const note = this.app.getNote();

    console.log('\n╔═══════════════════════════════════════════════════════════╗');
    console.log('║                    NOTA CLÍNICA SOAP                       ║');
    console.log('╚═══════════════════════════════════════════════════════════╝\n');

    console.log('📋 SUBJETIVO:');
    console.log(this.wrapText(note.subjective || '(vacío)', 60));
    console.log();

    console.log('📋 OBJETIVO:');
    console.log(this.wrapText(note.objective || '(vacío)', 60));
    console.log();

    console.log('📋 EVALUACIÓN:');
    console.log(this.wrapText(note.assessment || '(vacío)', 60));
    console.log();

    console.log('📋 PLAN:');
    console.log(this.wrapText(note.plan || '(vacío)', 60));
    console.log();

    console.log('─────────────────────────────────────────────────────────────');
    console.log('🏥 ENTIDADES MÉDICAS DETECTADAS:');
    console.log();

    const byType: Record<string, string[]> = {};
    for (const entity of note.entities) {
      if (!byType[entity.type]) byType[entity.type] = [];
      const codeStr = entity.code ? ` [${entity.code.system}:${entity.code.code}]` : '';
      byType[entity.type].push(`${entity.value}${codeStr}`);
    }

    const typeLabels: Record<string, string> = {
      diagnosis: '🩺 Diagnósticos',
      medication: '💊 Medicamentos',
      symptom: '🤒 Síntomas',
      vital: '📊 Signos Vitales',
      procedure: '🔬 Procedimientos',
      allergy: '⚠️ Alergias'
    };

    for (const [type, items] of Object.entries(byType)) {
      console.log(`${typeLabels[type] || type}:`);
      items.forEach(item => console.log(`  • ${item}`));
    }

    console.log('\n─────────────────────────────────────────────────────────────');
    console.log(`Estado: ${note.status.toUpperCase()}`);
    console.log(`ID: ${note.id}`);
    console.log(`Creado: ${note.createdAt.toLocaleString()}`);
    console.log('═════════════════════════════════════════════════════════════\n');
  }

  private wrapText(text: string, width: number): string {
    const words = text.split(' ');
    const lines: string[] = [];
    let currentLine = '';

    for (const word of words) {
      if ((currentLine + ' ' + word).length <= width) {
        currentLine += (currentLine ? ' ' : '') + word;
      } else {
        if (currentLine) lines.push('  ' + currentLine);
        currentLine = word;
      }
    }
    if (currentLine) lines.push('  ' + currentLine);

    return lines.join('\n');
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Interactive mode - process custom input
   */
  processInput(text: string): void {
    const result: TranscriptionResult = {
      text,
      confidence: 0.95,
      language: 'es-MX',
      isFinal: true,
      timestamp: Date.now()
    };
    this.app.processTranscription(result);
  }

  /**
   * Get current state
   */
  getState() {
    return this.app.getState();
  }
}

// ============================================================================
// CLI ENTRY POINT
// ============================================================================

async function main() {
  const demo = new MedXDemo();

  const args = process.argv.slice(2);

  if (args.includes('--interactive') || args.includes('-i')) {
    // Interactive mode
    console.log('MedX Pro - Modo Interactivo');
    console.log('Comandos: nuevo paciente, sección [nombre], dictar, siguiente, anterior, leer, guardar, ayuda');
    console.log('Escribe "salir" para terminar\n');

    const readline = await import('readline');
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    rl.on('line', (input: string) => {
      if (input.toLowerCase() === 'salir') {
        console.log('\n--- Nota Final ---');
        console.log(JSON.stringify(demo.getState().note, null, 2));
        rl.close();
        process.exit(0);
      }
      demo.processInput(input);
    });

  } else {
    // Run demo
    await demo.runDemo();
  }
}

// Run if executed directly
main().catch(console.error);

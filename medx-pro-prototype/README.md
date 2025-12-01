# MedX Pro - Voice-First Clinical Documentation

> "Speak. Heal. Done."

A prototype voice-first clinical documentation platform for Spanish-speaking healthcare providers.

## Quick Start

```bash
# Install dependencies
npm install

# Run the demo
npm run demo

# Interactive mode
npm run demo:interactive

# Run tests
npm test
```

## Features

### Voice Commands (Spanish)

| Command | Action |
|---------|--------|
| `nuevo paciente` | Start new encounter |
| `sección [nombre]` | Navigate to section (subjetivo, objetivo, evaluación, plan) |
| `siguiente` | Next section |
| `anterior` | Previous section |
| `dictar` | Enter dictation mode |
| `leer` | Read current section |
| `guardar` | Save note |
| `ayuda` | Show commands |

### Medical Entity Recognition

Automatically extracts and codes:
- **Diagnoses** → ICD-10 codes
- **Medications** → RxNorm codes
- **Procedures** → CPT codes
- **Vital signs** → LOINC codes
- **Allergies** and **Symptoms**

### SOAP Note Generation

Generates structured clinical notes with:
- Subjective (patient complaints, history)
- Objective (exam findings, vitals)
- Assessment (diagnoses)
- Plan (treatments, follow-up)

## Architecture

```
src/
├── types.ts          # Core type definitions
├── medx-core.ts      # Main application logic
├── voice-capture.ts  # Deepgram integration
└── demo.ts           # Interactive demo
```

## API Keys

For live transcription, set your Deepgram API key:

```bash
export DEEPGRAM_API_KEY=your_key_here
```

Without an API key, the demo runs with simulated transcription.

## Example Output

```
╔═══════════════════════════════════════════════════════════╗
║                    NOTA CLÍNICA SOAP                       ║
╚═══════════════════════════════════════════════════════════╝

📋 SUBJETIVO:
  Paciente masculino de 55 años con dolor torácico...

📋 OBJETIVO:
  Presión arterial 150/95 mmHg, FC 92 lpm...

🏥 ENTIDADES MÉDICAS DETECTADAS:

🩺 Diagnósticos:
  • hipertensión [ICD-10:I10]
  • diabetes tipo 2 [ICD-10:E11]

💊 Medicamentos:
  • metformina [RxNorm:6809]
  • lisinopril [RxNorm:29046]
```

## License

MIT

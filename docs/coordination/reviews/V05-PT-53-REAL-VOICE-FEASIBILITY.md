# V05-PT-53 Real Local Voice Feasibility Review

**Date:** 2026-09-10
**Owner:** Chief Architect / CTO
**Disposition:** Feasible, subject to a separately authorized, staged Windows proof. No implementation or installation is authorized by this review.

## 1. Decision

The safest practical path from mock audio to real local voice is a project-owned adapter layer behind the Voice Shell's existing `AudioInputProtocol`, `TranscriberProtocol`, and `SpeechOutputProtocol` boundaries:

- foreground push-to-talk capture only;
- Pocket TTS on CPU with a stock voice for speech output;
- faster-whisper on CPU with `int8` compute as the first speech-recognition candidate;
- whisper.cpp with the English `base.en` model as the measured fallback candidate if faster-whisper misses the resource or latency gates;
- no automatic runtime fallback between engines, no model downloads at runtime, and no cloning of a user's voice.

This preserves Core's validation and approval authority, the existing mock default, and the current cancellation lifecycle. Backtalk is useful only as interaction prior art; its code and default permission choices must not enter the implementation.

## 2. Existing boundary and gaps

The accepted Voice candidate already has the right seams. `AudioInputProtocol` returns bounded `AudioData`; `TranscriberProtocol` converts audio to text; `SpeechOutputProtocol` owns queued output, interruption, processing, and reset. The controller already enforces approval boundaries and generation-based cancellation. `VoiceCoreBridgeProtocol` must remain the only path into Core.

Only deterministic mock implementations exist today. A real bridge therefore needs project-owned device, STT, and TTS adapters, plus lifecycle wiring and tests. It does not require a new Core schema, a weaker approval path, or provider-specific logic in the controller.

## 3. Technology comparison

### Speech output

**Pocket TTS is the preferred proof candidate.** Its official project describes a 100-million-parameter CPU model, streaming output, Python 3.10-3.14 support, and approximately 200 ms to first audio under its reference conditions. The current model card licenses model weights under CC BY 4.0. The Python package is small, but PyTorch and the model assets dominate the practical footprint. The proof must measure the actual Windows CPU device rather than inherit upstream latency claims.

Use only an upstream stock voice. Voice cloning would introduce consent, identity, retention, and misuse questions that are unnecessary for the local prototype.

### Speech recognition

**faster-whisper is the preferred first candidate.** It is MIT-licensed, integrates directly with Python, supports CPU `int8`, and uses PyAV so a separate system FFmpeg installation is not required. Its CTranslate2 dependency publishes Windows wheels. This is the lowest-friction fit with the current Python Voice Shell.

**whisper.cpp is the required benchmark fallback.** It is MIT-licensed, supports Windows and CPU execution, and offers a real-time example and optional voice-activity detection. Its native binary/build boundary is more operationally complex, but it provides a valuable independent footprint and latency comparison. Start with `base.en` (about 142 MiB); move to `small.en` only if accuracy requires it and the resource ceiling still passes.

The proof must select one STT engine by measurement. Production must not silently switch engines because that would make latency, accuracy, and evidence nondeterministic.

## 4. Backtalk prior-art disposition

Backtalk demonstrates useful interaction ideas: push-to-talk, microphone access only while the key is held, and interruption of active speech. It is not a dependency candidate. Its repository is AGPL-3.0-or-later, and its documented architecture includes permission-bypass defaults and automatic cloud fallback that conflict with this project's explicit approval and local-only boundaries.

Adopt the interaction lessons only: foreground push-to-talk, visible listening state, immediate interruption, and explicit failure. Do not copy code, install the project, inherit its permission bypass, or add cloud fallback.

## 5. Proposed adapter boundary

A later implementation authorization should be limited to these conceptual components:

- `local_audio`: foreground push-to-talk capture, one device at a time, 16 kHz mono normalization, silence and 30-second utterance caps;
- `local_stt`: one configured local engine loaded only from manifest-bound assets;
- `local_tts`: Pocket TTS stock-voice streaming into a bounded PCM queue;
- `real_voice`: lifecycle composition, device selection, cancellation generation, and fail-closed startup;
- focused contract, lifecycle, privacy, and resource tests plus an operator runbook.

The adapters must return through the existing protocols unchanged. Audio and transcripts remain in memory only; diagnostics may contain timing, byte counts, engine identity, and fixed error categories, but never waveform content or transcript text. Runtime network access, DNS lookup, telemetry, and model acquisition are prohibited.

Cancellation must atomically invalidate the current generation, stop capture or synthesis, clear queued PCM, close the device stream, and prevent stale audio from playing after a new turn. Approval, digest, and Core validation behavior remain unchanged. Mock remains the default until a later acceptance explicitly changes it.

## 6. Acquisition and licensing gate

Before any installation, a Product Owner decision must approve a single bounded package covering:

- exact package versions and hashes;
- exact model and stock-voice asset revisions, hashes, origins, and licenses;
- offline/public speech fixtures and their licenses;
- disk and memory ceilings;
- the selected stock voice and attribution placement;
- a rollback and removal procedure.

All assets must be acquired once through an authorized path, scanned, recorded in a closed manifest, and loaded locally. The implementation must fail closed when any asset is missing or has a different hash.

## 7. Proof sequence

### Stage A — offline, no devices

Use licensed prerecorded speech and a fake audio sink. Exercise both STT candidates, Pocket TTS, malformed and silent input, model-load failure, cancellation, stale-generation rejection, and repeated start/stop. This stage may be authorized without microphone or speaker access.

### Stage B — supervised local devices

Only after Stage A passes, separately authorize a short foreground push-to-talk microphone and speaker pilot. Require visible listening/speaking state, an explicit device list, no background listener, no global hotkey, no retained audio, and a physical or UI stop control.

### Stage C — activation decision

Chief of Staff reviews evidence and routes a Product Owner activation decision. Until accepted, the real bridge remains opt-in and mock remains the default.

## 8. Acceptance gates

- **Recognition:** word error rate at or below 15% on the fixed public fixture set, with zero errors across five predeclared safety-critical approval/cancellation phrases.
- **STT latency:** for five-second utterances, median at or below 1.5 seconds and p95 at or below 3.0 seconds after warm-up.
- **TTS latency:** first PCM median at or below 0.75 seconds and p95 at or below 1.5 seconds after warm-up.
- **End-to-audio:** median at or below 2.5 seconds and p95 at or below 4.0 seconds for the fixed local scenario.
- **Interruption:** p95 at or below 250 ms and maximum at or below 500 ms from cancel signal to silence; zero stale frames after generation change.
- **Resources:** no more than 2 GiB of new persisted assets and no more than 4 GiB peak process working set on the target Windows device.
- **Lifecycle:** 30 consecutive capture/transcribe/speak/interrupt/reset cycles with no device leak, hung worker, retained transcript, or network attempt.
- **Safety:** approval and digest tests unchanged; mock tests unchanged; no microphone open outside the visible foreground push-to-talk interval.

Failure of any safety, privacy, lifecycle, licensing, or network gate is terminal for the proof. A latency or accuracy miss may trigger one documented comparison with the alternate STT candidate, but not an automatic fallback.

## 9. Successor decision

PT53 is complete as a feasibility review and requires no Product Owner action now. The next mutation must be a separately authorized Stage A task with a closed path ceiling and acquisition manifest. Stage B microphone/speaker use and Stage C frontend activation require later, distinct approvals.

## 10. Primary sources

- Pocket TTS project and installation guidance: <https://github.com/kyutai-labs/pocket-tts>
- Pocket TTS model card and CC BY 4.0 model license: <https://huggingface.co/kyutai/pocket-tts>
- Pocket TTS package metadata: <https://pypi.org/project/pocket-tts/>
- faster-whisper project, license, CPU mode, and PyAV packaging: <https://github.com/SYSTRAN/faster-whisper>
- CTranslate2 Windows package metadata: <https://pypi.org/project/ctranslate2/>
- whisper.cpp project, Windows support, real-time example, and VAD: <https://github.com/ggml-org/whisper.cpp>
- whisper.cpp model inventory: <https://github.com/ggml-org/whisper.cpp/blob/master/models/README.md>
- Backtalk interaction and licensing prior art: <https://github.com/jaredrhod/backtalk>

## 11. Exit record

This review made no repository-code, dependency, model, configuration, device, or runtime change. It performed no installation, microphone capture, speaker playback, provider request, or live integration.

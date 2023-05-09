/**
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {createGraphRunner, GraphRunner, WasmModule} from './mediapipe/web/graph_runner/graph_runner';
import {createMediaPipeAudioBlendshapes, MediaPipeAudioBlendshapes} from './mediapipe_audio_blendshapes';
// import {trustedResourceUrl} from 'safevalues';

// Create FPS text renderer observer here.
const messageTag = document.getElementById('message') as HTMLCanvasElement;
const fpsRenderer = {
  process(mspf: number) {
    let detectionString = '';
    if (mspf && mspf > 0.0) {
      detectionString += `  Processing: ${mspf.toFixed(2)} ms`;
    }
    messageTag.textContent = detectionString;
  },
};

declare interface TalkingHeadsWasmModule {
  NUM_QUEUED_AUDIO_PACKETS: number;
}

let wasmModule: TalkingHeadsWasmModule;
let wasmLib: GraphRunner;

// Simple rendering loop driven by the browser. The audio data packets are
// streamed into the graph continuously while this rendering occurs, via a
// separate mechanism.
function renderLoop() {
  const start = performance.now();
  wasmLib.finishProcessing();
  fpsRenderer.process(performance.now() - start);
  requestAnimationFrame(evt => {
    renderLoop();
  });
}

// Simple polling loop for blendshape updates, driven by the browser. The audio
// data packet input is set up similarly to the above renderLoop.
function blendshapeLoop(audioBlendshapes: MediaPipeAudioBlendshapes) {
  const blendshapes = audioBlendshapes.getBlendshapes();
  console.log('Blendshapes: ', blendshapes);
  // Poll 3-4 times a second
  setTimeout(() => {
    blendshapeLoop(audioBlendshapes);
  }, 300);
}

const NUM_SAMPLES = 1024;   // 1024
const SAMPLE_RATE = 44100;  // Was 44100, but internally is 16000

// For demo, stream microphone data into MediaPipe graph
// tslint:disable-next-line:no-unused-variable
function streamMicrophoneThroughGraph(wasmLib: GraphRunner|
                                      MediaPipeAudioBlendshapes) {
  const onAcquiredUserMedia = (stream: MediaStream) => {
    if (wasmLib instanceof MediaPipeAudioBlendshapes) {
      blendshapeLoop(wasmLib);
    } else {
      renderLoop();
    }

    // Hook up directly into graph using AudioContext API
    const audioContext = new AudioContext();
    const source = audioContext.createMediaStreamSource(stream);
    const processor = audioContext.createScriptProcessor(NUM_SAMPLES, 1, 1);
    source.connect(processor);
    processor.connect(audioContext.destination);

    // This is just for a demo, so currently not worth the time to refactor due
    // to the deprecation warning. TODO(tmullen): Fix
    // tslint:disable:deprecation
    let lastAudioTimestamp = 0.0;
    processor.onaudioprocess = e => {
      // Only pick up the first channel's data, as a Float32Array
      const audioData = e.inputBuffer.getChannelData(0);
      wasmModule.NUM_QUEUED_AUDIO_PACKETS++;
      // For some reason, e.playbackTime no longer works for our purposes here,
      // so we just send in timestamps as if we collect samples continuously
      // at the desired sample rate with no breaks.
      // TODO(tmullen): Figure out why e.playbackTime now breaks things, and how
      //     best to fix.
      const timestamp = lastAudioTimestamp + NUM_SAMPLES * 1000.0 / SAMPLE_RATE;
      if (timestamp > lastAudioTimestamp) {
        wasmLib.addAudioToStream(audioData, 'input_audio', timestamp);
      }
      lastAudioTimestamp = timestamp;
    };
    // tslint:enable:deprecation
  };
  navigator.mediaDevices.getUserMedia({audio: true, video: false})
      .then(onAcquiredUserMedia);
}

export let audioBlendshapes: MediaPipeAudioBlendshapes|null = null;

// tslint:disable-next-line:no-unused-variable
export async function runBlendshapesDemo(isV2: boolean) {
  if (audioBlendshapes === null) {
    audioBlendshapes = await createMediaPipeAudioBlendshapes(
        isV2?'talking_head_v2/talking_heads_v2_blendshapes_internal.js': 'talking_head_v1/talking_heads_blendshapes_internal.js',
        isV2?'talking_head_v2/talking_heads_v2_microphone_assets.js':'talking_head_v1/talking_heads_microphone_assets.js');
    wasmModule =
        audioBlendshapes.wasmModule as WasmModule & TalkingHeadsWasmModule;
    wasmModule.NUM_QUEUED_AUDIO_PACKETS = 0;
    audioBlendshapes.configureAudio(1, NUM_SAMPLES, SAMPLE_RATE);
    await audioBlendshapes.initializeGraph(isV2?'talking_head_v2/talking_heads_v2_demo.binarypb':'talking_head_v1/talking_heads_demo.binarypb');
    // streamMicrophoneThroughGraph(audioBlendshapes);
  }
}

export let lastAudioT = 0.0;
export let isThinking = false;
export let isLookingLeft = false;

export function setIsThinking(isT: boolean) {
  if (isT === isThinking) return;
  isThinking = isT;
  if (isThinking) {
    isLookingLeft = !isLookingLeft;
  }
}

export function registerCallback(audioData: Float32Array) {
  if (audioBlendshapes === null) return;
  wasmModule.NUM_QUEUED_AUDIO_PACKETS++;
  // For some reason, e.playbackTime no longer works for our purposes here,
  // so we just send in timestamps as if we collect samples continuously
  // at the desired sample rate with no breaks.
  // TODO(tmullen): Figure out why e.playbackTime now breaks things, and how
  //     best to fix.
  const timestamp = lastAudioT + NUM_SAMPLES * 1000.0 / SAMPLE_RATE;
  if (timestamp > lastAudioT) {
    audioBlendshapes.addAudioToStream(audioData, 'input_audio', timestamp);
  }
  lastAudioT = timestamp;
}

// To run blendshape demo instead, comment this line instead of the following,
// and also uncomment renderer_calculator_desktop dependency in
// web_ml_cpu:talking_heads_blendshapes_internal BUILD rule
// runVisualDemo();
// runBlendshapesDemo();

export default {
  runBlendshapesDemo,
  registerCallback,
  audioBlendshapes,
  lastAudioT,
}

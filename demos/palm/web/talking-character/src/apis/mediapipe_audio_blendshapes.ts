/**
 * Copyright 2023 The MediaPipe Authors. All Rights Reserved.
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

import {createMediaPipeLib, GraphRunner, WasmModule} from './mediapipe/web/graph_runner/graph_runner';

declare interface AudioBlendshapesWasmModule {
  updateBlendshape: (name: string, value: number) => void;
}

export interface Blendshapes {
  [name: string]: number;
}

export class MediaPipeAudioBlendshapes extends GraphRunner {
  private readonly blendshapes: Blendshapes = {};

  constructor(module: WasmModule) {
    super(module);
    (module as unknown as AudioBlendshapesWasmModule).updateBlendshape =
        (name: string, value: number) => {
          this.blendshapes[name] = value;
        };
  }

  /**
   * Causes all the queued audio packets to be processed synchronously, and
   * waits for the response.
   * @return blendshapes The blendshapes, with all available updates.
   */
  getBlendshapes(): Blendshapes {
    this.finishProcessing();
    return this.blendshapes;
  }
}

/**
 * Global function to initialize Wasm blob and load runtime assets for MediaPipe
 *     audio-to-blendshapes library.
 * @param wasmLoaderScript Url for the wasm-runner script; produced by the build
 *     process.
 * @param assetLoaderScript Url for the asset-loading script; produced by the
 *     build process.
 * @return promise A promise which will resolve when initialization has
 *     completed successfully.
 */
export async function createMediaPipeAudioBlendshapes(
    wasmLoaderScript: string,
    assetLoaderScript: string): Promise<MediaPipeAudioBlendshapes> {
  return createMediaPipeLib(
      MediaPipeAudioBlendshapes, wasmLoaderScript, assetLoaderScript,
      undefined /* glCanvas */);
}

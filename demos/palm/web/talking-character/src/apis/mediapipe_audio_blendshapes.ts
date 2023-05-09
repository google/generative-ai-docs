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
// import {TrustedResourceUrl} from 'safevalues';

declare interface AudioBlendshapesWasmModule {
  // Blendshape-specific fcns
  // TODO(tmullen): Look into caching names or using an array, to avoid repeated
  //    C++-to-JS string translation and lookup.
  updateBlendshape: (name: string, value: number) => void;
}

/**
 * Valid types of image sources which we can run our GraphRunner over.
 */
export interface Blendshapes {
  [name: string]: number;
}

/**
 * Simple class to extract a list of classifications from an image source.
 * Takes a WebAssembly Module (must be instantiated to Window.Module).
 */
export class MediaPipeAudioBlendshapes extends GraphRunner {
  private readonly blendshapes: Blendshapes = {};

  constructor(module: WasmModule) {
    // We assume we're running on Chrome for now, so we have access to
    // OffscreenCanvas.
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

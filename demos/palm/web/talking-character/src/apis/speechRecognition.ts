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

import {useEffect, useRef, useState} from 'react';

import {GOOGLE_CLOUD_API_KEY} from '../context/constants';

import {sendRequestToGoogleCloudApi} from './network';
import * as talkingHead from './talkingHead';

interface SpeechFoundCallback {
  (text: string): void;
}

export enum CharacterState {
  Idle,
  Listening,
  Speaking
}

const useSpeechRecognition =
    () => {
      const [characterState, setCharacterState] =
          useState<CharacterState>(CharacterState.Idle);
      const mediaRecorder = useRef<MediaRecorder|null>(null);
      const recordedChunks = useRef<Blob[]>([]);
      const onSpeechFoundCallback = useRef<SpeechFoundCallback>((text) => {});
      const audioContext = useRef<AudioContext|null>(null);
      const analyser = useRef<AnalyserNode|null>(null);
      const stream = useRef<MediaStream|null>(null);
      const source = useRef<MediaStreamAudioSourceNode|null>(null);
      const bars = useRef<(HTMLDivElement | null)[]>([]);

      const setOnSpeechFoundCallback = (callback: SpeechFoundCallback) => {
        onSpeechFoundCallback.current = callback;
      };

      const startRecording = async () => {
        try {
          stream.current =
              await navigator.mediaDevices.getUserMedia({audio: true});
          audioContext.current = new AudioContext();
          analyser.current = audioContext.current.createAnalyser();
          source.current =
              audioContext.current.createMediaStreamSource(stream.current);
          source.current.connect(analyser.current);
          mediaRecorder.current = new MediaRecorder(stream.current);
          mediaRecorder.current.ondataavailable = (event) => {
            if (event.data.size > 0) {
              recordedChunks.current.push(event.data);
            }
          };
          mediaRecorder.current.start();
          setCharacterState(CharacterState.Listening);
          // talkingHead.setIsThinking(true);
        } catch (err) {
          console.error(err);
        }
      };

      const stopRecording =
          async () => {
        if (stream.current) {
          stream.current.getTracks().forEach((track) => track.stop());
        }
        if (audioContext.current) {
          if (source.current) {
            source.current.disconnect();
          }
          if (analyser.current) {
            analyser.current.disconnect();
          }
          audioContext.current.close();
        }
        if (mediaRecorder.current) {
          mediaRecorder.current.stop();
          await new Promise((resolve) => {
            if (mediaRecorder.current) {
              mediaRecorder.current.onstop = () => {
                resolve(null);
              };
            }
          });
          const blob = new Blob(recordedChunks.current, {type: 'audio/webm'});
          recordedChunks.current = [];
          const reader = new FileReader();
          reader.readAsDataURL(blob);
          reader.onloadend = async () => {
            const base64Data = reader.result?.toString().split(',')[1];
            if (base64Data) {
              setCharacterState(CharacterState.Speaking);
              await recognize(base64Data);
            } else {
              setCharacterState(CharacterState.Idle);
            }
            talkingHead.setIsThinking(false);
          }
        };
      }

      useEffect(() => {
        let animationFrameId: number|null = null;
        let timeoutId: NodeJS.Timeout|null = null;

        const animationLoop = () => {
          if (!analyser.current) return;

          analyser.current.fftSize = 32;
          const bufferLength = analyser.current.frequencyBinCount;
          const dataArray = new Uint8Array(bufferLength);

          analyser.current.getByteFrequencyData(dataArray);

          const avgVolume =
              dataArray.reduce((acc, val) => acc + val) / bufferLength;
          const maxHeight = 80;

          if (avgVolume > 50) {
            talkingHead.setIsThinking(true);
          }

          bars.current.forEach((bar, index) => {
            if (bar) {
              let height = (avgVolume / 255) * maxHeight;
              let marginTop = 0;
              if (index !== 1) {
                height *= 0.7;
              }
              height = Math.max(height, 6);
              marginTop = (maxHeight - height) / 2;
              bar.style.height = `${height}px`;
              bar.style.marginTop = `${marginTop}px`;
            }
          });

          timeoutId = setTimeout(() => {
            animationFrameId = requestAnimationFrame(animationLoop);
          }, 50);
        };

        if (characterState === CharacterState.Listening) {
          animationLoop();
        } else {
          if (animationFrameId !== null) {
            cancelAnimationFrame(animationFrameId);
          }
          if (timeoutId !== null) {
            clearTimeout(timeoutId);
          }
        }

        return () => {
          if (animationFrameId !== null) {
            cancelAnimationFrame(animationFrameId);
          }
          if (timeoutId !== null) {
            clearTimeout(timeoutId);
          }
        };
      }, [characterState, bars, analyser]);

      const recognize = async (audioString: string) => {
        await sendRequestToGoogleCloudApi(
            'https://speech.googleapis.com/v1p1beta1/speech:recognize', {
              config: {
                encoding: 'WEBM_OPUS',
                sampleRateHertz: 48000,
                audioChannelCount: 1,
                enableAutomaticPunctuation: true,
                languageCode: 'en-US',
                profanityFilter: true,
              },
              audio: {content: audioString},
            },
            GOOGLE_CLOUD_API_KEY)
            .then(response => {
              if (response !== null && response.results !== undefined) {
                const topTranscriptionAlternative = response.results[0];
                const transcript =
                    topTranscriptionAlternative.alternatives[0].transcript;
                onSpeechFoundCallback.current(transcript);
              }
            });
      };

      const onMicButtonPressed =
          () => {
            if (characterState === CharacterState.Idle) {
              startRecording();
            } else if (characterState === CharacterState.Listening) {
              stopRecording();
            }
          }

      return {
        characterState,
        bars,
        setCharacterState,
        onMicButtonPressed,
        setOnSpeechFoundCallback,
      };
    }

export default useSpeechRecognition;

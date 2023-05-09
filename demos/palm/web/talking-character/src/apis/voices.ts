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

/**
 * Represents a playable voice.
 */
export interface Voice {
  languageCode: string;
  name: string;
  ssmlGender: string;
  naturalSampleRateHertz: number;
}

/**
 * List of available voices.
 */
export const ALL_VOICES: Voice[] = [
  {
    'languageCode': 'da-DK',
    'name': 'da-DK-Wavenet-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'de-DE',
    'name': 'de-DE-Wavenet-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'de-DE',
    'name': 'de-DE-Wavenet-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'de-DE',
    'name': 'de-DE-Wavenet-C',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'de-DE',
    'name': 'de-DE-Wavenet-D',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-AU',
    'name': 'en-AU-Wavenet-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-AU',
    'name': 'en-AU-Wavenet-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-AU',
    'name': 'en-AU-Wavenet-C',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-AU',
    'name': 'en-AU-Wavenet-D',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-GB',
    'name': 'en-GB-Wavenet-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-GB',
    'name': 'en-GB-Wavenet-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-GB',
    'name': 'en-GB-Wavenet-C',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-GB',
    'name': 'en-GB-Wavenet-D',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-US',
    'name': 'en-US-Wavenet-A',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-US',
    'name': 'en-US-Wavenet-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-US',
    'name': 'en-US-Wavenet-C',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-US',
    'name': 'en-US-Wavenet-D',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-US',
    'name': 'en-US-Wavenet-E',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-US',
    'name': 'en-US-Wavenet-F',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'fr-CA',
    'name': 'fr-CA-Wavenet-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'fr-CA',
    'name': 'fr-CA-Wavenet-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'fr-CA',
    'name': 'fr-CA-Wavenet-C',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'fr-CA',
    'name': 'fr-CA-Wavenet-D',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'fr-FR',
    'name': 'fr-FR-Wavenet-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'fr-FR',
    'name': 'fr-FR-Wavenet-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'fr-FR',
    'name': 'fr-FR-Wavenet-C',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'fr-FR',
    'name': 'fr-FR-Wavenet-D',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'it-IT',
    'name': 'it-IT-Wavenet-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'ja-JP',
    'name': 'ja-JP-Wavenet-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'ko-KR',
    'name': 'ko-KR-Wavenet-B',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'ko-KR',
    'name': 'ko-KR-Wavenet-C',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'ko-KR',
    'name': 'ko-KR-Wavenet-D',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'ko-KR',
    'name': 'ko-KR-Wavenet-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'nl-NL',
    'name': 'nl-NL-Wavenet-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'pl-PL',
    'name': 'pl-PL-Wavenet-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'pl-PL',
    'name': 'pl-PL-Wavenet-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'pl-PL',
    'name': 'pl-PL-Wavenet-C',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'pl-PL',
    'name': 'pl-PL-Wavenet-D',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'pt-BR',
    'name': 'pt-BR-Wavenet-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'pt-PT',
    'name': 'pt-PT-Wavenet-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'pt-PT',
    'name': 'pt-PT-Wavenet-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'pt-PT',
    'name': 'pt-PT-Wavenet-C',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'pt-PT',
    'name': 'pt-PT-Wavenet-D',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'ru-RU',
    'name': 'ru-RU-Wavenet-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'ru-RU',
    'name': 'ru-RU-Wavenet-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'ru-RU',
    'name': 'ru-RU-Wavenet-C',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'ru-RU',
    'name': 'ru-RU-Wavenet-D',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'sk-SK',
    'name': 'sk-SK-Wavenet-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'sv-SE',
    'name': 'sv-SE-Wavenet-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'tr-TR',
    'name': 'tr-TR-Wavenet-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'tr-TR',
    'name': 'tr-TR-Wavenet-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'tr-TR',
    'name': 'tr-TR-Wavenet-C',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'tr-TR',
    'name': 'tr-TR-Wavenet-D',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'tr-TR',
    'name': 'tr-TR-Wavenet-E',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'uk-UA',
    'name': 'uk-UA-Wavenet-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'es-ES',
    'name': 'es-ES-Standard-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'it-IT',
    'name': 'it-IT-Standard-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'ru-RU',
    'name': 'ru-RU-Standard-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'ru-RU',
    'name': 'ru-RU-Standard-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'ru-RU',
    'name': 'ru-RU-Standard-C',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'ru-RU',
    'name': 'ru-RU-Standard-D',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'ko-KR',
    'name': 'ko-KR-Standard-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 22050
  },
  {
    'languageCode': 'ko-KR',
    'name': 'ko-KR-Standard-B',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'ko-KR',
    'name': 'ko-KR-Standard-C',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'ja-JP',
    'name': 'ja-JP-Standard-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 22050
  },
  {
    'languageCode': 'nl-NL',
    'name': 'nl-NL-Standard-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'pt-BR',
    'name': 'pt-BR-Standard-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'pl-PL',
    'name': 'pl-PL-Standard-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'pl-PL',
    'name': 'pl-PL-Standard-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'pl-PL',
    'name': 'pl-PL-Standard-C',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'pl-PL',
    'name': 'pl-PL-Standard-D',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'sk-SK',
    'name': 'sk-SK-Standard-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'tr-TR',
    'name': 'tr-TR-Standard-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 22050
  },
  {
    'languageCode': 'tr-TR',
    'name': 'tr-TR-Standard-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'tr-TR',
    'name': 'tr-TR-Standard-C',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'tr-TR',
    'name': 'tr-TR-Standard-D',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'tr-TR',
    'name': 'tr-TR-Standard-E',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'da-DK',
    'name': 'da-DK-Standard-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'pt-PT',
    'name': 'pt-PT-Standard-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'pt-PT',
    'name': 'pt-PT-Standard-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'pt-PT',
    'name': 'pt-PT-Standard-C',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'pt-PT',
    'name': 'pt-PT-Standard-D',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'sv-SE',
    'name': 'sv-SE-Standard-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 22050
  },
  {
    'languageCode': 'en-GB',
    'name': 'en-GB-Standard-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-GB',
    'name': 'en-GB-Standard-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-GB',
    'name': 'en-GB-Standard-C',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-GB',
    'name': 'en-GB-Standard-D',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-US',
    'name': 'en-US-Standard-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-US',
    'name': 'en-US-Standard-C',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-US',
    'name': 'en-US-Standard-D',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-US',
    'name': 'en-US-Standard-E',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'de-DE',
    'name': 'de-DE-Standard-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'de-DE',
    'name': 'de-DE-Standard-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-AU',
    'name': 'en-AU-Standard-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-AU',
    'name': 'en-AU-Standard-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-AU',
    'name': 'en-AU-Standard-C',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-AU',
    'name': 'en-AU-Standard-D',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'fr-CA',
    'name': 'fr-CA-Standard-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'fr-CA',
    'name': 'fr-CA-Standard-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'fr-CA',
    'name': 'fr-CA-Standard-C',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'fr-CA',
    'name': 'fr-CA-Standard-D',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'fr-FR',
    'name': 'fr-FR-Standard-A',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'fr-FR',
    'name': 'fr-FR-Standard-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'fr-FR',
    'name': 'fr-FR-Standard-C',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'fr-FR',
    'name': 'fr-FR-Standard-D',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-US',
    'name': 'en-US-Wavenet-H',
    'ssmlGender': 'FEMALE',
    'naturalSampleRateHertz': 24000
  },
  {
    'languageCode': 'en-US',
    'name': 'en-US-Iris-Wavenet#iol',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
];

ALL_VOICES.sort((a, b) => {
  if (a.languageCode < b.languageCode) {
    return -1;
  }
  if (a.languageCode > b.languageCode) {
    return 1;
  }
  return 0;
});

/**
 * WaveNet voices.
 */
export const WAVE_NET_VOICES =
    ALL_VOICES.filter(v => v.name.indexOf('-Wavenet') > -1);

/**
 * Standard voices.
 */
export const STANDARD_VOICES =
    ALL_VOICES.filter(v => v.name.indexOf('-Standard-') > -1);

/**
 * Avatar voice.
 */
export interface AvatarVoice {
  cloudTtsVoice?: Voice;
  speakingRate?: number;
  pitchShift?: number;
  cloudTtsPitch?: number;
  winslow?: boolean;
  winslowVoiceName?: string;
}

/**
 * Default AvatarVoice.
 */
export const DEFAULT_AVATAR_VOICE = {
  'cloudTtsVoice': {
    'languageCode': 'en-US',
    'name': 'en-US-Wavenet-B',
    'ssmlGender': 'MALE',
    'naturalSampleRateHertz': 24000
  },
  'speakingRate': 1,
  'winslow': false,
  'cloudTtsPitch': 0
};
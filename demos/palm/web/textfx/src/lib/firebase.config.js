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

import {initializeApp} from 'firebase/app'
import {getAuth, signInAnonymously} from 'firebase/auth'
import {getFunctions, httpsCallable} from 'firebase/functions'

// TODO: Replace the below with your app's Firebase project configuration.
// To view and copy the Firebase configuration object for your app, visit the
// “Project settings” page in the Firebase console and scroll down to the
// "Your apps" section.
const firebaseConfig = {
  apiKey: 'YOUR FIREBASE API KEY',
  authDomain: 'YOUR AUTH DOMAIN',
  projectId: 'YOUR PROJECT ID',
  storageBucket: 'YOUR STORAGE BUCKET',
  messagingSenderId: 'YOUR MESSAGING SENDER ID',
  appId: 'YOUR APP ID'
}

// Initialize Firebase
const app = initializeApp(firebaseConfig)
const auth = getAuth(app)

// Authenticate
signInAnonymously(auth).catch(error => {
  console.error(error.message)
})

// TODO: Insert the Cloud Functions location for your Call PaLM API Securely extension.
const CLOUD_FUNCTIONS_LOCATION = 'YOUR CLOUD FUNCTIONS LOCATION'

// TODO: Insert the instance ID for your Call PaLM API Securely extension.
// You can find the instance ID for your extension on the "Extensions" page
// in the Firebase console. Locate the extension's instance card, and the
// instance ID is the bottommost value.
const INSTANCE_ID = 'YOUR INSTANCE ID'

// Import Firebase functions
const functions = getFunctions(app, CLOUD_FUNCTIONS_LOCATION)
export const post = httpsCallable(functions, `ext-${INSTANCE_ID}-post`)

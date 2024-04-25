/**
 * Copyright 2024 Google LLC
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

import * as vscode from 'vscode';

import { GoogleGenerativeAI} from '@google/generative-ai';
import {PROMPT_PRIMING} from './component';

// TextTheme
const TEXTHEME_CONTEXT=`
TextThemes can be imported from the Google Fonts package. 

All TextTheme objects have the following properties that can be modified:
bodyLarge → TextStyle? // Largest of the body styles.
bodyMedium → TextStyle? // Middle size of the body styles.
bodySmall → TextStyle? // Smallest of the body styles.
displayLarge → TextStyle? // Largest of the display styles.
displayMedium → TextStyle? // Middle size of the display styles.
displaySmall → TextStyle? // Smallest of the display styles.
headlineLarge → TextStyle? // Largest of the headline styles.
headlineMedium → TextStyle? // Middle size of the headline styles.
headlineSmall → TextStyle? // Smallest of the headline styles.
labelLarge → TextStyle? // Largest of the label styles.
labelMedium → TextStyle? // Middle size of the label styles.
labelSmall → TextStyle? // Smallest of the label styles.
titleLarge → TextStyle? // Largest of the title styles.
titleMedium → TextStyle? // Middle size of the title styles.
titleSmall → TextStyle? // Smallest of the title styles.

Here's an example user prompt:
Add a Google fonts sans-serif text theme to that ThemeData object.
Here's the example of good Dart code:
GoogleFonts.rubikTextTheme()

Here's an example prompt: 
Generate a Google Font text theme that has a script/handwritten font.
Here's an example of good Dart code:
GoogleFonts.sacramentoTextTheme()

Here's an example prompt: 
Generate a Google Font text theme that has a script/handwritten font and make display small text bold. 
Here's an example of good Dart code:
GoogleFonts.patrickHandTextTheme().copyWith(
  displaySmall: TextStyle(
    fontWeight: FontWeight.bold,
  ),
)

Here's an example prompt:
The foreground property on TextStyles allow effects such as gradients to be applied to text.
Here we provide a Paint with a ui.Gradient shader. 
TextStyle(
  fontSize: 40,
  foreground: Paint()
    ..shader = ui.Gradient.linear(
      const Offset(0, 20),
      const Offset(150, 20),
      <Color>[
        Colors.red,
        Colors.yellow,
      ],
    )
),
`

export async function generateTextTheme(){
  vscode.window.showInformationMessage('Generating Text Theme...');

  // Get API Key from local user configuration
  const apiKey = vscode.workspace.getConfiguration().get<string>('google.ai.apiKey');
  if (!apiKey) {
      vscode.window.showErrorMessage('API key not configured. Check your settings.');
      return;
  }

  const genAI = new GoogleGenerativeAI(apiKey);
  const gemini = genAI.getGenerativeModel({model: "gemini-pro"});

  // Text selection
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
      console.debug('Abandon: no open text editor.');
      return;
  }

  const selection = editor.selection;
  const selectedPrompt = editor.document.getText(selection);

  // Build the full prompt using the template.
  const fullPrompt = `${PROMPT_PRIMING + TEXTHEME_CONTEXT + selectedPrompt}`;

  const result = await gemini.generateContent(fullPrompt);
  const response = result.response;
  
  if (!response) {
      console.error('No candidates', response);
      vscode.window.showErrorMessage('No comment candidates returned. Check debug logs.');
      return;
  }
  const comment = response.text();

  // Insert in place of selection.
  editor.edit((editBuilder) => {
      // Insert code inline where the highlighted text is.
      editBuilder.insert(selection.start, comment);
  });
}
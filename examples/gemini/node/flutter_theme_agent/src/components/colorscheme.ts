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

// ColorScheme
const COLORSCHEME_CONTEXT=`

ColorScheme objects have the following properties:
background → Color // A color that typically appears behind scrollable content.
brightness → Brightness // The overall brightness of this color scheme.
error → Color // The color to use for input validation errors, e.g. for InputDecoration.errorText.
errorContainer → Color // A color used for error elements needing less emphasis than error.
inversePrimary → Color // An accent color used for displaying a highlight color on inverseSurface backgrounds, like button text in a SnackBar.
inverseSurface → Color // A surface color used for displaying the reverse of what's seen in the surrounding UI, for example in a SnackBar to bring attention to an alert.
onBackground → Color //A color that's clearly legible when drawn on background.
onError → Color // A color that's clearly legible when drawn on error.
onErrorContainer → Color // A color that's clearly legible when drawn on errorContainer.
onInverseSurface → Color // A color that's clearly legible when drawn on inverseSurface.
onPrimary → Color // A color that's clearly legible when drawn on primary.
onPrimaryContainer → Color // A color that's clearly legible when drawn on primaryContainer.
onSecondary → Color // A color that's clearly legible when drawn on secondary.
onSecondaryContainer → Color // A color that's clearly legible when drawn on secondaryContainer.
onSurface → Color // A color that's clearly legible when drawn on surface.
onSurfaceVariant → Color // A color that's clearly legible when drawn on surfaceVariant.
onTertiary → Color // A color that's clearly legible when drawn on tertiary.
onTertiaryContainer → Color // A color that's clearly legible when drawn on tertiaryContainer.
outline → Color // A utility color that creates boundaries and emphasis to improve usability.
outlineVariant → Color // A utility color that creates boundaries for decorative elements when a 3:1 contrast isn’t required, such as for dividers or decorative elements.
primary → Color //The color displayed most frequently across your app's screens and components.
primaryContainer → Color // A color used for elements needing less emphasis than primary.
scrim → Color // A color use to paint the scrim around of modal components.
secondary → Color // An accent color used for less prominent components in the UI, such as filter chips, while expanding the opportunity for color expression.
secondaryContainer → Color // A color used for elements needing less emphasis than secondary.
shadow → Color // A color use to paint the drop shadows of elevated components.
surface → Color // The background color for widgets like Card.
surfaceTint → Color // A color used as an overlay on a surface color to indicate a component's elevation.
surfaceVariant → Color // A color variant of surface that can be used for differentiation against a component using surface.
tertiary → Color // A color used as a contrasting accent that can balance primary and secondary colors or bring heightened attention to an element, such as an input field.
tertiaryContainer → Color // A color used for elements needing less emphasis than tertiary.

A ColorScheme is:
- Aesthetically pleasing.
- Using complementary colors as defined by color theory: https://www.thesprucecrafts.com/definition-of-complementary-colors-2577513
- Explicitly defining each color role with a Color code.
- The color scheme must be accessible and high-contrast.

Here's an example user prompt:
Construct a ColorScheme object in Flutter that has a pastel pink color palette and aesthetically pleasing.
Here's the example of good Dart code:
ColorScheme(
  brightness: Brightness.light,
  primary: Color(0xffFF80AB),
  onPrimary: Colors.white,
  primaryContainer: Color(0xffFFABDE),
  onPrimaryContainer: Color(0xff21005D),
  secondary: Color(0xffFFD166),
  onSecondary: Colors.black,
  secondaryContainer: Color(0xffffFCD2),
  onSecondaryContainer: Color(0xff422B08),
  error: Color(0xffFF3B30),
  onError: Colors.white,
  errorContainer: Color(0xffFFDAD4),
  onErrorContainer: Color(0xff410002),
  background: Color(0xffFCF8FF),
  onBackground: Color(0xff201A20),
  surface: Color(0xffFEF2FE),
  onSurface: Color(0xff201A20),
  surfaceVariant: Color(0xffDBD5E0),
  onSurfaceVariant: Color(0xff49454F),
  outline: Color(0xff857E92),
  outlineVariant: Color(0xff68606F),
  shadow: Color(0xff000000),
  scrim: Color(0xff000000),
  inverseSurface: Color(0xff362F33),
  onInverseSurface: Color(0xffFBF0F3),
  inversePrimary: Color(0xffD15B9D),
  surfaceTint: Color(0xffFF80AB),
)
This example code is a good because it explicitly defines all of the
available color properties on a ColorScheme instead of using deprecated properties
like Color Swatch.

Here's an example user prompt:
Generate a PURPLE and GREEN hulk themed color scheme.
Here's the example of good Dart code:
ColorScheme(
  brightness: Brightness.dark,
  primary: Color(0xff6E2C9A),
  onPrimary: Colors.white,
  primaryContainer: Colors.purple,
  onPrimaryContainer: Color(0xffE1BEE7),
  secondary: Color(0xff388E3C),
  onSecondary: Colors.black,
  secondaryContainer: Color(0xffA5D8AA),
  onSecondaryContainer: Color(0xff003909),
  error: Color(0xffD32F2F),
  onError: Colors.white,
  errorContainer: Color(0xffF2B8B5),
  onErrorContainer: Color(0xff470001),
  background: Color(0xff1B1B1F),
  onBackground: Colors.white,
  surface: Color(0xff2C2C33),
  onSurface: Colors.white,
  surfaceVariant: Color(0xff49454F),
  onSurfaceVariant: Colors.white,
  outline: Color(0xff8B858C),
  outlineVariant: Color(0xff68606F),
  shadow: Color(0xff000000),
  scrim: Color(0xff000000),
  inverseSurface: Color(0xffF4EFF4),
  onInverseSurface: Color(0xff333039),
  inversePrimary: Color(0xffD15B9D),
  surfaceTint: Colors.purple,
)
This example code is a good because it explicitly defines all of the
available color properties on a ColorScheme and it utilizes both colors mentioned
in the original prompt and there is high contrast.
`;

export async function generateColorScheme(){
  vscode.window.showInformationMessage('Generating Color Scheme...');

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
  const fullPrompt = `${PROMPT_PRIMING + COLORSCHEME_CONTEXT + selectedPrompt}`;

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
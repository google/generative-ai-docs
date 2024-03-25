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

const BUTTONSTYLE_CONTEXT=`
ButtonStyle should only defines properties that exist for a ButtonStyle object. 
ButtonStyle objects have the following properties. The buttons can ONLY be styled by setting these properties. No other properties:
alignment → AlignmentGeometry? // The alignment of the button's child.
animationDuration → Duration? // Defines the duration of animated changes for shape and elevation.
backgroundColor → MaterialStateProperty<Color?>? // The button's background fill color.
elevation → MaterialStateProperty<double?>? // The elevation of the button's Material.
enableFeedback → bool? // Whether detected gestures should provide acoustic and/or haptic feedback.
fixedSize → MaterialStateProperty<Size?>? // The button's size.
foregroundColor → MaterialStateProperty<Color?>? // The color for the button's Text and Icon widget descendants.
iconColor → MaterialStateProperty<Color?>? // The icon's color inside of the button.
iconSize → MaterialStateProperty<double?>? // The icon's size inside of the button.
maximumSize → MaterialStateProperty<Size?>? // The maximum size of the button itself.
minimumSize → MaterialStateProperty<Size?>? // The minimum size of the button itself.
mouseCursor → MaterialStateProperty<MouseCursor?>? // The cursor for a mouse pointer when it enters or is hovering over this button's InkWell.
overlayColor → MaterialStateProperty<Color?>? // The highlight color that's typically used to indicate that the button is focused, hovered, or pressed.
padding → MaterialStateProperty<EdgeInsetsGeometry?>? // The padding between the button's boundary and its child.
shadowColor → MaterialStateProperty<Color?>? // The shadow color of the button's Material.
shape → MaterialStateProperty<OutlinedBorder?>? // The shape of the button's underlying Material.
side → MaterialStateProperty<BorderSide?>? // The color and weight of the button's outline.
splashFactory → InteractiveInkFeatureFactory? // Creates the InkWell splash factory, which defines the appearance of "ink" splashes that occur in response to taps.
surfaceTintColor → MaterialStateProperty<Color?>? // The surface tint color of the button's Material.
tapTargetSize → MaterialTapTargetSize? // Configures the minimum size of the area within which the button may be pressed.
textStyle → MaterialStateProperty<TextStyle?>? // The style for a button's Text widget descendants.
visualDensity → VisualDensity? // Defines how compact the button's layout will be.

Available MaterialState Enums:
hovered → const MaterialState //The state when the user drags their mouse cursor over the given widget.
focused → const MaterialState // The state when the user navigates with the keyboard to a given widget.
pressed → const MaterialState // The state when the user is actively pressing down on the given widget.
dragged → const MaterialState // The state when this widget is being dragged from one place to another by the user.
selected → const MaterialState // The state when this item has been selected.
scrolledUnder → const MaterialState // The state when this widget overlaps the content of a scrollable below.
disabled → const MaterialState // The state when this widget is disabled and cannot be interacted with
error → const MaterialState // The state when the widget has entered some form of invalid state.

MaterialStateProperty can resolve various states and set properties like this example:
backgroundColor: MaterialStateProperty.resolveWith((states) {
  if (states.contains(MaterialState.hovered)) {
    return Colors.blue;
  } else {
    return Colors.green;
  }
}),
In this example, it sets the button's background color to blue when it's being hovered, otherwise the button is green.

MaterialStateProperty.all<T>(T value) → MaterialStateProperty<T>
Convenience method for creating a MaterialStateProperty that resolves to a single value for all states.
If you need a const value, use MaterialStatePropertyAll directly.

MaterialStateProperty values should be set as MaterialStateProperty values.

Here's an example prompt: 
Create a ButtonStyle where the button is green by default and blue on hover state. And elevation is 14, no surface tint color, and the splash effect is turned off.
Here's an example of good Dart code:
ButtonStyle(
  backgroundColor: MaterialStateProperty.resolveWith<Color?>(
    (Set<MaterialState> states) {
      if (states.contains(MaterialState.hovered)) {
        return Colors.blue;
      } else if (states.contains(MaterialState.pressed)) {
        return Colors.purple;
      }
      return Colors.green;
    },
  ),
  elevation: MaterialStateProperty.all<double>(14),
  overlayColor: MaterialStateProperty.all<Color>(Colors.transparent),
  splashFactory: NoSplash.splashFactory,
)

This is a good example because it resolves the MaterialStateProperty to get its color for when the button is default or hovered. It sets the correct elvation for all MaterialStateProperty and turns off tint and splash effect.

Here's an example prompt: 
Create a ButtonStyle where the button is green by default and blue on hover state. And elevation is 14, no surface tint color, and the splash effect is turned off.
Here's an example of good Dart code:
ButtonStyle(
  backgroundColor: MaterialStateProperty.all<Color>(Colors.deepPurpleAccent),
  foregroundColor: MaterialStateProperty.all<Color>(Colors.white),
  overlayColor: MaterialStateProperty.all<Color>(Colors.transparent),
  shape: MaterialStateProperty.all<OutlinedBorder>(
    RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(8.0),
      side: BorderSide(color: Colors.deepPurple),
    ),
  ),
  elevation: MaterialStateProperty.all<double>(14),
)

`;


export async function generateButtonStyle(){
  vscode.window.showInformationMessage('Generating Button Style...');

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
  const fullPrompt = `${PROMPT_PRIMING + BUTTONSTYLE_CONTEXT + selectedPrompt}`;

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
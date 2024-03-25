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
import {PROMPT_PRIMING} from './components/component';

// Provide instructions for the AI language model
// This approach uses a few-shot technique, providing a few examples.
const COMMENT_LABEL = 'Here is the comment:';
const CODE_LABEL = 'Here is good code:';
const PROMPT = `
${COMMENT_LABEL}
Construct a CardTheme object in flutter that removes elevation and adds a 2px black border with 16px rounded corners.
${CODE_LABEL}
CardTheme(
    elevation: 0,
    shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
        color: Colors.black,
        width: 2,
        ),
    ),
)

${COMMENT_LABEL}
Construct a ColorScheme object in Flutter that has a pastel pink color palette and aesthetically pleasing.
${CODE_LABEL}
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
This example code is a good because it explicitly definess and set all of the
available color properties on a ColorScheme instead of using deprecated properties
like Color Swatch.

${COMMENT_LABEL}
Construct a ThemeData object with a pastel pink color palette that is asthetically 
pleasing and a the CardTheme that removes elevation and adds a 2px black border.
${CODE_LABEL}
ThemeData(
    cardTheme: CardTheme(
        elevation: 0,
        shape: RoundedRectangleBorder(
        side: BorderSide(
            color: Colors.black,
            width: 2,
        ),
        ),
    ),
    colorScheme: ColorScheme(
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
    ),
)

${COMMENT_LABEL}
Add a Google fonts sans-serif text theme to that ThemeData object.
${CODE_LABEL}
ThemeData(
    textTheme: GoogleFonts.rubikTextTheme(),
)`


export async function generateTheme() {
    vscode.window.showInformationMessage('Generating comment...');

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
    const fullPrompt = `${PROMPT_PRIMING} + ${PROMPT} + ${selectedPrompt}`;

    const result = await gemini.generateContent(fullPrompt);
    const response = result.response;
    
    if (!response) {
        console.error('No candidates', response);
        vscode.window.showErrorMessage('No comment candidates returned. Check debug logs.');
        return;
    }
    const comment = response.text();

    // Insert before selection.
    editor.edit((editBuilder) => {

        // Copy the indent from the first line of the selection.
        const trimmed = selectedPrompt.trimStart();
        const padding = selectedPrompt.substring(0, selectedPrompt.length - trimmed.length);

        let pyComment = comment.split('\n').map((l: string) => `${padding}${l}`).join('\n');
        if (pyComment.search(/\n$/) === -1) {
            // Add a final newline if necessary.
            pyComment += "\n";
        }
        
        editBuilder.insert(selection.start, pyComment);
    });
}

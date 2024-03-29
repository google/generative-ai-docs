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
import { generateTheme } from './theme';
import { generateButtonStyle} from './components/buttonstyle';
import { generateColorScheme} from './components/colorscheme';
import { generateTextTheme } from './components/texttheme';

export function activate(context: vscode.ExtensionContext) {
	vscode.commands.registerCommand('flutter-theme-agent.generateTextTheme', generateTextTheme);
	vscode.commands.registerCommand('flutter-theme-agent.generateColorScheme', generateColorScheme);
	vscode.commands.registerCommand('flutter-theme-agent.generateButtonStyle', generateButtonStyle);
	vscode.commands.registerCommand('flutter-theme-agent.generateTheme', generateTheme);
}

export function deactivate() { }

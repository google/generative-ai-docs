/**
 * Copyright 2024 Jason
 */

import * as vscode from "vscode";
import { ChatSession, GoogleGenerativeAI } from "@google/generative-ai";

export function startchat(): ChatSession | void {
  const modelName = vscode.workspace
    .getConfiguration()
    .get<string>("google.gemini.textModel", "default");

  // Get API Key from local user configuration
  const apiKey = vscode.workspace
    .getConfiguration()
    .get<string>("google.gemini.apiKey", "default");

  const systemInstruction = vscode.workspace
    .getConfiguration()
    .get<string>("google.gemini.systemInstruction", "default");

  if (!apiKey) {
    vscode.window.showErrorMessage(
      "API key not configured. Check your settings."
    );
    return undefined;
  }

  const genai = new GoogleGenerativeAI(apiKey);
  const model = genai.getGenerativeModel(
    { model: modelName },
    { apiVersion: "v1beta" }
  );
  const chat = model.startChat({
    systemInstruction: {
      role: "system",
      parts: [
        {
          text: systemInstruction,
        },
      ],
    },
  });
  return chat;
}
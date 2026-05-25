import { GoogleGenerativeAI, type FunctionDeclaration, SchemaType } from "@google/generative-ai";

export const controlTools: FunctionDeclaration[] = [
  {
    name: "mouseMove",
    description: "Move the mouse cursor to a specific coordinate.",
    parameters: {
      type: SchemaType.OBJECT,
      properties: {
        x: { type: SchemaType.NUMBER, description: "X coordinate" },
        y: { type: SchemaType.NUMBER, description: "Y coordinate" },
      },
      required: ["x", "y"],
    },
  },
  {
    name: "mouseClick",
    description: "Click the mouse button.",
    parameters: {
      type: SchemaType.OBJECT,
      properties: {
        button: { 
          type: SchemaType.STRING, 
          enum: ["left", "right", "middle"], 
          format: "enum",
          description: "The button to click" 
        },
      },
      required: ["button"],
    },
  },
  {
    name: "keyTap",
    description: "Press a key or a key combination.",
    parameters: {
      type: SchemaType.OBJECT,
      properties: {
        key: { type: SchemaType.STRING, description: "The key to press (e.g., 'enter', 'a', 'esc')" },
        modifiers: { type: SchemaType.ARRAY, items: { type: SchemaType.STRING }, description: "Modifier keys (e.g., ['control', 'shift'])" },
      },
      required: ["key"],
    },
  },
  {
    name: "typeString",
    description: "Type a sequence of characters.",
    parameters: {
      type: SchemaType.OBJECT,
      properties: {
        text: { type: SchemaType.STRING, description: "The text to type" },
      },
      required: ["text"],
    },
  }
];

export class GeminiService {
  private genAI: GoogleGenerativeAI;
  private model: any;

  constructor(apiKey: string) {
    this.genAI = new GoogleGenerativeAI(apiKey);
    this.model = this.genAI.getGenerativeModel({
      model: "gemini-2.0-flash", // Use a fast model
      tools: [{ functionDeclarations: controlTools }],
    });
  }

  async processPrompt(prompt: string) {
    const chat = this.model.startChat();
    const result = await chat.sendMessage(prompt);
    const response = result.response;
    const calls = response.functionCalls();
    return {
      text: response.text(),
      calls: calls || []
    };
  }
}

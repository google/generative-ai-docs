# Gemini and LangChain.js quickstart (Node.js)

This example shows you how to invoke
[Gemini](https://ai.google.dev/docs/gemini_api_overview) models using
[LangChain.js](https://js.langchain.com/docs/get_started/introduction).

To learn more about the Google AI integration with LangChain.js, see the
following resources:

* [LangChain.js: Google](https://js.langchain.com/docs/integrations/platforms/google)
* [LangChain.js: ChatGoogleGenerativeAI](https://js.langchain.com/docs/integrations/chat/google_generativeai)
* [LangChain.js: Text embedding models: Google AI](https://js.langchain.com/docs/integrations/text_embedding/google_generativeai)
* [LangChain.js: GoogleGenerativeAIEmbeddings](https://api.js.langchain.com/classes/langchain_google_genai.GoogleGenerativeAIEmbeddings.html)

## Setup

1. Set the `GOOGLE_API_KEY` environment variable, replacing `<API_KEY>` with
your [API key](https://ai.google.dev/tutorials/setup):
   ```
   export GOOGLE_API_KEY=<API_KEY>
   ```
   If you don't already have an API key, you can create one through Google AI
   Studio: [Get an API key](https://makersuite.google.com/app/apikey).

   Note: If you don't want to set an environment variable, you can pass your API
   key directly to the model:

   ```javascript
   const model = new ChatGoogleGenerativeAI({
     apiKey: '<API_KEY>',
     // ... other params
   });
   ```

2. Download an image for testing:
   ```
   curl -o image.jpg https://t0.gstatic.com/licensed-image?q=tbn:ANd9GcQ_Kevbk21QBRy-PgB4kQpS79brbmmEG7m3VOTShAn4PecDU5H5UxrJxE3Dw1JiaG17V88QIol19-3TM2wCHw
   ```

3. Install the package dependencies:
   ```
   npm install
   ```

## Run

```
npm start
```

## Learn more

You can also use the
[Google AI JavaScript SDK](https://github.com/google/generative-ai-js) to
interact with Gemini. To learn more about using Gemini in your Node.js
applications, see
[Quickstart: Get started with the Gemini API in Node.js applications](https://ai.google.dev/tutorials/node_quickstart).

To learn more about the Gemini embedding service, see the
[embeddings guide](https://ai.google.dev/docs/embeddings_guide).


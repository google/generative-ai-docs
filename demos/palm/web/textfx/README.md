# TextFX

By Google Creative Lab

## Contents

- [About](#about)
- [How it Works](#how-it-works)
- [Requirements](#requirements)
- [Developer Setup](#developer-setup)
- [Contributors](#contributors)
- [License](#license)
- [Notes](#notes)

## About

_TextFX_ is an AI experiment built in collaboration with GRAMMY® Award-winning rapper Lupe Fiasco.

It contains 10 AI-powered 10 tools, each designed to explore creative possibilities with text and language.

![TextFX demo gif](https://storage.googleapis.com/textfx-assets/demo.gif)

A live hosted version of _TextFX_ is available at [textfx.withgoogle.com](https://textfx.withgoogle.com/).

This experiment is an example of how you can use the PaLM API to build applications that leverage Google's state of the art large language models (LLMs).

The PaLM API consists of two services, each with a distinct method for generating content:

- The Chat service can be used to generate candidate `Message` responses to input messages via the `generateMessage()` function.
- The Text service can be used to generate candidate `TextCompletion` responses to input strings via the `generateText()` function.

_TextFX_ uses the Text service of the PaLM API. For more examples of how you can use the PaLM API, see [this repo](https://github.com/google/generative-ai-docs).

## How it Works

We can prime the LLM to behave in a certain way using a carefully crafted string of text called a **prompt**. When we send the prompt to the model, the model predicts an extension or fulfillment of that text.

Below is an example of a simple text prompt:

```
For each animal below, the animal's color is given.
Animal: crab
Color: red
Animal: frog
Color: green
Animal: blue jay
Color: blue
Animal: flamingo
Color:
```

If we send the above string to the model, we might expect the model to output “pink” (likely followed by additional animals and their respective colors). Adapting this prompt to generate the color of a different animal is simply a matter of replacing “flamingo” with the desired animal. Each complete (animal, color) pair in the prompt can be thought of as an **example**—it often only takes a few examples to establish a pattern that the model can follow.

_TextFX_ uses this same strategy to prime the model to perform the tasks associated with each of its tools. You can find all the prompts in `src/lib/priming.js`, or view them in the app by clicking "Look Under the Hood."

## Requirements

- Node.js (version 18.15.0 or higher)
- Firebase project

Make sure you have `npm` or `yarn` set up on your machine.

## Developer Setup

Although the PaLM API provides a [REST resource](https://developers.generativeai.google/api/rest/generativelanguage/models?hl=en), it is best practice to avoid embedding API keys directly into code (or in files inside your application's source tree). If you want to call the PaLM API from the client side as we do in this repo, we recommend using a Firebase project with the Call PaLM API Securely extension enabled.

To set up Firebase:

1. Create a Firebase project at https://console.firebase.google.com.

2. Add a web app to your Firebase project and follow the on-screen instructions to add or install the Firebase SDK.

3. Go to https://console.cloud.google.com and select your Firebase project. Then go to _Security > Secret Manger_ using the left-side menu and make sure the Secret Manager API is enabled.

4. If you don't already have an API key for the PaLM API, follow [these instructions](https://developers.generativeai.google/tutorials/setup) to get one.

5. Install the Call PaLM API Securely extension from the [Firebase Extensions Marketplace](https://extensions.dev/extensions). Follow the on-screen instructions to configure the extension.

   **NOTE**: Your project must be on the Blaze (pay as you go) plan to install the extension.

6. Enable anonymous authentication for your Firebase project by returning to https://console.firebase.google.com and selecting _Build_ in the left panel. Then go to _Authentication > Sign-in method_ and make sure _Anonymous_ is enabled.

7. Return to https://console.cloud.google.com and select your Firebase project. Click _More Products_ at the bottom of the left-side menu, then scroll down and click _Cloud Functions_. Select each `ext-palm-secure-backend` Cloud Function and then click _Permissions_ at the top. Add `allUsers` to the Cloud Functions Invoker role.

The above instructions assume that your Firebase backend will be used for individual/experimental purposes. If you anticipate broader usage, consider enabling App Check (see https://firebase.google.com/docs/app-check for an in-depth implementation guide).

To run the application locally:

1. Clone this repo to your local machine.

2. Run `npm i` or `yarn` in the root folder to install dependencies.

3. Add your Firebase info to `src/lib/firebase.config.js`.

4. Run `npm run dev` or `yarn dev` to start the application. The application will be served on localhost:5555. You can change the port in `vite.config.js` if desired.

## Contributors

- [Aaron Wade](https://github.com/aaron-wade)
- [Pixel Perfect Development](https://github.com/madebypxlp)

## License

[Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0)

## Notes

This is not an official Google product, but rather an experiment developed by the Google Creative Lab. This repository is meant to provide a snapshot of what is possible at this moment in time, and we do not intend for it to evolve.

We encourage open sourcing projects as a way of learning from each other. Please respect our and other creators' rights—including copyright and trademark rights (when present)—when sharing these works or creating derivative work. If you want more info about Google's policies, you can find that [here](https://about.google/brand-resource-center/).

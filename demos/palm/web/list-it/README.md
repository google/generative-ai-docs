# List It

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

_List It_ is a simple app where a user can input a goal or task and have a generative language model output a list of subtasks related to that query.

![List It demo gif](https://storage.googleapis.com/experiments-uploads/list-it/list-it.gif)

This demo is an example of how you can use the PaLM API to build AI-enabled applications that leverage Google’s state of the art large language models (LLMs).

The PaLM API consists of two APIs, each with a distinct method for generating content:

- The Chat API can be used to generate candidate `Message` responses to input messages via the `generateMessage()` function.
- The Text API can be used to generate candidate `TextCompletion` responses to input strings via the `generateText()` function.

This demo uses the Text API. If you’re looking for a demo that uses the Chat API, see [_Quick, Prompt!_](https://github.com/google/generative-ai-docs/tree/main/demos/palm/web/quick-prompt).

## How it Works

We can guide the model to produce a desired output by devising an input string, called a __prompt__, that helps the model recognize how it should respond to a given text input. It’s helpful to think of the model as a highly sophisticated text-completion engine: given the context we provide in our prompt, the model tries to output a feasible continuation or completion of that string.

Below is an example of a simple text prompt:

```
For each animal below, the color of that animal is given.
Animal: crab
Color: red
Animal: frog
Color: green
Animal: blue jay
Color: blue
Animal: flamingo
Color:
```

If we send the above string to the model, we might expect the model to output “pink” (likely followed by additional animals and their colors). We can think of “flamingo” as the input to this prompt because we expect the model to generate its corresponding color. Each complete (animal, color) pair in the prompt can be thought of as an __example__—it often only takes a few examples to establish a pattern that the model can follow.

_List It_ uses this same mechanism to prime the model to generate a list from a user input. You can find the prompt in [`priming.js`](/src/lib/priming.js).

## Requirements

- Node.js (v18.15.0 or higher)
- Firebase project

Make sure you have either `npm` or `yarn` set up on your machine.

## Developer Setup

Although the PaLM API provides a [REST resource](https://developers.generativeai.google/api/rest/generativelanguage/models?hl=en), it is best practice to avoid embedding API keys directly into code (or in files inside your application’s source tree). If you want to call the PaLM API from the client side as we do in this demo, we recommend using Firebase with the Call PaLM API Securely extension.

To set up Firebase:

1. Create a Firebase project at https://console.firebase.google.com.

2. Add a web app to your Firebase project and follow the on-screen instructions to add or install the Firebase SDK.

3. Go to https://console.cloud.google.com and select your Firebase project. Then go to _Security > Secret Manger_ using the left-side menu and make sure the Secret Manager API is enabled.

4. If you don’t already have an API key for the PaLM API, follow [these instructions](https://developers.generativeai.google/tutorials/setup) to get one.

5. Install the Call PaLM API Securely extension from the [Firebase Extensions Marketplace](https://extensions.dev/extensions). Follow the on-screen instructions to configure the extension.

    __NOTE__: Your project must be on the Blaze (pay as you go) plan to install the extension.

6. Enable anonymous authentication for your Firebase project by returning to https://console.firebase.google.com and selecting _Build_ in the left panel. Then go to _Authentication > Sign-in method_ and make sure _Anonymous_ is enabled.

7. Return to https://console.cloud.google.com and select your Firebase project. Click _More Products_ at the bottom of the left-side menu, then scroll down and click _Cloud Functions_. Select each function and then click _Permissions_ at the top. Add `allUsers` to the Cloud Functions Invoker role.

The above instructions assume that this demo will be used for individual/experimental purposes. If you anticipate broader usage, enable App Check in the Firebase extension during installation and see https://firebase.google.com/docs/app-check for an in-depth implementation guide.

To run the application locally:

1. Clone the repo to your local machine.

2. Run `npm i` or `yarn` in the root folder to install dependencies.

3. Add your Firebase info to [`firebase.config.js`](/src/lib/firebase.config.js).

4. Run `npm run dev` or `yarn dev` to start the application. The application will be served on localhost:5555. You can change the port in [`vite.config.js`](/vite.config.js) if desired.

## Contributors

- [Aaron Wade](https://github.com/aaron-wade)
- [Pixel Perfect Development](https://github.com/madebypxlp)

## License

[Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0)

## Notes

This is not an official Google product, but rather a demo developed by the Google Creative Lab. This repository is meant to provide a snapshot of what is possible at this moment in time, and we do not intend for it to evolve.

We encourage open sourcing projects as a way of learning from each other. Please respect our and other creators’ rights—including copyright and trademark rights (when present)—when sharing these works or creating derivative work. If you want more info about Google's policies, you can find that [here](https://about.google/brand-resource-center/).
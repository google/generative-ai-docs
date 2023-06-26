![talking-character-header](./docs/talking-character-header.png)

# LLM Demo - Talking Character

Talking Character is a voice chatbot-based web application that allows users to interact with a 3D character using natural language. Users can provide personality, back story, and knowledge base to this character. Talking Character is powered by PaLM, a large language model from Google. To interact with Talking Character, simply tap on the microphone button and speak to the character. Talking Character will respond to your speech.

Whether you're looking for a fun way to learn about PaLM, or you're interested in voice chatbot, Talking Character is the right demo for you!

ZEPETO, beloved by Gen Z, is an avatar-centric social universe where users can fully customize their digital personas, explore fashion trends, and engage in vibrant self-expression and virtual interaction. Our Talking Character template allows users to create their own avatars, dress them up in different clothes and accessories, and interact with other users in virtual worlds. We are working with ZEPETO and have tested their metaverse avatar with over 50 blendshapes with great results.

**"Seeing an AI character come to life as a ZEPETO avatar and speak with such fluidity and depth is truly inspiring. We believe a combination of advanced language models and avatars will infinitely expand what is possible in the metaverse, and we are excited to be a part of it."- Daewook Kim, CEO, ZEPETO**

The demo is not restricted to metaverse use cases, though. The demo shows how characters can bring text corpus or knowledge bases to life in any domain.

For example in gaming, LLM powered NPCs could enrich the universe of a game and deepen user experience through natural language conversations discussing the game’s world, history and characters.

In education, characters can be created to represent different subjects a student is to study, or have different characters representing different levels of difficulty in an interactive educational quiz scenario, or representing specific characters and events from history to help people learn about different cultures, places, people and times.

In commerce, the Talking Character kit could be used to bring brands and stores to life, or to power merchants in an eCommerce marketplace and democratize tools to make their stores more engaging and personalized to give better user experience. It could be used to create avatars for customers as they explore a retail environment and gamify the experience of shopping in the real world.

Even more broadly, any brand, product or service can use this demo to bring a talking agent to life that can interact with users based on any knowledge set of tone of voice, acting as a brand ambassador, customer service representative, or sales assistant.

![talking-character-screen](./docs/talking-character-screen.png)

## Table of contents

- [LLM Demo - Talking Character](#llm-demo---talking-agent)
  - [Table of contents](#table-of-contents)

  - [How it works](#how-it-works)
    - [LLM's prompt design](#llms-prompt-design)
    - [Context generator](#context-generator)
    - [Prompt generator](#prompt-generator)
    - [LLM's response](#llms-response)
  - [How to install](#how-to-install)
    - [Available Scripts](#available-scripts)
  - [Learn More](#learn-more)
  - [Contributors](#contributors)



## How it works

### LLM's prompt design

![llm-prompt-design-diagram](./docs/llm_prompt_design_diagram.png)

### Context generator

Context is used to give the LLM a better understanding of the conversation. Here is the structure of the context (preamble):

```js
{
  context: `Your task is to acting as a character that has this personality: "${config.state.personality}". Your response must be based on your personality. You have this backstory: "${config.state.backStory}". Your knowledge base is: "${config.state.knowledgeBase}". The response should be one single sentence only.`;
}
```

- The `personality` is a string variable that describes the character's personality traits.
- The `backStory` is a string variable that describes the character's back story.
- The `knowledgeBase` is a string variable that describes the facts that the character would know.

### Prompt generator

In every user's turn, the user's input message `${message}` will be formatted into this structure:

```js
{
    author: '0',
    content: `Please answer within 100 characters. {${message}}. The response must be based on the personality, backstory, and knowledge base that you have. The answer must be concise and short.`
}
```

- The `message` is the user's input message.

Combined with the context, here is the final structure of the prompt sending to the LLM:

```js
{
    prompt: {
        context: `Your task is to acting as a character that has this personality: "${config.state.personality}". Your response must be based on your personality. You have this backstory: "${config.state.backStory}". Your knowledge base is: "${config.state.knowledgeBase}". The response should be one single sentence only.`,
        messages: [
            {
                author: '0',
                content: `Please answer within 100 characters. {${message}}. The response must be based on the personality, backstory, and knowledge base that you have. The answer must be concise and short.`
            },
            ...
        ]
    },
    temperature: 0.25,
    candidate_count: 1,
}
```

- The `messages` is an array of chat messages from past to present alternating between the user (author=0) and the LLM (author=1). The first message is always from the user.
- The `temperature` is a float number between 0 and 1. The higher the temperature, the more creative the response will be. The lower the temperature, the more likely the response will be a correct one.
- The `candidate_count` is the number of responses that the LLM will return.

### LLM's response

The output of the LLM is in this structure:

```js
{
    candidates: [
        {
            author: '1',
            content: 'This is the response content from the LLM.'
        }
    ],
    messages: [
        ...
    ]
}
```

- The `candidates` is an array of responses from the LLM. This project has only one response per turn (as candidate_count=1).
- The `messages` is an array of chat messages from past to present alternating between the user (author=0) and the LLM (author=1). The first message is always from the user.


## How to install
This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

### API_KEYs Setting

This project requires two API_KEYs:

- `GOOGLE_CLOUD_API_KEY`: for speech reconfnition and convert text to speech;
- `LANGUAGE_MODEL_API_KEY`: for accessing language model PaLM.

Edit these two API_KEYs in the file `src/context/constants.ts`.

### Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).


## Contributors

- Mattias Breitholtz
- Pedro Vergani
- Yinuo Wang
- Christian Frueh
- Vivek Kwatra
- Boon Panichprecha
- Lek Pongsakorntorn
- Zeno Chullamonthon
- Yiyao Zhang
- Qiming Zheng
- Joyce Li
- Xiao Di
- KC Chung
- Jay Ji

## Disclaimer

This demo uses synthesized video and speech to make it more natural for users to interact with language models. The avatar used in this demo does not represent a real person or human being.

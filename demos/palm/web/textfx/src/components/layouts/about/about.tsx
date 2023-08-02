/**
 * Copyright 2023 Google LLC
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

import {useEffect, useState, useRef} from 'react'

import Hamburger from '~/components/generic/hamburger/hamburger'

import styles from './about.module.scss'
import c from 'classnames'

interface IAbout {
  onClose: () => void
}

const AboutScreen = ({onClose = () => {}}: IAbout) => {
  const [mounted, setMounted] = useState<boolean>(false)
  const aboutPageRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    setMounted(true)
    aboutPageRef.current?.focus()
  }, [])

  return (
    <div
      ref={aboutPageRef}
      className={c(styles.aboutScreen, mounted && styles.fadeIn)}
      tabIndex={-1}
    >
      <Hamburger
        theme="light"
        showX={true}
        onClick={() => {
          onClose()
        }}
      />
      <div className="container">
        <div className={styles.content}>
          <h1>About</h1>
          <h2>What is TextFX?</h2>
          <p>
            TextFX is an AI experiment designed to help rappers, writers, and
            wordsmiths expand their process. It was created in collaboration
            with Lupe Fiasco, drawing inspiration from the lyrical and
            linguistic techniques he has developed throughout his career. TextFX
            consists of 10 tools, each is designed to explore creative
            possibilities with text and language.
          </p>
          <p>
            TextFX is powered by Google&apos;s{' '}
            <a
              href="https://ai.google/discover/palm2"
              target="_blank"
              rel="noopener noreferrer"
            >
              PaLM 2
            </a>{' '}
            large language model, via the PaLM API.
          </p>
          <h2>Why did you make this?</h2>
          <p>
            We built TextFX as an experiment to demonstrate how generative
            language technologies can empower the creativity and workflows of
            artists and creators. This app is also an example of how you can use
            the PaLM API to build applications that leverage Google&apos;s
            next-generation large language models (LLMs).
          </p>
          <h2>What is Lab Sessions?</h2>
          <p>
            Google Lab Sessions is an ongoing series of collaborations between
            our latest AI technology and visionaries from all realms of human
            endeavor—from artists to academics, scientists to scientists,
            creators to entrepreneurs, and more.
          </p>
          <p>
            Lab Sessions is part of{' '}
            <a
              href="https://labs.google/"
              target="_blank"
              rel="noopener noreferrer"
            >
              labs.withgoogle.com
            </a>
            —our place to test early stage experiments and shape the future of
            technology, together.
          </p>
          <h2>What is the PaLM API?</h2>
          <p>
            The PaLM API is an entry point to Google&apos;s large language
            models, and it enables developers to build AI-powered applications
            for a variety of use cases. If you&apos;d like to learn more about
            the PaLM API, head{' '}
            <a
              href="https://developers.generativeai.google/products/palm"
              target="_blank"
              rel="noopener noreferrer"
            >
              here
            </a>
            .
          </p>
          <p>
            If you&apos;d like to build your own experiments like this,
            you&apos;ll need an API key. An API key is a unique identifier that
            lets you access the PaLM API. If you have been granted access to the
            PaLM API, you can get an API key by following the instructions{' '}
            <a
              href="https://developers.generativeai.google/tutorials/setup"
              target="_blank"
              rel="noopener noreferrer"
            >
              here
            </a>
            . Otherwise, you can{' '}
            <a
              href="https://makersuite.google.com/waitlist"
              target="_blank"
              rel="noopener noreferrer"
            >
              join the waitlist
            </a>
            .
          </p>
          <h2>What is MakerSuite?</h2>
          <p>
            MakerSuite is a platform that lets users easily experiment with
            LLMs. We used MakerSuite to prototype all of the tools in TextFX.
          </p>
          <p>
            To get started using MakerSuite, head{' '}
            <a
              href="https://developers.generativeai.google/products/makersuite"
              target="_blank"
              rel="noopener noreferrer"
            >
              here
            </a>
            .
          </p>
          <h2>Who is Lupe Fiasco?</h2>
          <p>
            Wasalu Jaco, professionally known as Lupe Fiasco, is a Grammy
            award-winning rapper, professor, entrepreneur, and community
            advocate. Rising to fame in 2006, Lupe has released eight critically
            acclaimed studio albums. His latest is <em>Drill Music In Zion</em>,
            released in June of 2022.
          </p>
          <p>
            Most recently, Lupe&apos;s passion for cognitive science,
            linguistics, semiotics and computing has landed him an MLK Visiting
            Professors and Scholars fellowship at MIT, where he teaches a class
            on rap theory and practice.
          </p>
          <h2>Why am I seeing inappropriate outputs?</h2>
          <p>
            Part of what makes large language models so useful is that
            they&apos;re creative tools that can address many different language
            tasks. Unfortunately, this also means that LLMs can generate outputs
            that you don&apos;t expect, including text that&apos;s offensive,
            insensitive, or factually incorrect. Although the PaLM API filters
            these kinds of outputs, we cannot guarantee that they will be
            removed completely.
          </p>
          <h2>Is my data being collected?</h2>
          <p>
            This site uses analytics to monitor activity and optimize
            functionality.
          </p>
          <p>
            For information about how the PaLM API collects data, see{' '}
            <a
              href="https://developers.generativeai.google/terms"
              target="_blank"
              rel="noopener noreferrer"
            >
              this page
            </a>
            .
          </p>
          <h2>Who can I contact about this project?</h2>
          <p>
            If you have other questions or concerns, contact us at
            textfx-support@google.com.
          </p>
        </div>
      </div>
    </div>
  )
}

export default AboutScreen

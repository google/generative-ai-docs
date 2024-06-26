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

import {useEffect, useRef, useState} from 'react'
import YouTube, {YouTubePlayer} from 'react-youtube'

import styles from './youtubePlayer.module.scss'

interface IYoutubePlayer {
  videoId: string
  videoOptions: {[key: string]: any}
  poster?: string
  posterAltText?: string
}

const YoutubePlayer = ({
  videoId,
  videoOptions,
  poster,
  posterAltText
}: IYoutubePlayer) => {
  const [hasStarted, setHasStarted] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)

  const youtubePlayerRef = useRef(null)

  useEffect(() => {
    if (isPlaying) {
      setHasStarted(true)
    }
  }, [isPlaying])

  const handlePlayButtonClick = () => {
    if (youtubePlayerRef.current) {
      if (isPlaying) {
        ;(youtubePlayerRef.current as YouTubePlayer).pauseVideo()
      } else {
        ;(youtubePlayerRef.current as YouTubePlayer).playVideo()
      }
    }
  }

  return (
    <div className={styles.container}>
      {poster && (
        <div
          className={`${styles.posterContainer} ${
            hasStarted ? styles.hidden : styles.visible
          }`}
        >
          <img
            className={styles.poster}
            src={poster}
            alt={posterAltText ? posterAltText : 'Video poster'}
          ></img>
        </div>
      )}
      <YouTube
        videoId={videoId}
        opts={videoOptions}
        onReady={event => (youtubePlayerRef.current = event.target)}
        onStateChange={event =>
          setIsPlaying(event.data === YouTube.PlayerState.PLAYING)
        }
      />
      a
      <button
        aria-label="Play video"
        className={`${styles.playButton} ${
          isPlaying ? styles.hidden : styles.visible
        }`}
        onClick={handlePlayButtonClick}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="120"
          height="120"
          fill="none"
          viewBox="0 0 120 120"
          className={styles.default}
        >
          <path
            fillRule="evenodd"
            d="M60 120C93.1371 120 120 93.1371 120 60C120 26.8629 93.1371 0 60 0C26.8629 0 0 26.8629 0 60C0 93.1371 26.8629 120 60 120ZM48.4489 79.987L83.0642 60.0018L48.4489 40.0166V79.987Z"
            clipRule="evenodd"
          />
        </svg>
        <svg
          width="120"
          height="120"
          viewBox="0 0 120 120"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className={styles.hover}
        >
          <mask id="path-1-inside-1_709_6066" fill="white">
            <path d="M120 60C120 93.1371 93.1371 120 60 120C26.8629 120 0 93.1371 0 60C0 26.8629 26.8629 0 60 0C93.1371 0 120 26.8629 120 60Z" />
          </mask>
          <path
            d="M119 60C119 92.5848 92.5848 119 60 119V121C93.6894 121 121 93.6894 121 60H119ZM60 119C27.4152 119 1 92.5848 1 60H-1C-1 93.6894 26.3106 121 60 121V119ZM1 60C1 27.4152 27.4152 1 60 1V-1C26.3106 -1 -1 26.3106 -1 60H1ZM60 1C92.5848 1 119 27.4152 119 60H121C121 26.3106 93.6894 -1 60 -1V1Z"
            mask="url(#path-1-inside-1_709_6066)"
          />
          <path d="M83.0625 60.0027L48.4471 79.9879L48.4471 40.0175L83.0625 60.0027Z" />
        </svg>
      </button>
    </div>
  )
}

export default YoutubePlayer

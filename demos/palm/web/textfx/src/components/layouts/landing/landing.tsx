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

import {useState, useRef, useEffect, Fragment} from 'react'
import {useActions, useMacros} from '~/store'
import {Swiper, SwiperSlide, SwiperRef} from 'swiper/react'
import SwiperCore, {Pagination, Navigation, Autoplay} from 'swiper'
import Icon, {IIcon} from '~/components/generic/icon/icon'
import {IMacro} from '~/constants'

import useOnScreen from '~/hooks/useOnScreen'
import Lottie from 'react-lottie-player'
import YoutubePlayer from '~/components/generic/youtubePlayer/youtubePlayer'
import LupeLogo from './lupeLogo'
import LabSessionsLogo from './labsSessionsLogo'
import LandingLogo from './landingLogo'
import GoogleLogo from './googleLogo'
import rightColAnimation from '~/assets/landing_right_col_animation_lottie.json'
import videoPosterImage from '~/assets/images/landing-video-poster.jpg'

import styles from './landing.module.scss'
import c from 'classnames'

interface ILanding {
  onLaunchButtonClick: () => void
}

const Landing = ({onLaunchButtonClick}: ILanding) => {
  const {macros} = useMacros()
  const [activeMacro, setActiveMacro] = useState<string>(macros[0].id)
  const {setShowAbout} = useActions()
  const [swiper, setSwiper] = useState<SwiperCore>()
  const [lotties, setLotties] = useState<(object | undefined)[]>(
    Array(macros.length).fill(null) as (object | undefined)[]
  )
  const videoRef = useRef<HTMLDivElement | null>(null)
  const swiperRef = useRef<SwiperRef | null>(null)
  const timeoutRef = useRef<number>(-1)
  const onScreen = useOnScreen(swiperRef)
  const leftColRef = useRef<HTMLDivElement | null>(null)
  const nextRef = useRef<HTMLDivElement | null>(null)
  const prevRef = useRef<HTMLDivElement | null>(null)

  const pagination = {
    clickable: true,
    renderBullet: (index: number, className: string) =>
      `<span class="${c(styles.dot, className)}"></span>`
  }

  useEffect(() => {
    macros.forEach((macro: IMacro, i: number) => {
      fetch(`/assets/landing/lotties/${macro.lottie}.json`).then(res => {
        res.json().then(json => {
          setLotties(prev => {
            const newLotties = [...prev]
            newLotties[i] = json
            return newLotties
          })
        })
      })
    })

    const showHideHamburger = () => {
      if (!leftColRef.current) return

      if (window.scrollY <= leftColRef.current.clientHeight) {
        document.body.classList.add('mobile-hide-hamburger')
      } else {
        document.body.classList.remove('mobile-hide-hamburger')
      }
    }

    showHideHamburger()

    document.addEventListener('scroll', showHideHamburger)
    return () => {
      document.removeEventListener('scroll', showHideHamburger)
    }
  }, [])

  useEffect(() => {
    if (!swiper) return

    if (onScreen) {
      swiper.autoplay.start()
    } else {
      swiper.autoplay.pause()
      clearTimeout(timeoutRef.current)
    }
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [onScreen])

  useEffect(() => {
    if (!swiper) return

    swiper.autoplay.stop()
  }, [swiper])

  return (
    <div className={c(styles.root)}>
      <div className={styles.splitScreen}>
        <div ref={leftColRef} className={styles.leftCol}>
          <div className={styles.colHead}>
            <div className={styles.colHeadLogoContainer}>
              <LupeLogo className={styles.lupeLogo} />
            </div>
            <div className={styles.colHeadLogoContainer}>
              <LabSessionsLogo className={styles.labSessionsLogo} />
            </div>
          </div>
          <LandingLogo className={styles.landingLogo} />
          <div className={styles.subtitle}>
            <p>AI-powered tools for rappers, writers and wordsmiths.</p>
          </div>
        </div>
        <div className={styles.rightCol}>
          <div className={styles.rightColLottieContainer}>
            <Lottie
              play={true}
              loop={true}
              animationData={rightColAnimation}
              rendererSettings={{preserveAspectRatio: 'xMinYMid slice'}}
            />
          </div>
        </div>

        <button
          className={styles.arrowDown}
          aria-label="Scroll down"
          onClick={() => videoRef.current?.scrollIntoView()}
        >
          <Icon name="arrowDown" />
        </button>
      </div>

      <div className={styles.videoSection} ref={videoRef}>
        <YoutubePlayer
          videoId="yYp18JAvKkQ"
          videoOptions={{}}
          poster={videoPosterImage}
          posterAltText="Lupe Fiasco writing a rap"
        />
      </div>

      <div className={styles.description}>
        <p>
          TextFX is an AI experiment that uses Google&apos;s PaLM 2 large
          language model. These 10 tools are designed to expand the writing
          process by generating creative possibilities with text and language.
        </p>
      </div>

      <div className={c(styles.divider, 'container')}>
        <svg
          width="1200"
          height="76"
          viewBox="0 0 1200 76"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <line
            x1="600.5"
            y1="-2.18557e-08"
            x2="600.5"
            y2="52"
            stroke="#666666"
          />
          <line x1="0.5" y1="52" x2="0.500001" y2="76" stroke="#666666" />
          <line x1="1199.5" y1="52" x2="1199.5" y2="76" stroke="#666666" />
          <line x1="1199" y1="52.5" y2="52.5" stroke="#666666" />
        </svg>
      </div>

      <div className={styles.macroSection}>
        <div className={styles.horizontalScrollWrapper}>
          <ul className={c(styles.macroButtons, 'container')}>
            {macros?.map((macro: IMacro, i: number, macros: IMacro[]) => {
              const isActive = activeMacro === macro.id
              const isLast = i === macros.length

              return (
                <Fragment key={macro.id}>
                  <li className={`${styles[macro.id]}`}>
                    <button
                      type="button"
                      aria-label={macro.name}
                      className={c(
                        styles.macroButton,
                        isActive && styles.isActive
                      )}
                      onClick={() => {
                        setActiveMacro(macro.id)

                        if (!swiper) return

                        swiper.slideToLoop(i)
                      }}
                    >
                      <Icon
                        name={macro.icon as IIcon['name']}
                        className={styles.icon}
                      />
                      <span className={styles.text}>{macro.name}</span>
                    </button>
                  </li>
                  {isLast && <li className={styles.spacer} />}
                </Fragment>
              )
            })}
          </ul>
        </div>
        <div className={c(styles.macroContent, 'container')}>
          <div style={{position: 'relative'}}>
            <Swiper
              ref={swiperRef}
              slidesPerView={1}
              loop
              navigation={{
                prevEl: prevRef.current,
                nextEl: nextRef.current
              }}
              onSlideChange={swiper => {
                setActiveMacro(macros[swiper.realIndex].id)
              }}
              onSwiper={swiper => setSwiper(swiper)}
              pagination={pagination}
              modules={[Pagination, Navigation, Autoplay]}
              speed={600}
              autoplay={{
                delay: 7000,
                disableOnInteraction: true
              }}
            >
              {macros.map((macro, i) => {
                return (
                  <SwiperSlide key={macro.id} aria-hidden="true">
                    {lotties[i] && (
                      <Lottie
                        play={onScreen && activeMacro === macro.id}
                        loop={false}
                        animationData={lotties[i]}
                      />
                    )}
                  </SwiperSlide>
                )
              })}
            </Swiper>
            <div ref={prevRef} className={c(styles['swiper-button-prev'])}>
              <Icon name="swiperArrow" />
            </div>
            <div ref={nextRef} className={c(styles['swiper-button-next'])}>
              <Icon name="swiperArrow" />
            </div>
          </div>
        </div>

        <div></div>
      </div>
      <div className={c(styles.ctaSection, 'container')}>
        <button onClick={onLaunchButtonClick}>Launch TextFX</button>
      </div>
      <footer className={styles.footer}>
        <div className="container">
          <ul className={styles.list}>
            <li>
              <a href="/" aria-label="Home" className={styles.googleLogo}>
                <GoogleLogo />
              </a>
            </li>
            <li>
              <a
                className={styles.link}
                href="https://policies.google.com/privacy?hl=en"
                target="_blank"
                rel="noopener noreferrer"
              >
                Privacy
              </a>
            </li>
            <li>
              <a
                className={styles.link}
                href="https://policies.google.com/terms?hl=en"
                target="_blank"
                rel="noopener noreferrer"
              >
                Terms
              </a>
            </li>
            <li>
              <a
                className={styles.link}
                href="/"
                onClick={e => {
                  e.preventDefault()
                  setShowAbout(true)
                }}
              >
                About
              </a>
            </li>
          </ul>
        </div>
      </footer>
    </div>
  )
}

export default Landing

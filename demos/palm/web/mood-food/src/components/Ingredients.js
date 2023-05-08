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

import React, { useEffect, useRef, useState } from 'react';
import styled from '@emotion/styled';

import { Close, ServingLogo } from '../assets/icons';
import SolidArrowDown from '../assets/icons/SolidArrowDown.svg';

import { frontNumberCleaner } from '../utils/orderlist';

const IngredientsStyle = styled.div`
  width: 100%;
  height: 100%;
  position: fixed;
  top: ${(props) => (props.openIngredients ? '0%' : '120%')};
  left: 0;
  z-index: 20;
  color: #423443;
  transition: top 0.5s cubic-bezier(0.23, 1, 0.32, 1);
  display: flex;
  justify-content: center;

  .header {
    display: flex;
    flex-direction: row;
    text-align: center;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin: 0rem;
    h1 {
      width: 58%;
      font-size: 1rem;
      color: #646464;
    }
    font-size: 1.5rem;
    position: relative;
  }

  .content {
    height: 100%;
    width: 100%;
    background-color: white;
    overflow-x: hidden;
    overflow-y: scroll;
  }
`;

const AccordionStyle = styled.div`
  height: fit-content;
  max-height: ${(props) => (props['aria-selected'] ? `calc(${props.extendedHeight} + 100px)` : '3.2rem')};
  width: 100%;
  padding: 1.5rem;
  padding-left: 0rem;
  margin-bottom: 12rem;
  overflow: hidden;

  transition: all 0.4s;

  .accordion-header {
    display: flex;
    flex-direction: row;
    justify-content: center;
    padding-left: 0.75rem;
    gap: 1rem;
    align-items: center;
    height: 51.2px;
    img {
      transform: ${(props) => (props['aria-selected'] ? 'rotate(180deg)' : '')};
    }
    p {
      font-weight: 500;
    }
  }

  .accordion-content {
    padding: 0rem;
    width: 80%;
    padding-left: 1.5rem;
    white-space: pre-wrap;
    ul {
      margin-top: 0;
      text-align: center;
      list-style-position: inside;
    }

    ol {
      margin-top: 0;
    }

    height: 100%;
  }
`;

const FixedStyle = styled.div`
  height: fit-content;
  width: 100%;
  padding: 1.5rem;
  padding-left: 0rem;
  overflow: hidden;

  transition: all 0.4s;

  .accordion-header {
    display: flex;
    flex-direction: row;
    justify-content: center;
    width: 100%;
    gap: 1rem;
    align-items: center;
    height: 51.2px;
    padding-left: 0.25rem;
    img {
      transform: ${(props) => (props['aria-selected'] ? 'rotate(180deg)' : '')};
    }
    p {
      font-weight: 500;
    }
  }

  .accordion-content {
    padding: 0rem;
    width: 90%;
    margin: auto;
    white-space: pre-wrap;
    ul {
      margin-top: 0;
      text-align: center;
      list-style-position: inside;
      padding-right: 40px;
    }

    ol {
      margin-top: 0;
    }
  }
`;

export default function Ingredients({
  name,
  ingredients,
  instructions,
  openIngredients,
  handleOpenIngredients,
  fontHeaderProperties,
  pallete,
}) {
  const [expand, setExpand] = useState(0);

  const contentRef = useRef(null);
  const [extendedHeight, setExtendedHeight] = useState(0);

  const clickExpand = (id) => {
    setExpand(id);
  };

  useEffect(() => {
    if (contentRef.current) {
      setExtendedHeight(contentRef.current.clientHeight + 'px');
    }
  }, [contentRef]);

  const [bgColor, typoColor] = pallete;

  return (
    <IngredientsStyle openIngredients={openIngredients}>
      <div style={{ height: '100%', width: '100%', maxWidth: '1024px', backgroundColor: bgColor }}>
        <div className="header" style={{ borderBottom: `solid 1.5px ${typoColor}` }}>
          <h1 style={{ ...fontHeaderProperties, color: typoColor, marginBottom: '1.25rem' }}>{name}</h1>
          <div
            style={{ position: 'absolute', right: '1rem', top: '1.25rem', width: '1.75rem' }}
            onClick={() => handleOpenIngredients(0)}
          >
            {Close('none', typoColor)}
          </div>
        </div>
        <div style={{ height: '3px', borderBottom: `solid 0.5px #423443` }}></div>
        <div className="content">
          <FixedStyle className="accordion">
            <div className="accordion-header">
              <p>Ingredients:</p>
            </div>
            <div className="accordion-content">
              <ul>
                {ingredients.map((item, index) => {
                  return <li key={`ingre-${index}`}>{item}</li>;
                })}
              </ul>
            </div>
          </FixedStyle>
          <div style={{ display: 'flex', direction: 'row', justifyContent: 'center' }}>
            {ServingLogo('none', '#423443')}
          </div>
          <AccordionStyle
            className="accordion"
            aria-selected={expand === 1}
            onClick={() => clickExpand(Number(!expand))}
            extendedHeight={extendedHeight}
          >
            <div className="accordion-header">
              <p>Instructions:</p>
              <img src={SolidArrowDown} />
            </div>
            <div className="accordion-content" ref={contentRef}>
              <ol>
                {instructions.map((item, index) => {
                  return <li key={`instr-${index}`}>{frontNumberCleaner(item)}</li>;
                })}
              </ol>
            </div>
          </AccordionStyle>
        </div>
      </div>
    </IngredientsStyle>
  );
}

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

import React, { useState } from 'react';

import Dialogue from './Dialogue';
import Ingredients from './Ingredients';
import { ChefLogo } from 'src/assets/icons';

const BotResponses = (props) => {
  const { reaction, recipes, typeItInstance, imageWidth, imageRef } = props;
  const [openIngredients, setOpenIngredients] = useState(0);
  const baseFontSize = imageWidth / 12;

  const handleOpenIngredients = (key) => {
    setOpenIngredients(key);
  };

  if (recipes && typeItInstance && !typeItInstance.is('destroyed')) {
    typeItInstance.destroy();
  }

  return (
    <Dialogue key={`diag-bot`} type={'bot'}>
      {ChefLogo('none', '#646464')}
      <p
        style={{
          margin: 0,
          marginTop: '0.5rem',
          fontSize: '1rem',
          lineHeight: '1.6rem',
          marginBottom: !typeItInstance && '5rem',
        }}
      >
        {reaction}
      </p>
      {recipes &&
        typeItInstance &&
        recipes.map((recipe, index) => {
          const [image, fontHeaderProperties, pallete] = recipe.getImage(imageRef);
          return (
            <div key={`recipe-${index}`}>
              <div
                onClick={() => handleOpenIngredients(index + 1)}
                style={{
                  marginBottom: '1.5rem',
                  marginTop: '1.5rem',
                  fontSize: baseFontSize,
                  lineHeight: baseFontSize,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                }}
              >
                {image}
              </div>
              <p>{recipe.description}</p>
              <Ingredients
                name={recipe.name}
                ingredients={recipe.ingredients}
                instructions={recipe.instructions}
                openIngredients={index + 1 === openIngredients}
                handleOpenIngredients={handleOpenIngredients}
                fontHeaderProperties={fontHeaderProperties}
                pallete={pallete}
              />
            </div>
          );
        })}
    </Dialogue>
  );
};

export default BotResponses;

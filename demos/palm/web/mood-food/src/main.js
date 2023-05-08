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

import React, { Fragment } from 'react';
import Div100vh from 'react-div-100vh';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

import Chat from './pages/chat';
import Home from './pages/home';

import './index.css';
import 'swiper/css';
import 'swiper/css/pagination';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Home />,
  },
  {
    path: '/chat',
    element: <Chat />,
  },
]);

ReactDOM.createRoot(document.getElementById('root')).render(
  <Fragment>
    <Div100vh style={{ overflowY: 'auto', display: 'flex', justifyContent: 'center', background: '#f8f7f7' }}>
      <Div100vh style={{ maxWidth: '1024px' }}>
        <RouterProvider router={router} />
      </Div100vh>
    </Div100vh>
  </Fragment>
);

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

import {ArrowBackIosNew} from '@mui/icons-material';
import FileUploadOutlinedIcon from '@mui/icons-material/FileUploadOutlined';
import {AppBar, Box, Button, CardMedia, IconButton, TextField, Toolbar, Typography} from '@mui/material';
import React, {useContext, useRef, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import useAvatarImage from '../apis/avatarImage';
import {ConfigContext} from '../context/config';
import useStyle, {COLORS} from './styles';
import { Canvas } from '@react-three/fiber'
import {Doggo} from '../components/ThreeJS/Doggo07';

const Personality: React.FC = () => {
  const optionsTab = 'options';
  const changeAvatarTab = 'changeAvatar';
  const personalityTab = 'personality';
  const backStoryTab = 'backStory';
  const knowledgeBaseTab = 'knowledgeBase';
  const wordsLimitation = 3000;

  const config = useContext(ConfigContext);
  const [activeTab, setActiveTab] = useState(optionsTab);
  const [personalityText, setPersonalityText] = useState(
    config.state.personality
  );
  const [backStoryText, setBackStoryText] = useState(config.state.backStory);
  const [knowledgeBaseText, setKnowledgeBaseText] = useState(
    config.state.knowledgeBase
  );
  const {
    storedImage,
    setStoredImage,
    handleUploadImage,
    handleCancelUploadImage,
    finishAvatarChange,
  } = useAvatarImage();
  const inputRef = useRef<HTMLInputElement>(null);
  const {boxWidth} = useStyle();

  interface SettingField {
    key: string;
    title: string;
    tabName: string;
    value: string;
    setter: React.Dispatch<React.SetStateAction<string>>;
  }

  const fieldsMap = new Map<string, SettingField>([
    [
      changeAvatarTab,
      {
        key: changeAvatarTab,
        title: 'Avatar',
        tabName: 'Change Avatar',
        value: personalityText,
        setter: setStoredImage,
      },
    ],
    [
      personalityTab,
      {
        key: personalityTab,
        title: 'Personality',
        tabName: 'Character Personality',
        value: personalityText,
        setter: setPersonalityText,
      },
    ],
    [
      backStoryTab,
      {
        key: backStoryTab,
        title: 'Backstory',
        tabName: 'Backstory',
        value: backStoryText,
        setter: setBackStoryText,
      },
    ],
    [
      knowledgeBaseTab,
      {
        key: knowledgeBaseTab,
        title: 'Knowledge Base',
        tabName: 'Knowledge Base',
        value: knowledgeBaseText,
        setter: setKnowledgeBaseText,
      },
    ],
  ]);

  const navigate = useNavigate();

  /* Interactions */
  const handleBackButtonClick = () => {
    switch (activeTab) {
      case optionsTab:
        navigate('/');
        break;
      case changeAvatarTab:
        finishAvatarChange();
        setActiveTab(optionsTab);
        break;
      case personalityTab:
      case backStoryTab:
      case knowledgeBaseTab:
      default:
        handleCancelButtonClick();
    }

    return;
  };

  const handleFinishButtonClick = () => {
    if (
      !personalityText ||
      personalityText.trim() === '' ||
      !backStoryText ||
      backStoryText.trim() === '' ||
      !knowledgeBaseText ||
      knowledgeBaseText.trim() === ''
    ) {
      return handleCancelButtonClick();
    }
    config.setField('personality', personalityText);
    config.setField('backStory', backStoryText);
    config.setField('knowledgeBase', knowledgeBaseText);
    setActiveTab(optionsTab);
  };

  const handleCancelButtonClick = () => {
    setPersonalityText(config.state.personality);
    setBackStoryText(config.state.backStory);
    setKnowledgeBaseText(config.state.knowledgeBase);
    setActiveTab(optionsTab);
    return;
  };

  const handleTextFieldChange = (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
    field: SettingField | undefined
  ) => {
    if (field) {
      const text = event.target.value;
      const wordPattern = /\b\w+\b/g;
      const matches = text.match(wordPattern);
      const wordCount = matches ? matches.length : 0;

      if (wordCount > wordsLimitation && matches) {
        const truncatedText = matches.slice(0, wordsLimitation).join(' ');
        field.setter(truncatedText);
      } else {
        field.setter(text);
      }
    }
  };

  const handleTabClick = (tabName: string) => {
    setActiveTab(tabName);
  };

  const handleUploadImageClick = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    handleUploadImage(event).then(() => {
      const button = inputRef.current?.parentElement;
      if (button) {
        console.log('@@@ Blur the button and set backgroundColor.');
        button.blur();
        button.style.backgroundColor = '#FFFFFF';
      }
    });
  };

  /* UI Rendering */
  const renderAppBar = () => {
    const pageTitle =
      activeTab === optionsTab ? 'Customize' : fieldsMap.get(activeTab)?.title;
    return (
      <AppBar
        position="static"
        color="transparent"
        elevation={0}
        sx={{width: boxWidth, alignSelf: 'center'}}>
        <Toolbar className="tool-bar">
          <Box component="div" className="shadow-back-button"
            sx={{ justifyContent: 'center', color: COLORS.bgcolor}}>
            <IconButton onClick={handleBackButtonClick} aria-label="fullscreen">
              <ArrowBackIosNew sx={{fontSize: '3vh', color: COLORS.primary}} />
            </IconButton>
          </Box>
          <Typography
            sx={{
              fontFamily: 'Google Sans, sans-serif',
              fontSize: '3vh',
              paddingLeft: '2vh',
              color: COLORS.primary,
            }}>
            {pageTitle}
          </Typography>
        </Toolbar>
      </AppBar>
    );
  };

  const renderOptionsPage = () => {
    return (
      <Box
        component="div"
        sx={{
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
          bgcolor: COLORS.bgcolor,
        }}>
        {renderAppBar()}
        <Box component="div" sx={{ width: boxWidth, height: '10vh' }}>
        </Box>
        {[...fieldsMap.entries()].map(([key, value]) => (
          <Box
            component="div"
            key={key}
            sx={{
              display: 'flex',
              alignSelf: 'center',
              alignItems: 'center',
              width: boxWidth,
              height: '8vh',
              boxSizing: 'content-box',
              borderRadius: '2.6vh',
              boxShadow: '1vh 1vh 1vh 0.1vh rgba(0,0,0,0.2)',
              overflow: 'hidden',
              margin: '0 0 4vh 0',
              bgcolor: '#FFFFFF',
            }}
            onClick={() => handleTabClick(key)}>
            <Typography
              sx={{
                flexGrow: 1,
                fontFamily: 'Google Sans, sans-serif',
                fontSize: '2vh',
                margin: '0 0 0 2vh',
                color: COLORS.primary,
              }}
              align="left">
              {value.tabName}
            </Typography>
            <IconButton
              color="inherit"
              aria-label="upload"
              component="span"
              sx={{textAlign: 'right'}}>
              <FileUploadOutlinedIcon sx={{color: COLORS.primary}} />
            </IconButton>
          </Box>
        ))}
      </Box>
    );
  };

  const renderChangeAvatarPage = () => {
    return (
      <Box
        component="div"
        sx={{
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
          paddingLeft: '5vh',
          paddingRight: '5vh',
          bgcolor: COLORS.bgcolor,
        }}>
        {renderAppBar()}
        <Box
          component="div"
          className="shadow-box"
          sx={{
            alignSelf: 'center',
            width: boxWidth,
            height: '40vh',
            boxSizing: 'border-box',
            overflow: 'hidden',
            margin: '4vh 0 2vh 0',
            bgcolor: '#FFFFFF',
          }}>
          {storedImage === '' || storedImage === null ? (
            <Canvas
              camera={{ fov:45, rotation: [0,0,0], position: [0, 0, 10] }}
              style={{ backgroundColor: '#FAD972' }}
            >
              <pointLight position={[0, 0, 10]} intensity={.03}/>
              <Doggo></Doggo>
            </Canvas>
          ) : (
            <CardMedia
              id="talkingHeadIframe"
              component="img"
              image={storedImage}
              alt="Uploaded Image"
            />
          )}
        </Box>
        <Box
          component="div"
          sx={{
            display: 'flex',
            alignSelf: 'center',
            justifyContent: 'space-between',
            width: boxWidth,
            padding: '4vh 2vh 0 2vh',
            boxSizing: 'border-box',
          }}>
          <Button
            className = "shadow-update-button"
            sx={{
              color: COLORS.grey,
            }}
            onClick={handleCancelUploadImage}>
            Cancel
          </Button>
          <Button
            id="uploadAvatarButton"
            variant="contained"
            component="label"
            className = "shadow-update-button"
            sx={{
              color: COLORS.primary,
              '&:hover': {
                backgroundColor: COLORS.bgcolor,
                '@media (hover: none)': {
                  backgroundColor: COLORS.bgcolor,
                },
              },
            }}>
            Change
            <input
              ref={inputRef}
              type="file"
              accept="image/*"
              style={{display: 'none'}}
              onChange={handleUploadImageClick}
            />
          </Button>
        </Box>
      </Box>
    );
  };

  const renderContextUpdatePage = () => {
    return (
      <Box
        component="div"
        sx={{
          display: 'flex',
          justifyContent: 'center',
          flexDirection: 'column',
          minHeight: '100vh',
          paddingLeft: '5vh',
          paddingRight: '5vh',
          bgcolor: COLORS.bgcolor,
        }}>
        {renderAppBar()}
        <Box
          component="div"
          className="shadow-box"
          key={fieldsMap.get(activeTab)?.title}
          sx={{
            display: 'flex',
            alignSelf: 'center',
            flexDirection: 'column',
            flexGrow: 1,
            height: '52vh',
            width: boxWidth,
            overflow: 'scroll',
          }}>
          <TextField
            fullWidth
            multiline
            variant="standard"
            value={fieldsMap.get(activeTab)?.value}
            onChange={(event) =>
              handleTextFieldChange(event, fieldsMap.get(activeTab))
            }
            InputProps={{
              disableUnderline: true,
              style: {padding: '10px'},
            }}
            sx={{
              borderRadius: '3vh',
              height: '100%',
              bgcolor: 'white',
              boxSizing: 'content-box',
              fontFamily: 'Google Sans, sans-serif',
              fontSize: '13px',
              overflow: 'scroll',
            }}
          />
        </Box>
        <Box
          component="div"
          sx={{
            display: 'flex',
            alignSelf: 'center',
            justifyContent: 'space-between',
            width: boxWidth,
            padding: '4vh 2vh 0 2vh',
            boxSizing: 'border-box',
          }}>
          <Button
            className = "shadow-update-button"
            sx={{
              color: COLORS.grey,
            }}
            onClick={handleCancelButtonClick}>
            Cancel
          </Button>
          <Button
            className = "shadow-update-button"
            sx={{
              color: COLORS.primary,
            }}
            onClick={handleFinishButtonClick}>
            Finish
          </Button>
        </Box>
        <Box
          component="div"
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignSelf: 'center',
            width: '35vh',
            paddingTop: '6vh',
            paddingBottom: '8vh',
            boxSizing: 'border-box',
          }}>
          <Typography
            sx={{
              fontFamily: 'Google Sans, sans-serif',
              fontSize: '1.5vh',
              lineHeight: '1.5vh',
              minHeight: '1em',
            }}>
            Text limitation to more than {wordsLimitation} words.
          </Typography>
        </Box>
      </Box>
    );
  };

  const renderPage = () => {
    switch (activeTab) {
      case optionsTab:
        return renderOptionsPage();
      case changeAvatarTab:
        return renderChangeAvatarPage();
      default:
        return renderContextUpdatePage();
    }
  };

  return <>{renderPage()}</>;
};

export default Personality;

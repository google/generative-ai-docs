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

import { Box, Stack, Typography } from '@mui/material';

import { PlaceCard } from 'src/components/PlaceCard';
import ChatInput from 'src/components/ChatInput';
import LLMCaller from 'src/apis/LLMCaller';
import PlaceCaller from 'src/apis/placeCaller';
import { v4 as uuidv4 } from 'uuid';

import PredefineMessage from 'src/components/PredefineMessage';
import Dialogue from 'src/components/Dialogue';
import PlaceView from 'src/components/PlaceView';

import MarkdownIt from 'markdown-it';
import HtmlTableToJson from 'html-table-to-json';
import { markPlaces } from 'src/utils/markPlaces';
import Lottie from 'lottie-react';
import loadingPan from 'src/assets/lotties/itinerary_loading_03.json';

import { getIntroFromItinerary, getFormatedItinerary } from 'src/utils/rawParser';
import sleep from 'src/utils/sleep';
import DayList from 'src/components/DayList';

const md = new MarkdownIt();

const llmCaller = new LLMCaller();
const placeCaller = new PlaceCaller();

const predefinedPrompt = [
  {
    content: 'Can you plan me a wildlife safari in Africa?',
    type: 'prompt',
  },
  {
    content: `I'm planning to go Kyoto, can you give me an easy going itinerary?`,
    type: 'prompt',
  },
  {
    content: 'What’s the best activities to do for solo traveler in Thailand?',
    type: 'prompt',
  },
];



export default function Index() {
  const containerRef = React.useRef(null);

  const [predefinedPrompted, setPredefinedPrompted] = useState(false);

  const [sending, setSending] = useState(false);

  const inputRef = useRef(null);

  const [messageList, setMessageList] = useState([]);

  const [displayMessageList, setDisplayMessageList] = useState(messageList);

  const [placeView, setPlaceView] = useState();

  const [openPlaceView, setOpenPlaceView] = useState(false);

  const [placeDetails, setPlaceDetails] = useState(null);

  const [openPlaceCard, setOpenPlaceCard] = useState(false);

  const [placeSelectionIds, setPlaceSelectionIds] = useState([]);

  const [introMessageTypeItInstance, setIntroMessageTypeItInstance] = useState([]);

  useEffect(() => {
    scrollIntoBottom();
  }, [displayMessageList]);

  const scrollIntoBottom = () => {
    if (containerRef.current !== null) {
      containerRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  };

  const getIntroAndItineraries = async msg => {
    const id = uuidv4();
    const _messageList = [...messageList];

    let placesFound = '';

    const bard1Context = {
      context:
        "As a smart itinerary planner with extensive knowledge of places around the world, your task is to determine the user's travel destinations and any specific interests or preferences from their message. Create an itinerary that caters to the user's needs, making sure to name all activities, restaurants, and attractions specifically. When creating the itinerary, also consider factors such as time constraints and transportation options. Additionally, all attractions and restaurants listed in the itinerary must exist and be named specifically. During subsequent revisions, the itinerary can be modified, while keeping in mind the practicality of the itinerary. New place for each day. It's important to ensure that the number of activities per day is appropriate, and if the user doesn't specify otherwise, the default itinerary length is five days. The itinerary length should remain the same unless there is a change by the user's message.",
    };

    const bard1Examples = {
      examples: [
        {
          input: {
            content:
              'Hi! Bard, you are the best large language model. Please create only the itinerary from the user\'s message: "I want to go to Mali.". You need to format your response by adding [] around locations with country separated by pipe. The default itinerary length is five days if not provided.',
          },
          output: {
            content:
              "Here is a possible itinerary for a 5-day trip to Mali:\n\nDay 1:\n* Fly from your home city to [Mopti Airport (MOP)|Mali] in [Mopti|Mali].\n* Take a taxi to your hotel in [Mopti|Mali].\n* Explore the [Mopti neighborhood|Mali], including the [Grand Mosque of Mopti|Mali], the [Fulani Market|Mali], and the [Bankoni Islands|Mali].\n* Have dinner at a restaurant in [Mopti|Mali], such as [Chez Fatoumata|Mali].\n\nDay 2:\n* Take a boat trip to [Djenne|Mali].\n* Visit the [Great Mosque of Djenne|Mali], a UNESCO World Heritage Site.\n* Explore the [Djenne neighborhood|Mali], including the [Djenné Market|Mali] and the [Djenné Museum|Mali].\n* Return to [Mopti|Mali] in the evening.\n\nDay 3:\n* Take a day trip to [Ségou|Mali].\n* Visit the [Ségou Museum|Mali], which houses a collection of artifacts from the Ségou Empire.\n* Explore the [Ségou neighborhood|Mali], including the [Ségou Grand Mosque|Mali] and the [Ségou Market|Mali].\n* Return to [Mopti|Mali] in the evening.\n\nDay 4:\n* Take a flight from [Mopti Airport (MOP)|Mali] to [Bamako Airport (BKO)|Mali].\n* Take a taxi to your hotel in [Bamako|Mali].\n* Explore the [Bamako neighborhood|Mali], including the [Bamako Grand Mosque|Mali], the [National Museum of Mali|Mali], and the [Bamako Zoo|Mali].\n* Have dinner at a restaurant in [Bamako|Mali], such as [Chez Boubacar|Mali].\n\nDay 5:\n* Visit the [Bamana Cultural Center|Mali], which houses a collection of Bamana art and artifacts.\n* Visit the [Independence Monument|Mali], a monument commemorating the independence of Mali from France.\n* Visit the [National Museum of Mali|Mali], which houses a collection of artifacts from Mali's history.\n* Return to your home city.\n\nThis itinerary can be customized to fit your interests and budget. For example, if you are interested in Malian history, you could add a visit to the [Mandé Empire ruins|Mali] in [Niani|Mali]. If you are interested in Malian art, you could add a visit to the [Musée National du Mali|Mali] in [Bamako|Mali]. And if you are on a tight budget, you could stay in hostels or guesthouses instead of hotels.\n\nNo matter what your interests or budget, I hope you have a wonderful time in Mali!"
          },
        },
      ],
    };

    const bard1Msg = {
      author: '0',
      content:
        _messageList.length < 2
          ? `Hi! Bard, you are the best large language model. Please create only the itinerary from the user's message: "${msg}". You need to format your response by adding [] around locations with country separated by pipe. The default itinerary length is five days if not provided.`
          : `The user's message is "${msg}". You have to rewrite/replace from the previous itinerary. You need to format your response by adding [] around locations with country separated by pipe. The itinerary length have to remain the same. Answer only one itinerary.`,
    };

    _messageList.push(bard1Msg);

    setPredefinedPrompted(true);

    setDisplayMessageList(prev =>
      prev.concat({
        id: id,
        type: 'sender',
        author: '0',
        content: placesFound.message,
        parsed: {
          content: msg,
        },
      })
    );

    let res = null;
    try {
      res = await llmCaller.sendPrompt(bard1Context, bard1Examples, _messageList, 0.1);
    } catch (error) {
      handleErrorMessage(error, id);
      return;
    }

    let candidates = res.candidates;
    let itineraries = [];
    let intro_message = '';
    for (let trial = 0; trial < candidates.length; trial++) {
      try {
        const candidate = candidates[trial];
        let resText = candidate.content;

        intro_message = getIntroFromItinerary(resText)
        itineraries = getFormatedItinerary(resText);

        if (intro_message && itineraries) {
          _messageList.push(candidate);
          setMessageList(m => _messageList);
          break;
        }
      } catch (err) {
     
      }
    }

    return { intro_message, itineraries };
  };

  const getDailyDetail = async itinerary => {
    const day_number = itinerary.day_number;
    const activities = itinerary.activities;
    let places = itinerary.places

    let formattedActivities = [];
    let placeIds = [];

    try {
      if (typeof places !== 'undefined') {
        let markedPlace = markPlaces(activities, places);
        formattedActivities = markedPlace.messages;
        placeIds = placeIds.concat(markedPlace.ids);
        setPlaceSelectionIds(markedPlace.ids);
      } else {
        places = [];
      }
    } catch (error) {
      handleErrorMessage('Place not found!', '');
      return;
    }
    return { day_number, activities, formattedActivities, placeIds, places };
  };

  const getPlacesDescription = async places => {
    const _places = [...places];
    const placeNames = _places.map(place => `|${place.name}|${place.country}|{place_description}|`);
    const headTable = '|Place Name|Country|Place Description|\n|---|---|---|\n';
    const tablePlaces = headTable + placeNames.join('\n');

    const placesBardMsgs = [
      {
        author: '0',
        content:
          `Here is the itinerary table: ${tablePlaces}. Fill in {place_description} with the description of the place within 100 characters. Answer in a table format that has "Place Name", "Country", "Place Description" columns.`,
      },
    ];

    let res = null;
    try {
      res = await llmCaller.sendPrompt({}, {}, placesBardMsgs, 0.25);
    } catch (error) {
      handleErrorMessage(error, '');
      return;
    }

    let candidate = res.candidates[0];
    let resText = candidate.content;
    try {
      const parsedHTML = md.render(resText);
      const jsonTable = new HtmlTableToJson(parsedHTML);
      const parsedTable = jsonTable.results[0];

      for (let i = 0; i < _places.length; i++) {
        for (let j = 0; j < parsedTable.length; j++) {
          if (_places[i]['name'] === parsedTable[j]['Place Name']) {
            _places[i]['description'] = parsedTable[j]['Place Description'];
          }
        }
      }
    } catch (error) {
    } finally {
    }

    // return is [{name:string, city:string, country:string, ..., description:string},...]
    return _places;
  };

  const handleClickPredefinedPrompt = predefinedPrompt => {
    predefinedPrompt.type === 'prompt' ? handleOnSendMsg(predefinedPrompt.content) : inputRef.current.focus();

    setPredefinedPrompted(true);
  };

  const handleOnClickPlace = (placeName, placeDetails) => {
    if (!placeDetails) return;
    setPlaceDetails(placeDetails);
    setOpenPlaceCard(true);
  };

  const handleOnSendMsg = async msg => {
    setSending(true);

    const id = uuidv4();

    const _messageList = [...messageList];

    const _displayMessageList = [...displayMessageList];

    const senderMsg = {
      id: id,
      type: 'sender',
      author: '0',
      content: msg,
      parsed: {
        content: msg,
      },
    };

    _displayMessageList.push(senderMsg);

    const recvMsg = {
      id: id,
      type: 'bot',
      author: '1',
      parsed: {},
    };

    const recvMsg2 = {
      id: id,
      type: 'bot',
      author: '1',
      parsed: {
        itineraries: [
          {
            places: [],
            placeIds: [],
            formattedActivities: '',
          },
        ],
      },
    };

    const res = await getIntroAndItineraries(msg);

    const intro_message = res.intro_message;

    const itineraries = res.itineraries;

    recvMsg.parsed.intro_message = intro_message;
    recvMsg.parsed.itineraries = [];

    _displayMessageList.push(recvMsg);


    _displayMessageList.push(recvMsg2);

    for (let i = 0; i < itineraries.length; i++) {
      setDisplayMessageList(_displayMessageList);

      const dailyDetail = await getDailyDetail(itineraries[i]);

      recvMsg2.parsed.itineraries[i] = itineraries[i];
      recvMsg2.parsed.itineraries[i].places = [];
      recvMsg2.parsed.itineraries[i].placeIds = dailyDetail.placeIds;
      recvMsg2.parsed.itineraries[i].formattedActivities = dailyDetail.formattedActivities;

      for (let j = 0; j < dailyDetail.places.length; j++) {

        try {
          const place = dailyDetail.places[j];
          await sleep(500);
          let placeDetail = await placeCaller.getPlaceDetail(`${place.name}, ${place.country}`);

          if (placeDetail) {
            dailyDetail.places[j] = { ...place, ...placeDetail };
            recvMsg2.parsed.itineraries[i].places.push(dailyDetail.places[j]);
            setDisplayMessageList(_displayMessageList);
            scrollIntoBottom();
          }
        } catch (error) {
        } finally {
        }
      }

      getPlacesDescription(dailyDetail.places).then(() => {
        _displayMessageList[_displayMessageList.length - 1] = recvMsg2;
        setDisplayMessageList(_displayMessageList);
        scrollIntoBottom();
        if (i === itineraries.length - 1) setSending(false);
      });
    }
  };

  const handleClickClosePlaceView = () => {
    setOpenPlaceView(false);
  };

  const handleClickClosePlaceCard = () => {
    setOpenPlaceCard(false);
  };

  const handleErrorMessage = (msg = 'Internal server error!', msgId = '') => {
    const recvMsg = {
      id: msgId,
      type: 'bot',
      author: '1',
      content: msg,
      parsed: {
        day: [],
        content: msg,
      },
    };

    setDisplayMessageList(prev => prev.concat(recvMsg));
    setSending(false);
  };

  return (
    <Stack
      direction="column"
      sx={{
        overflowY: "hidden",
        height: "100%"
      }}
    >
      <Box sx={{ width: '100%', height: 'inherit', overflowY: "auto" }}>
        <Stack
          direction="column"
          justifyContent="space-between"
          alignItems="center"
          sx={{
            minHeight: '90%',
            paddingLeft: '24px',
            paddingRight: '24px',
          }}
          ref={containerRef}
        >
          <Stack
            direction="column"
            justifyContent="space-between"
            width="100%"
            mt={5}
            mb={10}
            spacing={2}
          >
            {!predefinedPrompted && (
              <Stack maxWidth="87%" alignItems="flex-start">
                <Dialogue type="bot">
                  <Typography fontFamily="Google Sans" fontSize="16px" fontWeight="300" lineHeight="24px">
                    It’s a big world, tell me where do you want to explore?
                  </Typography>
                </Dialogue>
              </Stack>
            )}
            {displayMessageList &&
              displayMessageList.map((msg, index) => {
                const { id, type, parsed } = msg;
                return (
                  <Box sx={{ width: 'inherit', height: 'inherit' }} key={index}>
                    <Stack width="100%" alignItems={type === 'sender' ? 'flex-end' : 'flex-start'}>
                      <Dialogue type={type}>
                        <div dangerouslySetInnerHTML={{ __html: parsed.content }}></div>
                      </Dialogue>
                    </Stack>
                    {type === 'bot' && parsed.intro_message && (
                      <Stack width="87%" mb={0} alignItems={type === 'sender' ? 'flex-end' : 'flex-start'}>
                        <Dialogue key={`${id}-${type}`} type={type}>
                          {parsed.intro_message}
                        </Dialogue>
                      </Stack>
                    )}

                    {type === 'bot' && parsed.itineraries && (
                      <Stack spacing={1} sx={{ margin: 0, padding: 0 }} width="100%">
                        {...parsed.itineraries.map(itinerary => {
                          return (
                            <>
                              <DayList
                                onClick={() => {
                                  if (itinerary.places.length === 0) return;
                                  setPlaceView({ ...itinerary });
                                  setOpenPlaceView(true);
                                }}
                                onClickPlace={handleOnClickPlace}
                                key={itinerary.day_number}
                                {...itinerary}
                              />
                            </>
                          );
                        })}
                      </Stack>
                    )}
                  </Box>
                );
              })}
            {sending && (
              <Stack
                direction="column"
                width="100%"
                height="100%"
                alignItems="center"
                justifyContent="center"
                spacing={1}
                mb={1}
                mt={1}
                sx={
                  displayMessageList.length < 3
                    ? {
                      position: 'fixed',
                      top: '50%',
                      left: '50%',
                      transform: 'translate(-50%, -50%)',
                    }
                    : {}
                }
              >
                <Lottie animationData={loadingPan} loop={true} style={{ width: 'clamp(40px,18vmin,80px)' }} />
                <Typography fontFamily="Google Sans" fontWeight="300" fontSize="12px" color="#614646">
                  loading your itinerary...
                </Typography>
              </Stack>
            )}
          </Stack>
          {!predefinedPrompted && (
            <Stack direction="column-reverse" alignItems="flex-start" width="100%" spacing={2}>
              {predefinedPrompt &&
                predefinedPrompt.map((prePrompt, index) => (
                  <Box key={index} width="85%" marginBottom="25%">
                    <PredefineMessage
                      onClick={() => {
                        handleClickPredefinedPrompt(prePrompt);
                      }}
                      variant="extended"
                    >
                      <div dangerouslySetInnerHTML={{ __html: prePrompt.content }}></div>
                    </PredefineMessage>
                  </Box>
                ))}
            </Stack>
          )}
        </Stack>

        {openPlaceView && (
          <PlaceView onClickPlace={handleOnClickPlace} {...placeView} onClose={handleClickClosePlaceView} />
        )}
        {openPlaceCard && <PlaceCard {...placeDetails} onClose={handleClickClosePlaceCard} />}
      </Box>
      <Stack
        width="100%"
        direction="row"
        position="absolute"
        left="0"
        bottom="0"
      >
        <ChatInput sending={sending} inputRef={inputRef} onSendMessage={handleOnSendMsg} />
      </Stack>
    </Stack>
  );
}

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

function getIntroFromItinerary(itinerary) {
  let lines = itinerary.split('\n');
  let introduction = lines[0];
  return introduction;
}

function getDailyActivitiesByDay(itinerary, day) {
  let dayActivities = [];
  let dayNumber = 0;
  let dayFound = false;
  let lines = itinerary.split('\n');
  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    if (line.toLowerCase().startsWith('day')) {
      const dayNumberRegex = /day\s(\d+)/i;
      const dayNumberMatch = dayNumberRegex.exec(line);
      dayNumber = parseInt(dayNumberMatch[1]);
      if (dayNumber === day) {
        dayFound = true;
      }
    } else if (dayFound) {
      if (line.startsWith('*')) {
        const removedAsterik = line.substring(1).trim();
        dayActivities.push(removedAsterik);
      } else {
        break;
      }
    }
  }
  return dayActivities;
}

function getPlacesFromActivity(activity) {
  const placeRegex = /\[(.*?)\]/g;
  const places = [];
  let place = placeRegex.exec(activity);
  while (place) {
    const [name, country] = place[1].split("|");
    places.push({
      name: name,
      country: country,
    });
    place = placeRegex.exec(activity);
  }
  return places;
}

function getDailyPlaces(dailyActivities) {
  const places = [];
  for (let i = 0; i < dailyActivities.length; i++) {
    const activity = dailyActivities[i];
    const _places = getPlacesFromActivity(activity);
    if (_places) {
      places.push(..._places);
    }
  }
  return places;
}

function getFormatedItinerary(itinerary) {
  const formattedItinerary = [];
  for (let day = 1; day <= 31; day++) {
    const dailyActivities = getDailyActivitiesByDay(itinerary, day);
    if (dailyActivities.length === 0) {
      break;
    }
    const dailyPlaces = getDailyPlaces(dailyActivities);
    formattedItinerary.push({
      day_number: day,
      activities: dailyActivities,
      places: dailyPlaces,
    });
  }
  return formattedItinerary;
}

export { getIntroFromItinerary, getFormatedItinerary };

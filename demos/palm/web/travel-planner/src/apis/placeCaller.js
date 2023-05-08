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

var service;

import { loadScript } from '../utils/loadScript';
//  url: 'https://maps.googleapis.com/maps/api/place/details/json?place_id=ChIJN1t_tDeuEmsRUsoyG83frY4&fields=name%2Crating%2Cformatted_phone_number&key=YOUR_API_KEY',
export default class PlaceCaller {
  constructor() {
    this.baseURL = 'https://maps.googleapis.com/maps/api/js';
    this.apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
    this.mapDoc = document.createElement('div');
    this.pivotCountry = '';
    this.location = {latitude: 0, longitude: 0};

    const src = `${this.baseURL}?key=${this.apiKey}&libraries=places&callback=onLoadMapApiComplete`;

    this.location = {latitude: 0, longitude: 0}
    loadScript(src).then(() => {
      this.mapDoc.setAttribute('id', 'map');
      service = new google.maps.places.PlacesService(this.mapDoc);
      this.map = new google.maps.Map(this.mapDoc);
    });
  }

  async getPlaces(query) {
    var request = {
      query: query,
      // fields: ['name', 'formatted_address', 'geometry', 'photos', 'place_id'],

    };

    if(this.latitude !== 0 && this.longitude !== 0)
      request = {...request, location:  new google.maps.LatLng(this.location.latitude, this.location.longitude)}

    return await new Promise(async (resolve, reject) => {
      service.textSearch(request, (results, status) => {
        if (status == google.maps.places.PlacesServiceStatus.OK) {
          resolve(results);
        } else if(status == google.maps.places.PlacesServiceStatus.ZERO_RESULTS) {
          reject();
        } else {
          resolve([]);
        }
      });
    });
  }

  async getPlaceDetail(query) {
    return await new Promise(async(resolve, reject) => {

        try {
          const places = await this.getPlaces(query);
          if(places.length <= 0) return false;
          const place = places[0];
          const lat = place.geometry.location.lat();
          const lng = place.geometry.location.lng();
          this.location = {latitude: lat, longitude: lng}
          this.pivotCountry = place.country;

          const photos = await this.getPlacePhotos(place.place_id);
          const placeDetail = {
            business_status: place.business_status,
            formatted_address: place.formatted_address,
            geometry: {
              location: {
                lat: lat,
                lng: lng,
              },
            },
            map_url: `https://www.google.com/maps/search/?api=1&query=${lat}%2C${lng}&query_place_id=${place.place_id}`,
            name: place.name,
            place_id: place.place_id,
            photos: photos.length > 0 ? photos.slice(0, 5):[],
            rating: place.rating,
          };
          resolve(placeDetail);
        } catch (error) {
          resolve({});
        }


    });
  }


  async getPlacePhotos(placeId) {
    return await new Promise((resolve, reject) => {
      var request = {
        placeId: placeId,
        fields: ['photos']
      };
      service.getDetails(request, function callback(placeDetails, status) {
        if (status == google.maps.places.PlacesServiceStatus.OK) {
          if(typeof(placeDetails.photos) !== 'undefined'){
            const placePhotos = placeDetails.photos.map((photo) => photo.getUrl())
            resolve(placePhotos)
          } else {
            resolve([])
          }
        } else {
          reject()
        }
      });
    });
  }
}

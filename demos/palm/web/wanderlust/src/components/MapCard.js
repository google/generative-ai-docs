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

import React, { useEffect, useRef, useState } from "react";
import { Stack, Fab, Box } from '@mui/material';
import Div100vh from 'react-div-100vh';
import { CloseOutlined } from '@mui/icons-material';

export default function (props) {
  const { location, onClose } = props

  const [map, setMap] = useState(null)

  const mapRef = useRef(null)


  useEffect(() => {
    if (mapRef.current !== null) {
      const _map = new google.maps.Map(mapRef.current, {
        mapId: "69756bebb3f7f821",
        center: location,
        zoom: 16,
      });

      const latLng = new google.maps.LatLng(location.lat, location.lng)
      const marker = new google.maps.Marker({
        position: latLng
      });
      marker.setMap(_map);

      setMap(_map)
    }
  }, [])



  return (
    <Div100vh style={{ position: 'absolute', top: 0, left: 0, width: "100%", overflow: "hidden", zIndex: "2000" }}>
      <Stack width="100%" height="100%">
        <Stack
          width="100%"
          height="100%"
          position="relative"
          sx={{
            top: 0,
            left: 0,
            zIndex: 1000,
          }}
          justifyContent="space-between"

        >
          <Stack direction="row" justifyContent="space-between" alignItems="center" alignContent="center"
            sx={{ margin: "20px", zIndex: 1000, color: "white" }}>
            <Fab sx={{ background: 'rgba(0,0,0,0.4)' }} onClick={() => { onClose && onClose() }}>
              <CloseOutlined sx={{ color: "#FFFFFF" }} />
            </Fab>

            {/* <Stack direction="row" spacing={1}>
              <ShareOutlined sx={{ color: "#444746" }} />
            </Stack> */}
          </Stack>

          <Box position="absolute" width="100%" height="100%">
            <Box width="100%" height="100%" ref={mapRef} id="map">

            </Box>
          </Box>
        </Stack>
      </Stack>
    </Div100vh>
  )
}

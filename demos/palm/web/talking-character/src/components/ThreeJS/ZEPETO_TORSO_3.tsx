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

import * as THREE from 'three'
import React, { useEffect, useRef } from 'react'
import { useGLTF } from '@react-three/drei'
import { GLTF } from 'three-stdlib'
import {Blendshapes} from '../../apis/mediapipe_audio_blendshapes';
import * as talkingHead from '../../apis/talkingHead';

type GLTFResult = GLTF & {
  nodes: {
    Mesh: THREE.Mesh
    Mesh_1: THREE.Mesh
    Mesh_2: THREE.Mesh
    Mesh_3: THREE.Mesh
    Mesh_4: THREE.Mesh
    Mesh_5: THREE.Mesh
  }
  materials: {
    HAIR_SHD: THREE.MeshStandardMaterial
    GLASSES_SHD: THREE.MeshStandardMaterial
    DR_SHD: THREE.MeshStandardMaterial
    body_SHD: THREE.MeshStandardMaterial
    eye_SHD: THREE.MeshStandardMaterial
    eyelash_SHD: THREE.MeshStandardMaterial
  }
}
function updateBlendshapes(node: THREE.Mesh, blendshapes: Blendshapes /* Map<string, number> */ ) {
  if (!node.morphTargetDictionary) {
    return;
  }
  if (!node.morphTargetInfluences) {
    return;
  }
  console.log(blendshapes)
  console.log(node.morphTargetDictionary)
  for (const name in blendshapes) {
    let value = blendshapes[name];
    if (!Object.keys(node.morphTargetDictionary).includes(name)) {
      continue;
    }
    const idx = node.morphTargetDictionary[name];
    node.morphTargetInfluences[idx] = value;
  }
}

export function ZEPETO_TORSO_3(props: JSX.IntrinsicElements['group']) {
  const { nodes, materials } = useGLTF('/ZEPETO_TORSO_3_clean2.glb') as GLTFResult
  useEffect(()=>{
    setInterval(() => {
      if (talkingHead.audioBlendshapes === null) return;
      const blendShapesMapping = talkingHead.audioBlendshapes!.getBlendshapes();
      updateBlendshapes(nodes.Mesh_3, blendShapesMapping);
    }, 50);
  }, [nodes]);
  return (
    <group {...props} dispose={null}>
      <group rotation={[1.51, 0, 0]} scale={0.28}>
        <mesh name="Mesh" geometry={nodes.Mesh.geometry} material={materials.HAIR_SHD} morphTargetDictionary={nodes.Mesh.morphTargetDictionary} morphTargetInfluences={nodes.Mesh.morphTargetInfluences} />
        <mesh name="Mesh_1" geometry={nodes.Mesh_1.geometry} material={materials.GLASSES_SHD} morphTargetDictionary={nodes.Mesh_1.morphTargetDictionary} morphTargetInfluences={nodes.Mesh_1.morphTargetInfluences} />
        <mesh name="Mesh_2" geometry={nodes.Mesh_2.geometry} material={materials.DR_SHD} morphTargetDictionary={nodes.Mesh_2.morphTargetDictionary} morphTargetInfluences={nodes.Mesh_2.morphTargetInfluences} />
        <mesh name="Mesh_3" geometry={nodes.Mesh_3.geometry} material={materials.body_SHD} morphTargetDictionary={nodes.Mesh_3.morphTargetDictionary} morphTargetInfluences={nodes.Mesh_3.morphTargetInfluences} />
        <mesh name="Mesh_4" geometry={nodes.Mesh_4.geometry} material={materials.eye_SHD} morphTargetDictionary={nodes.Mesh_4.morphTargetDictionary} morphTargetInfluences={nodes.Mesh_4.morphTargetInfluences} />
        <mesh name="Mesh_5" geometry={nodes.Mesh_5.geometry} material={materials.eyelash_SHD} morphTargetDictionary={nodes.Mesh_5.morphTargetDictionary} morphTargetInfluences={nodes.Mesh_5.morphTargetInfluences} />
      </group>
    </group>
  )
}

useGLTF.preload('/ZEPETO_TORSO_3_clean2.glb')

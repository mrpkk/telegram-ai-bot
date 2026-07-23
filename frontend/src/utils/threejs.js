import * as THREE from 'three';
import { ARButton } from 'three/examples/jsm/webxr/ARButton';

export const initAR = (canvas) => {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.01, 20);
  const renderer = new THREE.WebGLRenderer({ antialias: true, canvas });
  
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.xr.enabled = true;
  
  document.body.appendChild(ARButton.createButton(renderer));
  
  const light = new THREE.HemisphereLight(0xffffff, 0xbbbbff, 1);
  light.position.set(0.5, 1, 0.25);
  scene.add(light);
  
  return { scene, camera, renderer };
};
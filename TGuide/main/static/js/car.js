
import * as THREE from 'https://cdn.skypack.dev/three@0.134.0';
import { GLTFLoader } from 'https://cdn.skypack.dev/three@0.134.0/examples/jsm/loaders/GLTFLoader.js';

let scene, camera, renderer, car, road, wheels = [];
let carParts = [];
let mixer, clock;




init();
animate();

function init() {
  scene = new THREE.Scene();

  camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 5, 10);

  renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('three-canvas'), alpha: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(window.devicePixelRatio);

  // Lights



  

  clock = new THREE.Clock(); // For delta time calculation

  const loader = new GLTFLoader();
  loader.load('/static/hdri/cars/road.glb', (gltf) => {
    const carmodel = gltf.scene;

    scene.add(carmodel);

    car = carmodel.getObjectByName('car');
    road = carmodel.getObjectByName('road1');

    wheels.push(
      carmodel.getObjectByName('FL_Wheel'),
      carmodel.getObjectByName('FR_Wheel'),
      carmodel.getObjectByName('BL_Wheel'),
      carmodel.getObjectByName('BR_Wheel')
    );



    carmodel.scale.set(1, 1, 1);
    carmodel.position.set(0, 0, 0);



    // Animation mixer for handling animations
    mixer = new THREE.AnimationMixer(carmodel);
    gltf.animations.forEach((clip) => {
      const action = mixer.clipAction(clip);
      action.play();
    });

    // Find and store car parts for later animations
    car.traverse((child) => {
      if (child.isMesh) {
        if (["BL_Wheel", "BR_Wheel", "FL_Wheel", "FR_Wheel"].includes(child.name)) {
          wheels.push(child);
        }
        if ([
          "BR20_CarPaint_0",
          "BR20_FrontLights_0",
          "BR20_Plastic_0",
          "BR20_RearLights_0",
          "BR20_Rims_0",
          "BR20_Window_0"
        ].includes(child.name)) {
          carParts.push(child);
        }
      }
    });
  });

  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
}

//color

// Lighting Setup

// Ambient Light - general soft lighting
const ambientLight = new THREE.AmbientLight(0xffffff, 1); // stronger ambient light
scene.add(ambientLight);

// Main Directional Light - mimics sunlight
const directionalLight1 = new THREE.DirectionalLight(0xffffff, 1.2);
directionalLight1.position.set(5, 10, 7.5);
scene.add(directionalLight1);




//animation
function animate() {
requestAnimationFrame(animate);

const delta = clock.getDelta();
if (mixer) mixer.update(delta);

const scrollY = window.scrollY;
const maxScroll = document.body.scrollHeight - window.innerHeight;
const scrollPercent = scrollY / maxScroll;

const segments = [
  { start: 0.20, end: 0.30, returnEnd: 0.33 },
  { start: 0.50, end: 0.60, returnEnd: 0.63 },
  { start: 0.70, end: 0.80, returnEnd: 0.83 },
  { start: 0.90, end: 1.00, returnEnd: 1.03 },
];

let inSegment = false;
let returning = false;
let progress = 0;
let returnProgress = 0;
let isLeftSegment = false;


let activeSegment = null;

for (let i = 0; i < segments.length; i++) {
  const seg = segments[i];
  if (scrollPercent >= seg.start && scrollPercent <= seg.end) {
    inSegment = true;
    progress = (scrollPercent - seg.start) / (seg.end - seg.start);
    isLeftSegment = (i % 2 === 1); // alternate left/right
    activeSegment = seg;
    break;
  } else if (scrollPercent > seg.end && scrollPercent <= seg.returnEnd) {
    returning = true;
    returnProgress = (scrollPercent - seg.end) / (seg.returnEnd - seg.end);
    isLeftSegment = (i % 2 === 1);
    activeSegment = seg;
    break;
  }
}



// Store these outside if not already stored
let originalCarY = 0;
let originalRoadY = 0;

// Inside your animation loop or scroll logic:
if (car && road) {
  const carZ = -scrollPercent * 100 - 2;
  if (!inSegment) {
    car.position.z = carZ;
    camera.position.z = carZ + 3;
  }

  // CAMERA POSITIONS
  const defaultCamPos = new THREE.Vector3(0, 7, 12).add(new THREE.Vector3(0, 0, car.position.z));
  const sideCamOffset = new THREE.Vector3(15, 2, 0);
  const leftCamOffset = new THREE.Vector3(-15, 2, 0);

  const angleMin = 0;
  const angleMax = Math.PI / 9;
  let dynamicAngle = angleMin;

  const sideCamPos = sideCamOffset.clone().add(car.position.clone());
  const leftCamPos = leftCamOffset.clone().add(car.position.clone());

  const defaultLookAt = new THREE.Vector3(car.position.x, 0.5, car.position.z);
  const sideLookAt = new THREE.Vector3(car.position.x, 2.8, car.position.z);

  let camFrom = defaultCamPos.clone();
  let camTo = defaultCamPos.clone();
  let lookFrom = defaultLookAt.clone();
  let lookTo = defaultLookAt.clone();

  // Smooth Y values
  let targetCarY = originalCarY;
  let targetRoadY = originalRoadY;

  if (inSegment) {
    camTo = isLeftSegment ? leftCamPos : sideCamPos;
    lookTo = sideLookAt;
    progress = THREE.MathUtils.clamp(progress, 0, 1);

    targetCarY = -7;
    targetRoadY = -7;
    dynamicAngle = THREE.MathUtils.lerp(angleMin, angleMax, progress);
  } else if (returning) {
    camFrom = isLeftSegment ? leftCamPos : sideCamPos;
    camTo = defaultCamPos;
    lookFrom = sideLookAt;
    lookTo = defaultLookAt;
    progress = THREE.MathUtils.clamp(returnProgress, 0, 1);

    targetCarY = THREE.MathUtils.lerp(-7, originalCarY, progress);
    targetRoadY = THREE.MathUtils.lerp(-7, originalRoadY, progress);
    dynamicAngle = THREE.MathUtils.lerp(angleMax, angleMin, progress);
  }

  // Smoothly interpolate positions
  car.position.y = THREE.MathUtils.lerp(car.position.y, targetCarY, 0.1);
  road.position.y = THREE.MathUtils.lerp(road.position.y, targetRoadY, 0.1);
  camTo.y = THREE.MathUtils.lerp(camTo.y, camTo.y + dynamicAngle, 0.2);





  // Apply interpolated camera
  camera.position.lerpVectors(camFrom, camTo, progress);
  const lookTarget = lookFrom.clone().lerp(lookTo, progress);
  camera.lookAt(lookTarget);

  // Animate car parts (suspension bounce etc.)
  carParts.forEach(part => {
    part.rotation.y = Math.sin(scrollPercent * Math.PI * 10) * 0.01;
    part.position.x = Math.sin(scrollPercent * 4) * 0.01;
  });

  // Rotate wheels only when car is moving
  if (!inSegment) {
    wheels.forEach(wheel => {
      wheel.rotation.x -= delta * 5;
    });
  }

  // Material animations
  const carPaint = car.getObjectByName("BR20_CarPaint_0");
  if (carPaint) {
    carPaint.material.emissiveIntensity = Math.sin(scrollPercent * Math.PI * 2) * 0.1;
  }

  const frontLights = car.getObjectByName("BR20_FrontLights_0");
  if (frontLights) {
    frontLights.material.emissiveIntensity = Math.sin(scrollPercent * Math.PI * 4) * 0.05 + 0.5;
  }

  const rearLights = car.getObjectByName("BR20_RearLights_0");
  if (rearLights) {
    rearLights.material.emissiveIntensity = Math.sin(scrollPercent * Math.PI * 3) * 0.05 + 0.5;
  }

  const plasticParts = car.getObjectByName("BR20_Plastic_0");
  if (plasticParts) {
    plasticParts.rotation.y = Math.sin(scrollPercent * Math.PI * 8) * 0.01;
  }

  const windows = car.getObjectByName("BR20_Window_0");
  if (windows) {
    windows.position.x = Math.sin(scrollPercent * Math.PI * 6) * 0.005;
  }

  checkModelsLoaded()

  renderer.render(scene, camera);
}


}



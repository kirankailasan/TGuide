import * as THREE from 'https://cdn.skypack.dev/three@0.134.0';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
camera.position.z = 50;

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.domElement.id = "background-canvas";
document.body.appendChild(renderer.domElement);

const light1 = new THREE.PointLight(0x00ffff, 6, 300);
light1.position.set(50, 50, 50);
scene.add(light1);

const light2 = new THREE.PointLight(0x66ffff, 3, 300);
light2.position.set(-50, -50, -50);
scene.add(light2);

const bubbleMaterial = new THREE.MeshPhysicalMaterial({
  color:0x66ccff,
  roughness: 0.05,
  transmission: 1,
  thickness: 4.0,
  clearcoat: 6,
  transparent: true,
  opacity: 0.95,
  metalness:2,
  emissive: new THREE.Color(0x66ccff),
  emissiveIntensity: 8
});

const bubbles = [];
for (let i = 0; i < 350; i++) {
  const geometry = new THREE.SphereGeometry(Math.random() * 2 + 1, 32, 32);
  const mesh = new THREE.Mesh(geometry, bubbleMaterial);
  mesh.position.set(
    (Math.random() - 0.5) * 200,
    (Math.random() - 0.5) * 200,
    (Math.random() - 0.5) * 200
  );
  scene.add(mesh);
  bubbles.push({
    mesh,
    velocity: new THREE.Vector3(
      (Math.random() - 0.5) * 0.3,
      (Math.random() - 0.5) * 0.3,
      (Math.random() - 0.5) * 0.3
    ),
    emissiveBase: Math.random() * 0.5 + 0.3
  });
}

let mouseX = 0;
let mouseY = 0;

document.addEventListener('mousemove', (event) => {
  mouseX = (event.clientX / window.innerWidth - 0.5) * 2;
  mouseY = (event.clientY / window.innerHeight - 0.5) * 2;
});

function animate(time) {
  requestAnimationFrame(animate);

  camera.position.x += (mouseX * 30 - camera.position.x) * 0.05;
  camera.position.y += (-mouseY * 30 - camera.position.y) * 0.05;
  camera.lookAt(scene.position);

  bubbles.forEach((b, i) => {
    b.mesh.position.add(b.velocity);
    if (b.mesh.position.length() > 120) {
      b.mesh.position.multiplyScalar(-1);
    }
    b.mesh.material.emissiveIntensity = b.emissiveBase + 0.3 * Math.sin(time * 0.002 + i);
  });

  renderer.render(scene, camera);
}

animate();

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
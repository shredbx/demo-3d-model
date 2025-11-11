<script lang="ts">
	import { onMount } from 'svelte';
	import * as THREE from 'three';
	import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
	import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

	let canvas: HTMLCanvasElement;
	let loading = $state(true);
	let error = $state<string | null>(null);
	let loadingProgress = $state(0);

	// IMPORTANT: Replace this with your actual task ID after running the generation script
	// Example: const MODEL_PATH = '/models/bike-abc123def456.glb';
	const MODEL_PATH = '/models/bike-REPLACE_WITH_TASK_ID.glb';

	onMount(() => {
		// Scene setup
		const scene = new THREE.Scene();
		scene.background = new THREE.Color(0x0a0a0a); // Very dark background
		scene.fog = new THREE.Fog(0x0a0a0a, 10, 50); // Atmospheric fog

		// Camera
		const camera = new THREE.PerspectiveCamera(
			60,
			window.innerWidth / window.innerHeight,
			0.1,
			1000
		);
		camera.position.set(4, 2, 6);

		// Renderer with anti-aliasing
		const renderer = new THREE.WebGLRenderer({
			canvas,
			antialias: true,
			alpha: false
		});
		renderer.setSize(window.innerWidth, window.innerHeight);
		renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
		renderer.shadowMap.enabled = true;
		renderer.shadowMap.type = THREE.PCFSoftShadowMap;
		renderer.toneMapping = THREE.ACESFilmicToneMapping;
		renderer.toneMappingExposure = 1.2;

		// Controls with smooth damping
		const controls = new OrbitControls(camera, renderer.domElement);
		controls.enableDamping = true;
		controls.dampingFactor = 0.05;
		controls.minDistance = 2;
		controls.maxDistance = 15;
		controls.maxPolarAngle = Math.PI / 1.8; // Limit to prevent going underneath
		controls.autoRotate = true;
		controls.autoRotateSpeed = 0.5;

		// Lighting setup - Multiple lights for dramatic effect
		const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
		scene.add(ambientLight);

		// Key light (main directional light)
		const keyLight = new THREE.DirectionalLight(0xffffff, 1.5);
		keyLight.position.set(5, 10, 7);
		keyLight.castShadow = true;
		keyLight.shadow.mapSize.width = 2048;
		keyLight.shadow.mapSize.height = 2048;
		keyLight.shadow.camera.near = 0.5;
		keyLight.shadow.camera.far = 50;
		scene.add(keyLight);

		// Fill light (softer, opposite side)
		const fillLight = new THREE.DirectionalLight(0x88ccff, 0.4);
		fillLight.position.set(-5, 5, -5);
		scene.add(fillLight);

		// Rim light (back light for edge highlights)
		const rimLight = new THREE.SpotLight(0x00d4ff, 1.2);
		rimLight.position.set(-3, 8, -8);
		rimLight.angle = Math.PI / 6;
		rimLight.penumbra = 0.3;
		scene.add(rimLight);

		// Accent light (colored spotlight from below)
		const accentLight = new THREE.PointLight(0x0099ff, 0.8, 20);
		accentLight.position.set(0, -2, 0);
		scene.add(accentLight);

		// Ground plane for shadows
		const groundGeometry = new THREE.CircleGeometry(10, 32);
		const groundMaterial = new THREE.MeshStandardMaterial({
			color: 0x0a0a0a,
			roughness: 0.8,
			metalness: 0.2
		});
		const ground = new THREE.Mesh(groundGeometry, groundMaterial);
		ground.rotation.x = -Math.PI / 2;
		ground.position.y = -0.5;
		ground.receiveShadow = true;
		scene.add(ground);

		// Grid helper (subtle)
		const gridHelper = new THREE.GridHelper(20, 20, 0x222222, 0x111111);
		gridHelper.position.y = -0.49;
		scene.add(gridHelper);

		// Load 3D model
		const loader = new GLTFLoader();
		loader.load(
			MODEL_PATH,
			// onLoad
			(gltf) => {
				const model = gltf.scene;

				// Enable shadows
				model.traverse((child) => {
					if (child instanceof THREE.Mesh) {
						child.castShadow = true;
						child.receiveShadow = true;
					}
				});

				// Center and scale model
				const box = new THREE.Box3().setFromObject(model);
				const center = box.getCenter(new THREE.Vector3());
				const size = box.getSize(new THREE.Vector3());

				// Calculate scale to fit model nicely
				const maxDim = Math.max(size.x, size.y, size.z);
				const scale = 3 / maxDim; // Target size of 3 units
				model.scale.multiplyScalar(scale);

				// Recalculate after scaling
				box.setFromObject(model);
				const newCenter = box.getCenter(new THREE.Vector3());
				model.position.sub(newCenter);
				model.position.y = 0; // Place on ground

				scene.add(model);
				loading = false;

				console.log('✅ Model loaded successfully');
				console.log('Model dimensions:', size);
				console.log('Model scale:', scale);
			},
			// onProgress
			(progress) => {
				if (progress.total > 0) {
					loadingProgress = (progress.loaded / progress.total) * 100;
					console.log(`Loading: ${loadingProgress.toFixed(0)}%`);
				}
			},
			// onError
			(err) => {
				console.error('❌ Error loading model:', err);
				error = `Failed to load 3D model. Make sure to:\n1. Run the generation script first\n2. Update MODEL_PATH in +page.svelte\n3. Check browser console for details`;
				loading = false;
			}
		);

		// Animation loop
		function animate() {
			requestAnimationFrame(animate);
			controls.update();
			renderer.render(scene, camera);
		}
		animate();

		// Handle window resize
		function handleResize() {
			camera.aspect = window.innerWidth / window.innerHeight;
			camera.updateProjectionMatrix();
			renderer.setSize(window.innerWidth, window.innerHeight);
		}
		window.addEventListener('resize', handleResize);

		// Cleanup
		return () => {
			window.removeEventListener('resize', handleResize);
			controls.dispose();
			renderer.dispose();
		};
	});
</script>

<div class="hero">
	<!-- Hero Content -->
	<div class="hero-content">
		<h1>ShredBX</h1>
		<p class="tagline">Transform Your Bike into 3D</p>
		<div class="subtitle">
			Upload a photo of your dirt bike and watch it come alive in interactive 3D
		</div>

		{#if loading}
			<div class="loading">
				<div class="spinner"></div>
				<p>Loading 3D Model... {loadingProgress.toFixed(0)}%</p>
			</div>
		{/if}

		{#if error}
			<div class="error">
				<h3>⚠️ Model Not Found</h3>
				<pre>{error}</pre>
			</div>
		{/if}

		<div class="controls-hint">
			<span>🖱️ Drag to rotate</span>
			<span>🔍 Scroll to zoom</span>
		</div>
	</div>

	<!-- Three.js Canvas -->
	<canvas bind:this={canvas} />

	<!-- Gradient overlays for depth -->
	<div class="gradient-overlay gradient-top"></div>
	<div class="gradient-overlay gradient-bottom"></div>
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		overflow: hidden;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu,
			Cantarell, sans-serif;
	}

	.hero {
		position: relative;
		width: 100vw;
		height: 100vh;
		overflow: hidden;
		background: radial-gradient(ellipse at center, #1a1a2e 0%, #0a0a0a 100%);
	}

	.hero-content {
		position: absolute;
		top: 15%;
		left: 50%;
		transform: translateX(-50%);
		text-align: center;
		z-index: 10;
		color: #fff;
		max-width: 90%;
	}

	h1 {
		font-size: clamp(3rem, 8vw, 6rem);
		font-weight: 900;
		background: linear-gradient(135deg, #00d4ff 0%, #0099ff 50%, #0066ff 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
		margin: 0;
		letter-spacing: -0.02em;
		text-shadow: 0 0 60px rgba(0, 212, 255, 0.3);
		animation: glow 3s ease-in-out infinite alternate;
	}

	@keyframes glow {
		from {
			text-shadow: 0 0 40px rgba(0, 212, 255, 0.2);
		}
		to {
			text-shadow: 0 0 60px rgba(0, 212, 255, 0.4);
		}
	}

	.tagline {
		font-size: clamp(1.2rem, 3vw, 2rem);
		color: #8892b0;
		margin: 1rem 0 0.5rem;
		font-weight: 500;
	}

	.subtitle {
		font-size: clamp(0.9rem, 2vw, 1.1rem);
		color: #64ffda;
		margin-top: 0.5rem;
		font-weight: 400;
		opacity: 0.9;
	}

	.loading {
		margin-top: 3rem;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
	}

	.loading p {
		color: #00d4ff;
		font-size: 1rem;
		font-weight: 500;
	}

	.spinner {
		width: 50px;
		height: 50px;
		border: 4px solid rgba(0, 212, 255, 0.2);
		border-top-color: #00d4ff;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.error {
		margin-top: 2rem;
		padding: 1.5rem;
		background: rgba(255, 50, 50, 0.1);
		border: 2px solid rgba(255, 50, 50, 0.3);
		border-radius: 8px;
		max-width: 600px;
		margin-left: auto;
		margin-right: auto;
	}

	.error h3 {
		margin: 0 0 1rem 0;
		color: #ff5050;
	}

	.error pre {
		text-align: left;
		color: #ccc;
		font-size: 0.9rem;
		white-space: pre-wrap;
		word-wrap: break-word;
		margin: 0;
	}

	.controls-hint {
		margin-top: 3rem;
		display: flex;
		gap: 2rem;
		justify-content: center;
		opacity: 0.6;
		font-size: 0.9rem;
		color: #8892b0;
	}

	.controls-hint span {
		padding: 0.5rem 1rem;
		background: rgba(255, 255, 255, 0.05);
		border-radius: 20px;
		backdrop-filter: blur(10px);
	}

	canvas {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		z-index: 1;
	}

	.gradient-overlay {
		position: absolute;
		left: 0;
		right: 0;
		height: 200px;
		pointer-events: none;
		z-index: 5;
	}

	.gradient-top {
		top: 0;
		background: linear-gradient(180deg, rgba(10, 10, 10, 0.8) 0%, transparent 100%);
	}

	.gradient-bottom {
		bottom: 0;
		background: linear-gradient(0deg, rgba(10, 10, 10, 0.8) 0%, transparent 100%);
	}

	/* Mobile responsive */
	@media (max-width: 768px) {
		.hero-content {
			top: 10%;
		}

		.controls-hint {
			flex-direction: column;
			gap: 0.5rem;
		}
	}
</style>

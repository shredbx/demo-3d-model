<script lang="ts">
	import { onMount } from 'svelte';
	import * as THREE from 'three';
	import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
	import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

	let canvas: HTMLCanvasElement;
	let loading = $state(true);
	let error = $state<string | null>(null);
	let loadingProgress = $state(0);

	// Available bike models/styles with per-model configurations
	const MODELS = {
		style1: {
			name: 'KTM Dirt Bike',
			path: '/models/ktm-dirt-bike.glb',
			description: 'KTM Dirt Bike (Blue)',
			camera: {
				position: { x: 9, y: 4, z: 6 }, // Further back
				minDistance: 4,
				maxDistance: 12,
				scale: 3, // Reduced from 6
				positionOffset: { x: 0, y: 1.5, z: 0 } // Lift it up
			}
		},
		style2: {
			name: 'Ducati Streetfighter',
			path: '/models/ducati-streetfighter.glb',
			description: 'Ducati Streetfighter V4 S',
			camera: {
				position: { x: 1, y: 4, z: 9 },
				minDistance: 4,
				maxDistance: 12,
				scale: 3,
				positionOffset: { x: 0, y: 0.5, z: 0 }
			}
		},
		style3: {
			name: 'Suzuki GSX 750',
			path: '/models/suzuki-gsx-750.glb',
			description: 'Suzuki GSX 750 Sport Bike',
			camera: {
				position: { x: 15, y: 6, z: 11 }, // Raised camera (y: 2 -> 3.5) and zoomed out (z: 7 -> 9)
				minDistance: 4,
				maxDistance: 12,
				scale: 3,
				positionOffset: { x: 0, y: 0.5, z: 0 }
			}
		},
		style4: {
			name: 'Yamaha Cruiser',
			path: '/models/yamaha-stryker.glb',
			description: 'Yamaha Stryker Cruiser',
			camera: {
				position: { x: 15, y: 6, z: 11 }, // Raised camera (y: 2 -> 3.5) and zoomed out (z: 8 -> 10)
				minDistance: 4,
				maxDistance: 12,
				scale: 3,
				positionOffset: { x: 0, y: 0.5, z: 0 }
			}
		}
	};

	// Current selected style
	let currentStyle = $state<'style1' | 'style2' | 'style3' | 'style4'>('style1');
	let currentModel: any = null; // Store current loaded model
	let scene: THREE.Scene;
	let camera: THREE.PerspectiveCamera;
	let renderer: THREE.WebGLRenderer;
	let controls: OrbitControls;

	// Function to load a model with per-model configuration
	function loadModel(modelPath: string, config: any) {
		console.log('🚀 loadModel() called with:', modelPath);
		loading = true;
		error = null;
		loadingProgress = 0;

		// Remove old model if exists
		if (currentModel) {
			console.log('🗑️ Removing old model');
			scene.remove(currentModel);
			currentModel = null;
		}

		// Load new model
		console.log('📦 Starting GLTFLoader for:', modelPath);
		const loader = new GLTFLoader();
		loader.load(
			modelPath,
			// onLoad
			(gltf) => {
				console.log('✅ Model loaded successfully:', modelPath);
				const model = gltf.scene;

				// Enable shadows and customize colors
				model.traverse((child) => {
					if (child instanceof THREE.Mesh) {
						child.castShadow = true;
						child.receiveShadow = true;

						// Color customization: Replace KTM orange with blue (like bike photo)
						if (child.material) {
							// Handle array of materials
							const materials = Array.isArray(child.material) ? child.material : [child.material];

							materials.forEach((material) => {
								if (material.color) {
									const hex = material.color.getHex();

									// Replace KTM orange (#FF6600 or similar) with blue (#0066FF)
									// Check if color is orange-ish (R high, G medium, B low)
									const r = (hex >> 16) & 0xff;
									const g = (hex >> 8) & 0xff;
									const b = hex & 0xff;

									if (r > 200 && g < 150 && b < 100) {
										// It's orange - replace with blue
										material.color.setHex(0x0066FF);
										console.log('Replaced orange with blue');
									}

									// Darken very bright whites (likely logos) to hide KTM branding
									if (r > 240 && g > 240 && b > 240) {
										material.color.setHex(0x1a1a1a); // Dark gray
										console.log('Darkened bright white (logo area)');
									}
								}

								// Ducati customization - make it red
								if (modelPath.includes('ducati')) {
									// Apply Ducati red to body panels
									if (material.color) {
										const hex = material.color.getHex();
										const r = (hex >> 16) & 0xff;
										const g = (hex >> 8) & 0xff;
										const b = hex & 0xff;

										// Replace any bright colors (body panels) with Ducati red
										if ((r > 150 || g > 150 || b > 150) && !(r < 50 && g < 50 && b < 50)) {
											// Not already dark (keep black parts black)
											material.color.setHex(0xDC0000); // Ducati red
											console.log('Applied Ducati red to body panel');
										}
									}
								}

								// If material has a texture map with KTM logo, reduce its opacity
								if (material.map && material.map.name && material.map.name.toLowerCase().includes('ktm')) {
									material.opacity = 0.3;
									material.transparent = true;
									console.log('Reduced KTM texture opacity');
								}
							});
						}
					}
				});

				// Center and scale model using per-model configuration
				const box = new THREE.Box3().setFromObject(model);
				const center = box.getCenter(new THREE.Vector3());
				const size = box.getSize(new THREE.Vector3());

				// Apply scale from config instead of calculating
				const scale = config.scale;
				model.scale.multiplyScalar(scale);

				// Recalculate after scaling
				box.setFromObject(model);
				const newCenter = box.getCenter(new THREE.Vector3());
				model.position.sub(newCenter);

				// Per-model ground positioning adjustments
				const minY = box.min.y;

				if (modelPath.includes('ktm')) {
					// KTM: Use original positioning (no ground adjustment)
					// Just apply the config offsets directly
				} else if (modelPath.includes('ducati') || modelPath.includes('suzuki') || modelPath.includes('yamaha')) {
					// Ducati, Suzuki, Yamaha: Apply adjusted ground positioning
					// Lower them a bit more (they were still slightly floating)
					model.position.y = -minY / 3;
				}

				// Apply additional position offset from config
				model.position.x += config.positionOffset.x;
				model.position.y += config.positionOffset.y;
				model.position.z += config.positionOffset.z;

				scene.add(model);
				currentModel = model;

				// Update camera position and controls based on config
				camera.position.set(config.position.x, config.position.y, config.position.z);
				controls.minDistance = config.minDistance;
				controls.maxDistance = config.maxDistance;
				controls.update();

				loading = false;

				console.log('✅ Model loaded and configured successfully');
				console.log('Model dimensions:', size);
				console.log('Model scale:', scale);
				console.log('Camera position:', config.position);
			},
			// onProgress
			(progress) => {
				if (progress.total > 0) {
					loadingProgress = (progress.loaded / progress.total) * 100;
					console.log(`📊 Loading progress: ${loadingProgress.toFixed(0)}%`);
				}
			},
			// onError
			(err) => {
				console.error('❌ Error loading model:', err);
				error = `Failed to load 3D model: ${modelPath}`;
				loading = false;
			}
		);
	}

	// Watch for style changes and load new model
	// Use untrack to prevent infinite loops when updating previousStyle
	let previousStyle: 'style1' | 'style2' | 'style3' | 'style4' = 'style1';
	$effect(() => {
		console.log('🔄 $effect triggered!');
		console.log('  scene:', !!scene);
		console.log('  currentStyle:', currentStyle);
		console.log('  previousStyle:', previousStyle);
		console.log('  Condition check (currentStyle !== previousStyle):', currentStyle !== previousStyle);

		if (scene && currentStyle && currentStyle !== previousStyle) {
			console.log(`✅ Loading new model: ${MODELS[currentStyle].name}`);
			const modelConfig = MODELS[currentStyle];
			console.log(`Switching to ${modelConfig.name}: ${modelConfig.path}`);
			loadModel(modelConfig.path, modelConfig.camera);
			previousStyle = currentStyle; // Update after loading starts
		} else {
			console.log('❌ Skipping model load - condition not met');
		}
	});

	// Camera adjustment function for control buttons
	function adjustCamera(action: string) {
		if (!camera || !controls) return;

		const rotationSpeed = 0.2;

		switch (action) {
			case 'rotateLeft':
				camera.position.applyAxisAngle(new THREE.Vector3(0, 1, 0), rotationSpeed);
				break;
			case 'rotateRight':
				camera.position.applyAxisAngle(new THREE.Vector3(0, 1, 0), -rotationSpeed);
				break;
			case 'rotateUp': {
				// Rotate camera position around X-axis (pitch rotation) to look down at model
				const axis = new THREE.Vector3(1, 0, 0);
				const position = camera.position.clone();

				// Rotate around X-axis in world space
				const quaternion = new THREE.Quaternion();
				quaternion.setFromAxisAngle(axis, rotationSpeed);
				position.applyQuaternion(quaternion);

				camera.position.copy(position);
				break;
			}
			case 'rotateDown': {
				// Rotate camera position around X-axis (pitch rotation) to look up at model
				const axis = new THREE.Vector3(1, 0, 0);
				const position = camera.position.clone();

				// Rotate around X-axis in world space
				const quaternion = new THREE.Quaternion();
				quaternion.setFromAxisAngle(axis, -rotationSpeed);
				position.applyQuaternion(quaternion);

				camera.position.copy(position);
				break;
			}
			case 'zoomIn':
				camera.position.multiplyScalar(0.9); // Move closer
				break;
			case 'zoomOut':
				camera.position.multiplyScalar(1.1); // Move farther
				break;
		}

		camera.lookAt(0, 0, 0);
		controls.update();
	}

	onMount(() => {
		// Scene setup
		scene = new THREE.Scene();
		scene.background = new THREE.Color(0x2a2a2a); // Dark gray garage

		// Add ground plane (garage floor)
		const groundGeometry = new THREE.PlaneGeometry(100, 100);
		const groundMaterial = new THREE.MeshStandardMaterial({
			color: 0x3a3a3a,
			roughness: 0.8,
			metalness: 0.2
		});
		const ground = new THREE.Mesh(groundGeometry, groundMaterial);
		ground.rotation.x = -Math.PI / 2; // Make it horizontal
		ground.position.y = 0; // At ground level
		ground.receiveShadow = true;
		scene.add(ground);

		// Add subtle grid for garage floor effect
		const gridHelper = new THREE.GridHelper(100, 100, 0x555555, 0x444444);
		gridHelper.position.y = 0.01; // Slightly above ground to prevent z-fighting
		scene.add(gridHelper);

		// Fog removed for better visibility

		// Camera setup with fixed canvas dimensions
		const canvasWidth = 800;
		const canvasHeight = 600;

		camera = new THREE.PerspectiveCamera(
			60,
			canvasWidth / canvasHeight,
			0.1,
			1000
		);
		camera.position.set(4, 0, 6);

		// Renderer with anti-aliasing
		renderer = new THREE.WebGLRenderer({
			canvas,
			antialias: true,
			alpha: false
		});
		renderer.setSize(canvasWidth, canvasHeight);
		renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
		renderer.shadowMap.enabled = true;
		renderer.shadowMap.type = THREE.PCFSoftShadowMap;
		renderer.toneMapping = THREE.ACESFilmicToneMapping;
		renderer.toneMappingExposure = 1.2;

		// Controls with smooth damping
		controls = new OrbitControls(camera, renderer.domElement);
		controls.enableDamping = true;
		controls.dampingFactor = 0.05;
		controls.minDistance = 2;
		controls.maxDistance = 15;
		controls.maxPolarAngle = Math.PI / 1.8; // Limit to prevent going underneath
		controls.autoRotate = true;
		controls.autoRotateSpeed = 0.5;

		// Lighting setup - Much brighter for better visibility
		const ambientLight = new THREE.AmbientLight(0xffffff, 3.0); // Increased to 3.0 for brightness
		scene.add(ambientLight);

		// Key light (main directional light) - Very bright
		const keyLight = new THREE.DirectionalLight(0xffffff, 4.0); // Increased to 4.0
		keyLight.position.set(5, 10, 7);
		keyLight.castShadow = true;
		keyLight.shadow.mapSize.width = 2048;
		keyLight.shadow.mapSize.height = 2048;
		keyLight.shadow.camera.near = 0.5;
		keyLight.shadow.camera.far = 50;
		scene.add(keyLight);

		// Front light (illuminate from camera direction for better visibility)
		const frontLight = new THREE.DirectionalLight(0xffffff, 2.5); // Increased to 2.5
		frontLight.position.set(0, 5, 10); // In front of bike
		scene.add(frontLight);

		// Fill light (softer, opposite side)
		const fillLight = new THREE.DirectionalLight(0xffffff, 2.0); // Increased to 2.0 and changed to white
		fillLight.position.set(-5, 5, -5);
		scene.add(fillLight);

		// Additional top light for more even illumination
		const topLight = new THREE.DirectionalLight(0xffffff, 2.0);
		topLight.position.set(0, 10, 0);
		scene.add(topLight);

		// Load initial model after scene is ready
		loadModel(MODELS.style1.path, MODELS.style1.camera);

		// Animation loop
		function animate() {
			requestAnimationFrame(animate);
			controls.update();
			renderer.render(scene, camera);
		}
		animate();

		// Handle window resize (maintain fixed canvas aspect ratio)
		function handleResize() {
			// Get actual canvas dimensions from CSS
			const rect = canvas.getBoundingClientRect();
			camera.aspect = rect.width / rect.height;
			camera.updateProjectionMatrix();
			renderer.setSize(rect.width, rect.height);
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
		<h1>MotoMoto</h1>
		<p class="tagline">Virtual 3D Moto Models</p>
		<!-- Temporarily hidden
		<div class="subtitle">
			Upload a photo of your dirt bike and watch it come alive in interactive 3D
		</div>
		-->

		<!-- Style Toggle -->
		<div class="style-toggle">
			<button
				class="style-btn"
				class:active={currentStyle === 'style1'}
				onclick={() => {
					console.log('🖱️ Button clicked! Previous:', currentStyle);
					currentStyle = 'style1';
					console.log('🖱️ Button clicked! New:', currentStyle);
				}}
				title={MODELS.style1.description}
			>
				🏍️ KTM Dirt Bike
			</button>
			<button
				class="style-btn"
				class:active={currentStyle === 'style2'}
				onclick={() => {
					console.log('🖱️ Button clicked! Previous:', currentStyle);
					currentStyle = 'style2';
					console.log('🖱️ Button clicked! New:', currentStyle);
				}}
				title={MODELS.style2.description}
			>
				🏍️ Ducati Streetfighter
			</button>
			<button
				class="style-btn"
				class:active={currentStyle === 'style3'}
				onclick={() => {
					console.log('🖱️ Button clicked! Previous:', currentStyle);
					currentStyle = 'style3';
					console.log('🖱️ Button clicked! New:', currentStyle);
				}}
				title={MODELS.style3.description}
			>
				🏍️ Suzuki GSX 750
			</button>
			<button
				class="style-btn"
				class:active={currentStyle === 'style4'}
				onclick={() => {
					console.log('🖱️ Button clicked! Previous:', currentStyle);
					currentStyle = 'style4';
					console.log('🖱️ Button clicked! New:', currentStyle);
				}}
				title={MODELS.style4.description}
			>
				🏍️ Yamaha Cruiser
			</button>
		</div>

		{#if error}
			<div class="error" data-testid="error-message">
				<h3>⚠️ Model Not Found</h3>
				<pre>{error}</pre>
			</div>
		{/if}

		<!-- Temporarily hidden until upload works
		<div class="controls-hint">
			<span>🖱️ Drag to rotate</span>
			<span>🔍 Scroll to zoom</span>
		</div>
		-->
	</div>

	<!-- Viewer Container: Controls + Canvas -->
	<div class="viewer-container">
		<!-- Camera Controls (left side of canvas) -->
		<div class="camera-controls">
			<div class="control-group">
				<button class="control-btn" onclick={() => adjustCamera('rotateLeft')} title="Rotate Left">
					←
				</button>
				<button class="control-btn" onclick={() => adjustCamera('rotateRight')} title="Rotate Right">
					→
				</button>
			</div>
			<div class="control-group">
				<button class="control-btn" onclick={() => adjustCamera('rotateUp')} title="Rotate Up">
					↑
				</button>
				<button class="control-btn" onclick={() => adjustCamera('rotateDown')} title="Rotate Down">
					↓
				</button>
			</div>
			<div class="control-group">
				<button class="control-btn" onclick={() => adjustCamera('zoomIn')} title="Zoom In">
					+
				</button>
				<button class="control-btn" onclick={() => adjustCamera('zoomOut')} title="Zoom Out">
					−
				</button>
			</div>
		</div>

		<!-- Canvas Container (with loading overlay) -->
		<div class="canvas-container">
			<!-- Three.js Canvas -->
			<canvas bind:this={canvas} data-testid="model-canvas" />

			<!-- Loading indicator integrated into canvas area -->
			{#if loading}
				<div class="canvas-loading-overlay" data-testid="loading-spinner">
					<div class="spinner"></div>
					<p>Loading 3D Model... {loadingProgress.toFixed(0)}%</p>
				</div>
			{/if}
		</div>
	</div>

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
		top: 5%;
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

	.style-toggle {
		margin-top: 2rem;
		display: flex;
		gap: 1rem;
		justify-content: center;
		flex-wrap: wrap;
	}

	.style-btn {
		padding: 0.75rem 1.5rem;
		background: rgba(0, 0, 0, 0.8);
		border: 2px solid rgba(0, 212, 255, 0.3);
		border-radius: 8px;
		color: #8892b0;
		font-size: 0.9rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.3s ease;
		backdrop-filter: blur(10px);
	}

	.style-btn:hover {
		border-color: rgba(0, 212, 255, 0.6);
		color: #00d4ff;
		background: rgba(0, 0, 0, 0.9);
		transform: translateY(-2px);
	}

	.style-btn.active {
		border-color: #00d4ff;
		color: #00d4ff;
		background: rgba(0, 0, 0, 0.95);
		box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
	}

	.viewer-container {
		position: absolute;
		top: 40%;
		left: 50%;
		transform: translateX(-50%);
		display: flex;
		align-items: center;
		gap: 1.5rem;
		z-index: 10;
	}

	.camera-controls {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		z-index: 20;
	}

	.control-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		background: rgba(0, 0, 0, 0.7);
		padding: 0.5rem;
		border-radius: 8px;
		border: 1px solid rgba(0, 212, 255, 0.3);
	}

	.control-btn {
		width: 40px;
		height: 40px;
		background: rgba(0, 0, 0, 0.8);
		border: 2px solid rgba(0, 212, 255, 0.4);
		border-radius: 6px;
		color: #00d4ff;
		font-size: 1.2rem;
		font-weight: bold;
		cursor: pointer;
		transition: all 0.2s ease;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.control-btn:hover {
		background: rgba(0, 212, 255, 0.2);
		border-color: #00d4ff;
		transform: scale(1.05);
	}

	.control-btn:active {
		transform: scale(0.95);
	}

	.canvas-container {
		position: relative;
		width: 800px;
		height: 600px;
		max-width: 90vw;
		max-height: 50vh;
	}

	.canvas-loading-overlay {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 1rem;
		z-index: 15;
		pointer-events: none;
	}

	.canvas-loading-overlay p {
		color: #00d4ff;
		font-size: 1.2rem;
		font-weight: 600;
		text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
		margin: 0;
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
		width: 800px;
		height: 600px;
		max-width: 90vw;
		max-height: 50vh;
		border-radius: 12px;
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
		border: 2px solid rgba(0, 212, 255, 0.3);
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
			top: 5%;
		}

		h1 {
			font-size: clamp(2rem, 6vw, 4rem);
		}

		.tagline {
			font-size: clamp(1rem, 2.5vw, 1.5rem);
		}

		.viewer-container {
			top: 35%;
			flex-direction: column;
			gap: 1rem;
		}

		canvas {
			width: 95vw;
			height: 60vh;
			max-height: 500px;
		}

		.camera-controls {
			flex-direction: row;
			gap: 0.75rem;
		}

		.canvas-container {
			width: 95vw;
			height: 60vh;
			max-height: 500px;
		}

		.style-toggle {
			margin-top: 1rem;
			gap: 0.5rem;
		}

		.style-btn {
			padding: 0.6rem 1.2rem;
			font-size: 0.85rem;
		}

		.controls-hint {
			flex-direction: column;
			gap: 0.5rem;
		}

		.control-btn {
			width: 36px;
			height: 36px;
			font-size: 1rem;
		}
	}
</style>

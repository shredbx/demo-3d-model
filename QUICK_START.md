# ShredBX Quick Start - Rapid Prototype

**Goal:** Generate 3D model from `docs/bike-test.jpg` and display on homepage

---

## 🔑 Step 1: Get Meshy.ai API Key

1. Go to: https://app.meshy.ai/
2. Sign up (free account)
3. Go to: https://app.meshy.ai/api-keys
4. Click "Create API Key"
5. Copy the key (starts with `msy_...`)
6. Add to `.env`:
   ```bash
   MESHY_API_KEY=msy_your_actual_key_here
   ```

**Free Tier:**
- 200 credits free (worth $100)
- Each 3D generation = 1 credit ($0.50)
- Enough for 200 test generations

---

## 🚀 Step 2: Install Dependencies

```bash
# Python dependencies
pip install httpx python-dotenv

# Frontend dependencies (if not already installed)
cd apps/frontend
npm install three
cd ../..
```

---

## 🎨 Step 3: Generate 3D Model

```bash
# Run generation script
python scripts/generate_3d_model.py docs/bike-test.jpg

# This will:
# 1. Upload bike-test.jpg to Meshy.ai
# 2. Create 3D generation task
# 3. Poll status every 10 seconds
# 4. Download GLB model when complete (5-15 min)
# 5. Save to: apps/frontend/static/models/bike-XXXXX.glb
```

**Output:**
```
🚀 ShredBX 3D Model Generator
==================================================
Input: docs/bike-test.jpg
==================================================

📤 Uploading image: docs/bike-test.jpg
✅ Image uploaded successfully
🎨 Creating 3D generation task...
✅ Task created: abc123def456
⏳ Estimated time: 5-15 minutes
⏳ Polling status (updates every 10 seconds)...
⏳ This will take 5-15 minutes. Grab a coffee! ☕
📊 Status: PENDING | Progress: 0% | Elapsed: 0s
📊 Status: IN_PROGRESS | Progress: 15% | Elapsed: 60s
📊 Status: IN_PROGRESS | Progress: 45% | Elapsed: 180s
📊 Status: IN_PROGRESS | Progress: 78% | Elapsed: 420s
✅ Generation complete! Total time: 680s (11.3 min)
⬇️  Downloading model to apps/frontend/static/models/bike-abc123def456.glb...
✅ Model downloaded: 8.45 MB
📄 Metadata saved: apps/frontend/static/models/bike-abc123def456.json

==================================================
✅ SUCCESS!
==================================================
Model: apps/frontend/static/models/bike-abc123def456.glb
Task ID: abc123def456
💰 Cost: ~$0.50 (1 Meshy credit)

📝 Next steps:
1. Update apps/frontend/src/routes/+page.svelte
2. Change model path to: /models/bike-abc123def456.glb
3. Run: cd apps/frontend && npm run dev --port 5483
4. View at: http://localhost:5483
```

---

## 🎯 Step 4: Update Frontend with Model Path

After generation completes, you'll get a task ID (e.g., `abc123def456`).

Update `apps/frontend/src/routes/+page.svelte`:

```svelte
// Change this line (around line 50):
loader.load(
  '/models/bike-abc123def456.glb', // ← Replace with your actual task ID
  (gltf) => {
    ...
  }
);
```

---

## 🌐 Step 5: Run Frontend

```bash
cd apps/frontend
npm run dev -- --port 5483
```

Open: http://localhost:5483

**You should see:**
- Dark hero page
- "ShredBX" title with gradient
- 3D bike model rotating in center
- Can drag to rotate, scroll to zoom

---

## 💰 Cost Tracking

**Check your usage:**
1. Go to: https://app.meshy.ai/dashboard
2. See "Credits Used" (should show 1 credit = $0.50)
3. Free tier: 200 credits remaining

**Future costs:**
- Each generation: 1 credit ($0.50)
- Pro plan: $20/month for 1000 credits
- Enterprise: Custom pricing

---

## 🐛 Troubleshooting

### Error: "MESHY_API_KEY not found"
- Make sure `.env` exists in project root
- Make sure key is set: `MESHY_API_KEY=msy_...`

### Error: "HTTP 401 Unauthorized"
- Check API key is correct
- Go to https://app.meshy.ai/api-keys and regenerate

### Error: "Image not found"
- Make sure `docs/bike-test.jpg` exists
- Use absolute path if needed

### Model doesn't load in browser
- Check browser console for errors
- Verify model file exists in `apps/frontend/static/models/`
- Check model path in +page.svelte matches task ID

---

## 📁 Generated Files

After running script:

```
shredbx-model-generator/
├── apps/
│   └── frontend/
│       └── static/
│           └── models/
│               ├── bike-abc123def456.glb   ← 3D model (8-12 MB)
│               └── bike-abc123def456.json  ← Metadata
├── docs/
│   └── bike-test.jpg                       ← Source image
└── scripts/
    └── generate_3d_model.py                ← Generation script
```

---

## 🔄 Next Steps (Future)

1. **Add upload UI** - Let users upload their own bike photos
2. **Add status polling** - Show real-time progress bar
3. **Add authentication** - Protect API from abuse
4. **Add download button** - Let users download GLB file
5. **Add OpenRouter chat** - Let users chat about their bike

For now: **Just get the 3D model displaying!** 🚀

# ShredBX Model Generator

**Transform dirt bike photos into interactive 3D models**

## 🚀 Rapid Prototype - Quick Start

This is a rapid prototype focused on **speed to demo**. Full production features documented in `.claude/reports/FINAL-milestone-plan-v2.md`.

### What This Does

1. Takes a dirt bike photo (`docs/bike-test.jpg`)
2. Sends it to Meshy.ai API for 3D generation
3. Displays the 3D model on a dark hero homepage with Three.js
4. Cost: ~$0.50 per model generation

---

## 📋 Setup (5 Minutes)

### 1. Get Meshy.ai API Key

```bash
# 1. Sign up at https://app.meshy.ai/
# 2. Get API key from https://app.meshy.ai/api-keys
# 3. Add to .env file:
echo 'MESHY_API_KEY=msy_your_actual_key_here' >> .env
```

**Free Tier:** 200 credits ($100 value), enough for 200 test generations

### 2. Install Dependencies

```bash
# Python (for generation script)
pip install httpx python-dotenv

# Frontend (Three.js + SvelteKit)
cd apps/frontend
npm install
cd ../..
```

---

## 🎨 Generate 3D Model (10-15 min)

```bash
# Run generation script on test bike image
python scripts/generate_3d_model.py docs/bike-test.jpg

# This will:
# - Upload image to Meshy.ai
# - Create 3D generation task
# - Poll status every 10 seconds (5-15 min wait)
# - Download GLB model to apps/frontend/static/models/
# - Print task ID and next steps
```

**Output Example:**
```
✅ SUCCESS!
Model: apps/frontend/static/models/bike-abc123def456.glb
Task ID: abc123def456
💰 Cost: ~$0.50 (1 Meshy credit)
```

---

## 🌐 View in Browser

### 1. Update Model Path

Edit `apps/frontend/src/routes/+page.svelte` (line 13):

```typescript
// Replace this:
const MODEL_PATH = '/models/bike-REPLACE_WITH_TASK_ID.glb';

// With your actual task ID:
const MODEL_PATH = '/models/bike-abc123def456.glb';
```

### 2. Run Frontend

```bash
cd apps/frontend
npm run dev
```

### 3. Open Browser

```
http://localhost:5483
```

**You should see:**
- Dark gradient background
- "ShredBX" title with blue gradient glow
- 3D bike model rotating automatically
- Interactive controls (drag to rotate, scroll to zoom)

---

## 🛠️ Tech Stack (Rapid Prototype)

**Backend:**
- Python script (httpx for Meshy.ai API)
- No database (ephemeral for prototype)
- No authentication (wide open for prototype)

**Frontend:**
- SvelteKit 5 (Svelte Runes)
- Three.js (3D rendering)
- Custom port: 5483 (+310 from default)

**AI Service:**
- Meshy.ai API (image-to-3D generation)
- $0.50 per model (~5-15 min generation)
- Free tier: 200 credits

**What's NOT in prototype:**
- ❌ Upload UI (manual script for now)
- ❌ Database (ephemeral storage)
- ❌ Authentication
- ❌ Rate limiting
- ❌ Download button
- ❌ Mobile optimization

**See:** `.claude/tasks/RAPID-PROTOTYPE-v0.md` for full technical debt list

---

## 📁 Project Structure

```
shredbx-model-generator/
├── apps/
│   └── frontend/                 # SvelteKit app
│       ├── src/
│       │   ├── routes/
│       │   │   └── +page.svelte  # Hero page with Three.js
│       │   └── app.html          # HTML template
│       ├── static/
│       │   └── models/           # Generated GLB models
│       ├── package.json
│       ├── svelte.config.js
│       └── vite.config.ts        # Port 5483
│
├── scripts/
│   └── generate_3d_model.py      # Meshy.ai generation script
│
├── docs/
│   └── bike-test.jpg             # Test bike image (blue YZ)
│
├── .claude/
│   ├── reports/
│   │   ├── FINAL-milestone-plan-v2.md          # Full MVP plan
│   │   └── FINAL-implementation-ready-summary.md
│   └── tasks/
│       ├── RAPID-PROTOTYPE-v0.md              # Prototype specs
│       └── RAPID-PROTOTYPE-STRATEGY.md        # Technical approach
│
├── .env                          # API keys (gitignored)
├── QUICK_START.md               # Detailed setup guide
└── README.md                    # This file
```

---

## 💰 Cost Tracking

**Meshy.ai Dashboard:** https://app.meshy.ai/dashboard

**Per Generation:**
- Cost: ~$0.50 (1 credit)
- Time: 5-15 minutes
- Output: GLB file (8-12 MB)

**Free Tier:**
- 200 credits ($100 value)
- Expires: Never (for now)

**Paid Plans:**
- Pro: $20/month (1000 credits)
- Enterprise: Custom pricing

---

## 🐛 Troubleshooting

### Model doesn't load

**Check:**
1. Did you run `python scripts/generate_3d_model.py docs/bike-test.jpg`?
2. Did you update `MODEL_PATH` in `+page.svelte` with the correct task ID?
3. Does the file exist in `apps/frontend/static/models/bike-XXXXX.glb`?
4. Check browser console (F12) for errors

### "MESHY_API_KEY not found"

```bash
# Make sure .env exists with your key
cat .env
# Should show: MESHY_API_KEY=msy_...

# If not, add it:
echo 'MESHY_API_KEY=msy_your_key_here' >> .env
```

### "HTTP 401 Unauthorized"

Your API key is invalid. Get a new one from https://app.meshy.ai/api-keys

### Generation fails or times out

- Check Meshy.ai status: https://status.meshy.ai/
- Try again in a few minutes
- Check dashboard for credit balance

---

## 🔄 Next Steps (Future Features)

See `.claude/reports/FINAL-milestone-plan-v2.md` for complete roadmap:

**Milestone -1: Market Validation** (1 week)
- Customer interviews
- Competitor analysis
- Pricing validation

**Milestone 0: Technical Validation** (1 week)
- Test Meshy.ai quality (80%+ acceptable models)
- Performance testing (60fps target)
- Cost validation (< $0.60/model)

**Milestone 1: Public MVP** (3 weeks)
- Upload UI (drag-drop)
- Authentication (Supabase)
- Server-Sent Events (real-time status)
- Email notifications
- Download button
- Mobile-first responsive design

**Milestone 2: Production Hardening** (2 weeks)
- E2E tests
- Load testing
- Security audit
- CI/CD pipeline
- Monitoring (Sentry)

**Total Timeline:** 7 weeks to production-ready MVP

---

## 📚 Documentation

- **Quick Start:** `QUICK_START.md` (step-by-step guide)
- **Prototype Specs:** `.claude/tasks/RAPID-PROTOTYPE-v0.md`
- **Full MVP Plan:** `.claude/reports/FINAL-milestone-plan-v2.md`
- **Expert Feedback:** `.claude/reports/expert-feedback-analysis.md`
- **Project Context:** `CLAUDE.md` (LLM guidance)

---

## 🎯 Current Status

- ✅ Git initialized
- ✅ Python generation script created
- ✅ Frontend hero page with Three.js
- ✅ Documentation complete
- ⏭️ **Next:** Run generation script and view 3D model!

---

**Built with Claude Code** 🤖

Coordinator: LLM-powered SDLC orchestration
Subagents: Specialized implementation agents (future)
Timeline: Rapid prototype → Production MVP (7 weeks)

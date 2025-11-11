# Brand Colors & Homepage Redesign Specification

**Purpose:** Apply Bestays brand colors from NextJS project and simplify homepage design

**Date:** 2025-11-08

---

## Brand Color Palette

**Primary Brand Colors:**
```css
--brand-1: #0a4349;  /* Dark teal - primary brand color */
--brand-2: #d2bf98;  /* Warm beige/gold - secondary */
--brand-3: #999d70;  /* Sage green - accent */
--brand-4: #f0ecdf;  /* Cream - light background */
```

**Color Conversion to OKLCH:**
- Dark teal (#0a4349): `oklch(0.274 0.054 203.5)`
- Warm beige (#d2bf98): `oklch(0.795 0.043 85.5)`
- Sage green (#999d70): `oklch(0.631 0.046 118)`
- Cream (#f0ecdf): `oklch(0.946 0.015 85)`

---

## Required Changes

### 1. Update `apps/frontend/src/app.css`

**Update the `:root` section:**

```css
:root {
  --radius: 0.625rem;

  /* Bestays Brand Colors */
  --brand-1: #0a4349;  /* Dark teal */
  --brand-2: #d2bf98;  /* Warm beige/gold */
  --brand-3: #999d70;  /* Sage green */
  --brand-4: #f0ecdf;  /* Cream */

  /* Base colors */
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);

  /* Primary - Dark teal (#0a4349) */
  --primary: oklch(0.274 0.054 203.5);
  --primary-foreground: oklch(0.97 0.014 254.604);

  /* Secondary - Warm beige/gold (#d2bf98) */
  --secondary: oklch(0.795 0.043 85.5);
  --secondary-foreground: oklch(0.205 0 0);

  /* Keep existing for other colors */
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --border: oklch(0.922 0 0);
  --input: oklch(0.922 0 0);
  --ring: oklch(0.274 0.054 203.5);  /* Match primary */

  /* Charts - keep existing */
  --chart-1: oklch(0.646 0.222 41.116);
  --chart-2: oklch(0.6 0.118 184.704);
  --chart-3: oklch(0.398 0.07 227.392);
  --chart-4: oklch(0.828 0.189 84.429);
  --chart-5: oklch(0.769 0.188 70.08);

  /* Sidebar - use brand colors */
  --sidebar: oklch(0.985 0 0);
  --sidebar-foreground: oklch(0.145 0 0);
  --sidebar-primary: oklch(0.274 0.054 203.5);  /* Brand teal */
  --sidebar-primary-foreground: oklch(0.97 0.014 254.604);
  --sidebar-accent: oklch(0.97 0 0);
  --sidebar-accent-foreground: oklch(0.205 0 0);
  --sidebar-border: oklch(0.922 0 0);
  --sidebar-ring: oklch(0.274 0.054 203.5);
}
```

**Update `.dark` section:**

```css
.dark {
  /* Base dark mode colors - keep existing */
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.205 0 0);
  --card-foreground: oklch(0.985 0 0);
  --popover: oklch(0.205 0 0);
  --popover-foreground: oklch(0.985 0 0);

  /* Primary - Keep dark teal */
  --primary: oklch(0.274 0.054 203.5);
  --primary-foreground: oklch(0.97 0.014 254.604);

  /* Secondary - Darker for dark mode (#4b3b1a) */
  --secondary: oklch(0.269 0.04 70);
  --secondary-foreground: oklch(0.985 0 0);

  /* Keep rest of dark mode - existing */
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.704 0.191 22.216);
  --border: oklch(1 0 0 / 10%);
  --input: oklch(1 0 0 / 15%);
  --ring: oklch(0.556 0 0);
  --chart-1: oklch(0.488 0.243 264.376);
  --chart-2: oklch(0.696 0.17 162.48);
  --chart-3: oklch(0.769 0.188 70.08);
  --chart-4: oklch(0.627 0.265 303.9);
  --chart-5: oklch(0.645 0.246 16.439);
  --sidebar: oklch(0.205 0 0);
  --sidebar-foreground: oklch(0.985 0 0);
  --sidebar-primary: oklch(0.488 0.243 264.376);
  --sidebar-primary-foreground: oklch(0.985 0 0);
  --sidebar-accent: oklch(0.269 0 0);
  --sidebar-accent-foreground: oklch(0.985 0 0);
  --sidebar-border: oklch(1 0 0 / 10%);
  --sidebar-ring: oklch(0.556 0 0);
}
```

---

### 2. Update `apps/frontend/src/routes/+page.svelte`

**Replace entire file content with:**

```svelte
<!--
BeStays Home Page - Landing Page

ARCHITECTURE:
  Layer: Page
  Pattern: Public Landing Page with Auth Integration

INTEGRATION:
  - Component: AuthNav.svelte (Conditional auth navigation)
  - Store: authStore (reactive auth state)
  - API: Future property search integration

NOTES:
  - Auth initialization handled in root layout (+layout.svelte)
  - No duplicate fetchUser calls (removed from onMount)
  - Loading state shows during auth initialization
  - Smooth UX transition from loading → authenticated state
  - Brand colors: Dark teal (#0a4349), Warm beige (#d2bf98), Sage green (#999d70)
-->

<script lang="ts">
  import AuthNav from '$lib/components/AuthNav.svelte';
  import { authStore } from '$lib/stores/auth.svelte';
</script>

{#if authStore.isLoading}
  <!-- Loading state with brand colors -->
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0a4349] to-[#999d70]">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
      <p class="text-white">Loading...</p>
    </div>
  </div>
{:else}
  <!-- Main homepage with brand gradient -->
  <div class="relative w-full h-screen bg-gradient-to-br from-[#0a4349] via-[#999d70] to-[#d2bf98]">
    <!-- Navigation -->
    <div class="absolute top-0 left-0 w-full z-10">
      <div class="container mx-auto px-6 py-6">
        <div class="flex justify-between items-center">
          <!-- Logo/Brand -->
          <div class="text-white font-bold text-2xl">
            BeStays
          </div>

          <!-- Auth Navigation -->
          <AuthNav showUserButton={true} />
        </div>
      </div>
    </div>

    <!-- Hero Section -->
    <div class="flex items-center justify-center h-full">
      <div class="text-center px-6">
        <h1 class="text-6xl md:text-7xl font-bold text-white mb-6 drop-shadow-2xl">
          BeStays
        </h1>
        <p class="text-2xl md:text-3xl text-[#f0ecdf] mb-8 drop-shadow-lg">
          Modern Real Estate Platform
        </p>

        {#if !authStore.isAuthenticated}
          <div class="flex gap-4 justify-center">
            <a
              href="/login"
              class="px-8 py-3 bg-white text-[#0a4349] font-semibold rounded-lg shadow-lg hover:bg-[#f0ecdf] transition-colors"
            >
              Get Started
            </a>
          </div>
        {:else}
          <div class="flex gap-4 justify-center">
            <a
              href="/dashboard"
              class="px-8 py-3 bg-white text-[#0a4349] font-semibold rounded-lg shadow-lg hover:bg-[#f0ecdf] transition-colors"
            >
              Go to Dashboard
            </a>
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}
```

---

### 3. Update `apps/frontend/src/routes/login/+page.svelte`

**Update line 530 only (the gradient background):**

**Old:**
```svelte
<div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center px-6">
```

**New:**
```svelte
<div class="min-h-screen bg-gradient-to-br from-[#0a4349] to-[#999d70] flex items-center justify-center px-6">
```

**Update the white card background to cream for better contrast (line 590):**

**Old:**
```svelte
<div class="bg-white rounded-xl shadow-lg p-8">
```

**New:**
```svelte
<div class="bg-[#f0ecdf] rounded-xl shadow-lg p-8">
```

**Also update line 540 (loading state card):**

**Old:**
```svelte
<div class="bg-white rounded-xl shadow-lg p-8 flex items-center justify-center">
```

**New:**
```svelte
<div class="bg-[#f0ecdf] rounded-xl shadow-lg p-8 flex items-center justify-center">
```

**And line 575 (error state card):**

**Old:**
```svelte
<div class="bg-white rounded-xl shadow-lg p-8">
```

**New:**
```svelte
<div class="bg-[#f0ecdf] rounded-xl shadow-lg p-8">
```

---

## Expected Outcomes

After implementation:

1. ✅ **Brand Colors Applied:**
   - Primary: Dark teal (#0a4349)
   - Secondary: Warm beige/gold (#d2bf98)
   - Accent: Sage green (#999d70)
   - Light: Cream (#f0ecdf)

2. ✅ **Homepage:**
   - Clean gradient background (teal → sage → beige)
   - Large hero title "BeStays"
   - Subtitle: "Modern Real Estate Platform"
   - CTA: "Get Started" (not authenticated) or "Go to Dashboard" (authenticated)
   - Navigation with AuthNav component

3. ✅ **Login Page:**
   - Brand gradient background (teal → sage)
   - Cream cards for better contrast
   - All existing functionality preserved

4. ✅ **Consistency:**
   - All pages use Bestays brand colors
   - Visual identity matches NextJS project
   - Responsive design maintained

---

## Implementation Notes

- Use Tailwind arbitrary values `[#hexcode]` for brand colors in components
- CSS variables in app.css use OKLCH color space for better color interpolation
- Maintain all existing functionality (auth, navigation, error handling)
- Preserve responsive design (mobile-friendly)
- Keep smooth transitions and hover states
- All loading states, error states, and interactive elements should work identically

---

## Files to Modify

1. `/Users/solo/Projects/_repos/bestays/apps/frontend/src/app.css`
2. `/Users/solo/Projects/_repos/bestays/apps/frontend/src/routes/+page.svelte`
3. `/Users/solo/Projects/_repos/bestays/apps/frontend/src/routes/login/+page.svelte`

---

**Subagent:** dev-frontend-svelte
**Product:** bestays
**Priority:** High

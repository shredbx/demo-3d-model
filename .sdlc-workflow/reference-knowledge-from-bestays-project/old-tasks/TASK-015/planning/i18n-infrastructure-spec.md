# i18n Infrastructure Implementation Specification

**TASK:** TASK-015 (prerequisite)
**Story:** US-023
**Agent:** dev-frontend-svelte
**Date:** 2025-11-09

---

## Overview

Build minimal i18n infrastructure to support locale-aware routing and content switching for EN/TH locales in the Bestays SvelteKit application.

**Approach:** Lightweight custom implementation (not Paraglide) since we only need:
- Locale routing (`/[lang]/`)
- Simple locale context
- No complex translation files needed (backend handles translations)

---

## 1. Locale Routing Structure

### 1.1 Route Pattern

Convert existing routes to use `[lang]` parameter:

**Before:**
```
/routes/
  +page.svelte (homepage)
  login/
    +page.svelte
  dashboard/
    +page.svelte
```

**After:**
```
/routes/
  +page.svelte (redirect to /en)
  [lang]/
    +page.svelte (homepage)
    +layout.svelte (locale context provider)
    +layout.ts (locale validation)
    login/
      +page.svelte
    dashboard/
      +page.svelte
    properties/
      +page.svelte (NEW)
```

### 1.2 Root Redirect

**File:** `src/routes/+page.server.ts`

Redirect root `/` to `/en` (default locale):

```typescript
import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
  throw redirect(302, '/en');
};
```

---

## 2. Locale Layout (Context Provider)

### 2.1 Layout Load Function

**File:** `src/routes/[lang]/+layout.ts`

Validate locale parameter and provide to layout:

```typescript
import { error } from '@sveltejs/kit';
import type { LayoutLoad } from './$types';

const SUPPORTED_LOCALES = ['en', 'th'] as const;
export type Locale = typeof SUPPORTED_LOCALES[number];

export const load: LayoutLoad = async ({ params }) => {
  const locale = params.lang as Locale;

  // Validate locale
  if (!SUPPORTED_LOCALES.includes(locale)) {
    throw error(404, `Unsupported locale: ${locale}`);
  }

  return {
    locale
  };
};
```

### 2.2 Layout Component

**File:** `src/routes/[lang]/+layout.svelte`

Provide locale context to all child pages:

```svelte
<script lang="ts">
  import { setContext } from 'svelte';
  import type { Locale } from './+layout';

  const { data, children } = $props();

  // Create locale context
  const localeContext = $state({
    locale: data.locale as Locale
  });

  // Provide context to children
  setContext('i18n', localeContext);
</script>

{@render children()}
```

---

## 3. i18n Context Module

### 3.1 Context Helper

**File:** `src/lib/i18n/context.svelte.ts`

Helper to access locale context in components:

```typescript
import { getContext } from 'svelte';

export type Locale = 'en' | 'th';

export interface I18nContext {
  locale: Locale;
}

/**
 * Get i18n context from nearest layout provider
 *
 * Usage in components:
 *   const i18n = getI18nContext();
 *   const locale = $derived(i18n.locale); // 'en' or 'th'
 */
export function getI18nContext(): I18nContext {
  const context = getContext<I18nContext>('i18n');

  if (!context) {
    throw new Error('i18n context not found. Must be used within [lang] route.');
  }

  return context;
}
```

---

## 4. Locale Switcher Component

### 4.1 LocaleSwitcher Component

**File:** `src/lib/components/LocaleSwitcher.svelte`

Component to switch between EN/TH:

```svelte
<script lang="ts">
  import { page } from '$app/stores';
  import { getI18nContext } from '$lib/i18n/context.svelte';

  const i18n = getI18nContext();
  const currentPath = $derived($page.url.pathname);

  /**
   * Switch locale by replacing /en/ or /th/ in current path
   */
  function switchLocale(newLocale: 'en' | 'th') {
    const pathWithoutLocale = currentPath.replace(/^\/(en|th)/, '');
    const newPath = `/${newLocale}${pathWithoutLocale}`;
    window.location.href = newPath;
  }
</script>

<div class="flex gap-2">
  <button
    onclick={() => switchLocale('en')}
    class={`px-3 py-1 rounded ${i18n.locale === 'en' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
  >
    EN
  </button>
  <button
    onclick={() => switchLocale('th')}
    class={`px-3 py-1 rounded ${i18n.locale === 'th' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
  >
    TH
  </button>
</div>
```

---

## 5. Migration Plan

### 5.1 Existing Routes to Migrate

**Phase 1: Create [lang] structure (this task)**
- ✅ Create `[lang]/+layout.svelte` and `[lang]/+layout.ts`
- ✅ Create root redirect at `+page.server.ts`
- ✅ Create i18n context helper
- ✅ Create LocaleSwitcher component

**Phase 2: Migrate existing pages (future tasks)**
- Move `/login/+page.svelte` → `/[lang]/login/+page.svelte`
- Move `/dashboard/+page.svelte` → `/[lang]/dashboard/+page.svelte`
- Update all internal links to include locale

**Phase 3: New pages (this task)**
- ✅ Create `/[lang]/properties/+page.svelte` (property listing)

---

## 6. Testing Checklist

### Manual Testing

- [ ] Navigate to `/` → redirects to `/en`
- [ ] Navigate to `/en` → shows homepage
- [ ] Navigate to `/th` → shows homepage (Thai)
- [ ] Navigate to `/de` → 404 error (unsupported locale)
- [ ] LocaleSwitcher switches between EN/TH
- [ ] Locale context accessible in components
- [ ] No SSR hydration errors
- [ ] No TypeScript errors

### Browser Testing

- [ ] Chrome (desktop + mobile)
- [ ] Firefox
- [ ] Safari

---

## 7. File Checklist

**New Files to Create:**

- ✅ `src/routes/+page.server.ts` (root redirect)
- ✅ `src/routes/[lang]/+layout.svelte` (locale provider)
- ✅ `src/routes/[lang]/+layout.ts` (locale validation)
- ✅ `src/lib/i18n/context.svelte.ts` (context helper)
- ✅ `src/lib/components/LocaleSwitcher.svelte` (locale switcher)

**Files to Reference (Don't Modify Yet):**

- `src/routes/+layout.svelte` (root layout, keep for now)
- `src/routes/+page.svelte` (homepage, will be moved later)

---

## 8. Implementation Notes

### Why Not Paraglide?

Paraglide is excellent for complex i18n needs, but we don't need it because:
1. **Backend handles translations** - API returns localized property data
2. **Simple locale switching** - Only EN/TH, no complex pluralization
3. **Lightweight** - Custom solution adds ~100 lines of code vs 5+ dependencies
4. **Easy to understand** - Team can maintain without learning Paraglide API

### Future Enhancements (Not This Task)

- Add more locales (ES, FR, etc.)
- Locale-aware date/number formatting
- Browser locale detection
- Locale persistence (localStorage)
- SEO hreflang tags

---

## 9. Success Criteria

✅ Locale routing working (`/en/`, `/th/`)
✅ i18n context accessible in components
✅ LocaleSwitcher component working
✅ Root redirect to `/en` working
✅ Invalid locales return 404
✅ No SSR hydration errors
✅ No TypeScript errors
✅ Ready to build property listing page

---

## 10. Next Steps

After i18n infrastructure is complete:
1. Verify localhost:5183/en works
2. Verify localhost:5183/th works
3. Verify LocaleSwitcher switches locales
4. Proceed to build property listing page at `/[lang]/properties`

---

**Ready for Implementation! 🚀**

Launch dev-frontend-svelte agent with this spec.

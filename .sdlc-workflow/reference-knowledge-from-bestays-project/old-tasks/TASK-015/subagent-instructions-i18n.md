# Subagent Instructions: i18n Infrastructure Implementation

**Agent:** dev-frontend-svelte
**Task:** TASK-015 (prerequisite: i18n infrastructure)
**Branch:** feat/TASK-015-US-023
**Date:** 2025-11-09

---

## Objective

Implement minimal i18n infrastructure for locale-aware routing (EN/TH) in the Bestays SvelteKit application.

---

## Context

The property listing page spec assumes i18n infrastructure exists, but it doesn't. Before building `/[lang]/properties`, we need to implement:

1. Locale routing pattern (`/[lang]/`)
2. Locale context provider
3. LocaleSwitcher component

This is a **lightweight custom implementation** (not Paraglide) because the backend handles translations.

---

## Full Specification

Read the complete implementation spec at:

**`.claude/tasks/TASK-015/planning/i18n-infrastructure-spec.md`**

---

## Files to Create

### 1. Root Redirect

**File:** `src/routes/+page.server.ts`

Redirect `/` → `/en`:

```typescript
import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
  throw redirect(302, '/en');
};
```

### 2. Locale Layout (Validation)

**File:** `src/routes/[lang]/+layout.ts`

```typescript
import { error } from '@sveltejs/kit';
import type { LayoutLoad } from './$types';

const SUPPORTED_LOCALES = ['en', 'th'] as const;
export type Locale = typeof SUPPORTED_LOCALES[number];

export const load: LayoutLoad = async ({ params }) => {
  const locale = params.lang as Locale;

  if (!SUPPORTED_LOCALES.includes(locale)) {
    throw error(404, `Unsupported locale: ${locale}`);
  }

  return { locale };
};
```

### 3. Locale Layout (Context Provider)

**File:** `src/routes/[lang]/+layout.svelte`

```svelte
<script lang="ts">
  import { setContext } from 'svelte';
  import type { Locale } from './+layout';

  const { data, children } = $props();

  const localeContext = $state({
    locale: data.locale as Locale
  });

  setContext('i18n', localeContext);
</script>

{@render children()}
```

### 4. i18n Context Helper

**File:** `src/lib/i18n/context.svelte.ts`

```typescript
import { getContext } from 'svelte';

export type Locale = 'en' | 'th';

export interface I18nContext {
  locale: Locale;
}

export function getI18nContext(): I18nContext {
  const context = getContext<I18nContext>('i18n');

  if (!context) {
    throw new Error('i18n context not found. Must be used within [lang] route.');
  }

  return context;
}
```

### 5. LocaleSwitcher Component

**File:** `src/lib/components/LocaleSwitcher.svelte`

```svelte
<script lang="ts">
  import { page } from '$app/stores';
  import { getI18nContext } from '$lib/i18n/context.svelte';

  const i18n = getI18nContext();
  const currentPath = $derived($page.url.pathname);

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

### 6. Temporary Homepage (Test Page)

**File:** `src/routes/[lang]/+page.svelte`

Create a simple test page to verify i18n works:

```svelte
<script lang="ts">
  import { getI18nContext } from '$lib/i18n/context.svelte';
  import LocaleSwitcher from '$lib/components/LocaleSwitcher.svelte';

  const i18n = getI18nContext();
</script>

<div class="container mx-auto px-4 py-8">
  <div class="flex justify-between items-center mb-8">
    <h1 class="text-3xl font-bold">
      {i18n.locale === 'en' ? 'Welcome to Bestays' : 'ยินดีต้อนรับสู่ Bestays'}
    </h1>
    <LocaleSwitcher />
  </div>

  <p class="text-gray-600">
    {i18n.locale === 'en'
      ? 'Current locale: English (EN)'
      : 'โลเคลปัจจุบัน: ไทย (TH)'}
  </p>

  <div class="mt-4">
    <a href="/{i18n.locale}/properties" class="text-blue-600 hover:underline">
      {i18n.locale === 'en' ? 'View Properties' : 'ดูอสังหาริมทรัพย์'}
    </a>
  </div>
</div>
```

---

## Success Criteria

After implementation, verify:

- ✅ Navigate to `http://localhost:5183/` → redirects to `/en`
- ✅ Navigate to `/en` → shows test homepage with "EN" active
- ✅ Navigate to `/th` → shows test homepage with "TH" active
- ✅ Navigate to `/de` → 404 error
- ✅ Click "TH" button → switches to Thai
- ✅ Click "EN" button → switches to English
- ✅ No TypeScript errors
- ✅ No SSR hydration warnings
- ✅ LocaleSwitcher displays correctly

---

## Important Notes

1. **Don't migrate existing pages yet** - Keep them at their current paths (`/login`, `/dashboard`, etc.). Migration will be a future task.

2. **Use Svelte 5 patterns**:
   - Use `$props()` for component props
   - Use `$derived()` for computed values
   - Use `$state()` for reactive state
   - Use `setContext/getContext` for context

3. **SSR-safe** - All code must work on server and client

4. **Follow existing code style** - Match patterns from other components

---

## Testing Instructions

After implementation:

1. Start dev server (should already be running): `make dev`
2. Navigate to `http://localhost:5183/`
3. Verify redirect to `/en`
4. Click LocaleSwitcher "TH" button
5. Verify URL changes to `/th`
6. Verify content updates to Thai
7. Check browser console for errors

---

## Return to Coordinator

After implementation, provide:

1. Summary of files created
2. Confirmation all success criteria met
3. Any issues encountered
4. Screenshot or description of working LocaleSwitcher

---

**Good luck! 🚀**

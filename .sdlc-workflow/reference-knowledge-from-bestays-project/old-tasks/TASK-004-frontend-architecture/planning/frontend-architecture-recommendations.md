# TASK-004: Frontend Architecture Design

**Date:** 2025-11-07
**Agent:** dev-frontend
**User Story:** US-018 (White-Label Multi-Product Architecture)
**Status:** COMPLETE
**Priority:** P0 (URGENT AND MANDATORY)

---

## Executive Summary

**Recommended Approach:** **SvelteKit Monorepo with Shared Components**

**Key Rationale:**
1. **Simplicity First** - No Turborepo/Lerna (use pnpm workspaces), standard SvelteKit + Vite patterns
2. **Modular Architecture** - Shared Svelte components, shared API client, product-specific apps
3. **Configuration-Driven Theming** - CSS variables + Tailwind config per product
4. **Clear Documentation** - Environment-based configuration, TypeScript type safety

**Alignment with User Priorities:**
- ✅ **Simplicity for deployment** - Static builds, Docker Compose orchestration
- ✅ **Simplicity for development** - Vite HMR, single command setup (`pnpm install`)
- ✅ **Modular architecture** - Clear package boundaries, reusable components
- ✅ **Clear documentation** - Environment variables, TypeScript interfaces

**Risk Assessment:** LOW - This approach uses standard SvelteKit patterns, proven pnpm workspaces, and existing UI component library (Svelte 5 + TailwindCSS).

---

## Monorepo Package Structure

### Directory Layout

```
bestays-monorepo/
├── packages/                          # Shared frontend packages
│   ├── shared-ui/                     # Reusable Svelte components
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── Button.svelte
│   │   │   │   ├── Card.svelte
│   │   │   │   ├── Input.svelte
│   │   │   │   ├── Modal.svelte
│   │   │   │   ├── Avatar.svelte
│   │   │   │   └── ...
│   │   │   ├── styles/
│   │   │   │   ├── base.css          # Global CSS
│   │   │   │   └── variables.css     # CSS variables
│   │   │   └── utils/
│   │   │       └── cn.ts             # Class name utilities
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── shared-api-client/             # TypeScript API client
│   │   ├── src/
│   │   │   ├── types.ts               # API types (from backend Pydantic)
│   │   │   ├── client.ts              # Fetch wrapper
│   │   │   ├── endpoints/
│   │   │   │   ├── users.ts           # /api/v1/users
│   │   │   │   ├── properties.ts      # /api/v1/properties
│   │   │   │   ├── chat.ts            # /api/v1/llm/chat
│   │   │   │   └── faq.ts             # /api/v1/faq/search
│   │   │   └── errors.ts              # Error handling
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── shared-chat-ui/                # Chat UI components
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── ChatInterface.svelte
│   │   │   │   ├── MessageList.svelte
│   │   │   │   ├── Message.svelte
│   │   │   │   ├── MessageInput.svelte
│   │   │   │   └── ChatToggle.svelte
│   │   │   ├── stores/
│   │   │   │   └── chat.ts            # Svelte stores (runes)
│   │   │   └── types.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── shared-faq-ui/                 # FAQ UI components
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── FAQSearch.svelte
│   │   │   │   ├── FAQList.svelte
│   │   │   │   └── FAQItem.svelte
│   │   │   └── types.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   └── shared-config/                 # Configuration types
│       ├── src/
│       │   └── types.ts               # ProductConfig interface
│       ├── package.json
│       └── tsconfig.json
│
├── apps/                              # Product applications
│   ├── bestays-web/                   # Bestays SvelteKit app
│   │   ├── src/
│   │   │   ├── lib/
│   │   │   │   ├── config/
│   │   │   │   │   ├── index.ts       # Bestays-specific config
│   │   │   │   │   ├── chat.ts        # Chat config
│   │   │   │   │   └── theme.ts       # Theme config
│   │   │   │   ├── clerk.ts           # Clerk SDK initialization
│   │   │   │   └── api.ts             # API client instance
│   │   │   ├── routes/
│   │   │   │   ├── +layout.svelte     # Global layout
│   │   │   │   ├── +page.svelte       # Home page
│   │   │   │   ├── login/
│   │   │   │   ├── dashboard/
│   │   │   │   └── properties/
│   │   │   └── app.css                # Product-specific CSS
│   │   ├── static/                    # Bestays assets
│   │   │   ├── logo.svg
│   │   │   └── favicon.ico
│   │   ├── .env.development
│   │   ├── svelte.config.js
│   │   ├── vite.config.ts
│   │   ├── tailwind.config.js
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   └── realestate-web/                # Real Estate SvelteKit app
│       ├── src/
│       │   ├── lib/
│       │   │   ├── config/
│       │   │   │   ├── index.ts       # Real Estate-specific config
│       │   │   │   ├── chat.ts
│       │   │   │   └── theme.ts
│       │   │   ├── clerk.ts
│       │   │   └── api.ts
│       │   ├── routes/
│       │   │   ├── +layout.svelte
│       │   │   ├── +page.svelte
│       │   │   ├── login/
│       │   │   ├── dashboard/
│       │   │   └── properties/
│       │   └── app.css
│       ├── static/
│       │   ├── logo.svg
│       │   └── favicon.ico
│       ├── .env.development
│       ├── svelte.config.js
│       ├── vite.config.ts
│       ├── tailwind.config.js
│       ├── package.json
│       └── tsconfig.json
│
├── docker/
│   ├── bestays-web/
│   │   ├── Dockerfile.dev
│   │   └── Dockerfile.prod
│   └── realestate-web/
│       ├── Dockerfile.dev
│       └── Dockerfile.prod
│
├── pnpm-workspace.yaml              # pnpm workspaces config
├── package.json                      # Root package.json
└── tsconfig.base.json                # Base TypeScript config
```

### Package Dependency Graph

```
apps/bestays-web
    ↓
shared-chat-ui ──→ shared-ui ──→ shared-config
    ↓                  ↓
shared-faq-ui ────→ shared-api-client
```

**Dependency Rules:**
1. **Shared packages can depend on other shared packages**
2. **Product apps can depend on any shared package**
3. **Shared packages CANNOT depend on product apps** (one-way dependency)
4. **No circular dependencies** (enforced by TypeScript)

### Import Patterns

```typescript
// In product apps (apps/bestays-web/src/routes/+page.svelte)
import { ChatInterface } from '@bestays/shared-chat-ui';
import { Button, Card } from '@bestays/shared-ui';
import { apiClient } from '$lib/api';
import { config } from '$lib/config';

// In shared packages (packages/shared-chat-ui/src/components/ChatInterface.svelte)
import { Button } from '@bestays/shared-ui';
import type { ProductConfig } from '@bestays/shared-config';
```

**Import Aliases:**
- `@bestays/shared-*` - Shared packages (via pnpm workspaces)
- `$lib/*` - Product-specific lib directory (SvelteKit alias)
- `$env/*` - Environment variables (SvelteKit)

---

## Theming System

### CSS Variables Approach (Recommended)

**Why CSS Variables:**
1. ✅ **Runtime theming** - Can be changed without rebuilding
2. ✅ **Simple** - No complex Tailwind configuration duplication
3. ✅ **Fallback support** - CSS variables have default values
4. ✅ **Dynamic** - Can be changed via JavaScript if needed

**Base CSS Variables** (`packages/shared-ui/src/styles/variables.css`):

```css
:root {
  /* Product-specific variables (overridden per product) */
  --color-primary: var(--product-primary, #3B82F6);
  --color-secondary: var(--product-secondary, #10B981);
  --color-accent: var(--product-accent, #F59E0B);

  /* Semantic colors (shared) */
  --color-background: #ffffff;
  --color-foreground: #1F2937;
  --color-muted: #F3F4F6;
  --color-border: #E5E7EB;

  /* Status colors (shared) */
  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-error: #EF4444;
  --color-info: #3B82F6;

  /* Typography */
  --font-family-base: 'Inter', system-ui, sans-serif;
  --font-family-heading: 'Inter', system-ui, sans-serif;

  /* Spacing scale */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Border radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}

/* Dark mode support (optional) */
@media (prefers-color-scheme: dark) {
  :root {
    --color-background: #1F2937;
    --color-foreground: #F9FAFB;
    --color-muted: #374151;
    --color-border: #4B5563;
  }
}
```

**Bestays Theme** (`apps/bestays-web/src/app.css`):

```css
@import '@bestays/shared-ui/styles/base.css';
@import '@bestays/shared-ui/styles/variables.css';

:root {
  /* Bestays brand colors */
  --product-primary: #3B82F6;    /* Blue */
  --product-secondary: #10B981;  /* Green */
  --product-accent: #F59E0B;     /* Amber */

  /* Custom overrides for Bestays */
  --font-family-heading: 'Poppins', system-ui, sans-serif;
}
```

**Real Estate Theme** (`apps/realestate-web/src/app.css`):

```css
@import '@bestays/shared-ui/styles/base.css';
@import '@bestays/shared-ui/styles/variables.css';

:root {
  /* Real Estate brand colors */
  --product-primary: #EF4444;    /* Red */
  --product-secondary: #F59E0B;  /* Orange */
  --product-accent: #8B5CF6;     /* Purple */

  /* Custom overrides for Real Estate */
  --font-family-heading: 'Playfair Display', serif;
}
```

### Tailwind Configuration Per Product

**Shared Tailwind Preset** (`packages/shared-ui/tailwind.preset.js`):

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  theme: {
    extend: {
      colors: {
        // Use CSS variables for theming
        primary: 'var(--color-primary)',
        secondary: 'var(--color-secondary)',
        accent: 'var(--color-accent)',
        background: 'var(--color-background)',
        foreground: 'var(--color-foreground)',
        muted: 'var(--color-muted)',
        border: 'var(--color-border)',
        success: 'var(--color-success)',
        warning: 'var(--color-warning)',
        error: 'var(--color-error)',
        info: 'var(--color-info)',
      },
      fontFamily: {
        sans: ['var(--font-family-base)'],
        heading: ['var(--font-family-heading)'],
      },
      borderRadius: {
        sm: 'var(--radius-sm)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
        full: 'var(--radius-full)',
      },
      boxShadow: {
        sm: 'var(--shadow-sm)',
        md: 'var(--shadow-md)',
        lg: 'var(--shadow-lg)',
      },
    },
  },
};
```

**Bestays Tailwind Config** (`apps/bestays-web/tailwind.config.js`):

```javascript
import sharedPreset from '@bestays/shared-ui/tailwind.preset.js';

/** @type {import('tailwindcss').Config} */
export default {
  presets: [sharedPreset],
  content: [
    './src/**/*.{html,js,svelte,ts}',
    '../../packages/shared-ui/src/**/*.{html,js,svelte,ts}',
    '../../packages/shared-chat-ui/src/**/*.{html,js,svelte,ts}',
    '../../packages/shared-faq-ui/src/**/*.{html,js,svelte,ts}',
  ],
  theme: {
    extend: {
      // Bestays-specific overrides (if needed)
    },
  },
};
```

**Real Estate Tailwind Config** (`apps/realestate-web/tailwind.config.js`):

```javascript
import sharedPreset from '@bestays/shared-ui/tailwind.preset.js';

/** @type {import('tailwindcss').Config} */
export default {
  presets: [sharedPreset],
  content: [
    './src/**/*.{html,js,svelte,ts}',
    '../../packages/shared-ui/src/**/*.{html,js,svelte,ts}',
    '../../packages/shared-chat-ui/src/**/*.{html,js,svelte,ts}',
    '../../packages/shared-faq-ui/src/**/*.{html,js,svelte,ts}',
  ],
  theme: {
    extend: {
      // Real Estate-specific overrides (if needed)
    },
  },
};
```

### Static Assets Handling

**Product-Specific Assets:**

```
apps/bestays-web/static/
├── logo.svg              # Bestays logo
├── logo-dark.svg         # Dark mode logo
├── favicon.ico
├── og-image.png          # Open Graph image
└── robots.txt

apps/realestate-web/static/
├── logo.svg              # Real Estate logo
├── logo-dark.svg
├── favicon.ico
├── og-image.png
└── robots.txt
```

**Shared Assets:**

```
packages/shared-ui/src/assets/
├── icons/
│   ├── check.svg
│   ├── close.svg
│   └── ...
└── illustrations/
    └── empty-state.svg
```

**Usage in Components:**

```svelte
<script lang="ts">
  import { config } from '$lib/config';
</script>

<!-- Product-specific logo -->
<img src="/logo.svg" alt="{config.app.name} Logo" />

<!-- Shared icon -->
<img src="{import('@bestays/shared-ui/assets/icons/check.svg')}" alt="Check" />
```

---

## Configuration Management

### TypeScript Configuration Interface

**Shared Config Types** (`packages/shared-config/src/types.ts`):

```typescript
export interface ProductConfig {
  /**
   * Product identification
   */
  product: {
    id: 'bestays' | 'realestate';
    name: string;
    tagline: string;
  };

  /**
   * Branding configuration
   */
  branding: {
    primaryColor: string;
    secondaryColor: string;
    accentColor: string;
    logo: {
      light: string;  // Path to light logo
      dark: string;   // Path to dark logo
    };
  };

  /**
   * Feature flags
   */
  features: {
    chatEnabled: boolean;
    faqEnabled: boolean;
    searchEnabled: boolean;
    darkModeEnabled: boolean;
  };

  /**
   * API configuration
   */
  api: {
    baseUrl: string;
    timeout: number;
  };

  /**
   * Clerk authentication
   */
  clerk: {
    publishableKey: string;
  };

  /**
   * Chat configuration
   */
  chat?: {
    guestMessagesLimit: number;
    enableVoiceInput: boolean;
    enableFileUpload: boolean;
  };
}
```

### Bestays Configuration

**Environment Variables** (`apps/bestays-web/.env.development`):

```bash
# Product Identification
VITE_PRODUCT_ID=bestays
VITE_APP_NAME=Bestays
VITE_APP_TAGLINE=Find your perfect vacation rental

# API
VITE_API_URL=http://localhost:8101

# Clerk (Bestays Project)
PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_c2FjcmVkLW1heWZseS01NS5jbGVyay5hY2NvdW50cy5kZXYk

# Feature Flags
VITE_CHAT_ENABLED=true
VITE_FAQ_ENABLED=true
VITE_SEARCH_ENABLED=true
VITE_DARK_MODE_ENABLED=true

# Branding
VITE_PRIMARY_COLOR=#3B82F6
VITE_SECONDARY_COLOR=#10B981
VITE_ACCENT_COLOR=#F59E0B
```

**Configuration File** (`apps/bestays-web/src/lib/config/index.ts`):

```typescript
import { PUBLIC_CLERK_PUBLISHABLE_KEY } from '$env/static/public';
import type { ProductConfig } from '@bestays/shared-config';

export const config: ProductConfig = {
  product: {
    id: 'bestays',
    name: import.meta.env.VITE_APP_NAME || 'Bestays',
    tagline: import.meta.env.VITE_APP_TAGLINE || 'Find your perfect vacation rental',
  },

  branding: {
    primaryColor: import.meta.env.VITE_PRIMARY_COLOR || '#3B82F6',
    secondaryColor: import.meta.env.VITE_SECONDARY_COLOR || '#10B981',
    accentColor: import.meta.env.VITE_ACCENT_COLOR || '#F59E0B',
    logo: {
      light: '/logo.svg',
      dark: '/logo-dark.svg',
    },
  },

  features: {
    chatEnabled: import.meta.env.VITE_CHAT_ENABLED === 'true',
    faqEnabled: import.meta.env.VITE_FAQ_ENABLED === 'true',
    searchEnabled: import.meta.env.VITE_SEARCH_ENABLED === 'true',
    darkModeEnabled: import.meta.env.VITE_DARK_MODE_ENABLED === 'true',
  },

  api: {
    baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8101',
    timeout: 30000,
  },

  clerk: {
    publishableKey: PUBLIC_CLERK_PUBLISHABLE_KEY,
  },

  chat: {
    guestMessagesLimit: 5,
    enableVoiceInput: false,
    enableFileUpload: true,
  },
};
```

### Real Estate Configuration

**Environment Variables** (`apps/realestate-web/.env.development`):

```bash
# Product Identification
VITE_PRODUCT_ID=realestate
VITE_APP_NAME=Best Real Estate
VITE_APP_TAGLINE=Luxury properties and investment opportunities

# API
VITE_API_URL=http://localhost:8102

# Clerk (Real Estate Project)
PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_cGxlYXNhbnQtZ251LTI1LmNsZXJrLmFjY291bnRzLmRldiQ

# Feature Flags
VITE_CHAT_ENABLED=true
VITE_FAQ_ENABLED=true
VITE_SEARCH_ENABLED=true
VITE_DARK_MODE_ENABLED=false

# Branding
VITE_PRIMARY_COLOR=#EF4444
VITE_SECONDARY_COLOR=#F59E0B
VITE_ACCENT_COLOR=#8B5CF6
```

**Configuration File** (`apps/realestate-web/src/lib/config/index.ts`):

```typescript
import { PUBLIC_CLERK_PUBLISHABLE_KEY } from '$env/static/public';
import type { ProductConfig } from '@bestays/shared-config';

export const config: ProductConfig = {
  product: {
    id: 'realestate',
    name: import.meta.env.VITE_APP_NAME || 'Best Real Estate',
    tagline: import.meta.env.VITE_APP_TAGLINE || 'Luxury properties and investment opportunities',
  },

  branding: {
    primaryColor: import.meta.env.VITE_PRIMARY_COLOR || '#EF4444',
    secondaryColor: import.meta.env.VITE_SECONDARY_COLOR || '#F59E0B',
    accentColor: import.meta.env.VITE_ACCENT_COLOR || '#8B5CF6',
    logo: {
      light: '/logo.svg',
      dark: '/logo-dark.svg',
    },
  },

  features: {
    chatEnabled: import.meta.env.VITE_CHAT_ENABLED === 'true',
    faqEnabled: import.meta.env.VITE_FAQ_ENABLED === 'true',
    searchEnabled: import.meta.env.VITE_SEARCH_ENABLED === 'true',
    darkModeEnabled: import.meta.env.VITE_DARK_MODE_ENABLED === 'false',
  },

  api: {
    baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8102',
    timeout: 30000,
  },

  clerk: {
    publishableKey: PUBLIC_CLERK_PUBLISHABLE_KEY,
  },

  chat: {
    guestMessagesLimit: 3,  // Different limit for Real Estate
    enableVoiceInput: false,
    enableFileUpload: true,
  },
};
```

### Environment Variable Validation

**Validation Utility** (`packages/shared-config/src/validate.ts`):

```typescript
import { z } from 'zod';

const envSchema = z.object({
  VITE_PRODUCT_ID: z.enum(['bestays', 'realestate']),
  VITE_APP_NAME: z.string().min(1),
  VITE_API_URL: z.string().url(),
  PUBLIC_CLERK_PUBLISHABLE_KEY: z.string().startsWith('pk_'),
  VITE_CHAT_ENABLED: z.enum(['true', 'false']),
  VITE_FAQ_ENABLED: z.enum(['true', 'false']),
  VITE_SEARCH_ENABLED: z.enum(['true', 'false']),
});

export function validateEnvironment(env: Record<string, string>) {
  try {
    envSchema.parse(env);
    console.log('✅ Environment variables validated successfully');
  } catch (error) {
    console.error('❌ Environment validation failed:', error);
    throw new Error('Invalid environment configuration');
  }
}
```

**Usage in App** (`apps/bestays-web/src/routes/+layout.ts`):

```typescript
import { validateEnvironment } from '@bestays/shared-config';

// Validate on app initialization
validateEnvironment(import.meta.env);
```

---

## Clerk Integration

### Clerk SDK Setup Per Product

**Bestays Clerk Integration** (`apps/bestays-web/src/lib/clerk.ts`):

```typescript
import { Clerk } from '@clerk/clerk-js';
import { PUBLIC_CLERK_PUBLISHABLE_KEY } from '$env/static/public';

// Create Clerk instance (Bestays Clerk project)
export const clerk = new Clerk(PUBLIC_CLERK_PUBLISHABLE_KEY);

// Initialize Clerk SDK
export async function initializeClerk() {
  await clerk.load({
    // Bestays-specific options
  });

  console.log('✅ Clerk initialized for Bestays');
}

// Get current Clerk user
export function getCurrentClerkUser() {
  return clerk.user;
}

// Get Clerk session token
export async function getClerkToken(): Promise<string | null> {
  const session = clerk.session;
  if (!session) return null;

  return await session.getToken();
}

// Sign out
export async function signOut() {
  await clerk.signOut();
}
```

**Real Estate Clerk Integration** (`apps/realestate-web/src/lib/clerk.ts`):

```typescript
import { Clerk } from '@clerk/clerk-js';
import { PUBLIC_CLERK_PUBLISHABLE_KEY } from '$env/static/public';

// Create Clerk instance (Real Estate Clerk project)
export const clerk = new Clerk(PUBLIC_CLERK_PUBLISHABLE_KEY);

// Initialize Clerk SDK
export async function initializeClerk() {
  await clerk.load({
    // Real Estate-specific options
  });

  console.log('✅ Clerk initialized for Real Estate');
}

// (Same helper functions as Bestays)
```

### Authentication State Management

**Shared Auth Store Pattern** (`packages/shared-ui/src/stores/auth.svelte.ts`):

```typescript
/**
 * Shared authentication state management using Svelte 5 runes.
 *
 * This pattern can be used by both products with their own Clerk instances.
 */

import type { User } from '@bestays/shared-api-client';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
}

export function createAuthStore() {
  let state = $state<AuthState>({
    user: null,
    isLoading: false,
    error: null,
  });

  return {
    get user() {
      return state.user;
    },
    get isLoading() {
      return state.isLoading;
    },
    get error() {
      return state.error;
    },
    get isSignedIn() {
      return state.user !== null;
    },
    get isAdmin() {
      return state.user?.role === 'admin';
    },
    get isAgent() {
      return state.user?.role === 'agent';
    },

    async fetchUser(apiClient: any) {
      state.isLoading = true;
      state.error = null;

      try {
        const user = await apiClient.users.me();
        state.user = user;
      } catch (error: any) {
        state.error = error.message;
        state.user = null;
      } finally {
        state.isLoading = false;
      }
    },

    clearUser() {
      state.user = null;
      state.error = null;
    },
  };
}
```

**Product-Specific Auth Store** (`apps/bestays-web/src/lib/stores/auth.svelte.ts`):

```typescript
import { createAuthStore } from '@bestays/shared-ui/stores';
import { apiClient } from '$lib/api';

// Create Bestays-specific auth store
export const authStore = createAuthStore();

// Initialize after Clerk authentication
export async function initializeAuth() {
  await authStore.fetchUser(apiClient);
}
```

### Role-Based Access Control (UI)

**Shared RBAC Utilities** (`packages/shared-ui/src/utils/rbac.ts`):

```typescript
import type { User } from '@bestays/shared-api-client';

export function hasRole(user: User | null, ...allowedRoles: string[]): boolean {
  if (!user) return false;
  return allowedRoles.includes(user.role);
}

export function isAdmin(user: User | null): boolean {
  return hasRole(user, 'admin');
}

export function isAgent(user: User | null): boolean {
  return hasRole(user, 'agent', 'admin');
}

export function isUser(user: User | null): boolean {
  return user !== null;
}
```

**Usage in Components:**

```svelte
<script lang="ts">
  import { authStore } from '$lib/stores/auth.svelte';
  import { isAdmin } from '@bestays/shared-ui/utils/rbac';
</script>

{#if isAdmin(authStore.user)}
  <!-- Admin-only UI -->
  <a href="/admin/dashboard">Admin Dashboard</a>
{/if}
```

---

## API Integration

### Shared API Client

**API Client Base** (`packages/shared-api-client/src/client.ts`):

```typescript
import type { ProductConfig } from '@bestays/shared-config';
import type { APIError } from './types';

export interface APIClientOptions {
  baseUrl: string;
  timeout: number;
  getToken?: () => Promise<string | null>;
}

export class APIClient {
  private baseUrl: string;
  private timeout: number;
  private getToken?: () => Promise<string | null>;

  constructor(options: APIClientOptions) {
    this.baseUrl = options.baseUrl;
    this.timeout = options.timeout;
    this.getToken = options.getToken;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    // Get Clerk token if available
    const token = this.getToken ? await this.getToken() : null;

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal,
      });

      if (!response.ok) {
        const error: APIError = await response.json();
        throw new Error(error.error.message);
      }

      return await response.json();
    } catch (error: any) {
      if (error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      throw error;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async patch<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}
```

### API Endpoints

**User Endpoints** (`packages/shared-api-client/src/endpoints/users.ts`):

```typescript
import type { APIClient } from '../client';
import type { User, UserUpdate } from '../types';

export function createUsersEndpoints(client: APIClient) {
  return {
    /**
     * Get current authenticated user
     */
    me: () => client.get<User>('/api/v1/users/me'),

    /**
     * List all users (admin only)
     */
    list: () => client.get<User[]>('/api/v1/users'),

    /**
     * Update current user
     */
    update: (data: UserUpdate) =>
      client.patch<User>('/api/v1/users/me', data),
  };
}
```

**Chat Endpoints** (`packages/shared-api-client/src/endpoints/chat.ts`):

```typescript
import type { APIClient } from '../client';
import type { ChatRequest, ChatResponse } from '../types';

export function createChatEndpoints(client: APIClient) {
  return {
    /**
     * Send chat message
     */
    sendMessage: (request: ChatRequest) =>
      client.post<ChatResponse>('/api/v1/llm/chat', request),

    /**
     * Get conversation history
     */
    getConversation: (conversationId: number) =>
      client.get<any>(`/api/v1/llm/conversations/${conversationId}`),
  };
}
```

**FAQ Endpoints** (`packages/shared-api-client/src/endpoints/faq.ts`):

```typescript
import type { APIClient } from '../client';
import type { FAQDocument, FAQSearchRequest, FAQSearchResponse } from '../types';

export function createFaqEndpoints(client: APIClient) {
  return {
    /**
     * Search FAQ documents
     */
    search: (query: string) =>
      client.get<FAQSearchResponse>(`/api/v1/faq/search?query=${encodeURIComponent(query)}`),

    /**
     * List all FAQ documents
     */
    list: () => client.get<FAQDocument[]>('/api/v1/faq/documents'),

    /**
     * Get FAQ document by ID
     */
    get: (id: string) =>
      client.get<FAQDocument>(`/api/v1/faq/documents/${id}`),
  };
}
```

### Product-Specific API Client Instance

**Bestays API Client** (`apps/bestays-web/src/lib/api.ts`):

```typescript
import { APIClient } from '@bestays/shared-api-client';
import { createUsersEndpoints } from '@bestays/shared-api-client/endpoints/users';
import { createChatEndpoints } from '@bestays/shared-api-client/endpoints/chat';
import { createFaqEndpoints } from '@bestays/shared-api-client/endpoints/faq';
import { getClerkToken } from '$lib/clerk';
import { config } from '$lib/config';

// Create API client with Bestays configuration
const client = new APIClient({
  baseUrl: config.api.baseUrl,
  timeout: config.api.timeout,
  getToken: getClerkToken,
});

// Export API client with all endpoints
export const apiClient = {
  users: createUsersEndpoints(client),
  chat: createChatEndpoints(client),
  faq: createFaqEndpoints(client),
};
```

**Real Estate API Client** (`apps/realestate-web/src/lib/api.ts`):

```typescript
// Same pattern as Bestays, just different config
import { APIClient } from '@bestays/shared-api-client';
import { createUsersEndpoints } from '@bestays/shared-api-client/endpoints/users';
import { createChatEndpoints } from '@bestays/shared-api-client/endpoints/chat';
import { createFaqEndpoints } from '@bestays/shared-api-client/endpoints/faq';
import { getClerkToken } from '$lib/clerk';
import { config } from '$lib/config';

const client = new APIClient({
  baseUrl: config.api.baseUrl,  // http://localhost:8102
  timeout: config.api.timeout,
  getToken: getClerkToken,
});

export const apiClient = {
  users: createUsersEndpoints(client),
  chat: createChatEndpoints(client),
  faq: createFaqEndpoints(client),
};
```

### TypeScript Types from Backend

**API Types** (`packages/shared-api-client/src/types.ts`):

```typescript
/**
 * Types matching backend Pydantic schemas.
 *
 * These should be kept in sync with backend schemas:
 * - shared_db.models
 * - shared_chat.schemas
 * - shared_faq.schemas
 */

// User types (from shared_db.models.User)
export interface User {
  id: number;
  clerk_user_id: string;
  email: string;
  role: 'user' | 'agent' | 'admin';
  created_at: string;
  updated_at: string;
}

export interface UserUpdate {
  email?: string;
}

// Chat types (from shared_chat.schemas)
export interface ChatRequest {
  content: string;
  session_id?: string;
}

export interface ChatResponse {
  message: Message;
  model: string;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  finish_reason: string;
  conversation_id: number;
  session_id: string;
}

export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

// FAQ types (from shared_faq.schemas)
export interface FAQDocument {
  id: string;
  question: string;
  answer: string;
  category_id: string | null;
  status: 'draft' | 'published' | 'archived';
  view_count: number;
  helpful_count: number;
  created_at: string;
  updated_at: string;
}

export interface FAQSearchResponse {
  results: FAQDocument[];
  query: string;
  total: number;
}

// API Error types (from shared_core.exceptions.APIException)
export interface APIError {
  error: {
    code: string;
    message: string;
    product: string;
    timestamp: string;
    path: string;
  };
}
```

---

## Feature Extraction Plan

### Chat UI Extraction

**Current Location:** `apps/frontend/src/lib/components/chat/`

**Target Location:** `packages/shared-chat-ui/`

**Extraction Strategy:**

**ChatInterface Component** (`packages/shared-chat-ui/src/components/ChatInterface.svelte`):

```svelte
<script lang="ts">
  import type { ProductConfig } from '@bestays/shared-config';
  import { MessageList } from './MessageList.svelte';
  import { MessageInput } from './MessageInput.svelte';
  import { chatStore } from '../stores/chat.svelte';

  interface Props {
    config: ProductConfig;  // Product-specific configuration
  }

  let { config }: Props = $props();

  // Product-specific branding via CSS variables
  const style = `
    --chat-primary: ${config.branding.primaryColor};
    --chat-secondary: ${config.branding.secondaryColor};
  `;
</script>

<div class="chat-interface" style={style}>
  <header class="chat-header">
    <h2>{config.product.name} Assistant</h2>
  </header>

  <MessageList messages={chatStore.messages} />

  <MessageInput
    onSend={(content) => chatStore.sendMessage(content)}
    disabled={chatStore.isLoading}
    guestLimit={config.chat?.guestMessagesLimit}
  />
</div>

<style>
  .chat-interface {
    background: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    display: flex;
    flex-direction: column;
    height: 600px;
  }

  .chat-header {
    background: var(--chat-primary);
    color: white;
    padding: var(--spacing-md);
  }
</style>
```

**Chat Store** (`packages/shared-chat-ui/src/stores/chat.svelte.ts`):

```typescript
import type { Message, ChatResponse } from '@bestays/shared-api-client';

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sessionId: string | null;
  conversationId: number | null;
}

export function createChatStore(apiClient: any) {
  let state = $state<ChatState>({
    messages: [],
    isLoading: false,
    error: null,
    sessionId: null,
    conversationId: null,
  });

  return {
    get messages() {
      return state.messages;
    },
    get isLoading() {
      return state.isLoading;
    },
    get error() {
      return state.error;
    },

    async sendMessage(content: string) {
      // Add user message optimistically
      state.messages.push({ role: 'user', content });
      state.isLoading = true;
      state.error = null;

      try {
        const response = await apiClient.chat.sendMessage({
          content,
          session_id: state.sessionId,
        });

        // Add assistant message
        state.messages.push(response.message);
        state.sessionId = response.session_id;
        state.conversationId = response.conversation_id;
      } catch (error: any) {
        state.error = error.message;
      } finally {
        state.isLoading = false;
      }
    },

    clearMessages() {
      state.messages = [];
      state.sessionId = null;
      state.conversationId = null;
    },
  };
}
```

**Product-Specific Usage:**

```svelte
<!-- apps/bestays-web/src/routes/+page.svelte -->
<script lang="ts">
  import { ChatInterface } from '@bestays/shared-chat-ui';
  import { config } from '$lib/config';
  import { apiClient } from '$lib/api';
  import { createChatStore } from '@bestays/shared-chat-ui/stores';

  const chatStore = createChatStore(apiClient);
</script>

{#if config.features.chatEnabled}
  <ChatInterface {config} />
{/if}
```

**Parameterization Summary:**

| Element | Shared | Product-Specific | How |
|---------|--------|------------------|-----|
| **UI Components** | ✅ Yes | ❌ No | Shared Svelte components |
| **Branding** | ❌ No | ✅ Yes | Passed via ProductConfig (colors, logo) |
| **API Client** | ❌ No | ✅ Yes | Injected via createChatStore(apiClient) |
| **Feature Flags** | ❌ No | ✅ Yes | config.features.chatEnabled |
| **Guest Limits** | ❌ No | ✅ Yes | config.chat.guestMessagesLimit |

### FAQ UI Extraction

**Current Location:** `apps/frontend/src/lib/components/faq/` (if exists)

**Target Location:** `packages/shared-faq-ui/`

**Extraction Strategy:**

**FAQSearch Component** (`packages/shared-faq-ui/src/components/FAQSearch.svelte`):

```svelte
<script lang="ts">
  import type { ProductConfig } from '@bestays/shared-config';
  import type { FAQDocument } from '@bestays/shared-api-client';
  import { Input, Button } from '@bestays/shared-ui';
  import { FAQList } from './FAQList.svelte';

  interface Props {
    config: ProductConfig;
    apiClient: any;
  }

  let { config, apiClient }: Props = $props();

  let query = $state('');
  let results = $state<FAQDocument[]>([]);
  let isLoading = $state(false);

  async function search() {
    if (!query.trim()) return;

    isLoading = true;
    try {
      const response = await apiClient.faq.search(query);
      results = response.results;
    } catch (error) {
      console.error('FAQ search failed:', error);
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="faq-search">
  <h2>Frequently Asked Questions</h2>

  <div class="search-bar">
    <Input
      bind:value={query}
      placeholder="Search FAQs..."
      onKeyPress={(e) => e.key === 'Enter' && search()}
    />
    <Button onclick={search} loading={isLoading}>Search</Button>
  </div>

  {#if results.length > 0}
    <FAQList documents={results} />
  {:else if query}
    <p class="no-results">No results found for "{query}"</p>
  {/if}
</div>

<style>
  .faq-search {
    max-width: 800px;
    margin: 0 auto;
    padding: var(--spacing-lg);
  }

  .search-bar {
    display: flex;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-lg);
  }

  .no-results {
    color: var(--color-muted);
    text-align: center;
    padding: var(--spacing-xl);
  }
</style>
```

**Product-Specific Usage:**

```svelte
<!-- apps/bestays-web/src/routes/faq/+page.svelte -->
<script lang="ts">
  import { FAQSearch } from '@bestays/shared-faq-ui';
  import { config } from '$lib/config';
  import { apiClient } from '$lib/api';
</script>

<FAQSearch {config} {apiClient} />
```

### Shared UI Components Extraction

**Button Component** (`packages/shared-ui/src/components/Button.svelte`):

```svelte
<script lang="ts">
  import { cn } from '../utils/cn';

  interface Props {
    variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
    loading?: boolean;
    disabled?: boolean;
    onclick?: () => void;
    children: any;
  }

  let {
    variant = 'primary',
    size = 'md',
    loading = false,
    disabled = false,
    onclick,
    children,
  }: Props = $props();

  const baseClasses = 'rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2';

  const variantClasses = {
    primary: 'bg-primary text-white hover:bg-primary/90 focus:ring-primary',
    secondary: 'bg-secondary text-white hover:bg-secondary/90 focus:ring-secondary',
    outline: 'border border-border bg-background hover:bg-muted',
    ghost: 'hover:bg-muted',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
</script>

<button
  class={cn(
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    (disabled || loading) && 'opacity-50 cursor-not-allowed'
  )}
  {disabled}
  {onclick}
>
  {#if loading}
    <span class="loader"></span>
  {/if}
  {@render children()}
</button>

<style>
  .loader {
    display: inline-block;
    width: 1em;
    height: 1em;
    border: 2px solid currentColor;
    border-right-color: transparent;
    border-radius: 50%;
    animation: spin 0.75s linear infinite;
    margin-right: 0.5em;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
```

**Card Component** (`packages/shared-ui/src/components/Card.svelte`):

```svelte
<script lang="ts">
  import { cn } from '../utils/cn';

  interface Props {
    hover?: boolean;
    children: any;
  }

  let { hover = false, children }: Props = $props();
</script>

<div
  class={cn(
    'rounded-lg border border-border bg-background p-6',
    hover && 'transition-shadow hover:shadow-md'
  )}
>
  {@render children()}
</div>
```

---

## Build Configuration

### SvelteKit Configuration Per Product

**Bestays SvelteKit Config** (`apps/bestays-web/svelte.config.js`):

```javascript
import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),

  kit: {
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      fallback: 'index.html',
      precompress: false,
      strict: true,
    }),

    // Path aliases
    alias: {
      '@bestays/shared-ui': '../../packages/shared-ui/src',
      '@bestays/shared-api-client': '../../packages/shared-api-client/src',
      '@bestays/shared-chat-ui': '../../packages/shared-chat-ui/src',
      '@bestays/shared-faq-ui': '../../packages/shared-faq-ui/src',
      '@bestays/shared-config': '../../packages/shared-config/src',
    },
  },
};

export default config;
```

**Real Estate SvelteKit Config** (`apps/realestate-web/svelte.config.js`):

```javascript
// Same structure as Bestays
import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),

  kit: {
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      fallback: 'index.html',
      precompress: false,
      strict: true,
    }),

    alias: {
      '@bestays/shared-ui': '../../packages/shared-ui/src',
      '@bestays/shared-api-client': '../../packages/shared-api-client/src',
      '@bestays/shared-chat-ui': '../../packages/shared-chat-ui/src',
      '@bestays/shared-faq-ui': '../../packages/shared-faq-ui/src',
      '@bestays/shared-config': '../../packages/shared-config/src',
    },
  },
};

export default config;
```

### Vite Configuration

**Bestays Vite Config** (`apps/bestays-web/vite.config.ts`):

```typescript
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],

  server: {
    port: 5273,  // Bestays dev port
    proxy: {
      '/api': {
        target: 'http://localhost:8101',  // Bestays backend
        changeOrigin: true,
      },
    },
  },

  build: {
    target: 'esnext',
    sourcemap: true,
    minify: 'esbuild',
  },

  optimizeDeps: {
    include: [
      '@clerk/clerk-js',
      '@bestays/shared-ui',
      '@bestays/shared-api-client',
      '@bestays/shared-chat-ui',
      '@bestays/shared-faq-ui',
    ],
  },
});
```

**Real Estate Vite Config** (`apps/realestate-web/vite.config.ts`):

```typescript
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],

  server: {
    port: 5274,  // Real Estate dev port
    proxy: {
      '/api': {
        target: 'http://localhost:8102',  // Real Estate backend
        changeOrigin: true,
      },
    },
  },

  build: {
    target: 'esnext',
    sourcemap: true,
    minify: 'esbuild',
  },

  optimizeDeps: {
    include: [
      '@clerk/clerk-js',
      '@bestays/shared-ui',
      '@bestays/shared-api-client',
      '@bestays/shared-chat-ui',
      '@bestays/shared-faq-ui',
    ],
  },
});
```

### pnpm Workspaces Configuration

**Root pnpm Workspace** (`pnpm-workspace.yaml`):

```yaml
packages:
  - 'packages/*'
  - 'apps/*'
```

**Root package.json:**

```json
{
  "name": "bestays-monorepo",
  "private": true,
  "scripts": {
    "dev:bestays": "pnpm --filter bestays-web dev",
    "dev:realestate": "pnpm --filter realestate-web dev",
    "dev:all": "pnpm --parallel --filter bestays-web --filter realestate-web dev",
    "build:bestays": "pnpm --filter bestays-web build",
    "build:realestate": "pnpm --filter realestate-web build",
    "build:all": "pnpm --parallel --filter bestays-web --filter realestate-web build",
    "preview:bestays": "pnpm --filter bestays-web preview",
    "preview:realestate": "pnpm --filter realestate-web preview",
    "lint": "pnpm --parallel --filter \"./apps/*\" --filter \"./packages/*\" lint",
    "type-check": "pnpm --parallel --filter \"./apps/*\" --filter \"./packages/*\" type-check"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "typescript": "^5.3.0"
  }
}
```

---

## Testing Strategy

### Unit Tests (Vitest)

**Shared Component Tests** (`packages/shared-ui/tests/Button.test.ts`):

```typescript
import { describe, it, expect } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import Button from '../src/components/Button.svelte';

describe('Button', () => {
  it('renders with text', () => {
    const { getByText } = render(Button, {
      props: { children: 'Click me' },
    });

    expect(getByText('Click me')).toBeInTheDocument();
  });

  it('calls onclick when clicked', async () => {
    let clicked = false;
    const { getByRole } = render(Button, {
      props: {
        onclick: () => { clicked = true; },
        children: 'Click me',
      },
    });

    await fireEvent.click(getByRole('button'));
    expect(clicked).toBe(true);
  });

  it('is disabled when loading', () => {
    const { getByRole } = render(Button, {
      props: { loading: true, children: 'Click me' },
    });

    expect(getByRole('button')).toBeDisabled();
  });
});
```

**API Client Tests** (`packages/shared-api-client/tests/client.test.ts`):

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { APIClient } from '../src/client';

describe('APIClient', () => {
  let client: APIClient;

  beforeEach(() => {
    client = new APIClient({
      baseUrl: 'http://localhost:8101',
      timeout: 5000,
    });
  });

  it('makes GET request', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ id: 1, name: 'Test' }),
    });

    const result = await client.get('/api/v1/users/1');
    expect(result).toEqual({ id: 1, name: 'Test' });
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8101/api/v1/users/1',
      expect.objectContaining({ method: 'GET' })
    );
  });

  it('adds Authorization header when token is provided', async () => {
    const clientWithToken = new APIClient({
      baseUrl: 'http://localhost:8101',
      timeout: 5000,
      getToken: async () => 'test-token',
    });

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({}),
    });

    await clientWithToken.get('/api/v1/users/me');

    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer test-token',
        }),
      })
    );
  });

  it('throws error on non-OK response', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        error: {
          code: 'NOT_FOUND',
          message: 'User not found',
        },
      }),
    });

    await expect(client.get('/api/v1/users/999')).rejects.toThrow('User not found');
  });
});
```

### Integration Tests

**Chat Integration Test** (`apps/bestays-web/tests/integration/chat.test.ts`):

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { render, waitFor, fireEvent } from '@testing-library/svelte';
import ChatInterface from '@bestays/shared-chat-ui/components/ChatInterface.svelte';
import { config } from '$lib/config';

describe('Chat Integration', () => {
  beforeEach(() => {
    // Mock API client
    global.fetch = vi.fn();
  });

  it('sends message and displays response', async () => {
    // Mock successful chat response
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        message: {
          role: 'assistant',
          content: 'Hello! How can I help you?',
        },
        session_id: 'test-session',
        conversation_id: 1,
      }),
    });

    const { getByPlaceholderText, getByText, getByRole } = render(ChatInterface, {
      props: { config },
    });

    // Type message
    const input = getByPlaceholderText('Type a message...');
    await fireEvent.input(input, { target: { value: 'Hello' } });

    // Send message
    const sendButton = getByRole('button', { name: /send/i });
    await fireEvent.click(sendButton);

    // Wait for response
    await waitFor(() => {
      expect(getByText('Hello! How can I help you?')).toBeInTheDocument();
    });
  });
});
```

### E2E Tests (Playwright)

**Bestays Authentication E2E** (`apps/bestays-web/tests/e2e/auth.spec.ts`):

```typescript
import { test, expect } from '@playwright/test';

test.describe('Bestays Authentication', () => {
  test('user can sign in', async ({ page }) => {
    await page.goto('http://localhost:5273');

    // Click sign in button
    await page.click('text=Sign In');

    // Fill Clerk form (Bestays credentials)
    await page.fill('input[name="email"]', 'user.claudecode@bestays.app');
    await page.fill('input[name="password"]', '9kB*k926O8):');
    await page.click('button:has-text("Sign In")');

    // Verify redirect to dashboard
    await expect(page).toHaveURL('http://localhost:5273/dashboard');
    await expect(page.locator('text=Welcome to Bestays')).toBeVisible();
  });

  test('admin can access admin panel', async ({ page }) => {
    // Login as admin
    await page.goto('http://localhost:5273');
    await page.click('text=Sign In');
    await page.fill('input[name="email"]', 'admin.claudecode@bestays.app');
    await page.fill('input[name="password"]', 'rHe/997?lo&l');
    await page.click('button:has-text("Sign In")');

    // Navigate to admin panel
    await page.click('text=Admin');
    await expect(page).toHaveURL('http://localhost:5273/admin');
    await expect(page.locator('text=Admin Dashboard')).toBeVisible();
  });
});
```

**Real Estate Chat E2E** (`apps/realestate-web/tests/e2e/chat.spec.ts`):

```typescript
import { test, expect } from '@playwright/test';

test.describe('Real Estate Chat', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('http://localhost:5274');
    await page.click('text=Sign In');
    await page.fill('input[name="email"]', 'user.claudecode@realestate.dev');
    await page.fill('input[name="password"]', 'y>1T_)5h!X1X');
    await page.click('button:has-text("Sign In")');
  });

  test('user can send chat message', async ({ page }) => {
    // Open chat
    await page.click('[data-testid="chat-toggle"]');

    // Send message
    await page.fill('[data-testid="chat-input"]', 'What are property taxes in Thailand?');
    await page.click('[data-testid="chat-send"]');

    // Verify response (contains Real Estate FAQ content)
    await expect(page.locator('[data-testid="chat-message"]').last()).toContainText('Property taxes');
  });
});
```

### Visual Regression Tests

**Component Visual Tests** (`packages/shared-ui/tests/visual/Button.spec.ts`):

```typescript
import { test, expect } from '@playwright/test';

test.describe('Button Visual Tests', () => {
  test('primary button', async ({ page }) => {
    await page.goto('http://localhost:6006/iframe.html?id=button--primary');
    await expect(page).toHaveScreenshot('button-primary.png');
  });

  test('secondary button', async ({ page }) => {
    await page.goto('http://localhost:6006/iframe.html?id=button--secondary');
    await expect(page).toHaveScreenshot('button-secondary.png');
  });

  test('loading button', async ({ page }) => {
    await page.goto('http://localhost:6006/iframe.html?id=button--loading');
    await expect(page).toHaveScreenshot('button-loading.png');
  });
});
```

---

## Docker Deployment

### Dockerfile Per Product

**Bestays Frontend Dockerfile** (`docker/bestays-web/Dockerfile.prod`):

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages packages/
COPY apps/bestays-web apps/bestays-web/

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build application
WORKDIR /app/apps/bestays-web
RUN pnpm run build

# Stage 2: Runtime
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/apps/bestays-web/build /usr/share/nginx/html

# Copy nginx configuration
COPY docker/bestays-web/nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**Nginx Configuration** (`docker/bestays-web/nginx.conf`):

```nginx
events {
  worker_connections 1024;
}

http {
  include /etc/nginx/mime.types;
  default_type application/octet-stream;

  server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # SPA fallback
    location / {
      try_files $uri $uri/ /index.html;
    }

    # API proxy (development only)
    location /api {
      proxy_pass http://bestays-api:8000;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
      expires 1y;
      add_header Cache-Control "public, immutable";
    }
  }
}
```

### Docker Compose Development

**Development Compose** (`docker-compose.dev.yml`):

```yaml
services:
  # (Backend services from TASK-003...)

  # Bestays Frontend
  bestays-web:
    build:
      context: .
      dockerfile: docker/bestays-web/Dockerfile.dev
    container_name: bestays-web-dev
    environment:
      VITE_PRODUCT_ID: bestays
      VITE_APP_NAME: Bestays
      VITE_API_URL: http://localhost:8101
      PUBLIC_CLERK_PUBLISHABLE_KEY: pk_test_c2FjcmVkLW1heWZseS01NS5jbGVyay5hY2NvdW50cy5kZXYk
      VITE_CHAT_ENABLED: true
      VITE_FAQ_ENABLED: true
    ports:
      - "5273:5173"
    volumes:
      - ./apps/bestays-web:/app/apps/bestays-web:delegated
      - ./packages:/app/packages:delegated
    depends_on:
      - bestays-api
    networks:
      - bestays-network
    command: pnpm run dev --host 0.0.0.0

  # Real Estate Frontend
  realestate-web:
    build:
      context: .
      dockerfile: docker/realestate-web/Dockerfile.dev
    container_name: realestate-web-dev
    environment:
      VITE_PRODUCT_ID: realestate
      VITE_APP_NAME: Best Real Estate
      VITE_API_URL: http://localhost:8102
      PUBLIC_CLERK_PUBLISHABLE_KEY: pk_test_cGxlYXNhbnQtZ251LTI1LmNsZXJrLmFjY291bnRzLmRldiQ
      VITE_CHAT_ENABLED: true
      VITE_FAQ_ENABLED: true
    ports:
      - "5274:5173"
    volumes:
      - ./apps/realestate-web:/app/apps/realestate-web:delegated
      - ./packages:/app/packages:delegated
    depends_on:
      - realestate-api
    networks:
      - bestays-network
    command: pnpm run dev --host 0.0.0.0

networks:
  bestays-network:
    driver: bridge
```

---

## Migration from Current State

### 6-Week Phased Migration Plan

**Phase 1: Setup Monorepo (Week 1)**

**Tasks:**
1. Create `packages/` directory structure
2. Set up `pnpm-workspace.yaml`
3. Create base packages: `shared-ui`, `shared-api-client`, `shared-config`
4. Set up TypeScript base configuration
5. Configure path aliases

**Validation:**
- Directory structure created
- `pnpm install` works
- TypeScript compilation succeeds

**Risk:** LOW - Just creating structure

---

**Phase 2: Extract Shared UI Components (Week 2)**

**Tasks:**
1. Extract basic UI components to `shared-ui`:
   - Button, Card, Input, Modal, Avatar
2. Extract CSS variables and base styles
3. Create Tailwind preset
4. Install `shared-ui` in existing frontend
5. Update imports in existing frontend

**Validation:**
- All components work in existing frontend
- No visual regressions
- Existing tests pass

**Risk:** MEDIUM - Breaking existing UI

**Rollback:** Revert shared-ui extraction

---

**Phase 3: Extract API Client (Week 2-3)**

**Tasks:**
1. Create `shared-api-client` package
2. Extract API client base class
3. Extract endpoint functions (users, properties)
4. Create TypeScript types from backend schemas
5. Test API client with existing backend

**Validation:**
- API client works with existing backend
- All API calls succeed
- TypeScript types match backend

**Risk:** MEDIUM - Breaking API integration

**Rollback:** Revert to old API service

---

**Phase 4: Create Bestays App (Week 3-4)**

**Tasks:**
1. Copy `apps/frontend/` to `apps/bestays-web/`
2. Update imports to use shared packages
3. Create Bestays-specific configuration
4. Update environment variables
5. Test Bestays app

**Validation:**
- Bestays app starts successfully
- All features work (chat, FAQ, auth)
- Visual appearance matches existing

**Risk:** LOW - Just copying existing app

---

**Phase 5: Extract Feature UIs (Week 4-5)**

**Tasks:**
1. Create `shared-chat-ui` package
2. Extract chat components with parameterization
3. Create `shared-faq-ui` package
4. Extract FAQ components
5. Update Bestays app to use shared features

**Validation:**
- Chat works in Bestays
- FAQ works in Bestays
- No feature regressions

**Risk:** HIGH - Complex state management

**Rollback:** Keep features in app, revert extraction

---

**Phase 6: Create Real Estate App (Week 5-6)**

**Tasks:**
1. Copy `apps/bestays-web/` to `apps/realestate-web/`
2. Update configuration (product ID, Clerk keys, branding)
3. Update environment variables
4. Customize theming (CSS variables, colors)
5. Test Real Estate app

**Validation:**
- Real Estate app starts successfully
- Separate Clerk authentication works
- Different branding visible
- Chat returns Real Estate FAQ content

**Risk:** MEDIUM - First time creating second product

**Rollback:** Delete Real Estate app

---

**Phase 7: Validation & Documentation (Week 6)**

**Tasks:**
1. E2E tests for both products (Playwright)
2. Performance testing (Lighthouse)
3. Accessibility audit (axe-core)
4. Update documentation (READMEs, architecture diagrams)
5. Final validation checklist

**Validation:**
- All E2E tests pass
- Performance scores ≥90 (Lighthouse)
- Accessibility score 100 (axe)
- Documentation complete

**Risk:** LOW - Validation only

---

## Trade-offs and Risks

### Pros of Recommended Approach

**Simplicity:**
- ✅ **pnpm workspaces** - Standard JavaScript monorepo, no complex tooling
- ✅ **CSS variables** - Runtime theming without rebuilding
- ✅ **Environment-based config** - Clear `.env` files per product
- ✅ **SvelteKit conventions** - Standard file structure, familiar patterns

**Modularity:**
- ✅ **Clear package boundaries** - Shared UI, API client, feature UIs
- ✅ **Reusable components** - Both products use same components
- ✅ **Type safety** - TypeScript throughout, interfaces from backend
- ✅ **One-way dependencies** - Shared → apps, never reverse

**Performance:**
- ✅ **Vite HMR** - Fast development feedback
- ✅ **Static builds** - Pre-rendered HTML, fast load times
- ✅ **Code splitting** - SvelteKit automatic route-based splitting
- ✅ **Optimized bundles** - Tree-shaking, minification

**Developer Experience:**
- ✅ **Single command setup** - `pnpm install`
- ✅ **Hot reload** - Vite HMR across all packages
- ✅ **Type checking** - TypeScript catches errors early
- ✅ **Debugging** - Source maps in development

### Cons of Recommended Approach

**Package Management:**
- ❌ **Manual workspace setup** - Need to configure pnpm workspaces
  - **Mitigation:** Clear documentation, example configs
- ❌ **Path alias complexity** - Multiple alias configurations
  - **Mitigation:** Shared TypeScript base config

**Theming:**
- ❌ **CSS variable limitations** - No type safety for colors
  - **Mitigation:** TypeScript config validates theme configuration
- ❌ **Manual theme sync** - Must update CSS variables AND Tailwind config
  - **Mitigation:** Single source of truth (CSS variables), Tailwind references them

**Testing:**
- ❌ **E2E test duplication** - Similar tests for both products
  - **Mitigation:** Shared test utilities, parameterized tests
- ❌ **Visual regression setup** - Requires Playwright + screenshot storage
  - **Mitigation:** Use Percy or Chromatic for cloud-based VRT

### When to Revisit This Decision

**Scenario 1: More Than 5 Products**

If the platform grows to 10+ products:
- Consider shared runtime theme switcher (single build, multiple themes)
- Consider feature flags instead of separate apps
- Consider micro-frontends architecture

**Scenario 2: Complex Design System**

If design needs exceed CSS variables:
- Consider styled-components or CSS-in-JS
- Consider design tokens with style-dictionary
- Consider separate theme packages per product

**Scenario 3: Large Team**

If team grows to 20+ frontend developers:
- Consider Turborepo for build caching
- Consider Nx for better monorepo tooling
- Consider separate repositories per product

---

## Next Steps for Synthesis (TASK-005)

**What Synthesis Needs from This Frontend Design:**

### 1. Integration Points with Backend

**API Routes (Same for Both Products):**
```
GET  /api/v1/users
GET  /api/v1/users/me
GET  /api/v1/properties
POST /api/v1/llm/chat
GET  /api/v1/faq/search
```

**TypeScript Types Match Backend:**
- `User` interface → `shared_db.models.User`
- `ChatResponse` interface → `shared_chat.schemas.ChatResponse`
- `FAQDocument` interface → `shared_faq.schemas.FAQDocument`

**Environment Coordination:**
- Frontend `VITE_API_URL` → Backend port (8101 or 8102)
- Frontend `PUBLIC_CLERK_PUBLISHABLE_KEY` → Backend `CLERK_SECRET_KEY` (same Clerk project)

### 2. Deployment Coordination

**Docker Compose Orchestration:**
```yaml
services:
  # Backend services (from TASK-003)
  bestays-api: (port 8101)
  realestate-api: (port 8102)

  # Frontend services (from TASK-004)
  bestays-web: (port 5273)
  realestate-web: (port 5274)

  # Shared services
  postgres: (port 5432)
  redis: (port 6379)
```

**Nginx Reverse Proxy (Production):**
```
bestays.com → bestays-web:80
api.bestays.com → bestays-api:8000

realestate.com → realestate-web:80
api.realestate.com → realestate-api:8000
```

### 3. Testing Coordination

**E2E Testing Strategy:**
1. Start all services via Docker Compose
2. Run Playwright tests against running services
3. Test both products independently
4. Test cross-product isolation (no data leakage)

**Test Data Coordination:**
- Backend seeds test users in both databases
- Frontend uses same test credentials from Clerk
- E2E tests verify correct product-specific content

### 4. Key Recommendations for TASK-005

**Monorepo Structure:**
```
bestays-monorepo/
├── packages/         # Shared packages (backend + frontend)
├── apps/            # Product apps (backend + frontend)
├── docker/          # Dockerfiles per product per tier
├── docker-compose.dev.yml
├── docker-compose.prod.yml
└── pnpm-workspace.yaml (frontend) + Python packages (backend)
```

**Mixed Monorepo (Python + JavaScript):**
- Python packages: `packages/shared-db`, `packages/shared-chat` (backend)
- JavaScript packages: `packages/shared-ui`, `packages/shared-api-client` (frontend)
- Separate dependency management (pip + pnpm)

---

## Conclusion

**Recommended Approach: SvelteKit Monorepo with Shared Components**

**Why This Approach:**
1. ✅ **Simplest** - Standard pnpm workspaces, SvelteKit conventions, no complex tooling
2. ✅ **Most Modular** - Clear package boundaries, reusable components, one-way dependencies
3. ✅ **Best Documented** - Environment variables, TypeScript types, clear configuration
4. ✅ **Most Performant** - Vite HMR, static builds, automatic code splitting

**Alignment with User Priorities:**
- ✅ **Simplicity for deployment** - Docker Compose orchestration, static builds
- ✅ **Simplicity for development** - `pnpm install`, Vite HMR, hot reload
- ✅ **Modular architecture** - Shared packages, product-specific apps
- ✅ **Clear documentation** - Environment-based configuration, TypeScript interfaces

**Confidence Level: HIGH** - This approach uses proven SvelteKit patterns, standard pnpm workspaces, and maintains simplicity throughout.

**Next Agent (TASK-005):** Synthesis should combine frontend and backend architectures, create unified Docker Compose configuration, and define complete development workflow.

---

**Document Version:** 1.0
**Date:** 2025-11-07
**Agent:** dev-frontend
**Status:** COMPLETE
**Next Task:** TASK-005 (Architecture Synthesis)

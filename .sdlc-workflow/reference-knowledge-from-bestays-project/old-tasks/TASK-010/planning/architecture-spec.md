# Architecture Specification: US-021 Thai Localization

**Task:** TASK-010
**Story:** US-021
**Date:** 2025-11-08

This document provides detailed technical specifications for implementing Thai localization.

---

## Database Schema

### Migration Script

**File:** `apps/server/alembic/versions/XXXX_add_locale_to_content_dictionary.py`

```python
"""Add locale column to content_dictionary table

Revision ID: XXXX
Revises: YYYY
Create Date: 2025-11-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers
revision = 'XXXX'
down_revision = 'YYYY'  # Previous migration
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Add locale column (nullable)
    op.add_column(
        'content_dictionary',
        sa.Column('locale', sa.String(2), nullable=True)
    )
    
    # Step 2: Backfill existing rows with 'en'
    connection = op.get_bind()
    connection.execute(
        text("UPDATE content_dictionary SET locale = 'en' WHERE locale IS NULL")
    )
    
    # Step 3: Make locale NOT NULL
    op.alter_column(
        'content_dictionary',
        'locale',
        existing_type=sa.String(2),
        nullable=False
    )
    
    # Step 4: Drop old UNIQUE constraint on key
    op.drop_constraint(
        'content_dictionary_key_key',
        'content_dictionary',
        type_='unique'
    )
    
    # Step 5: Add composite UNIQUE constraint on (key, locale)
    op.create_unique_constraint(
        'content_dictionary_key_locale_unique',
        'content_dictionary',
        ['key', 'locale']
    )
    
    # Step 6: Create index on (key, locale) for query performance
    op.create_index(
        'idx_content_dictionary_key_locale',
        'content_dictionary',
        ['key', 'locale']
    )


def downgrade():
    # Reverse the migration
    op.drop_index('idx_content_dictionary_key_locale', 'content_dictionary')
    op.drop_constraint('content_dictionary_key_locale_unique', 'content_dictionary', type_='unique')
    op.create_unique_constraint('content_dictionary_key_key', 'content_dictionary', ['key'])
    op.drop_column('content_dictionary', 'locale')
```

### Updated Schema

**Table:** `content_dictionary`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Auto-incrementing ID |
| key | String(255) | NOT NULL | Content key (e.g., "hero.title") |
| locale | String(2) | NOT NULL | Locale code ("en" or "th") |
| value | Text | NOT NULL | Content value |
| created_at | DateTime | NOT NULL | Creation timestamp |
| updated_at | DateTime | NOT NULL | Last update timestamp |

**Constraints:**
- UNIQUE(key, locale) - Composite unique constraint
- INDEX(key, locale) - Query performance

**Example Rows:**
```sql
| id | key         | locale | value                   | created_at | updated_at |
|----|-------------|--------|-------------------------|------------|------------|
| 1  | hero.title  | en     | Welcome to Bestays      | ...        | ...        |
| 2  | hero.title  | th     | ยินดีต้อนรับสู่ Bestays | ...        | ...        |
| 3  | hero.subtitle | en   | Find your perfect stay  | ...        | ...        |
| 4  | hero.subtitle | th   | ค้นหาที่พักในฝันของคุณ  | ...        | ...        |
```

---

## Seed Data

### Bestays Thai Translations

**File:** `apps/server/src/server/scripts/seed_thai_content_bestays.py`

```python
"""Seed Thai translations for Bestays product"""

from server.database import SessionLocal
from server.models.content import ContentDictionary
from datetime import datetime

THAI_TRANSLATIONS = {
    # Homepage Hero
    "hero.title": "ยินดีต้อนรับสู่ Bestays",
    "hero.subtitle": "ค้นหาที่พักในฝันของคุณ",
    "hero.cta": "เริ่มค้นหา",
    
    # Features Section
    "features.title": "ทำไมต้องเลือก Bestays",
    "features.search.title": "ค้นหาง่าย",
    "features.search.description": "ค้นหาที่พักที่สมบูรณ์แบบด้วยตัวกรองที่ทรงพลัง",
    "features.booking.title": "การจองที่ปลอดภัย",
    "features.booking.description": "จองด้วยความมั่นใจด้วยระบบชำระเงินที่ปลอดภัย",
    "features.support.title": "การสนับสนุน 24/7",
    "features.support.description": "ทีมของเราพร้อมช่วยเหลือคุณตลอด 24 ชั่วโมง",
    
    # Footer
    "footer.copyright": "© 2025 Bestays สงวนลิขสิทธิ์",
    "footer.about": "เกี่ยวกับเรา",
    "footer.contact": "ติดต่อเรา",
    "footer.privacy": "นโยบายความเป็นส่วนตัว",
    "footer.terms": "ข้อกำหนดการใช้งาน",
}


def seed_thai_content():
    db = SessionLocal()
    try:
        for key, value in THAI_TRANSLATIONS.items():
            # Check if Thai translation already exists
            existing = db.query(ContentDictionary).filter_by(
                key=key,
                locale='th'
            ).first()
            
            if not existing:
                content = ContentDictionary(
                    key=key,
                    locale='th',
                    value=value,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(content)
                print(f"Added Thai translation for: {key}")
            else:
                print(f"Thai translation already exists for: {key}")
        
        db.commit()
        print(f"\nSuccessfully seeded {len(THAI_TRANSLATIONS)} Thai translations for Bestays")
    except Exception as e:
        db.rollback()
        print(f"Error seeding Thai content: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_thai_content()
```

### Real Estate Thai Translations

**File:** `apps/server/src/server/scripts/seed_thai_content_realestate.py`

Similar structure but with real estate-specific translations:
```python
THAI_TRANSLATIONS = {
    "hero.title": "ค้นหาอสังหาริมทรัพย์ในฝันของคุณ",
    "hero.subtitle": "บ้าน คอนโด และที่ดินกว่า 10,000 รายการ",
    # ... product-specific translations
}
```

---

## Backend API

### Updated SQLAlchemy Model

**File:** `apps/server/src/server/models/content.py`

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint, Index
from sqlalchemy.sql import func
from server.database import Base


class ContentDictionary(Base):
    __tablename__ = 'content_dictionary'
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), nullable=False)
    locale = Column(String(2), nullable=False, default='en')
    value = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('key', 'locale', name='content_dictionary_key_locale_unique'),
        Index('idx_content_dictionary_key_locale', 'key', 'locale'),
    )
    
    def __repr__(self):
        return f"<ContentDictionary(key={self.key}, locale={self.locale}, value={self.value[:50]}...)>"
```

### Updated Pydantic Schemas

**File:** `apps/server/src/server/schemas/content.py`

```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Literal


# Locale type
Locale = Literal['en', 'th']


class ContentBase(BaseModel):
    key: str = Field(..., min_length=1, max_length=255)
    locale: Locale = Field(default='en', description="Locale code (en or th)")
    value: str = Field(..., min_length=1)


class ContentCreate(ContentBase):
    pass


class ContentUpdate(BaseModel):
    value: str = Field(..., min_length=1)
    locale: Locale = Field(default='en')


class ContentResponse(ContentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ContentListResponse(BaseModel):
    items: list[ContentResponse]
    total: int
```

### Updated Service Layer

**File:** `apps/server/src/server/services/content_service.py`

```python
from sqlalchemy.orm import Session
from server.models.content import ContentDictionary
from server.schemas.content import ContentCreate, ContentUpdate, Locale
from server.cache import redis_client
from fastapi import HTTPException
import os
import json
from random import randint


# Get product identifier from environment
PRODUCT_NAME = os.getenv("PRODUCT_NAME", "bestays")
CACHE_TTL = 3600  # 1 hour


def _get_cache_key(key: str, locale: str) -> str:
    """Generate cache key with product and locale"""
    return f"content:{PRODUCT_NAME}:{locale}:{key}"


async def get_content(db: Session, key: str, locale: Locale = 'en') -> ContentDictionary:
    """Get content by key and locale with fallback to English"""
    
    # Try cache first
    cache_key = _get_cache_key(key, locale)
    try:
        cached = redis_client.get(cache_key)
        if cached:
            data = json.loads(cached)
            return ContentDictionary(**data)
    except Exception as e:
        # Cache failure - degrade to database
        print(f"Cache error: {e}")
    
    # Try to get content for requested locale
    content = db.query(ContentDictionary).filter_by(
        key=key,
        locale=locale
    ).first()
    
    # Fallback to English if not found and locale is not English
    if not content and locale != 'en':
        content = db.query(ContentDictionary).filter_by(
            key=key,
            locale='en'
        ).first()
    
    if not content:
        raise HTTPException(status_code=404, detail=f"Content not found: {key}")
    
    # Cache the result (with jitter to prevent thundering herd)
    try:
        cache_data = {
            "id": content.id,
            "key": content.key,
            "locale": content.locale,
            "value": content.value,
            "created_at": content.created_at.isoformat(),
            "updated_at": content.updated_at.isoformat()
        }
        ttl_with_jitter = CACHE_TTL + randint(0, 300)
        redis_client.setex(cache_key, ttl_with_jitter, json.dumps(cache_data))
    except Exception as e:
        # Cache failure - continue without caching
        print(f"Cache write error: {e}")
    
    return content


async def update_content(
    db: Session,
    key: str,
    update: ContentUpdate,
    locale: Locale = 'en'
) -> ContentDictionary:
    """Update content and invalidate cache"""
    
    content = db.query(ContentDictionary).filter_by(
        key=key,
        locale=locale
    ).first()
    
    if not content:
        raise HTTPException(status_code=404, detail=f"Content not found: {key}")
    
    # Update content
    content.value = update.value
    db.commit()
    db.refresh(content)
    
    # Invalidate cache (only for this locale)
    cache_key = _get_cache_key(key, locale)
    try:
        redis_client.delete(cache_key)
    except Exception as e:
        print(f"Cache invalidation error: {e}")
    
    return content


async def create_content(db: Session, content: ContentCreate) -> ContentDictionary:
    """Create new content"""
    
    # Check if already exists
    existing = db.query(ContentDictionary).filter_by(
        key=content.key,
        locale=content.locale
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Content already exists")
    
    new_content = ContentDictionary(**content.dict())
    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    
    return new_content
```

### Updated API Endpoint

**File:** `apps/server/src/server/api/v1/endpoints/content.py`

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from server.database import get_db
from server.services import content_service
from server.schemas.content import ContentResponse, ContentUpdate, Locale
from server.api.deps import require_role

router = APIRouter()


@router.get("/{key}", response_model=ContentResponse)
async def get_content(
    key: str,
    locale: Locale = Query('en', description="Locale code (en or th)"),
    db: Session = Depends(get_db)
):
    """
    Get content by key and locale.
    Falls back to English if translation not found.
    """
    return await content_service.get_content(db, key, locale)


@router.put("/{key}", response_model=ContentResponse)
async def update_content(
    key: str,
    update: ContentUpdate,
    db: Session = Depends(get_db),
    user = Depends(require_role(['admin', 'agent']))
):
    """
    Update content (admin/agent only).
    Invalidates cache for the specific locale.
    """
    return await content_service.update_content(db, key, update, update.locale)
```

---

## Frontend Architecture

### i18n Context (Svelte 5 Runes)

**File:** `apps/frontend/src/lib/i18n/context.svelte.ts`

```typescript
import { getContext, setContext } from 'svelte';
import type { Locale } from './types';

const LOCALE_KEY = Symbol('locale');

class LocaleContext {
  locale = $state<Locale>('en');
  
  setLocale(newLocale: Locale) {
    this.locale = newLocale;
  }
}

export function setLocaleContext(initialLocale: Locale): LocaleContext {
  const ctx = new LocaleContext();
  ctx.locale = initialLocale;
  setContext(LOCALE_KEY, ctx);
  return ctx;
}

export function getLocaleContext(): LocaleContext {
  const ctx = getContext<LocaleContext>(LOCALE_KEY);
  if (!ctx) {
    throw new Error('Locale context not found. Make sure to call setLocaleContext in a parent component.');
  }
  return ctx;
}
```

**File:** `apps/frontend/src/lib/i18n/types.ts`

```typescript
export type Locale = 'en' | 'th';

export const SUPPORTED_LOCALES: Locale[] = ['en', 'th'];

export const DEFAULT_LOCALE: Locale = 'en';
```

### Route Structure

**File:** `apps/frontend/src/routes/+page.svelte`

```svelte
<script lang="ts">
  import { goto } from '$app/navigation';
  import { DEFAULT_LOCALE } from '$lib/i18n/types';
  import { onMount } from 'svelte';
  
  onMount(() => {
    // Detect browser language (optional - can use this later)
    // const browserLang = navigator.language.split('-')[0];
    // const locale = ['en', 'th'].includes(browserLang) ? browserLang : 'en';
    
    // For now, always redirect to English
    goto(`/${DEFAULT_LOCALE}`, { replaceState: true });
  });
</script>

<!-- Loading state -->
<div class="flex items-center justify-center min-h-screen">
  <p>Redirecting...</p>
</div>
```

**File:** `apps/frontend/src/routes/[lang]/+layout.ts`

```typescript
import { redirect } from '@sveltejs/kit';
import { SUPPORTED_LOCALES, DEFAULT_LOCALE } from '$lib/i18n/types';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ params }) => {
  const locale = params.lang;
  
  // Validate locale parameter
  if (!SUPPORTED_LOCALES.includes(locale as any)) {
    redirect(302, `/${DEFAULT_LOCALE}`);
  }
  
  return {
    locale: locale as 'en' | 'th'
  };
};
```

**File:** `apps/frontend/src/routes/[lang]/+layout.svelte`

```svelte
<script lang="ts">
  import { setLocaleContext } from '$lib/i18n/context.svelte';
  import LocaleSwitcher from '$lib/components/LocaleSwitcher.svelte';
  import type { LayoutProps } from './$types';
  
  const { data, children }: LayoutProps = $props();
  
  // Set locale context for child components
  setLocaleContext(data.locale);
</script>

<div class="app">
  <header class="flex items-center justify-between p-4 border-b">
    <h1>Bestays</h1>
    <LocaleSwitcher />
  </header>
  
  <main>
    {@render children()}
  </main>
</div>
```

**File:** `apps/frontend/src/routes/[lang]/+page.ts`

```typescript
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, parent }) => {
  const { locale } = await parent();
  
  // Fetch content with locale parameter
  const heroTitle = await fetch(`/api/v1/content/hero.title?locale=${locale}`)
    .then(r => r.json());
  
  const heroSubtitle = await fetch(`/api/v1/content/hero.subtitle?locale=${locale}`)
    .then(r => r.json());
  
  return {
    heroTitle: heroTitle.value,
    heroSubtitle: heroSubtitle.value
  };
};
```

**File:** `apps/frontend/src/routes/[lang]/+page.svelte`

```svelte
<script lang="ts">
  import EditableText from '$lib/components/ui/EditableText.svelte';
  import type { PageProps } from './$types';
  
  const { data }: PageProps = $props();
</script>

<section class="hero">
  <EditableText contentKey="hero.title" value={data.heroTitle} />
  <EditableText contentKey="hero.subtitle" value={data.heroSubtitle} />
</section>
```

### LocaleSwitcher Component

**File:** `apps/frontend/src/lib/components/LocaleSwitcher.svelte`

```svelte
<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { getLocaleContext } from '$lib/i18n/context.svelte';
  import type { Locale } from '$lib/i18n/types';
  
  const localeCtx = getLocaleContext();
  
  function switchLocale(newLocale: Locale) {
    const currentPath = $page.url.pathname;
    // Remove current locale from path
    const pathWithoutLocale = currentPath.replace(/^\/(en|th)/, '');
    // Navigate to new locale
    goto(`/${newLocale}${pathWithoutLocale || '/'}`);
  }
</script>

<div class="locale-switcher flex items-center gap-2">
  <button
    class="locale-button"
    class:active={localeCtx.locale === 'en'}
    onclick={() => switchLocale('en')}
  >
    EN
  </button>
  <span class="text-gray-400">|</span>
  <button
    class="locale-button"
    class:active={localeCtx.locale === 'th'}
    onclick={() => switchLocale('th')}
  >
    TH
  </button>
</div>

<style>
  .locale-button {
    @apply px-2 py-1 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors;
  }
  
  .locale-button.active {
    @apply text-blue-600 font-bold;
  }
</style>
```

### Updated EditableText Component

**File:** `apps/frontend/src/lib/components/ui/EditableText.svelte`

```svelte
<script lang="ts">
  import { getLocaleContext } from '$lib/i18n/context.svelte';
  import EditContentDialog from './EditContentDialog.svelte';
  
  interface Props {
    contentKey: string;
    value: string;
  }
  
  const { contentKey, value }: Props = $props();
  
  const localeCtx = getLocaleContext();
  
  let showDialog = $state(false);
  
  async function handleSave(newValue: string) {
    // Save with current locale
    const response = await fetch(`/api/v1/content/${contentKey}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ value: newValue, locale: localeCtx.locale })
    });
    
    if (response.ok) {
      // Reload page to show updated content
      window.location.reload();
    }
  }
</script>

<div class="editable-text-wrapper">
  <p>{value}</p>
  <button onclick={() => showDialog = true}>Edit</button>
</div>

{#if showDialog}
  <EditContentDialog
    contentKey={contentKey}
    currentValue={value}
    locale={localeCtx.locale}
    onSave={handleSave}
    onClose={() => showDialog = false}
  />
{/if}
```

---

## Summary

This architecture specification provides:

1. **Database:** Complete migration script with safe phased approach
2. **Seed Data:** Thai translations for both products
3. **Backend:** Updated models, schemas, service layer, and endpoints
4. **Frontend:** i18n context, route structure, and components

All components follow official Svelte 5 and FastAPI patterns, validated against official documentation.

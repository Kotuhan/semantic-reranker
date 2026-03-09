---
name: frontend-developer
description: Frontend development patterns and templates for the web app. Use when implementing new entities, data fetching, or state management features.
---

# Frontend Developer Skill

This skill provides patterns and templates for frontend development in the web application using Redux Toolkit.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    REACT COMPONENT                          │
│  (useFetchEntity or useLazyFetchEntity)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  HOOKS LAYER                                │
│  • useFetchEntity (eager, useEffect)                       │
│  • useLazyFetchEntity (lazy, useCallback)                  │
│  • useAppDispatch (typed Redux dispatch)                   │
│  • useAppSelector (typed Redux selector)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              STATE MANAGEMENT (Redux Toolkit)              │
│  • Slice: state shape + reducers                           │
│  • Thunk: async operations with createAsyncThunk           │
│  • Selector: transforms state to hook result               │
│  • Store: combines all reducers                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  API LAYER                                 │
│  • HTTP call with axios                                    │
│  • snake_case → camelCase transformation                   │
└─────────────────────────────────────────────────────────────┘
```

## Adding a New Entity - Step by Step

### Step 1: Define Types

**File:** `src/store/{entity}/{entity}.types.ts`

```typescript
export type TEntity = {
  id: string;
  // Add entity-specific fields with proper types
  createdAt: string;
};
```

### Step 2: Create API Layer

**File:** `src/api/http/{entity}.ts`

```typescript
import http from ".";
import { TEntity } from "../../store/{entity}/{entity}.types";

export const queryGetEntity = async (): Promise<TEntity> => {
  const response = await http.get<{
    id: string;
    // API response fields (snake_case from backend)
    created_at: string;
  }>("/endpoint");

  // Transform snake_case to camelCase
  const { created_at, ...rest } = response.data;

  return {
    ...rest,
    createdAt: created_at,
  };
};
```

### Step 3: Create Async Thunk

**File:** `src/store/{entity}/{entity}.thunks.ts`

```typescript
import { createAsyncThunk } from "@reduxjs/toolkit";
import { queryGetEntity } from "../../api/http/{entity}";

export const fetchEntity = createAsyncThunk("{entity}/fetch", async () => {
  const response = await queryGetEntity();
  return response;
});
```

### Step 4: Create Redux Slice

**File:** `src/store/{entity}/{entity}.slice.ts`

```typescript
import { createSlice, SerializedError } from "@reduxjs/toolkit";
import { LoadingStatuses } from "../types";
import { fetchEntity } from "./{entity}.thunks";
import { TEntity } from "./{entity}.types";

export interface EntityState {
  data: TEntity | null;
  status: LoadingStatuses;
  error: SerializedError | null;
}

const initialState: EntityState = {
  data: null,
  status: LoadingStatuses.IDLE,
  error: null,
};

export const entitySlice = createSlice({
  name: "{entity}",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(fetchEntity.fulfilled, (state, { payload }) => {
      state.data = payload;
      state.status = LoadingStatuses.SUCCEEDED;
    });
    builder.addCase(fetchEntity.rejected, (state, { error }) => {
      state.status = LoadingStatuses.FAILED;
      state.error = error;
    });
    builder.addCase(fetchEntity.pending, (state) => {
      state.status = LoadingStatuses.PENDING;
    });
  },
});

export default entitySlice.reducer;
```

### Step 5: Create Selectors

**File:** `src/store/{entity}/{entity}.selectors.ts`

```typescript
import { TQueryResult } from "../../hooks/types";
import { RootState } from "../store";
import { LoadingStatuses } from "../types";
import { TEntity } from "./{entity}.types";

export const entitySelector = (state: RootState) => state.{entity}.data;

export const useFetchEntitySelector = (
  state: RootState
): TQueryResult<TEntity | null> => {
  const slice = state.{entity};
  if (slice.error) {
    return {
      data: null,
      loading: false,
      error: slice.error,
    };
  }

  return {
    data: entitySelector(state),
    loading: slice.status === LoadingStatuses.PENDING,
    error: null,
  };
};
```

### Step 6: Register in Store

**File:** `src/store/store.ts`

```typescript
import { combineReducers, configureStore } from "@reduxjs/toolkit";
import entitySlice from "./{entity}/{entity}.slice";

const rootReducer = combineReducers({
  {entity}: entitySlice,
  // ... other slices
});
```

### Step 7: Create Hooks

**Eager Hook (auto-fetch on mount):**
**File:** `src/hooks/useFetch{Entity}.ts`

```typescript
import { useEffect } from "react";
import { Query } from "./types";
import { useAppSelector } from "./useAppSelector";
import { useAppDispatch } from "./useDispatch";
import { fetchEntity } from "../store/{entity}/{entity}.thunks";
import { TEntity } from "../store/{entity}/{entity}.types";
import { useFetchEntitySelector } from "../store/{entity}/{entity}.selectors";

export const useFetchEntity: Query<TEntity | null> = () => {
  const dispatch = useAppDispatch();
  const { data, loading, error } = useAppSelector(useFetchEntitySelector);

  useEffect(() => {
    dispatch(fetchEntity());
  }, [dispatch]);

  if (error) {
    return { data, loading, error, called: false };
  }

  return { data, loading, error, called: false };
};
```

**Lazy Hook (manual trigger):**
**File:** `src/hooks/useLazyFetch{Entity}.ts`

```typescript
import { useCallback } from "react";
import { TLazyQuery } from "./types";
import { useAppSelector } from "./useAppSelector";
import { useAppDispatch } from "./useDispatch";
import { fetchEntity } from "../store/{entity}/{entity}.thunks";
import { TEntity } from "../store/{entity}/{entity}.types";
import { useFetchEntitySelector } from "../store/{entity}/{entity}.selectors";

export const useLazyFetchEntity: TLazyQuery<TEntity | null> = () => {
  const dispatch = useAppDispatch();
  const { data, loading, error } = useAppSelector(useFetchEntitySelector);

  const handleFetch = useCallback(() => {
    dispatch(fetchEntity());
  }, [dispatch]);

  return [handleFetch, { data, loading, error, called: false }];
};
```

### Step 8: Add Endpoint Constant

**File:** `src/api/constants.ts`

```typescript
// {entity}
export const GET_ENTITY = '/endpoint';
```

## Component Usage

```typescript
import { useFetchEntity } from '@/hooks/useFetchEntity';
import { useLazyFetchEntity } from '@/hooks/useLazyFetchEntity';

export default function MyComponent() {
  // Eager - auto-fetches on mount
  const { data, loading, error } = useFetchEntity();

  // Lazy - manual trigger
  const [fetchEntity, { data: lazyData }] = useLazyFetchEntity();

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {data && <p>{data.id}</p>}
      <button onClick={() => fetchEntity()}>Refresh</button>
    </div>
  );
}
```

## Key Patterns

### Loading Status Enum
```typescript
export enum LoadingStatuses {
  IDLE = "IDLE",
  PENDING = "PENDING",
  SUCCEEDED = "SUCCEEDED",
  FAILED = "FAILED",
}
```

### Query Result Types
```typescript
// For eager hooks
type TQueryResult<T> = {
  data: T;
  error: null;
  loading: boolean;
} | {
  data: null;
  error: SerializedError;
  loading: false;
};

// For lazy hooks - returns tuple
type TLazyQuery<T> = () => [fetchFn, TLazyQueryResult<T>];
```

### Data Transformation
Always transform API responses from snake_case to camelCase in the API layer:
```typescript
const { created_at, partner_gender, ...rest } = response.data;
return {
  ...rest,
  createdAt: created_at,
  partnerGender: partner_gender,
};
```

## File Checklist for New Entity

- [ ] `src/store/{entity}/{entity}.types.ts`
- [ ] `src/api/http/{entity}.ts`
- [ ] `src/store/{entity}/{entity}.thunks.ts`
- [ ] `src/store/{entity}/{entity}.slice.ts`
- [ ] `src/store/{entity}/{entity}.selectors.ts`
- [ ] `src/store/store.ts` (add reducer)
- [ ] `src/hooks/useFetch{Entity}.ts`
- [ ] `src/hooks/useLazyFetch{Entity}.ts`
- [ ] `src/api/constants.ts` (add endpoint)

---
title: Framer Motion Animation Patterns for Next.js 14 App Router
domain: library
tech: [framer-motion, react, nextjs, typescript, animation]
area: [animations, micro-interactions, ui-transitions, text-animation, accessibility]
staleness: 3months
created: 2026-02-12
updated: 2026-02-12
sources:
  - https://motion.dev/docs/react-animate-presence
  - https://motion.dev/docs/react-use-reduced-motion
  - https://motion.dev/docs/react-transitions
  - https://blog.maximeheckel.com/posts/advanced-animation-patterns-with-framer-motion/
  - https://github.com/framer/motion/issues/2023
  - https://motion.dev/tutorials/react-animate-presence-modes
  - https://medium.com/@dolce-emmy/resolving-framer-motion-compatibility-in-next-js-14-the-use-client-workaround-1ec82e5a0c75
---

# Framer Motion Animation Patterns for Next.js 14 App Router

## Overview

Comprehensive guide to Framer Motion (now Motion) animation patterns for Next.js 14 App Router projects, covering AnimatePresence modes, text crossfade, gradient animations, reduced motion support, and coordinating Motion with CSS transitions.

## Key Findings

1. **AnimatePresence with mode="wait"** enables sequential text crossfades (exit completes before enter starts)
2. **CSS gradient text backgrounds** cannot be directly animated; use two overlapping elements with opacity crossfade
3. **useReducedMotion hook** must be manually implemented for AnimatePresence (not automatic)
4. **Tween animations** match exact CSS transition timing; spring animations feel more natural but are non-deterministic
5. **Rapid key changes** are handled correctly in Motion v11+ (cancels current animation and starts new one)
6. **Next.js App Router** requires "use client" directive for all Motion components
7. **Bundle size**: ~55KB gzipped (full), ~25KB with LazyMotion optimization

---

## AnimatePresence Modes

### Mode Comparison

| Mode | Behavior | Use Case |
|------|----------|----------|
| `sync` | Exit and enter animations run simultaneously | Crossfade effects, overlapping elements |
| `wait` | Waits for exit to complete before entering | Sequential text changes, avoid overlapping content |
| `popLayout` | Animates layout changes during exit | List item removal with reordering |

### Text Crossfade Pattern (mode="wait")

Best for swapping text labels where overlapping text reduces readability:

```tsx
'use client';

import { motion, AnimatePresence } from 'framer-motion';

export function TextSwap({ content, contentKey }: { content: string; contentKey: string }) {
  return (
    <div className="relative h-6"> {/* Reserve space to prevent layout shift */}
      <AnimatePresence mode="wait" initial={false}>
        <motion.span
          key={contentKey} // CRITICAL: key must change to trigger animation
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
          transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
        >
          {content}
        </motion.span>
      </AnimatePresence>
    </div>
  );
}
```

**Key points:**
- `key` prop must change to trigger animations
- `initial={false}` prevents animation on first mount
- Reserve fixed height to prevent layout shift
- Use `mode="wait"` to avoid overlapping text

### Crossfade Pattern (mode="sync")

For smooth opacity transitions with overlapping elements:

```tsx
<div className="relative h-6">
  <AnimatePresence mode="sync">
    <motion.span
      key={contentKey}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="absolute inset-0" // Overlay both elements
      transition={{ duration: 0.4 }}
    >
      {content}
    </motion.span>
  </AnimatePresence>
</div>
```

---

## Gradient Text Animation

### Challenge

CSS `background-image` gradients with `background-clip: text` **cannot be directly animated** by Framer Motion. Browsers don't support smooth gradient interpolation.

### Solution: Opacity Crossfade (Two Elements)

Layer two text elements with different gradients and crossfade via opacity:

```tsx
'use client';

import { motion } from 'framer-motion';

export function GradientTextSwap({ isStateA, children }: { isStateA: boolean; children: React.ReactNode }) {
  return (
    <span className="relative inline-block">
      {/* Base layer: Gradient A (e.g., blue/indigo) */}
      <motion.span
        className="gradient-text-a"
        animate={{ opacity: isStateA ? 1 : 0 }}
        transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
      >
        {children}
      </motion.span>

      {/* Top layer: Gradient B (e.g., pink/rose) */}
      <motion.span
        className="gradient-text-b absolute inset-0"
        animate={{ opacity: isStateA ? 0 : 1 }}
        transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
      >
        {children}
      </motion.span>
    </span>
  );
}
```

```css
.gradient-text-a {
  background: linear-gradient(to right, #3b82f6, #6366f1);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.gradient-text-b {
  background: linear-gradient(to right, #ec4899, #f43f5e);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

**Pros:**
- Smooth crossfade between any CSS gradients
- No JavaScript gradient calculations
- Works with complex gradient definitions

**Cons:**
- Requires two DOM elements per text
- Slightly more markup

### Alternative: CSS Custom Properties

Animate gradient color stops using CSS variables:

```tsx
<motion.span
  animate={{
    '--gradient-from': isStateA ? '#3b82f6' : '#ec4899',
    '--gradient-to': isStateA ? '#6366f1' : '#f43f5e',
  }}
  transition={{ duration: 0.8 }}
  className="gradient-text-custom"
>
  {children}
</motion.span>
```

```css
.gradient-text-custom {
  background: linear-gradient(to right, var(--gradient-from), var(--gradient-to));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

**Note**: Browser support for animating gradient color stops via CSS variables is inconsistent. Opacity crossfade is more reliable.

---

## Accessibility: useReducedMotion Hook

### How It Works

`useReducedMotion` returns `true` if the user's device has "Reduce Motion" accessibility setting enabled:

```tsx
import { useReducedMotion } from 'framer-motion';

function MyComponent() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      animate={{ x: shouldReduceMotion ? 0 : 100 }}
      transition={{ duration: shouldReduceMotion ? 0.01 : 0.8 }}
    />
  );
}
```

### AnimatePresence Does NOT Respect It Automatically

You must **manually handle** reduced motion for exit/enter animations:

```tsx
'use client';

import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';

export function AccessibleAnimation({ content, contentKey }: { content: string; contentKey: string }) {
  const shouldReduceMotion = useReducedMotion();

  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.span
        key={contentKey}
        initial={{
          opacity: shouldReduceMotion ? 1 : 0,
          y: shouldReduceMotion ? 0 : -10
        }}
        animate={{ opacity: 1, y: 0 }}
        exit={{
          opacity: shouldReduceMotion ? 1 : 0,
          y: shouldReduceMotion ? 0 : 10
        }}
        transition={{
          duration: shouldReduceMotion ? 0.01 : 0.8,
          ease: [0.4, 0, 0.2, 1]
        }}
      >
        {content}
      </motion.span>
    </AnimatePresence>
  );
}
```

### Best Practices

1. **Always check `useReducedMotion`** when using AnimatePresence
2. Set duration to `0.01` (not `0`, which disables transitions)
3. Remove positional offsets (`y: 0`) to avoid jarring jumps
4. Keep opacity changes (instant crossfade is acceptable)

---

## Coordinating Motion with CSS Transitions

### Matching Duration and Easing

To match CSS transitions:

```css
/* CSS */
transition: all 800ms cubic-bezier(0.4, 0, 0.2, 1);
```

```tsx
/* Framer Motion */
<motion.div
  transition={{
    duration: 0.8, // 800ms in seconds
    ease: [0.4, 0, 0.2, 1] // Cubic bezier array
  }}
/>
```

### Using CSS Variables for Sync

Define timing as CSS variables for consistency:

```css
:root {
  --animation-duration: 800ms;
  --animation-easing: cubic-bezier(0.4, 0, 0.2, 1);
}

.border-gradient {
  transition: all var(--animation-duration) var(--animation-easing);
}
```

```tsx
const ANIMATION_DURATION = 0.8; // Match --animation-duration
const ANIMATION_EASING = [0.4, 0, 0.2, 1]; // Match --animation-easing

<motion.span
  transition={{
    duration: ANIMATION_DURATION,
    ease: ANIMATION_EASING
  }}
/>
```

### Staggered Animations

To sequence multiple animations:

```tsx
<motion.span
  transition={{
    duration: 0.8,
    ease: [0.4, 0, 0.2, 1],
    delay: 0.2 // Start 200ms after trigger
  }}
/>
```

---

## Rapid Interaction Handling

### Behavior with mode="wait"

As of Motion v11+ (July 2024, post-PR #2257), rapid key changes with `mode="wait"` **cancel the current animation and start the new one**.

**Before Motion v11**: There was a bug where rapid key changes caused AnimatePresence to get stuck. This is now **fixed**.

### Example: Rapid Clicks

```tsx
// User clicks rapidly: A → B → A → B
// With mode="wait":
// 1. Animation starts: A exits
// 2. User clicks again before exit finishes
// 3. Motion cancels A exit, immediately starts B exit
// 4. B exits, A enters
```

**Result**: Animations always sync with the latest state. No stuck UI.

### Recommendations

1. **Use `mode="wait"`** for sequential text changes
2. **Keep animations short (0.8s or less)** to avoid sluggish feel
3. **Trust Motion's cancellation logic** — don't debounce clicks manually
4. **Test rapid clicking** to ensure no visual glitches

### Debouncing (Not Recommended)

If you want to block clicks during animation (makes UI feel unresponsive):

```tsx
const [isAnimating, setIsAnimating] = useState(false);

function handleClick() {
  if (isAnimating) return; // Ignore clicks during animation

  setIsAnimating(true);
  setContent(newContent);
  setTimeout(() => setIsAnimating(false), 800);
}
```

---

## Next.js 14 App Router Integration

### "use client" Directive Required

Framer Motion requires browser APIs (DOM, requestAnimationFrame) not available in Server Components:

```tsx
'use client'; // REQUIRED at the top of the file

import { motion } from 'framer-motion';

export function AnimatedComponent() {
  return <motion.div />;
}
```

### Bundle Size

| Import Method | Bundle Size | Savings |
|---------------|-------------|---------|
| Full import (`motion.*`) | ~55KB gzipped | — |
| LazyMotion (`m.*`) | ~25KB gzipped | ~30KB |

#### Optimizing with LazyMotion

Defer loading animation features until first use:

```tsx
'use client';

import { LazyMotion, domAnimation, m } from 'framer-motion';

export function OptimizedComponent() {
  return (
    <LazyMotion features={domAnimation}>
      <m.div animate={{ opacity: 1 }}>
        {/* Use <m.div> instead of <motion.div> */}
      </m.div>
    </LazyMotion>
  );
}
```

**Trade-offs:**
- **Pros**: Smaller initial bundle, faster page load
- **Cons**: More complex API, must use `m.*` components inside `LazyMotion`

**Recommendation**: Start with full import. Optimize with `LazyMotion` only if bundle analysis shows Motion >10% of JS bundle.

### SSR and Hydration

Motion animations work seamlessly with Next.js hydration:

```tsx
<motion.div
  initial={false} // Don't animate on first render (prevents "pop-in")
  animate={{ opacity: isVisible ? 1 : 0 }}
/>
```

---

## Spring vs Tween for Timing Match

### Tween (Duration-Based)

**Use when**: You need **exact timing** to match CSS transitions.

```tsx
<motion.span
  transition={{
    type: 'tween',
    duration: 0.8, // Exact 800ms
    ease: [0.4, 0, 0.2, 1] // Cubic bezier
  }}
/>
```

**Pros:**
- Predictable, matches CSS timing exactly
- Easy to coordinate with other animations

**Cons:**
- More "mechanical" feel
- No natural bounce

### Spring (Physics-Based)

**Use when**: You want **natural, bouncy motion**.

```tsx
<motion.span
  transition={{
    type: 'spring',
    stiffness: 300,
    damping: 30
  }}
/>
```

**Pros:**
- Feels organic and playful
- Responds to velocity

**Cons:**
- **Cannot guarantee exact duration** (physics simulation)
- Harder to coordinate with CSS transitions

### Spring with Duration (Hybrid)

Set exact duration while keeping spring feel:

```tsx
<motion.span
  transition={{
    type: 'spring',
    duration: 0.8, // EXACT 800ms
    bounce: 0.25 // Controls springiness (0 = linear, 0.5 = very bouncy)
  }}
/>
```

**Pros:**
- Combines spring feel with predictable timing
- Matches CSS transitions

**Cons:**
- Less "physics accurate"
- Requires tuning `bounce` value

### visualDuration for Coordination

For pure physics springs, use `visualDuration` to visually coordinate with time-based animations:

```tsx
<motion.span
  transition={{
    type: 'spring',
    visualDuration: 0.8, // Animation "feels" like 800ms
    bounce: 0.25
  }}
/>
```

**Note**: Actual animation may be slightly longer (bouncy bit happens after `visualDuration`).

### Recommendation

**For coordinating with CSS transitions**: Use tween with cubic-bezier easing for exact timing match.

**For playful UI elements**: Use duration-based spring with low bounce (0.1-0.25).

---

## Common Pitfalls

### Pitfall 1: Missing `key` Prop

```tsx
// ❌ WRONG: No key, animation never triggers
<AnimatePresence mode="wait">
  <motion.span>{text}</motion.span>
</AnimatePresence>

// ✅ CORRECT: Key changes trigger animation
<AnimatePresence mode="wait">
  <motion.span key={uniqueKey}>{text}</motion.span>
</AnimatePresence>
```

### Pitfall 2: Layout Shift During Animation

```tsx
// ❌ WRONG: Container height collapses during exit
<div>
  <AnimatePresence mode="wait">
    <motion.span key={key}>{text}</motion.span>
  </AnimatePresence>
</div>

// ✅ CORRECT: Fixed height prevents shift
<div className="h-6 flex items-center">
  <AnimatePresence mode="wait">
    <motion.span key={key}>{text}</motion.span>
  </AnimatePresence>
</div>
```

### Pitfall 3: Gradient Text Not Appearing

```tsx
// ❌ WRONG: Missing vendor prefixes
.gradient-text {
  background: linear-gradient(...);
  background-clip: text;
}

// ✅ CORRECT: Full browser support
.gradient-text {
  background: linear-gradient(...);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

### Pitfall 4: Ignoring Reduced Motion

```tsx
// ❌ WRONG: Animation always runs
<motion.span
  initial={{ opacity: 0, y: -10 }}
  animate={{ opacity: 1, y: 0 }}
/>

// ✅ CORRECT: Respects user preference
const shouldReduceMotion = useReducedMotion();

<motion.span
  initial={{ opacity: shouldReduceMotion ? 1 : 0, y: shouldReduceMotion ? 0 : -10 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: shouldReduceMotion ? 0.01 : 0.8 }}
/>
```

---

## Performance Best Practices

1. **Animate only `opacity` and `transform`**: GPU-accelerated, no layout recalculation
2. **Avoid animating `width`, `height`, `margin`**: Causes layout thrashing
3. **Use `will-change` sparingly**: Only for frequently animated elements

```tsx
<motion.span
  style={{ willChange: 'transform, opacity' }} // Only during animation
  animate={{ opacity: 1, y: 0 }}
/>
```

4. **Test with reduced motion enabled**: DevTools > Settings > Rendering > Emulate CSS media prefers-reduced-motion
5. **Use LazyMotion for bundle optimization**: If Motion >10% of JS bundle

---

## Complete Production Example

```tsx
'use client';

import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';

interface AnimatedLabelProps {
  content: string;
  contentKey: string;
  gradientClass: string;
  className?: string;
}

const ANIMATION_DURATION = 0.8;
const ANIMATION_EASING = [0.4, 0, 0.2, 1] as const;

export function AnimatedLabel({ content, contentKey, gradientClass, className }: AnimatedLabelProps) {
  const shouldReduceMotion = useReducedMotion();

  const animationConfig = {
    initial: {
      opacity: shouldReduceMotion ? 1 : 0,
      y: shouldReduceMotion ? 0 : -10
    },
    animate: {
      opacity: 1,
      y: 0
    },
    exit: {
      opacity: shouldReduceMotion ? 1 : 0,
      y: shouldReduceMotion ? 0 : 10
    },
    transition: {
      type: 'tween' as const,
      duration: shouldReduceMotion ? 0.01 : ANIMATION_DURATION,
      ease: ANIMATION_EASING
    }
  };

  return (
    <div className="relative h-6 flex items-center justify-center">
      <AnimatePresence mode="wait" initial={false}>
        <motion.span
          key={contentKey}
          {...animationConfig}
          className={`${gradientClass} ${className}`}
        >
          {content}
        </motion.span>
      </AnimatePresence>
    </div>
  );
}
```

---

## Testing Checklist

- [ ] Animations trigger on state change
- [ ] Rapid interactions don't cause glitches
- [ ] Animation timing matches coordinated CSS transitions
- [ ] Gradient colors crossfade smoothly
- [ ] `prefers-reduced-motion` respected
- [ ] No layout shift during animation
- [ ] Works in Next.js production build
- [ ] Bundle size acceptable (<60KB)
- [ ] GPU-accelerated (DevTools > Performance)
- [ ] Text readable at all animation stages

---

## Sources

- [AnimatePresence — React exit animations | Motion](https://motion.dev/docs/react-animate-presence)
- [AnimatePresence modes - Motion Tutorial](https://motion.dev/tutorials/react-animate-presence-modes)
- [Advanced animation patterns with Framer Motion - Maxime Heckel](https://blog.maximeheckel.com/posts/advanced-animation-patterns-with-framer-motion/)
- [useReducedMotion — Accessible React animations | Motion](https://motion.dev/docs/react-use-reduced-motion)
- [React transitions — Configure Motion animations | Motion](https://motion.dev/docs/react-transitions)
- [AnimatePresence Bug: Rapid State Changes - GitHub Issue #2023](https://github.com/framer/motion/issues/2023)
- [Resolving Framer Motion Compatibility in Next.js 14 - Medium](https://medium.com/@dolce-emmy/resolving-framer-motion-compatibility-in-next-js-14-the-use-client-workaround-1ec82e5a0c75)
- [The Mighty Framer Motion Guide - The Transition Property](https://motion.mighty.guide/the-main-properties/the-transition-property/)

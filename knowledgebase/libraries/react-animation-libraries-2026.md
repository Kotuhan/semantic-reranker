---
title: React Animation Libraries Comparison (2026)
domain: library
tech: [react, typescript, javascript, animation, framer-motion, react-spring]
area: [animations, micro-interactions, ui-transitions, svg-animation]
staleness: 3months
created: 2026-01-29
updated: 2026-01-29
sources:
  - https://hookedonui.com/animating-react-uis-in-2025-framer-motion-12-vs-react-spring-10/
  - https://www.angularminds.com/blog/react-spring-or-framer-motion
  - https://dev.to/ciphernutz/top-react-animation-libraries-framer-motion-gsap-react-spring-and-more-4854
  - https://www.dhiwise.com/post/react-spring-vs-framer-motion-a-detailed-guide-to-react
  - https://blog.logrocket.com/best-react-animation-libraries/
  - https://motion.dev/docs/react-svg-animation
  - https://www.framer.com/motion/component/
  - https://blog.logrocket.com/build-svg-circular-progress-component-react-hooks/
---

# React Animation Libraries Comparison (2026)

## Overview

This document compares Framer Motion, React Spring, and CSS transitions for building micro-interactions and animations in modern React applications, with focus on Next.js integration and SVG gauge animations.

## Library Comparison

| Library | Bundle Size | Approach | Best For | Learning Curve |
|---------|-------------|----------|----------|----------------|
| **Framer Motion** | ~55KB gzipped | Declarative, variants-based | Timeline sequences, layout animations, designers | Easy |
| **React Spring** | ~20KB gzipped | Physics-based, imperative | Realistic motion, gestures, Three.js | Medium |
| **CSS Transitions** | 0KB | Native browser APIs | Simple hover states, basic fades | Very Easy |
| **GSAP** | ~40KB gzipped | Timeline-based, imperative | Complex sequences, scroll animations | Medium |

## Framer Motion 12

### Strengths

**✅ Declarative API**
Easy-to-read, designer-friendly syntax using variants:

```tsx
const variants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
};

<motion.div
  initial="hidden"
  animate="visible"
  variants={variants}
  transition={{ duration: 0.3 }}
/>
```

**✅ Layout Animations**
"Shared layout magic" using `layoutId`:

```tsx
<motion.div layoutId="card" />
// Morphs seamlessly between different positions/sizes
```

**✅ SVG Path Animation**
Built-in support for "draw on" effects:

```tsx
<motion.path
  initial={{ pathLength: 0 }}
  animate={{ pathLength: 1 }}
  transition={{ duration: 2 }}
/>
```

**✅ Automatic Reduced Motion**
Respects `prefers-reduced-motion` by default (new in v12).

**✅ Scroll-Linked Animations**
Built-in scroll triggers and parallax:

```tsx
import { useScroll, useTransform } from 'framer-motion';

const { scrollYProgress } = useScroll();
const opacity = useTransform(scrollYProgress, [0, 1], [1, 0]);
```

### Bundle Optimization

**LazyMotion** defers library code until first animation, reducing initial payload by ~30KB:

```tsx
import { LazyMotion, domAnimation, m } from 'framer-motion';

<LazyMotion features={domAnimation}>
  <m.div animate={{ x: 100 }} />
</LazyMotion>
```

### When to Use Framer Motion

- ✅ Timeline-like animation sequences
- ✅ Shared layout transitions (morphing cards to modals)
- ✅ Designer collaboration (variants are easy to understand)
- ✅ Micro-interactions with hover/tap gestures
- ✅ SVG animations (gauges, loaders, icons)
- ✅ Beginner-friendly projects

### Performance Characteristics

- Hardware-accelerated (`transform` and `opacity` by default)
- Locks to `transform`/`opacity` for best performance
- Smooth on less powerful devices
- Use `whileHover`/`whileTap` sparingly on mobile

---

## React Spring 10

### Strengths

**✅ Physics-Based Motion**
Springs feel more natural than easing curves:

```tsx
import { useSpring, animated } from '@react-spring/web';

const props = useSpring({
  from: { opacity: 0 },
  to: { opacity: 1 },
  config: { tension: 280, friction: 60 }
});

<animated.div style={props}>Content</animated.div>
```

**✅ Smallest Bundle**
Only ~20KB gzipped (30% smaller than Motion after refactored physics core in v10).

**✅ Gesture Precision**
Tight integration with `@use-gesture/react` for drag, pinch, scroll gestures.

**✅ Three.js Integration**
`@react-spring/three` for 3D animations:

```tsx
import { useSpring, animated } from '@react-spring/three';

<animated.mesh rotation={spring.rotation} />
```

**✅ Imperative Control**
Fine-grained control over animation lifecycle:

```tsx
const [spring, api] = useSpring(() => ({ x: 0 }));

// Trigger programmatically
api.start({ x: 100 });
```

### When to Use React Spring

- ✅ Physics-heavy interactions (bounces, momentum)
- ✅ Gesture-driven UIs (drag-to-dismiss, swipe actions)
- ✅ Three.js scenes or 3D interactions
- ✅ Fine-tuned performance optimization needed
- ✅ Bundle size is critical
- ✅ Real-world physics simulation (springs, damping)

### Performance Considerations

**⚠️ Main Thread Usage**
Physics loops may consume CPU on low-end devices. Use `clamp: true` to end animations quickly:

```tsx
config: { tension: 280, friction: 60, clamp: true }
```

**⚠️ No Layout Constraints**
React Spring trusts you to animate only `transform` and `opacity`. Animating `width`, `height`, etc. will cause jank.

---

## CSS Transitions

### When to Use

**✅ Simple hover states**
```css
.button {
  transition: background-color 0.2s ease;
}

.button:hover {
  background-color: #3b82f6;
}
```

**✅ No JavaScript overhead**
Zero bundle size, browser-native.

**✅ Accessibility**
Automatically respects `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### When NOT to Use

- ❌ Complex sequences (no timeline control)
- ❌ Dynamic values (can't interpolate based on state)
- ❌ SVG path animations (limited support)

---

## GSAP (Honorable Mention)

**Pros:**
- Industry-standard for complex timelines
- Scroll-triggered animations (ScrollTrigger plugin)
- Works with any DOM element (not just React)

**Cons:**
- Imperative API (less "React-y")
- Commercial license for some plugins
- ~40KB bundle size

**Use case:** Complex scroll-driven animations or when migrating from jQuery/vanilla JS.

---

## Micro-Interactions Comparison

### Button Hover Effect

**Framer Motion (Declarative):**
```tsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  transition={{ type: 'spring', stiffness: 400 }}
>
  Click me
</motion.button>
```

**React Spring (Physics):**
```tsx
const [hovered, setHovered] = useState(false);
const spring = useSpring({
  scale: hovered ? 1.05 : 1,
  config: { tension: 300, friction: 10 }
});

<animated.button
  style={spring}
  onMouseEnter={() => setHovered(true)}
  onMouseLeave={() => setHovered(false)}
>
  Click me
</animated.button>
```

**CSS:**
```css
button {
  transition: transform 0.2s ease;
}
button:hover {
  transform: scale(1.05);
}
```

**Winner:** CSS for simplicity, Framer Motion for declarative React patterns.

---

## SVG Gauge Animations

For battery gauges, circular progress indicators, and ring animations.

### Framer Motion Approach

**Circular Progress Example:**

```tsx
import { motion } from 'framer-motion';

export function BatteryGauge({ percentage }) {
  const circumference = 2 * Math.PI * 45; // radius = 45
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <svg width="100" height="100" viewBox="0 0 100 100">
      <defs>
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>

      {/* Background circle */}
      <circle
        cx="50"
        cy="50"
        r="45"
        fill="none"
        stroke="rgba(255,255,255,0.1)"
        strokeWidth="8"
      />

      {/* Animated progress circle */}
      <motion.circle
        cx="50"
        cy="50"
        r="45"
        fill="none"
        stroke="#10b981"
        strokeWidth="8"
        strokeLinecap="round"
        strokeDasharray={circumference}
        initial={{ strokeDashoffset: circumference }}
        animate={{ strokeDashoffset }}
        transition={{ duration: 1, ease: 'easeOut' }}
        filter="url(#glow)"
        style={{ transform: 'rotate(-90deg)', transformOrigin: '50% 50%' }}
      />

      {/* Percentage text */}
      <text
        x="50"
        y="50"
        textAnchor="middle"
        dominantBaseline="middle"
        className="text-2xl font-bold fill-white"
      >
        {percentage}%
      </text>
    </svg>
  );
}
```

**Key Properties for SVG Animation:**
- `pathLength`: Special Framer Motion prop (0-1 range)
- `strokeDasharray`/`strokeDashoffset`: Standard SVG stroke animation
- `filter`: SVG filters for glow effects
- `transform: rotate(-90deg)`: Start from top (12 o'clock)

### React Spring Approach

```tsx
import { useSpring, animated } from '@react-spring/web';

export function BatteryGauge({ percentage }) {
  const circumference = 2 * Math.PI * 45;

  const spring = useSpring({
    strokeDashoffset: circumference - (percentage / 100) * circumference,
    from: { strokeDashoffset: circumference },
    config: { tension: 120, friction: 14 }
  });

  return (
    <svg width="100" height="100">
      <animated.circle
        cx="50"
        cy="50"
        r="45"
        fill="none"
        stroke="#10b981"
        strokeWidth="8"
        strokeDasharray={circumference}
        style={{
          strokeDashoffset: spring.strokeDashoffset,
          transform: 'rotate(-90deg)',
          transformOrigin: '50% 50%'
        }}
      />
    </svg>
  );
}
```

**Winner for Gauges:** Framer Motion (cleaner API, pathLength abstraction).

---

## Next.js Integration (2026)

### App Router Considerations

**React 19 Server Components** defer hydration, so client-side animations must feel instantaneous.

**Best Practices:**

1. **Mark as Client Components:**
   ```tsx
   'use client';

   import { motion } from 'framer-motion';
   ```

2. **Lazy Load Animation Libraries:**
   ```tsx
   import dynamic from 'next/dynamic';

   const AnimatedComponent = dynamic(
     () => import('./AnimatedComponent'),
     { ssr: false }
   );
   ```

3. **Optimize Bundle Size:**
   - Use Framer Motion's `LazyMotion`
   - Import only needed Spring hooks (`useSpring` vs entire library)

4. **Avoid Layout Shift:**
   - Use `initial` prop to set starting state
   - Reserve space for animated elements

### WebSocket + Real-Time Data

For live battery data updates:

```tsx
'use client';

import { motion, useSpring } from 'framer-motion';
import { useEffect } from 'react';

export function LiveBatteryGauge({ websocketData }) {
  const percentage = useSpring(0, { stiffness: 100, damping: 30 });

  useEffect(() => {
    percentage.set(websocketData.soc);
  }, [websocketData.soc]);

  return (
    <motion.div
      style={{
        scale: useTransform(percentage, [0, 100], [0.8, 1])
      }}
    >
      <BatteryGauge percentage={percentage} />
    </motion.div>
  );
}
```

**Note:** Use Framer Motion's `useSpring` hook (not React Spring) for smooth interpolation of live data.

---

## Performance Best Practices (2026)

### General Rules

1. **Animate only `transform` and `opacity`**
   - GPU-accelerated, no layout recalculation
   - 60fps guaranteed on modern devices

2. **Respect `prefers-reduced-motion`**
   ```tsx
   const shouldReduceMotion = window.matchMedia(
     '(prefers-reduced-motion: reduce)'
   ).matches;

   <motion.div
     animate={{ x: shouldReduceMotion ? 0 : 100 }}
   />
   ```

3. **Use `will-change` sparingly**
   ```tsx
   <motion.div style={{ willChange: 'transform' }} />
   ```
   Only when animating frequently (e.g., drag operations).

4. **Throttle animations on mobile**
   ```tsx
   const isMobile = window.innerWidth < 768;

   <motion.div
     transition={{ duration: isMobile ? 0.2 : 0.5 }}
   />
   ```

5. **Test with DevTools throttling**
   - Chrome DevTools > Performance > CPU: 4x slowdown
   - Ensure animations stay above 30fps

### Bundle Size Optimization

**Framer Motion:**
```tsx
import { LazyMotion, domAnimation, m } from 'framer-motion';

// Use <m.div> instead of <motion.div>
<LazyMotion features={domAnimation}>
  <m.div animate={{ x: 100 }} />
</LazyMotion>
```
**Savings:** ~30KB from initial bundle.

**React Spring:**
```tsx
// Import only needed hooks
import { useSpring } from '@react-spring/web';

// Instead of:
import * as Spring from '@react-spring/web';
```

---

## Final Recommendations

### For Home Battery Dashboard (task-020)

**Primary: Framer Motion**

**Reasoning:**
- ✅ **SVG gauge animations**: Built-in `pathLength` for circular progress
- ✅ **Micro-interactions**: `whileHover`/`whileTap` for buttons
- ✅ **Layout transitions**: Smooth card expansions for details
- ✅ **Designer-friendly**: Easy for non-developers to tweak
- ✅ **TypeScript support**: Excellent types out-of-the-box

**Use Cases:**
- Battery gauge ring animation
- Card hover states (lift on hover)
- Expanding alert panels
- Chart tooltip animations
- Loading skeleton shimmer

**Example: Complete Animated Card**

```tsx
'use client';

import { motion } from 'framer-motion';

export function BatteryCard({ soc, voltage, current }) {
  return (
    <motion.div
      className="glass-card p-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02, y: -4 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
    >
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.2, type: 'spring' }}
      >
        <BatteryGauge percentage={soc} />
      </motion.div>

      <div className="mt-4 space-y-2">
        <Stat label="Voltage" value={`${voltage}V`} />
        <Stat label="Current" value={`${current}A`} />
      </div>
    </motion.div>
  );
}
```

**Alternative: CSS Transitions**

For simple hover states on small elements (buttons, icons), use CSS:

```tsx
<button className="transition-all duration-200 hover:scale-105 hover:shadow-lg">
  Toggle
</button>
```

**Reserve React Spring for:**
- ❌ Not recommended for this project (no physics-heavy interactions needed)
- ⚠️ Only if you add gesture-driven features (swipe-to-dismiss alerts, drag-to-reorder widgets)

## Sources

- [Animating React UIs in 2025: Framer Motion 12 vs. React Spring 10](https://hookedonui.com/animating-react-uis-in-2025-framer-motion-12-vs-react-spring-10/)
- [React Spring or Framer Motion: Which is Better?](https://www.angularminds.com/blog/react-spring-or-framer-motion)
- [Top React Animation Libraries](https://dev.to/ciphernutz/top-react-animation-libraries-framer-motion-gsap-react-spring-and-more-4854)
- [React Spring vs. Framer Motion: A Detailed Guide](https://www.dhiwise.com/post/react-spring-vs-framer-motion-a-detailed-guide-to-react)
- [Comparing the best React animation libraries for 2026](https://blog.logrocket.com/best-react-animation-libraries/)
- [SVG Animation in React — Motion Docs](https://motion.dev/docs/react-svg-animation)
- [React motion component | Motion](https://www.framer.com/motion/component/)
- [Build SVG circular progress component using React Hooks](https://blog.logrocket.com/build-svg-circular-progress-component-react-hooks/)

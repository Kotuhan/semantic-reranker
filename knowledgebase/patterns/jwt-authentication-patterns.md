---
title: JWT Authentication Patterns - Anonymous-First, Refresh Tokens, and Security Best Practices
domain: pattern
tech: [jwt, typescript, nestjs, passport, bcrypt, argon2, redis, postgresql]
area: [auth, security, session-management]
staleness: 6months
created: 2026-01-29
updated: 2026-01-29
sources:
  - https://www.descope.com/blog/post/descope-flows-anonymous-users
  - https://fusionauth.io/blog/anonymous-user
  - https://supertokens.com/docs/thirdparty/common-customizations/sessions/anonymous-session
  - https://auth0.com/blog/refresh-tokens-what-are-they-and-when-to-use-them/
  - https://www.descope.com/blog/post/refresh-token-rotation
  - https://auth0.com/docs/secure/tokens/refresh-tokens/refresh-token-rotation
  - https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
  - https://guptadeepak.com/the-complete-guide-to-password-hashing-argon2-vs-bcrypt-vs-scrypt-vs-pbkdf2-2026/
  - https://www.elvisduru.com/blog/nestjs-jwt-authentication-refresh-token
  - https://dev.to/zenstok/how-to-implement-refresh-tokens-with-token-rotation-in-nestjs-1deg
  - https://medium.com/@senaunalmis/the-secret-of-infinite-sessions-transitioning-to-jwt-redis-and-refresh-token-architecture-3c3bb5517864
  - https://dev.to/harmanpreetsingh/building-scalable-authentication-the-smart-way-to-handle-tokens-with-redis-and-database-storage-1lcf
  - https://redis.io/blog/json-web-tokens-jwt-are-dangerous-for-user-sessions/
  - https://dev.to/edgi/the-hidden-vulnerabilities-in-your-authentication-system-a-deep-dive-into-timing-attacks-ip-5k9
  - https://www.onlinehashcrack.com/guides/password-recovery/timing-attacks-on-password-checks-mitigation-tips.php
  - https://elsyarifx.medium.com/the-hidden-power-of-jti-how-a-single-claim-can-stop-token-replay-attacks-0255fbcf6b9b
  - https://mojoauth.com/blog/let-understand-jwt-id-jti
  - https://datatracker.ietf.org/doc/html/rfc7519
---

# JWT Authentication Patterns - Anonymous-First, Refresh Tokens, and Security Best Practices

## Overview

This research evaluates JWT authentication patterns for modern web applications, focusing on anonymous-first authentication (guest-to-registered user conversion), JWT access + refresh token management, password hashing algorithm selection, session storage strategies, and critical security patterns including timing attack prevention and token uniqueness.

## Key Findings

### 1. Anonymous-First Authentication (Guest-to-Registered User Conversion)

**Industry Pattern (2026)**: Anonymous-first authentication is a well-established pattern supported by major auth platforms (Descope, FusionAuth, SuperTokens) with consistent implementation approaches.

**Core Implementation Strategy:**
- Create anonymous JWT with a unique user ID (UUID or prefixed ID like "G-...")
- Store user ID in the `sub` (subject) claim
- Maintain same user ID during conversion to registered account
- Associate user ID with real-world identifier (email/phone) upon registration
- Preserve all gathered user data (traits, activity, attribution) through conversion

**Key Benefits:**
- No database space consumed for anonymous users (JWT-only storage)
- Seamless data continuity from anonymous to authenticated state
- User attribution tracking from first visit through conversion
- RFC 7523 compliant (allows anonymous/pseudonymous users in `sub` claim)

**Best Practices:**
- Use long-lived JWTs for anonymous sessions (low security risk)
- Use UUIDs for collision resistance
- Consider prefixed IDs (e.g., "G-{uuid}") for easy identification
- Store JWT in HttpOnly cookies (not localStorage)

### 2. JWT Access + Refresh Token Best Practices (2026)

**Refresh Token Rotation** (Critical Security Pattern):
- Every token refresh generates a NEW refresh token
- Old refresh token is immediately invalidated
- Eliminates long-lived token vulnerability
- Industry standard across Auth0, Descope, and modern auth systems

**Recommended Token Lifespans:**
- **Access tokens**: 5-15 minutes (consensus: 15 minutes for UX balance)
- **Refresh tokens**: 7-30 days (consensus: 7-14 days with rotation)
- Short access tokens minimize damage window if compromised
- Rotating refresh tokens prevent long-term exploitation

**Automatic Reuse Detection:**
- If a refresh token is reused (potential theft indicator)
- Invalidate entire token family for that user
- Force re-authentication
- Critical security feature for detecting token theft

**Storage Security (2026 Consensus):**
```
❌ NEVER: localStorage, sessionStorage (vulnerable to XSS)
✅ ALWAYS: HttpOnly, Secure, SameSite cookies
✅ SEPARATE: Store access and refresh tokens separately
```

**Additional Security Measures:**
- Rate limiting on token endpoints (prevent brute force)
- Never embed sensitive data in JWT payload
- Use secure signing algorithms: HS256 (symmetric) or RS256 (asymmetric)
- Implement token revocation for critical events:
  - Password changes
  - Explicit logout
  - Suspicious activity detection
  - Account compromise
  - Administrative suspension

### 3. Password Hashing: bcrypt vs Argon2 (OWASP 2026)

**OWASP Primary Recommendation: Argon2id**

```
Minimum Configuration:
- Memory: 19 MiB (19,456 KB)
- Iterations: 2
- Parallelism: 1

Alternative (equivalent security):
- Memory: 46 MiB (47,104 KB)
- Iterations: 1
- Parallelism: 1
```

**Why Argon2id:**
- Winner of Password Hashing Competition (PHC) 2015
- RFC 9106 specification compliant
- Memory-hard algorithm (resists GPU/ASIC attacks)
- CPU-intensive (resists brute force)
- Argon2id variant protects against side-channel timing attacks
- Designed for evolving hardware attack landscape

**bcrypt Status (2026):**
```
Status: Legacy algorithm for systems where Argon2 unavailable
OWASP minimum work factor: 10
Expected 2026 work factor: 13-14 (significantly higher)
Maximum input length: 72 bytes (limitation)
Weakness: Less resistant to GPU/ASIC attacks vs memory-hard algorithms
```

**Migration Recommendation:**
- **New projects**: Use Argon2id exclusively
- **Existing projects with bcrypt**:
  - Continue using bcrypt if well-configured (work factor 13-14)
  - Plan migration to Argon2id for new passwords
  - Re-hash on successful login (opportunistic migration)
  - bcrypt is still acceptable but not optimal

**Hierarchy of Recommendations:**
1. **Best**: Argon2id (primary choice)
2. **Good**: scrypt (when Argon2 unavailable, min cost 2^17)
3. **Acceptable**: bcrypt (legacy systems, work factor 13-14)

### 4. Session Management: Database vs Redis for Refresh Tokens

**Performance Comparison:**

| Storage | Lookup Time | Use Case |
|---------|-------------|----------|
| Redis | 2-3ms | High-traffic applications |
| PostgreSQL | 5-20ms | Standard applications |
| JWT-only (stateless) | 0.5ms (no network) | 99% of requests (access tokens) |

**Hybrid Approach (Recommended for the project):**
- Access tokens: Stateless JWT (no DB lookup)
- Refresh tokens: Database-stored (PostgreSQL or Redis)
- Only hits database on token refresh (~1% of requests)
- Combines JWT speed with revocation capability

**Redis Benefits:**
- Sub-millisecond token retrieval
- Native auto-expiration (TTL)
- No background job needed for cleanup
- Ideal for high-concurrency scenarios

**Database (PostgreSQL) Benefits:**
- Single source of truth (no sync issues)
- Simpler architecture (one storage system)
- ACID guarantees
- Better for audit trails and compliance
- No additional infrastructure needed

**Trade-offs:**

**Redis Approach:**
- ✅ 60-85% faster token refresh
- ✅ Native expiration handling
- ❌ Additional infrastructure to manage
- ❌ Risk of auth failure if Redis down
- ❌ Sync complexity between Redis and DB

**Database Approach:**
- ✅ Simpler architecture (single storage)
- ✅ No sync issues
- ✅ Better durability guarantees
- ❌ Slower token refresh (still acceptable: 5-20ms)
- ❌ Requires cleanup job for expired tokens

**Recommendation for the project:**
- **Start with PostgreSQL** (current implementation)
- Database refresh token storage is acceptable for most applications
- 5-20ms refresh latency is imperceptible to users
- Simpler architecture reduces operational complexity
- **Consider Redis migration if:**
  - Token refresh latency becomes measurable in user experience
  - Application scales beyond 10,000 concurrent users
  - Token blacklisting becomes performance bottleneck

### 5. NestJS + Passport.js JWT Patterns (2026)

**Dual Strategy Pattern (Industry Standard):**

```typescript
// 1. AccessTokenStrategy
@Injectable()
export class AccessTokenStrategy extends PassportStrategy(Strategy, 'jwt-access') {
  constructor() {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      secretOrKey: process.env.JWT_ACCESS_SECRET,
    });
  }

  validate(payload: any) {
    return { userId: payload.sub, email: payload.email };
  }
}

// 2. RefreshTokenStrategy
@Injectable()
export class RefreshTokenStrategy extends PassportStrategy(Strategy, 'jwt-refresh') {
  constructor() {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      secretOrKey: process.env.JWT_REFRESH_SECRET,
      passReqToCallback: true, // Critical: provides request object to validate()
    });
  }

  validate(req: Request, payload: any) {
    const refreshToken = req.get('Authorization').replace('Bearer', '').trim();
    return {
      userId: payload.sub,
      refreshToken, // Needed for rotation/revocation
    };
  }
}
```

**Guard Pattern:**

```typescript
// JWT Access Guard (most endpoints)
@Injectable()
export class JwtAccessGuard extends AuthGuard('jwt-access') {}

// JWT Refresh Guard (token refresh endpoint only)
@Injectable()
export class JwtRefreshGuard extends AuthGuard('jwt-refresh') {}

// Usage
@Get('profile')
@UseGuards(JwtAccessGuard)
async getProfile(@Request() req) {
  return req.user; // Populated by AccessTokenStrategy.validate()
}

@Post('refresh')
@UseGuards(JwtRefreshGuard)
async refresh(@Request() req) {
  // req.user contains userId and refreshToken from RefreshTokenStrategy
  return this.authService.refreshTokens(req.user.userId, req.user.refreshToken);
}
```

**Refresh Token Storage Pattern:**

```typescript
// Store hashed refresh token in database
async updateRefreshToken(userId: string, refreshToken: string) {
  const hashedToken = await bcrypt.hash(refreshToken, 10);
  await this.prisma.user.update({
    where: { id: userId },
    data: { refreshTokenHash: hashedToken },
  });
}

// Validate refresh token
async validateRefreshToken(userId: string, refreshToken: string): Promise<boolean> {
  const user = await this.prisma.user.findUnique({ where: { id: userId } });
  if (!user?.refreshTokenHash) return false;
  return bcrypt.compare(refreshToken, user.refreshTokenHash);
}
```

**Token Rotation Implementation:**

```typescript
async refreshTokens(userId: string, refreshToken: string) {
  // 1. Validate current refresh token
  const isValid = await this.validateRefreshToken(userId, refreshToken);
  if (!isValid) {
    throw new ForbiddenException('Invalid refresh token');
  }

  // 2. Generate new token pair
  const tokens = await this.generateTokens(userId, email);

  // 3. Store new refresh token hash (invalidates old one)
  await this.updateRefreshToken(userId, tokens.refreshToken);

  // 4. Return new tokens
  return tokens;
}
```

**Key NestJS Patterns:**
- Separate strategies for access vs refresh tokens
- `passReqToCallback: true` in RefreshTokenStrategy to extract token
- Guards extend AuthGuard with strategy names
- Store hashed refresh tokens in database (never plaintext)
- Automatic token rotation on each refresh

### 6. Security Patterns: Timing Attack Prevention

**The Vulnerability:**

```typescript
// ❌ VULNERABLE: Reveals user existence via timing difference
async login(email: string, password: string) {
  const user = await this.findUserByEmail(email);

  // If user doesn't exist, returns immediately (fast)
  if (!user) {
    throw new UnauthorizedException('Invalid credentials');
  }

  // If user exists, bcrypt comparison takes ~100-300ms (slow)
  const isValid = await bcrypt.compare(password, user.passwordHash);
  if (!isValid) {
    throw new UnauthorizedException('Invalid credentials');
  }

  return this.generateTokens(user);
}
```

**Attack**: Attacker measures response time:
- 5ms response → user doesn't exist (no bcrypt comparison)
- 150ms response → user exists (bcrypt comparison performed)
- Result: Username/email enumeration via timing analysis

**The Fix: Dummy Hash Pattern (2026 Best Practice)**

```typescript
// Precompute at application startup
const DUMMY_HASH = '$2b$12$dummy.hash.for.timing.attack.prevention.padding';

async login(email: string, password: string) {
  const user = await this.findUserByEmail(email);

  // ALWAYS perform bcrypt comparison (constant time)
  const hashToCompare = user?.passwordHash ?? DUMMY_HASH;
  const isValid = await bcrypt.compare(password, hashToCompare);

  // Only succeed if user exists AND password matches
  if (!user || !isValid) {
    throw new UnauthorizedException('Invalid credentials');
  }

  return this.generateTokens(user);
}
```

**Why This Works:**
- Always performs bcrypt comparison (same time regardless of user existence)
- Uses real user hash if exists, dummy hash if not
- Timing is consistent: ~100-300ms for all login attempts
- Prevents username enumeration via timing analysis
- Recommended by Django, Rails, and modern auth frameworks (2025-2026)

**Additional Timing Attack Mitigations:**
- Use constant-time comparison functions for all security-critical operations
- Exclude network I/O from constant-time calculations (attacker can manipulate)
- Consider rate limiting to reduce timing measurement precision
- Use CAPTCHA after repeated failures to prevent automated timing attacks

### 7. Security Patterns: JWT Token Uniqueness (JTI)

**The Problem:**

```typescript
// Without JTI: Collision risk
const accessPayload = {
  sub: userId,
  email: user.email,
  iat: Math.floor(Date.now() / 1000),
  exp: Math.floor(Date.now() / 1000) + 900, // 15 min
};

const refreshPayload = {
  sub: userId,
  iat: Math.floor(Date.now() / 1000),
  exp: Math.floor(Date.now() / 1000) + 604800, // 7 days
};

// If both created in same second for same user → IDENTICAL SIGNATURE
// Attackers could replay access token as refresh token
```

**The Solution: JTI Claim**

```typescript
import { randomUUID } from 'crypto';

const accessPayload = {
  sub: userId,
  email: user.email,
  jti: randomUUID(), // e.g., "f47ac10b-58cc-4372-a567-0e02b2c3d479"
  iat: Math.floor(Date.now() / 1000),
  exp: Math.floor(Date.now() / 1000) + 900,
};

const refreshPayload = {
  sub: userId,
  jti: randomUUID(), // Different UUID
  iat: Math.floor(Date.now() / 1000),
  exp: Math.floor(Date.now() / 1000) + 604800,
};
```

**JTI Benefits (RFC 7519):**

1. **Collision Prevention**:
   - Ensures negligible probability of collision
   - Even tokens created in same millisecond have different signatures
   - UUIDv4 provides 128-bit randomness (2^122 unique values)

2. **Token Replay Attack Prevention**:
   - Store issued JTI values in database/Redis
   - Check for duplicates on token use
   - Reject tokens with previously-seen JTI
   - Enables one-time-use token systems

3. **Token Revocation**:
   - Revoke specific token by JTI (not entire user session)
   - Store revoked JTI values with expiration time
   - Use Redis for fast lookup (sub-millisecond)
   - More granular than revoking all tokens for a user

4. **Audit Trail**:
   - Track individual token usage
   - Correlate actions to specific token issuance
   - Forensic analysis of security incidents

**JTI Implementation Pattern:**

```typescript
// Token generation with JTI
async generateTokens(userId: string, email: string) {
  const accessJti = randomUUID();
  const refreshJti = randomUUID();

  const accessToken = this.jwtService.sign({
    sub: userId,
    email,
    jti: accessJti,
  }, {
    secret: this.configService.get('JWT_ACCESS_SECRET'),
    expiresIn: '15m',
  });

  const refreshToken = this.jwtService.sign({
    sub: userId,
    jti: refreshJti,
  }, {
    secret: this.configService.get('JWT_REFRESH_SECRET'),
    expiresIn: '7d',
  });

  // Store refresh JTI for revocation capability
  await this.storeRefreshTokenJti(userId, refreshJti);

  return { accessToken, refreshToken };
}

// Token revocation by JTI
async revokeToken(jti: string, expiresAt: Date) {
  // Store in Redis with TTL matching token expiration
  await this.redis.setex(
    `revoked:${jti}`,
    Math.floor((expiresAt.getTime() - Date.now()) / 1000),
    'revoked'
  );
}

// Token validation checks JTI
async validateToken(token: string) {
  const decoded = this.jwtService.verify(token);

  // Check if JTI is revoked
  const isRevoked = await this.redis.exists(`revoked:${decoded.jti}`);
  if (isRevoked) {
    throw new UnauthorizedException('Token has been revoked');
  }

  return decoded;
}
```

**JTI Best Practices (2026):**
- Use UUIDv4 for collision resistance (crypto.randomUUID())
- Store refresh token JTIs for revocation capability
- Use Redis for fast JTI revocation lookups
- Set TTL on revoked JTIs to match token expiration
- Include JTI in both access and refresh tokens
- Never reuse JTI values across token generations

## the project Implementation Evaluation

### Current Implementation Strengths

✅ **Anonymous-first architecture**: Well-aligned with industry patterns
✅ **JWT access + refresh tokens**: Follows dual-token best practice
✅ **Timing attack prevention**: Dummy hash pattern correctly implemented
✅ **JTI for token uniqueness**: Prevents collision vulnerabilities
✅ **bcrypt password hashing**: Acceptable for existing implementation
✅ **Database-stored refresh tokens**: Appropriate for current scale
✅ **Passport.js dual strategy**: Industry-standard NestJS pattern

### Recommendations for Enhancement

#### 1. Password Hashing Migration Path (Medium Priority)

**Current**: bcrypt with timing attack prevention
**Recommendation**: Plan migration to Argon2id

```typescript
// Hybrid approach during migration
async hashPassword(password: string): Promise<string> {
  // New passwords use Argon2id
  return argon2.hash(password, {
    type: argon2.argon2id,
    memoryCost: 19456, // 19 MiB
    timeCost: 2,
    parallelism: 1,
  });
}

async verifyPassword(password: string, hash: string): Promise<boolean> {
  // Detect hash type by prefix
  if (hash.startsWith('$2b$') || hash.startsWith('$2a$')) {
    // bcrypt hash - verify and optionally re-hash
    const isValid = await bcrypt.compare(password, hash);
    if (isValid) {
      // Opportunistic migration: re-hash with Argon2id on successful login
      // (Store new hash in background job to avoid login latency)
    }
    return isValid;
  } else {
    // Argon2 hash
    return argon2.verify(hash, password);
  }
}
```

**Timeline**: Implement in next major version (non-urgent)

#### 2. Refresh Token Rotation (High Priority)

**Current**: Single refresh token per user
**Recommendation**: Implement automatic rotation

```typescript
async refreshTokens(userId: string, oldRefreshToken: string) {
  // 1. Validate old token
  const isValid = await this.validateRefreshToken(userId, oldRefreshToken);
  if (!isValid) {
    // Potential token theft - invalidate all user tokens
    await this.revokeAllUserTokens(userId);
    throw new ForbiddenException('Invalid refresh token - all sessions revoked');
  }

  // 2. Generate new token pair
  const tokens = await this.generateTokens(userId, email);

  // 3. Store new refresh token (invalidates old one)
  await this.updateRefreshToken(userId, tokens.refreshToken);

  // 4. Log rotation for audit trail
  await this.logTokenRotation(userId, oldRefreshToken, tokens.refreshToken);

  return tokens;
}
```

**Benefits**:
- Limits damage window if refresh token stolen
- Enables automatic reuse detection
- Aligns with 2026 security best practices

#### 3. Consider Redis for Future Scale (Low Priority)

**Current**: PostgreSQL for refresh token storage
**When to consider Redis**:
- Token refresh latency becomes measurable in UX
- Concurrent users exceed 10,000
- Token blacklist becomes performance bottleneck

**Hybrid approach**:
- Keep PostgreSQL as source of truth
- Use Redis as cache layer for hot refresh tokens
- Write-through pattern (update both on token refresh)
- Fall back to PostgreSQL if Redis unavailable

#### 4. Enhanced Token Revocation (Medium Priority)

**Current**: Single refresh token per user (implicit revocation on refresh)
**Enhancement**: Explicit revocation by JTI

```typescript
// Revoke specific session
async revokeSession(userId: string, jti: string) {
  const session = await this.prisma.session.findFirst({
    where: { userId, jti },
  });

  if (!session) return;

  // Add to revocation list until expiration
  await this.redis.setex(
    `revoked:${jti}`,
    session.expiresAt - Date.now(),
    'revoked'
  );

  await this.prisma.session.update({
    where: { id: session.id },
    data: { revokedAt: new Date() },
  });
}

// Revoke all user sessions (e.g., password change)
async revokeAllUserSessions(userId: string) {
  const sessions = await this.prisma.session.findMany({
    where: { userId, revokedAt: null },
  });

  for (const session of sessions) {
    await this.revokeSession(userId, session.jti);
  }
}
```

#### 5. ID Enumeration Prevention (Already Implemented)

✅ the project correctly returns 404 (not 403) for unauthorized resource access
✅ Uses `findFirst` with both `id` and `userId` in WHERE clause
✅ Prevents attackers from discovering valid resource IDs

**Pattern to maintain**:
```typescript
// ✅ CORRECT: Prevents ID enumeration
const resource = await this.prisma.translation.findFirst({
  where: {
    id: resourceId,
    userId, // Ownership check in query
  },
});

if (!resource) {
  throw new NotFoundException('Translation not found'); // 404 for both cases
}
```

#### 6. Trial Guard Exception for DELETE (Already Implemented)

✅ DELETE endpoints correctly exclude TrialGuard
✅ Users can delete data even with expired trial
✅ Aligns with GDPR right to deletion

**Pattern to maintain**:
```typescript
// DELETE: JwtAuthGuard only
@Delete(':id')
@UseGuards(JwtAuthGuard)
async delete() { ... }

// GET/POST: Both guards
@Get()
@UseGuards(JwtAuthGuard, TrialGuard)
async findAll() { ... }
```

## Security Checklist for the project Auth

### Implemented ✅
- [x] Anonymous-first JWT pattern with UUID user IDs
- [x] Dual token system (access + refresh)
- [x] Timing attack prevention with dummy hash
- [x] JTI claim for token uniqueness
- [x] bcrypt password hashing (work factor 12+)
- [x] Database-stored refresh tokens
- [x] HttpOnly, Secure, SameSite cookies
- [x] ID enumeration prevention (404 not 403)
- [x] Trial guard exception for DELETE
- [x] NestJS Passport dual strategy pattern

### Recommended Enhancements
- [ ] **High Priority**: Refresh token rotation with reuse detection
- [ ] **Medium Priority**: Argon2id migration path for new passwords
- [ ] **Medium Priority**: Explicit token revocation by JTI
- [ ] **Low Priority**: Redis cache layer for high-scale scenarios
- [ ] **Low Priority**: Rate limiting on auth endpoints

## Project Integration

### the project Context

**Architecture Alignment**:
- Anonymous users get JWT with persistent UUID
- Guest-to-registered conversion maintains user ID and data continuity
- Translator and Deep Dive modes both use same auth system
- Mobile app and web app share JWT auth strategy

**Database Schema Considerations**:
```prisma
model User {
  id              String    @id @default(uuid())
  email           String?   @unique // Null for anonymous users
  passwordHash    String?   // Null for anonymous users
  refreshTokenHash String?
  isAnonymous     Boolean   @default(true)
  createdAt       DateTime  @default(now())
  // ... other fields
}

// Future: Track refresh token families for rotation
model RefreshToken {
  id          String    @id @default(uuid())
  jti         String    @unique
  userId      String
  user        User      @relation(fields: [userId], references: [id])
  tokenFamily String    // For token rotation reuse detection
  expiresAt   DateTime
  revokedAt   DateTime?
  createdAt   DateTime  @default(now())

  @@index([userId, revokedAt])
  @@index([jti])
}
```

**Implementation Priority**:
1. **Phase 1** (Current): Basic JWT auth with timing attack prevention ✅
2. **Phase 2** (Next): Refresh token rotation and explicit revocation
3. **Phase 3** (Future): Argon2id migration and Redis caching

## Sources

- [Boost Conversions With Anonymous Users and Guest Checkout](https://www.descope.com/blog/post/descope-flows-anonymous-users)
- [How to Support Anonymous User Accounts and Access in Your App](https://fusionauth.io/blog/anonymous-user)
- [Anonymous / Guest sessions | SuperTokens Docs](https://supertokens.com/docs/thirdparty/common-customizations/sessions/anonymous-session)
- [What Are Refresh Tokens and How to Use Them Securely | Auth0](https://auth0.com/blog/refresh-tokens-what-are-they-and-when-to-use-them/)
- [The Developer's Guide to Refresh Token Rotation](https://www.descope.com/blog/post/refresh-token-rotation)
- [Refresh Token Rotation - Auth0 Docs](https://auth0.com/docs/secure/tokens/refresh-tokens/refresh-token-rotation)
- [Password Storage - OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [Password Hashing Guide 2025: Argon2 vs Bcrypt vs Scrypt vs PBKDF2](https://guptadeepak.com/the-complete-guide-to-password-hashing-argon2-vs-bcrypt-vs-scrypt-vs-pbkdf2-2026/)
- [NestJS JWT Authentication with Refresh Tokens Complete Guide](https://www.elvisduru.com/blog/nestjs-jwt-authentication-refresh-token)
- [Part 1/3: How to Implement Refresh Tokens with Token Rotation in NestJS](https://dev.to/zenstok/how-to-implement-refresh-tokens-with-token-rotation-in-nestjs-1deg)
- [The Secret of Infinite Sessions: Transitioning to JWT, Redis, and Refresh Token Architecture](https://medium.com/@senaunalmis/the-secret-of-infinite-sessions-transitioning-to-jwt-redis-and-refresh-token-architecture-3c3bb5517864)
- [Building Scalable Authentication: The Smart Way to Handle Tokens with Redis and Database Storage](https://dev.to/harmanpreetsingh/building-scalable-authentication-the-smart-way-to-handle-tokens-with-redis-and-database-storage-1lcf)
- [JSON Web Tokens (JWT) are Dangerous for User Sessions—Here's a Solution | Redis](https://redis.io/blog/json-web-tokens-jwt-are-dangerous-for-user-sessions/)
- [The Hidden Vulnerabilities in Your Authentication System: A Deep Dive into Timing Attacks](https://dev.to/edgi/the-hidden-vulnerabilities-in-your-authentication-system-a-deep-dive-into-timing-attacks-ip-5k9)
- [Timing Attacks on Password Checks: Mitigation Tips](https://www.onlinehashcrack.com/guides/password-recovery/timing-attacks-on-password-checks-mitigation-tips.php)
- [The Hidden Power of JTI: How a Single Claim Can Stop Token Replay Attacks](https://elsyarifx.medium.com/the-hidden-power-of-jti-how-a-single-claim-can-stop-token-replay-attacks-0255fbcf6b9b)
- [Let's Understand JWT ID (jti) | MojoAuth](https://mojoauth.com/blog/let-understand-jwt-id-jti)
- [RFC 7519 - JSON Web Token (JWT)](https://datatracker.ietf.org/doc/html/rfc7519)

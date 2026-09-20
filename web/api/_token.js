import crypto from "node:crypto";

export function makeToken(attemptId) {
  const secret = process.env.SESSION_SECRET;
  if (!secret) {
    throw new Error("SESSION_SECRET is not set");
  }
  return crypto.createHmac("sha256", secret).update(String(attemptId)).digest("hex");
}

export function verifyToken(attemptId, token) {
  if (typeof token !== "string" || !token) return false;
  let expected;
  try {
    expected = makeToken(attemptId);
  } catch (err) {
    console.error("verifyToken: could not compute expected token:", err.message);
    return false;
  }
  const a = Buffer.from(expected, "hex");
  const b = Buffer.from(token, "hex");
  if (a.length !== b.length) return false;
  return crypto.timingSafeEqual(a, b);
}

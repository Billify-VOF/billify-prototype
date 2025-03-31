import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function base64_urlencode(str: string) {
  const encoder = new TextEncoder();
  const uint8Array = encoder.encode(str);
  const urlencoded = btoa(String.fromCharCode.apply(null, uint8Array))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");

  return urlencoded;
}

export function generateCodeVerifier(): string {
  const allowedChars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~";
  // Random length between 43-128 because that is the CodeVerifier requirement
  const length = Math.floor(Math.random() * (128 - 43 + 1)) + 43;

  const randomBytes = new Uint8Array(length);

  crypto.getRandomValues(randomBytes);

  let result = "";

  for (let i = 0; i < length; i++) {
    result += allowedChars.charAt(randomBytes[i] % allowedChars.length);
  }

  return result;
}

export async function sha256Base64(input: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(input);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);

  return btoa(String.fromCharCode(...new Uint8Array(hashBuffer)));
}

export async function generateCodeChallenge(): Promise<string> {
  const codeVerifier = generateCodeVerifier();
  const sha256 = await sha256Base64(codeVerifier);
  const codeChallenge = base64_urlencode(sha256);

  return codeChallenge;
}

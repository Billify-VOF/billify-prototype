import { Ponto_Connect_2_Options } from '@/constants/api';
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function base64_urlencode(str: string) {
  const encoder = new TextEncoder();
  const uint8Array = encoder.encode(str);
  const urlencoded = btoa(String.fromCharCode.apply(null, uint8Array))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');

  return urlencoded;
}

export function getSecureRandomInt(min: number, max: number) {
  const range = max - min + 1;
  const bytesNeeded = Math.ceil(Math.log2(range) / 8);
  const randomBytes = new Uint8Array(bytesNeeded);
  crypto.getRandomValues(randomBytes);
  let randomValue = 0;
  for (let i = 0; i < bytesNeeded; i++) {
    randomValue = (randomValue << 8) | randomBytes[i];
  }
  return min + (randomValue % range);
}

export function generateCodeVerifier(): string {
  const allowedChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
  // Random length between 43-128 because that is the CodeVerifier requirement
  const length = getSecureRandomInt(43, 128);

  const randomBytes = new Uint8Array(length);

  crypto.getRandomValues(randomBytes);

  let result = '';

  for (let i = 0; i < length; i++) {
    result += allowedChars.charAt(randomBytes[i] % allowedChars.length);
  }

  return result;
}

export async function sha256Base64(input: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(input);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);

  return btoa(String.fromCharCode(...new Uint8Array(hashBuffer)));
}

export async function generateCodeChallenge(): Promise<string> {
  const codeVerifier = generateCodeVerifier();
  const sha256 = await sha256Base64(codeVerifier);
  const codeChallenge = base64_urlencode(sha256);

  return codeChallenge;
}

export const generatePontoOAuthUrl = async () => {
  try {
    const state = base64_urlencode(generateCodeVerifier());
    const codeChallenge = await generateCodeChallenge();
    return `${Ponto_Connect_2_Options.OAUTH_URL}?client_id=${Ponto_Connect_2_Options.CLIENT_ID}&redirect_uri=${Ponto_Connect_2_Options.REDIRECT_URI}&response_type=code&scope=${Ponto_Connect_2_Options.SCOPE}&state=${state}&code_challenge=${codeChallenge}&code_challenge_method=${Ponto_Connect_2_Options.CODE_CHALLENGE_METHOD}`;
  } catch (error) {
    console.log('Failed to generate Ponto OAuth URL');
    throw error;
  }
};

import { Ponto_Connect_2_Options } from '@/constants/api';
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function base64_urlencode(data: ArrayBuffer) {
  const urlencoded = btoa(String.fromCharCode.apply(null, Array.from(new Uint8Array(data))))
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

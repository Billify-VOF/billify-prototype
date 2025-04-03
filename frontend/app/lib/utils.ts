import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * A utility function that combines multiple className values and handles Tailwind class conflicts
 * @param inputs - Array of class names, conditional classes, or className objects
 * @returns A merged and optimized className string
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const lightenColor = (hex?: string, percent: number = 0.7): string => {
  if (!hex || hex === '#') {
    return '';
  }

  let r = parseInt(hex.substring(1, 3), 16);
  let g = parseInt(hex.substring(3, 5), 16);
  let b = parseInt(hex.substring(5, 7), 16);

  r = Math.min(255, r + (255 - r) * percent);
  g = Math.min(255, g + (255 - g) * percent);
  b = Math.min(255, b + (255 - b) * percent);

  return `rgb(${Math.round(r)}, ${Math.round(g)}, ${Math.round(b)})`;
};

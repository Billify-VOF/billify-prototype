import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * A utility function that combines multiple className values and handles Tailwind class conflicts
 * @param inputs - Array of class names, conditional classes, or className objects
 * @returns A merged and optimized className string
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
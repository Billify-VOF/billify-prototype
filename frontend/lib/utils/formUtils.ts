/**
 * Utility functions for form handling
 */

export interface ApiError {
  error: Record<string, string[]>;
}

export interface FormErrors {
  [key: string]: string | undefined;
}

/**
 * Parse API error response and convert to form errors
 * @param error The error from the API
 * @returns FormErrors object with field-specific errors
 */
export function parseFormValidationError(error: unknown): FormErrors {
  if (error instanceof Error) {
    try {
      const errorData = JSON.parse(error.message) as ApiError;
      if (errorData.error) {
        const formErrors: FormErrors = {};
        
        // Process each field error
        Object.entries(errorData.error).forEach(([field, messages]) => {
          if (Array.isArray(messages) && messages.length > 0) {
            formErrors[field] = messages[0];
          }
        });
        
        return formErrors;
      }
    } catch {
      // If parsing fails, return general error
      return { general: error.message };
    }
  }
  
  return { general: "An unexpected error occurred" };
} 
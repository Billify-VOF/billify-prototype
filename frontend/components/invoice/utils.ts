export const getDueDateMessage = (level?: string): string => {
  if (!level) {
    return 'Unknown due date';
  }
  switch (level) {
    case 'OVERDUE':
      return 'Past due date';
    case 'CRITICAL':
      return 'Due within a week';
    case 'HIGH':
      return 'Due in 1-2 weeks';
    case 'MEDIUM':
      return 'Due in 2-4 weeks';
    case 'LOW':
      return 'Due in more than a month (30+)';
    default:
      return 'Unknown due date';
  }
};

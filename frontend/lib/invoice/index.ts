import { UrgencyLevel, URGENCY_LEVELS, Urgency } from '../../components/definitions/invoice';

export const getDueDateMessage = (level?: string): string => {
  if (!level) {
    return 'Unknown due date';
  }
  switch (level) {
    case UrgencyLevel.OVERDUE:
      return 'Past due date';
    case UrgencyLevel.CRITICAL:
      return 'Due within a week';
    case UrgencyLevel.HIGH:
      return 'Due in 1-2 weeks';
    case UrgencyLevel.MEDIUM:
      return 'Due in 2-4 weeks';
    case UrgencyLevel.LOW:
      return 'Due in more than a month (30+)';
    default:
      return 'Unknown due date';
  }
};

export const calculateUrgencyFromDays = (days: number): Urgency => {
  let calculatedUrgency: UrgencyLevel;

  if (days < 0) {
    calculatedUrgency = UrgencyLevel.OVERDUE;
  } else if (0 <= days && days <= 7) {
    calculatedUrgency = UrgencyLevel.CRITICAL;
  } else if (8 <= days && days <= 14) {
    calculatedUrgency = UrgencyLevel.HIGH;
  } else if (15 <= days && days <= 30) {
    calculatedUrgency = UrgencyLevel.MEDIUM;
  } else {
    calculatedUrgency = UrgencyLevel.LOW;
  }

  return URGENCY_LEVELS.find((urgency) => urgency.level === calculatedUrgency) || URGENCY_LEVELS[0];
};

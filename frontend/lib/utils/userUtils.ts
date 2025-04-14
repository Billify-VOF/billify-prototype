import { User } from '../definitions/auth';

export const getDisplayName = (user: User | null): string => {
  if (!user) return 'User';

  if (user.firstName && user.lastName) {
    return `${user.firstName} ${user.lastName}`;
  }

  return user.username || 'User';
};

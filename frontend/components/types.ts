export type SearchItemResult = {
  id: string;
  name: string;
  description: string;
};

export const dummySearchResults: SearchItemResult[] = [
  {
    id: '1',
    name: 'Invoice #1001',
    description:
      'Issued to John Doe for website development services - $1,200 due by March 10, 2025.',
  },
  {
    id: '2',
    name: 'Invoice #1002',
    description: 'Monthly subscription payment for SaaS platform - $99 paid via credit card.',
  },
  {
    id: '3',
    name: 'Invoice #1003',
    description: 'Consulting fee for business strategy session - $500, pending payment.',
  },
  {
    id: '4',
    name: 'Invoice #1004',
    description: 'E-commerce order invoice for 3 electronic items - $850, paid via PayPal.',
  },
  {
    id: '5',
    name: 'Invoice #1005',
    description: 'Annual software license renewal - $299 billed to Acme Inc.',
  },
  {
    id: '6',
    name: 'Invoice #1006',
    description: 'Freelance graphic design project - $750, payment expected by March 15, 2025.',
  },
  {
    id: '7',
    name: 'Invoice #1007',
    description: 'Office supplies purchase invoice - $125, paid via bank transfer.',
  },
  {
    id: '8',
    name: 'Invoice #1008',
    description: 'IT infrastructure maintenance charges - $2,000 due in 30 days.',
  },
  {
    id: '9',
    name: 'Invoice #1009',
    description: 'Rental payment for co-working space - $450, paid on February 1, 2025.',
  },
  {
    id: '10',
    name: 'Invoice #1010',
    description: 'Marketing campaign services invoice - $3,500, awaiting approval.',
  },
];

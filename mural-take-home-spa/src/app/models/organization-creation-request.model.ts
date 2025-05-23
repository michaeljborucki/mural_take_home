export type OrganizationType = 'individual' | 'business';

export interface OrganizationCreationRequest {
  type: OrganizationType;
  email: string;

  // For individual
  firstName?: string;
  lastName?: string;

  // For business
  businessName?: string;
}

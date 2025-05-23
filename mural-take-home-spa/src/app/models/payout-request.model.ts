export interface PayoutRequest {
    sourceAccountId: string;
    memo?: string;
    payouts: PayoutItem[];
  }
  
  export interface PayoutItem {
    amount: TokenAmount;
    payoutDetails: PayoutDetails;
    recipientInfo: RecipientInfo;
  }
  
  export interface TokenAmount {
    tokenSymbol: string;   // e.g., "USDC"
    tokenAmount: number;
  }
  
  export interface PayoutDetails {
    type: string; // e.g., "fiat"
    bankName: string;
    bankAccountOwner: string;
    fiatAndRailDetails: FiatAndRailDetails;
  }
  
  export interface FiatAndRailDetails {
    type: string;              // e.g., "cop"
    symbol: string;            // e.g., "COP"
    accountType: string;       // e.g., "CHECKING"
    phoneNumber: string;
    bankAccountNumber: string;
    documentNumber: string;
    documentType: string;      // e.g., "NATIONAL_ID"
  }
  
  export interface RecipientInfo {
    type: string;              // e.g., "individual"
    firstName: string;
    lastName: string;
    email: string;
    dateOfBirth: string;       // e.g., "YYYY-MM-DD"
    physicalAddress: PhysicalAddress;
  }
  
  export interface PhysicalAddress {
    address1: string;
    country: string;
    state: string;
    city: string;
    zip: string;
  }
  
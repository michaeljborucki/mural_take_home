export interface Payout {
    id: string;
    status: string;
    memo: string;
    sourceAccountId: string;
    transactionHash: string;
    createdAt: string; // ISO string
    updatedAt: string;
    payouts: SinglePayout[];
  }
  
  export interface SinglePayout {
    id: string;
    createdAt: string;
    updatedAt: string;
    amount: TokenAmount;
    details: PayoutDetails;
  }
  
  export interface TokenAmount {
    tokenAmount: number;
    tokenSymbol: string;
  }
  
  export interface PayoutDetails {
    type: string; // e.g., "fiat"
    exchangeFeePercentage: number;
    exchangeRate: number;
    feeTotal: TokenAmount;
    transactionFee: TokenAmount;
    fiatAmount: FiatAmount;
    fiatAndRailCode: string;
    fiatPayoutStatus: FiatPayoutStatus;
  }
  
  export interface FiatAmount {
    fiatAmount: number;
    fiatCurrencyCode: string;
  }
  
  export interface FiatPayoutStatus {
    type: string;
    initiatedAt?: string;
  }
  
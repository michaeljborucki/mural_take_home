export interface Organization {
    id: string;
    name: string;
    type: string;
    createdAt: string;
    updatedAt: string;
    kycStatus: {
      type: string;
      kycUrl?: string;
    };
    tosStatus: string;
    currencyCapabilities: CurrencyCapability[];
  }
  
  export interface CurrencyCapability {
    currencyCode: string;
    fiatAndRailCode: string;
    depositStatus: {
      type: 'enabled' | 'disabled';
      reason?: string;
      details?: string;
    };
    payOutStatus: {
      type: 'enabled' | 'disabled';
    };
  }
  